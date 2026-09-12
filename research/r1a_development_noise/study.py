"""Real pre2021 Development noise accounting, NOT another significance test.

No 2021-2025 prices, ETF returns, new confirmation data, model fit or p-values.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

BASELINE = 'e4854fbce1eda324a1dfa8ba06e3afadd1986b15'
FREEZE_COMMIT = '6315a8c8f0f31b34b02d40392ea2d5b484ad5f33'
FREEZE = 'docs/governance/R1A_DEVELOPMENT_NOISE_DECOMPOSITION_FREEZE@1.0.json'
HORIZONS = (1, 5, 15, 30, 60, 120, 240)
LAGS = (0, 1, 5, 20, 60)
SCOPES = {'000852.SH': ('2015-01-05', '2020-12-31'), '000688.SH': ('2020-07-23', '2020-12-31')}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def guard(path: Path, expected: str) -> None:
    data = path.read_bytes()
    actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(actual == expected, 'frozen source changed: '+str(path))


def ratio(a: float, b: float):
    return float(a/b) if b > 0 else None


def matrix(e: np.ndarray, c: np.ndarray) -> np.ndarray:
    x = np.column_stack([e, c]).astype(float)
    require(len(x) > 0 and np.isfinite(x).all(), 'empty/nonfinite moments')
    x = x - x.mean(axis=0)
    return x.T @ x / len(x)


def parts(v: np.ndarray) -> dict:
    ve, vc, cov = float(v[0, 0]), float(v[1, 1]), float(v[0, 1])
    vd = ve + vc - 2*cov
    require(vd >= -1e-10*max(1., ve+vc), 'negative difference variance')
    vd = max(0., vd)
    return {'event_var_bp2': ve, 'control_var_bp2': vc, 'event_control_cov_bp2': cov,
            'covariance_term_bp2': -2*cov, 'difference_var_bp2': vd,
            'event_sd_bp': math.sqrt(max(0., ve)), 'control_sd_bp': math.sqrt(max(0., vc)),
            'difference_sd_bp': math.sqrt(vd), 'event_control_correlation': ratio(cov, math.sqrt(max(0., ve*vc))),
            'event_share_of_difference': ratio(ve, vd), 'control_share_of_difference': ratio(vc, vd),
            'covariance_share_of_difference': ratio(-2*cov, vd),
            'cancellation_relative_to_marginal_sum': ratio(2*cov, ve+vc)}


def moments(e, c) -> dict:
    e, c = np.asarray(e, float), np.asarray(c, float)
    require(e.ndim == c.ndim == 1 and e.shape == c.shape, 'leg shape mismatch')
    out = {'n': len(e), **parts(matrix(e, c))}
    d = e-c
    direct = float(np.mean((d-d.mean())**2))
    require(np.isclose(direct, out['difference_var_bp2'], rtol=1e-11, atol=1e-8), 'variance identity')
    q = np.sort((d-d.mean())**2)[::-1]
    out['top_1pct_centered_square_share'] = ratio(q[:max(1, math.ceil(.01*len(q)))].sum(), q.sum())
    out['top_5pct_centered_square_share'] = ratio(q[:max(1, math.ceil(.05*len(q)))].sum(), q.sum())
    out['variance_identity_error_bp2'] = float(abs(direct-out['difference_var_bp2']))
    return out


def partition_moments(frame: pd.DataFrame) -> list[dict]:
    """Exact finite-distribution total covariance; group means are EX POST."""
    e, c = frame.event_bp.to_numpy(float), frame.control_bp.to_numpy(float)
    total = matrix(e, c); n = len(frame)
    within = np.zeros((2, 2)); mu = np.column_stack([e, c]).mean(axis=0)
    between = np.zeros((2, 2)); counts = []
    for _, g in frame.groupby(['calendar_year', 'parent_direction', 'clock_bucket'], sort=True):
        counts.append(len(g)); w = len(g)/n
        within += w*matrix(g.event_bp.to_numpy(float), g.control_bp.to_numpy(float))
        gm = g[['event_bp', 'control_bp']].to_numpy(float).mean(axis=0)-mu
        between += w*np.outer(gm, gm)
    require(np.allclose(total, within+between, rtol=1e-11, atol=1e-8), 'total covariance identity')
    meta = {'n': n, 'strata': len(counts), 'singleton_strata': int(sum(x == 1 for x in counts)),
            'minimum_stratum_n': min(counts), 'ex_post_not_causally_available': True,
            'reconstruction_error_bp2': float(np.max(np.abs(total-within-between)))}
    return [{**meta, 'component': label, **parts(value)} for label, value in [('TOTAL', total), ('WITHIN', within), ('BETWEEN', between)]]


def load_development(root: Path, symbol: str, manifest: dict) -> tuple[pd.DataFrame, list[dict]]:
    require(symbol in SCOPES, 'unknown development symbol')
    start, end = SCOPES[symbol]; frames = []; sources = []
    for item in manifest['files']:
        if item['symbol'] != symbol or item['frequency'] != '1m' or item['last_day'] < start or item['first_day'] > end:
            continue
        require(item['last_day'] <= end and item['first_day'] >= start, 'mixed-role file prohibited')
        p = (root/item['path']).resolve()
        require(p.is_relative_to(root.resolve()) and p.is_file(), 'missing/escaping development file')
        require(sha(p) == item['sha256'], 'development source checksum mismatch')
        cols = ['symbol', 'trading_day', 'timestamp', 'close']
        f = pq.read_table(p, columns=cols).to_pandas()
        f['trading_day'] = f.trading_day.astype(str)
        require(set(f.symbol) == {symbol} and f.trading_day.between(start, end).all(), 'source role/symbol mismatch')
        frames.append(f)
        sources.append({'path': item['path'], 'sha256': item['sha256'], 'bytes': p.stat().st_size,
                        'rows': len(f), 'columns_read': cols})
    require(bool(frames), 'no original Development files')
    f = pd.concat(frames, ignore_index=True)
    # Preserve the admitted index-source convention; no outcome-selected time shift.
    f['time'] = pd.to_datetime(f.timestamp.astype(str).str[:19]).dt.tz_localize('Asia/Shanghai')
    require((f.time.dt.strftime('%Y-%m-%d') == f.trading_day).all(), 'source calendar mismatch')
    f = f.sort_values('time', kind='stable').reset_index(drop=True)
    require(not f.time.duplicated().any() and np.isfinite(f.close).all() and (f.close > 0).all(), 'bad development prices')
    return f, sources


def control_geometry(pairs: pd.DataFrame, day_codes: np.ndarray, horizon: int) -> dict:
    e = pairs.event_entry_idx.to_numpy(int); c = pairs.control_entry_idx.to_numpy(int)
    counts = pairs.groupby('control_entry_idx', sort=True).size().to_numpy(int)
    gaps = day_codes[c]-day_codes[e]
    overlap = np.maximum(0, np.minimum(e+horizon, c+horizon)-np.maximum(e, c))
    return {'n': len(pairs), 'unique_controls': len(counts), 'maximum_control_reuse': int(counts.max()),
            'pairs_using_repeated_control_fraction': float(counts[counts>1].sum()/len(pairs)),
            'effective_controls_IF_independent_equal_variance': float(len(pairs)**2/np.sum(counts**2)),
            'control_after_event_fraction': float((c > e).mean()), 'same_day_fraction': float((gaps == 0).mean()),
            'median_absolute_control_gap_trading_days': float(np.median(np.abs(gaps))),
            'p90_absolute_control_gap_trading_days': float(np.quantile(np.abs(gaps), .9)),
            'within_pair_overlap_fraction': float((overlap > 0).mean()),
            'maximum_within_pair_overlap_bars': int(overlap.max())}


def weights(prices: np.ndarray, starts: np.ndarray, direction: np.ndarray, horizon: int) -> tuple[np.ndarray, float]:
    require(len(starts) == len(direction) and len(starts) > 0 and horizon > 0, 'bad weight geometry')
    require((starts >= 0).all() and (starts+horizon < len(prices)).all(), 'out-of-range path')
    require(np.isin(direction, [-1, 1]).all(), 'bad direction')
    w = np.zeros(len(prices)); individual_energy = 0.
    for a, d in zip(starts, direction):
        w[a+1:a+horizon+1] += d/prices[a]
        individual_energy += float(np.sum((prices[a:a+horizon]/prices[a])**2))
    return w, individual_energy


def clock_accounting(pairs: pd.DataFrame, prices: np.ndarray, day_codes: np.ndarray, dates: list[str],
                     horizon: int, signed: bool) -> tuple[dict, pd.DataFrame, list[dict]]:
    e = pairs.event_entry_idx.to_numpy(int); c = pairs.control_entry_idx.to_numpy(int)
    d = pairs.parent_direction.to_numpy(int) if signed else np.ones(len(pairs), dtype=int)
    we, ee_ind = weights(prices, e, d, horizon); wc, cc_ind = weights(prices, c, d, horizon)
    change = np.r_[0., np.diff(prices)]*1e4
    ep = we*change; cp = wc*change
    direct_e = d*(prices[e+horizon]/prices[e]-1)*1e4
    direct_c = d*(prices[c+horizon]/prices[c]-1)*1e4
    require(np.isclose(ep.sum(), direct_e.sum(), rtol=1e-10, atol=1e-6), 'event simple-return telescoping error')
    require(np.isclose(cp.sum(), direct_c.sum(), rtol=1e-10, atol=1e-6), 'control simple-return telescoping error')
    prev = np.r_[prices[0], prices[:-1]]
    ae, ac = we*prev, wc*prev
    ee = float(ae@ae); cc = float(ac@ac); cross = float(ae@ac)
    n = len(pairs); rate = n/len(dates)
    de = np.bincount(day_codes, weights=ep, minlength=len(dates))/rate
    dc = np.bincount(day_codes, weights=cp, minlength=len(dates))/rate
    require(np.isclose((de-dc).mean(), (direct_e-direct_c).mean(), rtol=1e-10, atol=1e-8), 'calendar-mean conservation')
    reuse = 0.
    for a, g in pairs.groupby('control_entry_idx', sort=True):
        require(g.parent_direction.nunique() == 1, 'same control contradictory parent direction')
        m = len(g)
        reuse += m*(m-1)*float(np.sum((prices[int(a):int(a)+horizon]/prices[int(a)])**2))
    denom = float(np.abs(ae).sum()+np.abs(ac).sum())
    info = {'view': 'SIGNED' if signed else 'UNSIGNED', **control_geometry(pairs, day_codes, horizon),
            'event_primitive_weight_energy': ee, 'control_primitive_weight_energy': cc,
            'event_sum_individual_energies': ee_ind, 'control_sum_individual_energies': cc_ind,
            'control_exact_reuse_excess_energy': reuse, 'control_other_overlap_energy': cc-cc_ind-reuse,
            'net_primitive_weight_energy': ee+cc-2*cross,
            'primitive_covariance_cancellation_ratio_ASSUMPTION': ratio(2*cross, ee+cc),
            'control_exact_reuse_fraction_of_energy': ratio(reuse, cc),
            'minute_absolute_exposure_cancellation': 1-float(np.abs(ae-ac).sum())/denom if denom>0 else None,
            'calendar_trading_days': len(dates), 'pairs_per_calendar_day': rate,
            'event_reconstruction_error_bp': float(abs(ep.sum()-direct_e.sum())),
            'control_reconstruction_error_bp': float(abs(cp.sum()-direct_c.sum())),
            **{'daily_'+k: v for k,v in moments(de, dc).items()}}
    daily = pd.DataFrame({'day': dates, 'event_contribution_bp': de, 'control_contribution_bp': dc,
                          'difference_contribution_bp': de-dc})
    ue, uc = de-de.mean(), dc-dc.mean(); ud=ue-uc
    lags = []
    for lag in LAGS:
        if lag >= len(dates):
            continue
        a = slice(lag, None); b = slice(None, -lag) if lag else slice(None)
        ge = float(ue[a]@ue[b]/len(dates)); gc = float(uc[a]@uc[b]/len(dates))
        gec = float(ue[a]@uc[b]/len(dates)); gce = float(uc[a]@ue[b]/len(dates))
        gd = float(ud[a]@ud[b]/len(dates))
        require(np.isclose(gd, ge+gc-gec-gce, rtol=1e-10, atol=1e-7), 'calendar lag identity')
        lags.append({'lag_trading_days': lag, 'products': len(dates)-lag, 'event_lag_product_bp2': ge,
                     'control_lag_product_bp2': gc, 'event_control_lag_product_bp2': gec,
                     'control_event_lag_product_bp2': gce, 'difference_lag_product_bp2': gd,
                     'mean_variance_estimator': False})
    return info, daily, lags


def scale_scenarios(ve: float, vc: float) -> list[dict]:
    require(ve >= 0 and vc >= 0 and ve+vc > 0, 'invalid marginal scale')
    rows = []
    for rho in (0., .5):
        for k in (1, 2, 5, 10, 'infinity'):
            inv = 0. if k == 'infinity' else 1/k
            v = ve+vc*(rho+(1-rho)*inv)
            rows.append({'K': str(k), 'control_correlation_ASSUMED': rho,
                         'event_control_covariance_ASSUMED': 0., 'variance_ratio_to_independent_one_control': v/(ve+vc),
                         'information_multiple_ASSUMPTION': (ve+vc)/v if v>0 else None,
                         'actual_matching_changed': False})
    return rows


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient='records', double_precision=15))


def run(root: Path, output: Path) -> dict:
    require(not output.exists(), 'fresh output directory required')
    frozen = json.loads((root/FREEZE).read_text())
    require(frozen['baseline_commit'] == BASELINE and frozen['status'] == 'FROZEN_BEFORE_DEVELOPMENT_DECOMPOSITION', 'wrong freeze')
    require(frozen['horizons'] == list(HORIZONS) and frozen['BLACKBOX_query_count'] == 3 and not frozen['production_authority'], 'scope drift')
    require({s:(v['start'],v['end']) for s,v in frozen['scope'].items()} == SCOPES, 'date drift')
    for path, blob in frozen['source_guards'].items():
        guard(root/path, blob)
    from research.r1_incremental_alpha_attribution.core import build_r1_events_and_controls, match_events
    source_freeze = json.loads((root/'docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json').read_text())
    manifest = json.loads((root/'data/manifest.json').read_text())
    output.mkdir(parents=True)
    tables = {k: [] for k in ['leg_variance', 'stratum_covariance', 'clock_accounting', 'calendar_lag_products', 'control_scale_scenarios']}
    all_pairs=[]; all_returns=[]; all_daily=[]; sources=[]; cohorts={}
    for symbol, (start,end) in SCOPES.items():
        tape, files = load_development(root,symbol,manifest); sources.extend(files)
        px = tape.close.to_numpy(float); days=tape.trading_day.to_numpy(str)
        day_codes, unique_days = pd.factorize(tape.trading_day, sort=True); dates=list(map(str, unique_days))
        print('Building unchanged Development geometry:',symbol,start,end,flush=True)
        events, controls = build_r1_events_and_controls(px, days, tape.time,
            source_freeze['directional_change_thresholds'],source_freeze['r1_vol_reference'],start,end,max_horizon=240)
        events=events.loc[events.cell=='R1_A'].copy(); controls=controls.loc[controls.cell=='R1_A'].copy()
        pairs, meta=match_events(events,controls)
        require(not pairs.empty and not pairs.event_entry_idx.duplicated().any(), 'no/duplicate Development pairs')
        require((pairs.event_entry_idx+240<len(px)).all() and (pairs.control_entry_idx+240<len(px)).all(), 'boundary drift')
        pairs['symbol']=symbol
        pairs['pair_id']=symbol+':DEV_R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
        pairs['event_entry_time']=[tape.time.iloc[i].isoformat() for i in pairs.event_entry_idx]
        pairs['control_entry_time']=[tape.time.iloc[i].isoformat() for i in pairs.control_entry_idx]
        all_pairs.append(pairs)
        cohorts[symbol]={**meta,'role':frozen['scope'][symbol]['role'],'start':start,'end':end,
                         'index_rows':len(tape),'trading_days':len(dates),'candidate_control_rows':len(controls),
                         'cohort_boundary': 'same 240-bar-complete Development cohort at every horizon',
                         'retrospective_control_rule_NOT_online':True}
        for h in HORIZONS:
            e=pairs.event_entry_idx.to_numpy(int); c=pairs.control_entry_idx.to_numpy(int); d=pairs.parent_direction.to_numpy(int)
            er=(px[e+h]/px[e]-1)*1e4; cr=(px[c+h]/px[c]-1)*1e4
            ledger=pairs[['pair_id','symbol','event_day','control_day','calendar_year','parent_direction','side','clock_bucket']].copy()
            ledger['horizon']=h; ledger['event_bp']=d*er; ledger['control_bp']=d*cr; ledger['difference_bp']=d*(er-cr)
            all_returns.append(ledger)
            base={'symbol':symbol,'horizon':h}
            tables['leg_variance'].append({**base,'view':'POOLED_SIGNED',**moments(d*er,d*cr)})
            tables['leg_variance'].append({**base,'view':'POOLED_UNSIGNED',**moments(er,cr)})
            for year,g in ledger.groupby('calendar_year',sort=True):
                tables['leg_variance'].append({**base,'view':'YEAR_'+str(year),**moments(g.event_bp,g.control_bp)})
            for side,g in ledger.groupby('side',sort=True):
                tables['leg_variance'].append({**base,'view':side,**moments(g.event_bp,g.control_bp)})
            tables['stratum_covariance'].extend({**base,**x} for x in partition_moments(ledger))
            for signed in (True,False):
                info,daily,lags=clock_accounting(pairs,px,day_codes,dates,h,signed)
                tables['clock_accounting'].append({**base,**info})
                view=info['view']; daily['symbol']=symbol; daily['horizon']=h; daily['view']=view; all_daily.append(daily)
                tables['calendar_lag_products'].extend({**base,'view':view,**x} for x in lags)
            v=matrix(d*er,d*cr)
            tables['control_scale_scenarios'].extend({**base,**x} for x in scale_scenarios(float(v[0,0]),float(v[1,1])))
    frames={k:pd.DataFrame(v) for k,v in tables.items()}
    frames.update({'development_pairs':pd.concat(all_pairs,ignore_index=True),
                   'development_leg_returns_NOT_confirmation':pd.concat(all_returns,ignore_index=True),
                   'calendar_contributions_NOT_strategy_backtest':pd.concat(all_daily,ignore_index=True)})
    for name,f in frames.items():
        f.to_csv(output/(name+'.csv'),index=False,float_format='%.12g')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    pooled=frames['leg_variance'].loc[frames['leg_variance'].view=='POOLED_SIGNED']
    clock=frames['clock_accounting'].loc[frames['clock_accounting'].view=='SIGNED']
    receipt={'schema_id':'factorlab_r1a_development_noise_receipt@1.0',
        'decision':'DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST',
        'baseline_commit':BASELINE,'freeze_commit':FREEZE_COMMIT,'freeze_sha256':sha(root/FREEZE),
        'code_commit':head,'github_run_id':os.environ.get('GITHUB_RUN_ID'),'sources':sources,'cohorts':cohorts,
        'pooled_signed':records(pooled),'signed_clock_accounting':records(clock),
        'table_rows':{k+'.csv':len(f) for k,f in frames.items()},
        'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.glob('*.csv'))],
        'post2020_price_files_read':[],'ETF_price_files_read':[],'validation_pairs_modified':False,
        'new_significance_tests':False,'horizon_selected':False,'causal_noise_components_identified':False,
        'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
        'confirmation_protocol_frozen':False,'confirmation_clock_started':False}
    (output/'noise_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    report=['# Development actual difference-noise accounting','',receipt['decision'],'',
        'Original CSI1000 Development 2015-2020; STAR50 short 2020 context only. No 2021-2025/ETF/2026 returns read.',
        'Observed centered dispersion is not identified irreducible noise or a standard error of the mean.',
        '', '| Symbol | h | n | Event SD bp | Control SD bp | Difference SD bp | Correlation | Covariance cancellation |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in pooled.itertuples():
        corr='NA' if r.event_control_correlation is None else f'{r.event_control_correlation:.4f}'
        cancel='NA' if r.cancellation_relative_to_marginal_sum is None else f'{100*r.cancellation_relative_to_marginal_sum:.2f}%'
        report.append(f'| {r.symbol} | {r.horizon} | {r.n} | {r.event_sd_bp:.3f} | {r.control_sd_bp:.3f} | {r.difference_sd_bp:.3f} | {corr} | {cancel} |')
    report.extend(['','## Limits','',
        'Full-year nearest-control selection is retrospective, not an online control. It is reused unchanged for accounting only.',
        'Calendar decomposition uses exact telescoping simple returns, allocates overnight changes to the next observed price date, and includes zero-exposure days.',
        'Primitive weight-energy ratios assume independent equal-variance minute-return shocks; daily variance and lag cross-products are realized diagnostics, not calibrated inference.',
        'Within/between-stratum components use future-complete group means and do not establish achievable causal variance reduction.',
        'Counterfactual control-count tables impose zero event-control covariance and fixed correlations; no controls were added and no estimator was selected.',
        'Signed/unsigned differences do not identify latent common market factors. No p-values, new alpha PASS, fitted residualization or confirmation launch.',
        '', 'BLACKBOX_query_count=3; production_authority=false; fresh_oos=false.'])
    (output/'REPORT.md').write_text('\n'.join(report)+'\n')
    print(json.dumps({'decision':receipt['decision'],'cohorts':cohorts,'table_rows':receipt['table_rows']},indent=2))
    return receipt


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); run(args.root.resolve(),args.output.resolve())


if __name__=='__main__':
    main()
