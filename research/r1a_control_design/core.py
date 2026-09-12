"""Outcome-blind control allocation. No prices, returns or significance tests.

A fixed, chronological design screen; diagnostic shadows are not fallback
strategies. Inclusion losses always remain in the original-event denominator.
"""
from __future__ import annotations
from bisect import insort
import numpy as np
import pandas as pd

FEATURES = ('parent_abs_drift', 'parent_efficiency', 'log1p_parent_age_bars', 'local_vol_30_over_240')
HORIZONS = (1, 5, 15, 30, 60, 120, 240)
STAGES = ('PAST_NEAREST', 'PAST_CALIPER', 'PAST_CALIPER_EXCLUSIVE')
SPAN = 240
CALIPER = 0.5
COVERAGE_MIN = 0.80
BALANCE_MAX = 0.10
IDENTITY = ('symbol', 'entry_idx', 'day', 'calendar_year', 'parent_direction', 'clock_bucket')


def require(ok, message):
    if not bool(ok):
        raise ValueError(message)


def check_features(frame: pd.DataFrame) -> pd.DataFrame:
    allowed = set(IDENTITY) | set(FEATURES)
    require(set(frame.columns) == allowed, 'allocator only accepts identity/time/covariate columns')
    f = frame.copy()
    require(f[list(FEATURES)].apply(pd.to_numeric, errors='raise').notna().all().all(), 'missing feature')
    require(np.isfinite(f[list(FEATURES)].to_numpy(float)).all(), 'nonfinite feature')
    for col in ('entry_idx', 'parent_direction', 'clock_bucket'):
        x = pd.to_numeric(f[col], errors='raise').to_numpy(float)
        require(np.isfinite(x).all() and np.equal(x, np.floor(x)).all(), 'invalid integer identity')
        f[col] = x.astype(np.int64)
    require((f.entry_idx >= 1).all() and f.parent_direction.isin([-1, 1]).all(), 'bad clock/direction')
    require(not f[['symbol', 'entry_idx']].duplicated().any(), 'duplicate input identity')
    f['calendar_year'] = f.calendar_year.astype(str)
    f['day'] = f.day.astype(str)
    require((f.day.str[:4] == f.calendar_year).all(), 'calendar year mismatch')
    return f.sort_values('entry_idx', kind='stable').reset_index(drop=True)


def prefix_scale(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    require(x.ndim == 2 and x.shape[1] == 4 and len(x) > 0, 'empty prefix')
    center = np.median(x, axis=0)
    scale = np.median(np.abs(x-center), axis=0)*1.4826
    sd = np.std(x, axis=0, ddof=0)
    scale = np.where(scale > 0, scale, np.where(sd > 0, sd, 1.0))
    return center, scale


def free_intervals(starts: np.ndarray, reserved: list[int]) -> np.ndarray:
    """Inclusive price intervals [c,c+240]; even a shared endpoint is blocked."""
    if not reserved:
        return np.ones(len(starts), dtype=bool)
    s = np.asarray(reserved, dtype=np.int64)
    pos = np.searchsorted(s, starts, side='left')
    lo = s[np.maximum(pos-1, 0)]
    hi = s[np.minimum(pos, len(s)-1)]
    return ((pos == 0) | (starts-lo > SPAN)) & ((pos == len(s)) | (hi-starts > SPAN))


def allocate(events: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    e, c = check_features(events), check_features(controls)
    require(e.symbol.nunique() == 1, 'allocate exactly one symbol per call')
    require(c.empty or set(c.symbol) == set(e.symbol), 'wrong control symbol')
    years = {y: g.reset_index(drop=True) for y, g in c.groupby('calendar_year', sort=True)}
    reserved: list[int] = []
    rows, norms = [], []
    for event in e.itertuples(index=False):
        cutoff = int(event.entry_idx)-1
        pool = years.get(str(event.calendar_year), c.iloc[:0])
        count = int(np.searchsorted(pool.entry_idx.to_numpy(int), cutoff-SPAN, side='right'))
        mature = pool.iloc[:count]
        x = np.asarray([getattr(event, f) for f in FEATURES], float)
        center, scale = prefix_scale(mature[list(FEATURES)].to_numpy(float)) if count else (np.full(4, np.nan), np.full(4, np.nan))
        norm = {'symbol': event.symbol, 'event_entry_idx': int(event.entry_idx), 'information_cutoff_idx': cutoff,
                'mature_prefix_rows': count, 'maximum_control_source_idx': int(mature.entry_idx.max()) if count else -1}
        norm.update({f'center_{f}': center[k] for k,f in enumerate(FEATURES)})
        norm.update({f'scale_{f}': scale[k] for k,f in enumerate(FEATURES)})
        norms.append(norm)
        block = mature.loc[(mature.parent_direction == event.parent_direction) & (mature.clock_bucket == event.clock_bucket)]
        delta = (block[list(FEATURES)].to_numpy(float)-x)/scale
        dist2 = np.sum(delta*delta, axis=1)
        cap = np.max(np.abs(delta), axis=1) <= CALIPER if len(block) else np.zeros(0, bool)
        free = free_intervals(block.entry_idx.to_numpy(int), reserved)
        for stage in STAGES:
            allowed = np.ones(len(block), bool) if stage == STAGES[0] else cap if stage == STAGES[1] else cap & free
            row = {'symbol': event.symbol, 'stage': stage, 'event_entry_idx': int(event.entry_idx),
                   'event_day': event.day, 'calendar_year': str(event.calendar_year), 'parent_direction': int(event.parent_direction),
                   'side': 'LONG' if event.parent_direction > 0 else 'SHORT', 'clock_bucket': int(event.clock_bucket),
                   'information_cutoff_idx': cutoff, 'mature_prefix_rows': count,
                   'mature_exact_candidates': len(block), 'caliper_candidates': int(cap.sum()),
                   'unreserved_caliper_candidates': int((cap & free).sum()), 'matched': bool(allowed.any()),
                   'control_entry_idx': -1, 'control_day': '', 'distance': np.nan, 'maximum_scaled_gap': np.nan}
            row.update({f'event_{f}': x[k] for k,f in enumerate(FEATURES)})
            row.update({f'control_{f}': np.nan for f in FEATURES})
            if allowed.any():
                pos = np.flatnonzero(allowed)
                j = int(pos[np.argmin(dist2[pos])])
                chosen = block.iloc[j]
                row.update({'control_entry_idx': int(chosen.entry_idx), 'control_day': str(chosen.day),
                            'distance': float(np.sqrt(dist2[j])), 'maximum_scaled_gap': float(np.max(np.abs(delta[j]))),
                            'reason': 'MATCHED'})
                row.update({f'control_{f}': float(chosen[f]) for f in FEATURES})
                if stage == STAGES[2]:
                    insort(reserved, int(chosen.entry_idx))
            else:
                row['reason'] = 'NO_MATURE_EXACT_STRATUM' if block.empty else 'NO_CALIPER_SUPPORT' if not cap.any() else 'INTERVAL_CAPACITY_BLOCKED'
            rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(norms)


def standardized(numerator: float, denominator: float):
    if not np.isfinite(numerator) or not np.isfinite(denominator):
        return None
    if denominator > 0:
        return float(numerator/denominator)
    return 0.0 if abs(numerator) <= 1e-12 else None


def groups(f: pd.DataFrame):
    yield 'POOLED', f
    for year,g in f.groupby('calendar_year', sort=True):
        yield 'YEAR_'+str(year),g
    for side,g in f.groupby('side', sort=True):
        yield 'SIDE_'+side,g
    for (year,side),g in f.groupby(['calendar_year','side'], sort=True):
        yield 'YEAR_SIDE_'+str(year)+'_'+side,g


def coverage_balance(ledger: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    coverage, balance = [], []
    for (symbol,stage),f in ledger.groupby(['symbol','stage'], sort=True):
        for group,g in groups(f):
            m = g.loc[g.matched]
            required = group == 'POOLED' or len(g) >= 30
            rate = len(m)/len(g)
            cv = {'symbol':symbol,'stage':stage,'group':group,'original_events':len(g),'matched_events':len(m),
                  'coverage':rate,'gate_required':required,'coverage_pass':rate >= COVERAGE_MIN,
                  'no_mature_exact':int((g.reason == 'NO_MATURE_EXACT_STRATUM').sum()),
                  'no_caliper_support':int((g.reason == 'NO_CALIPER_SUPPORT').sum()),
                  'interval_blocked':int((g.reason == 'INTERVAL_CAPACITY_BLOCKED').sum())}
            passed = True
            for feature in FEATURES:
                full = g['event_'+feature].to_numpy(float)
                ev = m['event_'+feature].to_numpy(float); co = m['control_'+feature].to_numpy(float)
                den = float(np.std(full, ddof=0))
                smd = standardized(float(np.mean(ev)-np.mean(co)),den) if len(m) else None
                shift = standardized(float(np.mean(ev)-np.mean(full)),den) if len(m) else None
                ve,vc = (float(np.var(ev)),float(np.var(co))) if len(m) else (np.nan,np.nan)
                vr = ve/vc if vc > 0 else 1.0 if vc == ve == 0 else None
                ok = smd is not None and shift is not None and abs(smd) <= BALANCE_MAX and abs(shift) <= BALANCE_MAX
                passed &= ok
                balance.append({'symbol':symbol,'stage':stage,'group':group,'feature':feature,'original_events':len(g),
                    'matched_events':len(m),'original_event_SD':den,'matched_SMD':smd,'retention_shift_SMD':shift,
                    'matched_event_control_variance_ratio':vr,'gate_required':required,'balance_pass':ok})
            cv['balance_pass'] = bool(passed)
            coverage.append(cv)
    return pd.DataFrame(coverage), pd.DataFrame(balance)


def overlap_pairs(starts: np.ndarray, h: int) -> int:
    s = np.sort(np.asarray(starts, int))
    return int(sum(int(np.searchsorted(s, x+h, side='right'))-i-1 for i,x in enumerate(s)))


def incidence(starts: np.ndarray, directions: np.ndarray, h: int, n: int) -> np.ndarray:
    """Unit incidence on return increments (entry,entry+h], NOT price weights."""
    starts = np.asarray(starts, int); directions = np.asarray(directions, int)
    require(len(starts) == len(directions) and (starts >= 0).all() and (starts+h < n).all(), 'interval outside clock')
    z = np.zeros(n+1, dtype=np.int64)
    np.add.at(z, starts+1, directions)
    np.add.at(z, starts+h+1, -directions)
    return np.cumsum(z[:-1])


def geometry(e: np.ndarray, c: np.ndarray, d: np.ndarray, day_codes: np.ndarray, h: int) -> dict:
    n = len(day_codes); count = len(c)
    we = incidence(e,d,h,n); wc = incidence(c,d,h,n)
    ae = incidence(e,np.ones(count,int),h,n); ac = incidence(c,np.ones(count,int),h,n)
    ee,cc,ec = float(we@we),float(wc@wc),float(we@wc)
    _,reuse = np.unique(c,return_counts=True)
    daily = np.bincount(day_codes,weights=ac)
    total = float(daily.sum())
    return {'pairs':count,'unique_controls':len(reuse),'maximum_exact_reuse':int(reuse.max()) if len(reuse) else 0,
            'control_inclusive_overlap_pairs':overlap_pairs(c,h),'maximum_control_increment_multiplicity':int(ac.max()),
            'control_increment_minutes_used_more_than_once':int((ac>1).sum()),
            'event_control_shared_increment_minutes':int(((ae>0)&(ac>0)).sum()),
            'within_pair_interval_overlaps':int((np.abs(e-c) <= h).sum()),
            'event_unit_energy':ee,'control_unit_energy':cc,'net_unit_energy':float((we-wc)@(we-wc)),
            'control_unit_energy_ratio_NOT_variance_effect':cc/(count*h) if count else None,
            'unit_covariance_cancellation_NOT_observed_noise':2*ec/(ee+cc) if ee+cc else None,
            'control_calendar_HHI_unit_incidence':float(np.sum((daily/total)**2)) if total else None,
            'largest_control_day_unit_share':float(daily.max()/total) if total else None,
            'control_after_event_count':int((c>e).sum()),'full_240_maturity_violations':int((c+SPAN>e-1).sum())}


def make_geometry(ledger: pd.DataFrame, legacy: pd.DataFrame, clocks: dict) -> pd.DataFrame:
    rows = []
    for symbol,base in legacy.groupby('symbol',sort=True):
        e=base.event_entry_idx.to_numpy(int); c=base.control_entry_idx.to_numpy(int); d=base.parent_direction.to_numpy(int)
        for h in HORIZONS:
            rows.append({'symbol':symbol,'stage':'ORIGINAL_REFERENCE','cohort':'ALL_ORIGINAL_EVENTS','horizon':h,
                         **geometry(e,c,d,clocks[symbol],h)})
        old = base.set_index('event_entry_idx')
        for stage in STAGES:
            m=ledger.loc[(ledger.symbol==symbol)&(ledger.stage==stage)&ledger.matched]
            e=m.event_entry_idx.to_numpy(int); c=m.control_entry_idx.to_numpy(int); d=m.parent_direction.to_numpy(int)
            oc=old.loc[e,'control_entry_idx'].to_numpy(int)
            for h in HORIZONS:
                for cohort,cp in [('NEW_ASSIGNMENT_SAME_EVENTS',c),('ORIGINAL_REFERENCE_SAME_EVENTS',oc)]:
                    rows.append({'symbol':symbol,'stage':stage,'cohort':cohort,'horizon':h,**geometry(e,cp,d,clocks[symbol],h)})
    return pd.DataFrame(rows)


def adjudicate(ledger: pd.DataFrame, coverage: pd.DataFrame) -> dict:
    decisions={}
    for symbol,f in ledger.groupby('symbol',sort=True):
        m=f.loc[(f.stage==STAGES[2])&f.matched]
        g=coverage.loc[(coverage.symbol==symbol)&(coverage.stage==STAGES[2])&coverage.gate_required]
        temporal=bool((m.control_entry_idx+SPAN <= m.information_cutoff_idx).all())
        exclusive=bool(overlap_pairs(m.control_entry_idx.to_numpy(int),SPAN)==0)
        quality=bool((m.maximum_scaled_gap<=CALIPER).all())
        cov=bool(g.coverage_pass.all()); bal=bool(g.balance_pass.all())
        valid=temporal and exclusive and quality
        reasons=[]
        if not cov: reasons.append('INSUFFICIENT_COVERAGE')
        if not bal: reasons.append('COVARIATE_BALANCE_OR_RETENTION_SHIFT')
        if not valid: reasons.append('IMPLEMENTATION_CONTRACT_VIOLATION')
        stages={}
        for stage in STAGES:
            t=f.loc[f.stage==stage]
            stages[stage]={'original_events':len(t),'matched_events':int(t.matched.sum()),'coverage':float(t.matched.mean()),
                           'reasons':{str(k):int(v) for k,v in t.reason.value_counts().items()}}
        decisions[symbol]={'decision':'DESIGN_SCREEN_PASS_ONLY' if not reasons else 'DESIGN_SCREEN_FAIL_NO_OUTCOMES',
            'failure_reasons':reasons,'maturity_pass':temporal,'exclusive_control_intervals_pass':exclusive,'caliper_pass':quality,
            'coverage_pass':cov,'balance_pass':bal,'stage_summary':stages,
            'failed_coverage_groups':g.loc[~g.coverage_pass,'group'].tolist(),
            'failed_balance_groups':g.loc[~g.balance_pass,'group'].tolist(),
            'new_outcomes_read':False,'noise_reduction_demonstrated':False,'full_population_identified':False}
    return decisions
