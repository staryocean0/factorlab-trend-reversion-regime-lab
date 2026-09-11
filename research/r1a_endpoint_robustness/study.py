"""Retrospective robustness of the immutable R1_A endpoint table.

No refit, no missing ETF return imputation, no primary common-cohort opening.
Graph-sandwich/t intervals are assumption-dependent approximations, not a new
confirmatory test or a correction for the repository's entire research history.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

FREEZE = 'docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json'
FREEZE_COMMIT = 'f098e4702c03a6374dfd8332fcfc1ee10882cced'
BASELINE = '02c4873e78eac0fe1a7a3810866e8f21ed9263c9'
OLD = 'docs/ops/evidence/r1a_endpoint_diagnostic_20260912'
PAIRS = 'docs/ops/evidence/r1_incremental_alpha_20260911/matched_pairs.csv'
MAP = {'000852.SH': '512100.SH', '000688.SH': '588000.SH'}
COUNTS = {'000852.SH': 1296, '000688.SH': 1802}
HORIZONS = (1, 5, 15, 30, 60, 120, 240)
SPECS = ((20, 0), (20, 10), (5, 0), (5, 2))
YEARS = tuple(str(y) for y in range(2021, 2026))
GAMMAS = (-100, -50, -25, -10, -5, 0, 5, 10, 25, 50, 100)

class RobustnessError(ValueError):
    """An immutable input or frozen method contract was violated."""

def require(ok: bool, message: str) -> None:
    if not ok:
        raise RobustnessError(message)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def blob_guard(path: Path, expected: str) -> None:
    raw = path.read_bytes()
    got = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(got == expected, 'pinned Git blob changed: ' + str(path))

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision='round_trip')

def block_memberships(bounds: np.ndarray, length: int, shift: int) -> list[set[int]]:
    """bounds: event start/end, control start/end in the SAME trading-day clock."""
    b = np.asarray(bounds)
    require(b.ndim == 2 and b.shape[1] == 4, 'bad exposure bounds')
    require(length > 0 and 0 <= shift < length, 'bad block specification')
    require(np.isfinite(b).all() and np.equal(b, np.floor(b)).all(), 'noninteger bounds')
    require((b >= 0).all() and (b[:, 1] >= b[:, 0]).all() and (b[:, 3] >= b[:, 2]).all(), 'reversed exposure interval')
    result = []
    for e0, e1, c0, c1 in b.astype(int):
        event = range((e0 + shift)//length, (e1 + shift)//length + 1)
        control = range((c0 + shift)//length, (c1 + shift)//length + 1)
        result.append(set(event) | set(control))
    return result

def shared_adjacency(members: list[set[int]]) -> tuple[np.ndarray, dict]:
    n = len(members)
    require(n > 0 and all(len(s) for s in members), 'empty exposure membership')
    positions: dict[int, list[int]] = {}
    for i, group in enumerate(members):
        for b in group:
            positions.setdefault(int(b), []).append(i)
    adjacency = np.eye(n, dtype=bool)
    for ids in positions.values():
        adjacency[np.ix_(ids, ids)] = True
    counts = np.array([len(ids) for ids in positions.values()], dtype=float)
    degrees = adjacency.sum(axis=1) - 1
    return adjacency, {
        'occupied_blocks': len(positions),
        'edge_density': float(degrees.sum() / (n*(n-1))) if n > 1 else 0.,
        'maximum_degree': int(degrees.max()),
        'mean_degree': float(degrees.mean()),
        'largest_block_pair_fraction': float(counts.max()/n),
        'incidence_effective_blocks': float(counts.sum()**2 / np.square(counts).sum()),
        'maximum_blocks_per_pair': max(map(len, members)),
    }

def graph_inference(values_bp: np.ndarray, members: list[set[int]]) -> dict:
    x = np.asarray(values_bp, dtype=float)
    require(x.ndim == 1 and len(x) == len(members) and np.isfinite(x).all(), 'invalid inference data')
    n = len(x)
    require(n > 1, 'too few observations')
    a, info = shared_adjacency(members)
    g = info['occupied_blocks']; mean = float(x.mean()); u = x-mean
    iid = float(np.dot(u, u)/(n*(n-1)))
    meat = float(u @ (a @ u))
    raw = float(meat/(n*n)*(n/(n-1))*(g/(g-1))) if g > 1 else None
    out = {'n': n, 'mean_increment_bp': mean, 'iid_se_bp': float(np.sqrt(iid)),
           'graph_meat_bp2': meat, 'graph_variance_bp2': raw, **info}
    for k in ('graph_se_bp', 'used_se_bp', 'df_heuristic', 'point_lo_bp', 'point_hi_bp',
              'family14_lo_bp', 'family14_hi_bp', 'family56_lo_bp', 'family56_hi_bp',
              'p_two_sided_approx', 'p_bonferroni14_approx', 'p_bonferroni56_approx'):
        out[k] = None
    if n < 30 or g < 30 or raw is None or not np.isfinite(raw) or raw <= 0:
        out['inference_status'] = 'UNQUANTIFIED_INADEQUATE_UNITS_OR_NONPOSITIVE_GRAPH_VARIANCE'
        out['iid_floor_applied'] = False
        return out
    se = float(np.sqrt(max(raw, iid))); df = min(g-1, n-1)
    out.update({'inference_status': 'APPROXIMATE_CONDITIONAL_GRAPH_SANDWICH',
                'graph_se_bp': float(np.sqrt(raw)), 'used_se_bp': se,
                'iid_floor_applied': bool(iid > raw), 'df_heuristic': df})
    for family, label in ((1, 'point'), (14, 'family14'), (56, 'family56')):
        critical = float(student_t.ppf(1 - .05/(2*family), df))
        out[label+'_lo_bp'] = mean-critical*se
        out[label+'_hi_bp'] = mean+critical*se
    p = float(2*student_t.sf(abs(mean)/se, df))
    out.update({'p_two_sided_approx': p, 'p_bonferroni14_approx': min(1., 14*p),
                'p_bonferroni56_approx': min(1., 56*p)})
    return out

def greedy_nonoverlap(pairs: pd.DataFrame, horizon: int) -> set[str]:
    """Use ALL pairs before availability/outcomes; block overlap in either role."""
    require(horizon in HORIZONS and not pairs.pair_id.duplicated().any(), 'invalid thinning inputs')
    require((pairs[['event_entry_idx','control_entry_idx']].to_numpy(int) >= 0).all(), 'negative bar index')
    size = int(pairs[['event_entry_idx','control_entry_idx']].to_numpy(int).max())+horizon+1
    used = np.zeros(size, dtype=bool); selected: set[str] = set()
    ordered = pairs.sort_values(['event_entry_idx','control_entry_idx','pair_id'], kind='stable')
    for p in ordered.itertuples(index=False):
        e, c = int(p.event_entry_idx), int(p.control_entry_idx)
        if used[e:e+horizon+1].any() or used[c:c+horizon+1].any():
            continue
        selected.add(p.pair_id)
        used[e:e+horizon+1] = True; used[c:c+horizon+1] = True
    return selected

def missing_sensitivity(index_all_bp: np.ndarray, observed_mask: np.ndarray,
                        observed_etf_bp: np.ndarray, gammas=GAMMAS) -> dict:
    """Algebraic assumptions, NOT imputation or identified all-event estimates."""
    ix = np.asarray(index_all_bp, float); ok = np.asarray(observed_mask, bool)
    etf = np.asarray(observed_etf_bp, float)
    require(len(ix) == len(ok) and len(etf) == int(ok.sum()) and np.isfinite(ix).all() and np.isfinite(etf).all(), 'missingness alignment mismatch')
    n, N = len(etf), len(ix); m = N-n
    require(N > 0 and n > 0, 'empty missingness group')
    residual = float((etf-ix[ok]).mean())
    center = float(ix.mean()+residual)
    return {'N_original': N, 'n_observed': n, 'n_missing': m, 'observed_fraction': n/N,
            'observed_etf_mean_bp': float(etf.mean()), 'full_index_mean_bp': float(ix.mean()),
            'eligible_index_mean_bp': float(ix[ok].mean()),
            'excluded_index_mean_bp': float(ix[~ok].mean()) if m else None,
            'index_composition_shift_bp': float(ix[ok].mean()-ix.mean()),
            'observed_mean_tracking_residual_bp': residual,
            'missing_etf_mean_to_zero_bp': float(-etf.sum()/m) if m else None,
            'gamma_to_zero_bp': float(-center*N/m) if m else None,
            'gamma_zero_scenario_bp_NOT_ESTIMATE': center,
            'scenarios': [{'gamma_bp': float(d), 'scenario_all_pair_mean_bp_NOT_ESTIMATE': float(center+(m/N)*d)} for d in gammas],
            'missing_returns_imputed': False, 'unconditional_mean_identified': bool(m == 0)}

def frame_stats(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {'n': 0, 'etf_increment_bp': None, 'index_increment_bp': None, 'event_mean_bp': None}
    return {'n': len(frame), 'etf_increment_bp': float(frame.etf_incremental.mean()*1e4),
            'index_increment_bp': float(frame.index_incremental.mean()*1e4),
            'event_mean_bp': float(frame.etf_event.mean()*1e4)}

def influence(pairs: pd.DataFrame, a: pd.DataFrame, ledger: pd.DataFrame, h: int) -> tuple[dict, pd.DataFrame]:
    p = pairs.set_index('pair_id').loc[ledger.pair_id]
    counts = p.control_entry_idx.value_counts()
    w = (1/p.control_entry_idx.map(counts)).to_numpy(float)
    chosen = greedy_nonoverlap(pairs, h)
    available = set(ledger.pair_id)
    thin = ledger.loc[ledger.pair_id.isin(chosen)]
    audit = pairs[['pair_id','event_day','control_day']].copy()
    audit['horizon'] = h; audit['clock_selected_before_eligibility'] = audit.pair_id.isin(chosen)
    audit['endpoint_eligible'] = audit.pair_id.isin(available)
    audit['retained_for_sensitivity'] = audit.clock_selected_before_eligibility & audit.endpoint_eligible
    year_info = {}
    aa = a.set_index('pair_id').loc[ledger.pair_id]
    for y in YEARS:
        touches = np.zeros(len(aa), bool)
        for leg in ('event','control'):
            start = aa[leg+'_entry_timestamp'].str[:4].to_numpy()
            end = aa[leg+'_exit_timestamp'].str[:4].to_numpy()
            touches |= (start <= y) & (end >= y)
        year_info[y] = frame_stats(ledger.loc[~touches])
    return {'unique_exact_controls': len(counts), 'maximum_control_reuse': int(counts.max()),
            'reused_control_groups': int((counts > 1).sum()),
            'control_incidence_effective_count_NOT_independent_n': float(len(p)**2/np.square(counts.to_numpy(float)).sum()),
            'control_equal_weight_increment_bp': float(np.average(ledger.etf_incremental.to_numpy()*1e4, weights=w)),
            'control_equal_weight_index_increment_bp': float(np.average(ledger.index_incremental.to_numpy()*1e4, weights=w)),
            'clock_disjoint_selected_all': len(chosen), 'clock_disjoint_observed': frame_stats(thin),
            'leave_exposure_year_out': year_info,
            'sides': {s: frame_stats(ledger.loc[ledger.side == s]) for s in ('LONG','SHORT')},
            'years': {y: frame_stats(ledger.loc[ledger.event_day.str.startswith(y)]) for y in YEARS}}, audit

def _bounds(a: pd.DataFrame, day_map: dict[str, int]) -> np.ndarray:
    columns = ['event_entry_timestamp','event_exit_timestamp','control_entry_timestamp','control_exit_timestamp']
    vectors = []
    for c in columns:
        values = a[c].str[:10].map(day_map)
        require(not values.isna().any(), 'endpoint date outside pinned trading calendar')
        vectors.append(values.to_numpy(int))
    return np.column_stack(vectors)

def run(root: Path, output: Path) -> dict:
    from regime_lab.market_data import load_market_data
    require(not output.exists(), 'fresh output directory required')
    contract = json.loads((root/FREEZE).read_text())
    require(contract['baseline_commit'] == BASELINE and contract['horizons'] == list(HORIZONS), 'freeze scope drift')
    require(contract['dependence']['all_prespecified_specs'] == [list(x) for x in SPECS], 'dependence specifications changed')
    require(contract['missing_outcome_sensitivity']['gamma_grid_bp'] == list(GAMMAS), 'gamma grid changed')
    require(contract['carriers'] == MAP and contract['BLACKBOX_query_count'] == 3 and contract['production_authority'] is False, 'authority changed')
    blob_guard(root/OLD/'endpoint_receipt.json', '89f188522ddd657c8957ec2b85f8d0b57892143b')
    blob_guard(root/PAIRS, '95191091d1a26c360c3efb5ae2d5be9cf194211d')
    blob_guard(root/'data/manifest.json', 'a1935d30326dc9306dc23cdb309ac463114e2a2a')
    previous = json.loads((root/OLD/'endpoint_receipt.json').read_text())
    require(previous['decision'] == 'ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE', 'wrong endpoint study')
    verified = []
    for s in previous['evidence_files']:
        require(Path(s['path']).name == s['path'], 'unsafe receipt path')
        path = root/OLD/s['path']
        require(path.is_file() and sha(path) == s['sha256'] and path.stat().st_size == s['bytes'], 'retained endpoint evidence changed')
        verified.append(s)
    all_pairs = read_csv(root/PAIRS)
    all_pairs = all_pairs.loc[all_pairs.cell == 'R1_A'].copy()
    all_pairs['pair_id'] = all_pairs.symbol.astype(str)+':R1_A:'+all_pairs.event_entry_idx.astype(str)+':'+all_pairs.control_entry_idx.astype(str)
    require(not all_pairs.pair_id.duplicated().any(), 'duplicate frozen pair')
    info = {}; inference_rows = []; sensitivity_rows = []; thinning_rows = []; overview_rows = []
    for symbol, carrier in MAP.items():
        pairs = all_pairs.loc[all_pairs.symbol == symbol].copy().reset_index(drop=True)
        require(len(pairs) == COUNTS[symbol], 'frozen pair count drift')
        ix = load_market_data(symbol, '1m', '2015-01-05' if symbol == '000852.SH' else '2020-07-23', '2025-12-31', root=root)
        times = pd.DatetimeIndex(ix.market_time_shanghai)
        if symbol == '000852.SH':
            calendar = sorted(set(times[times.year >= 2021].strftime('%Y-%m-%d')))
            day_map = {day: i for i, day in enumerate(calendar)}
        av = read_csv(root/OLD/(carrier+'_endpoint_availability.csv'))
        le = read_csv(root/OLD/(carrier+'_endpoint_returns.csv'))
        require(not av.duplicated(['pair_id','horizon']).any() and not le.duplicated(['pair_id','horizon']).any(), 'duplicate endpoint key')
        require(set(le.horizon) == set(HORIZONS) and set(av.horizon) == set(HORIZONS), 'horizon table changed')
        require(av.eligible.isin([True,False]).all(), 'invalid eligibility')
        e = pairs.event_entry_idx.to_numpy(int); c = pairs.control_entry_idx.to_numpy(int)
        direction = pairs.parent_direction.to_numpy(int); prices = ix.close.to_numpy(float)
        require(np.isin(direction, [-1,1]).all(), 'direction changed')
        info[carrier] = {'index_symbol': symbol, 'horizons': {}}
        for h in HORIZONS:
            a = av.loc[av.horizon == h].set_index('pair_id').loc[pairs.pair_id].reset_index()
            require(set(a.pair_id) == set(pairs.pair_id), 'availability denominator drift')
            observed_ids = set(a.loc[a.eligible, 'pair_id'])
            rows = le.loc[le.horizon == h].copy()
            require(set(rows.pair_id) == observed_ids, 'changed observed cohort')
            rows = rows.set_index('pair_id').loc[pairs.loc[pairs.pair_id.isin(observed_ids),'pair_id']].reset_index()
            ok = pairs.pair_id.isin(observed_ids).to_numpy()
            for k in ('event_day','control_day','side'):
                require(np.array_equal(rows[k].to_numpy(), pairs.loc[ok,k].to_numpy()), 'pair identity changed: '+k)
            index_all = direction*(prices[e+h]/prices[e]-prices[c+h]/prices[c])
            require(np.allclose(index_all[ok], rows.index_incremental, rtol=0, atol=1e-12), 'same-sample index reconciliation failed')
            prior = previous['carriers'][carrier]['horizons'][str(h)]
            require(abs(index_all.mean()*1e4-prior['composition']['all']['index']['index_incremental']['mean_bp']) < 1e-8, 'full index comparator changed')
            require(abs(rows.etf_incremental.mean()*1e4-prior['summary']['pooled']['etf_incremental']['mean_bp']) < 1e-8, 'ETF mean changed')
            require(np.allclose(rows.etf_incremental, rows.etf_event-rows.etf_control, rtol=0, atol=1e-12), 'ETF algebra changed')
            bounds = _bounds(a.loc[ok].reset_index(drop=True), day_map)
            by_spec = {}
            for length, shift in SPECS:
                estimate = graph_inference(rows.etf_incremental.to_numpy(float)*1e4, block_memberships(bounds,length,shift))
                name = f'L{length}_shift{shift}'
                by_spec[name] = estimate
                inference_rows.append({'carrier': carrier, 'horizon': h, 'spec': name, **estimate})
            infl, thin = influence(pairs, a, rows, h)
            thin['carrier'] = carrier; thinning_rows.append(thin)
            miss = {}
            for y in ('pooled',) + YEARS:
                mask = np.ones(len(pairs), bool) if y == 'pooled' else pairs.event_day.str.startswith(y).to_numpy()
                obs_year = np.ones(len(rows), bool) if y == 'pooled' else rows.event_day.str.startswith(y).to_numpy()
                calc = missing_sensitivity(index_all[mask]*1e4, ok[mask], rows.loc[obs_year,'etf_incremental'].to_numpy(float)*1e4)
                miss[y] = calc
                for sc in calc['scenarios']:
                    sensitivity_rows.append({'carrier': carrier, 'horizon': h, 'event_year': y,
                                             **{k:v for k,v in calc.items() if k != 'scenarios'}, **sc})
            cross_positive = all(v['family56_lo_bp'] is not None and v['family56_lo_bp'] > 0 for v in by_spec.values())
            primary = by_spec['L20_shift0']
            row = {'carrier': carrier, 'horizon': h, 'n_observed': len(rows),
                   'mean_increment_bp': float(rows.etf_incremental.mean()*1e4),
                   'primary_se_bp': primary['used_se_bp'],
                   'primary_point_lo_bp': primary['point_lo_bp'], 'primary_point_hi_bp': primary['point_hi_bp'],
                   'primary_family14_lo_bp': primary['family14_lo_bp'], 'primary_family14_hi_bp': primary['family14_hi_bp'],
                   'primary_family14_positive': bool(primary['family14_lo_bp'] is not None and primary['family14_lo_bp'] > 0),
                   'all_four_family56_positive': cross_positive,
                   'unique_controls': infl['unique_exact_controls'], 'maximum_control_reuse': infl['maximum_control_reuse'],
                   'control_equal_weight_increment_bp': infl['control_equal_weight_increment_bp'],
                   'clock_disjoint_n': infl['clock_disjoint_observed']['n'],
                   'clock_disjoint_increment_bp': infl['clock_disjoint_observed']['etf_increment_bp'],
                   'leave_year_out_min_increment_bp': min(v['etf_increment_bp'] for v in infl['leave_exposure_year_out'].values()),
                   'gamma_to_zero_pooled_bp': miss['pooled']['gamma_to_zero_bp'],
                   'missing_etf_mean_to_zero_pooled_bp': miss['pooled']['missing_etf_mean_to_zero_bp']}
            overview_rows.append(row)
            info[carrier]['horizons'][str(h)] = {'inference': by_spec, 'influence': infl, 'missing_sensitivity': miss, 'overview': row}
    output.mkdir(parents=True)
    pd.DataFrame(inference_rows).to_csv(output/'all_56_inference_cells.csv', index=False)
    pd.DataFrame(overview_rows).to_csv(output/'robustness_overview.csv', index=False)
    pd.DataFrame(sensitivity_rows).to_csv(output/'missing_residual_scenarios_NOT_ESTIMATES.csv', index=False)
    pd.concat(thinning_rows, ignore_index=True).to_csv(output/'clock_disjoint_selection_audit.csv', index=False)
    receipt = {'schema_id': 'factorlab_r1a_endpoint_robustness_receipt@1.0',
               'decision': 'RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION',
               'baseline_commit': BASELINE, 'freeze_commit': FREEZE_COMMIT, 'freeze_sha256': sha(root/FREEZE),
               'code_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
               'github_run_id': os.environ.get('GITHUB_RUN_ID'), 'pinned_endpoint_receipt_sha256': sha(root/OLD/'endpoint_receipt.json'),
               'verified_endpoint_files': verified, 'carriers': info,
               'primary_family14_positive_cells': [f"{r['carrier']}:{r['horizon']}" for r in overview_rows if r['primary_family14_positive']],
               'all_four_family56_positive_cells': [f"{r['carrier']}:{r['horizon']}" for r in overview_rows if r['all_four_family56_positive']],
               'inference_assumptions_verified': False, 'research_history_multiplicity_corrected': False,
               'missing_ETF_outcomes_imputed': False, 'primary_common_cohort_opened': False,
               'BLACKBOX_query_count': 3, 'production_authority': False, 'fresh_oos': False,
               'signal_refitted': False, 'horizon_selected': False, 'old_protocols_changed': False,
               'limitations': ['Graph-sandwich dependence neighborhoods and t calibration are approximations, not finite-sample guarantees.',
                               'Displayed-family multiplicity does not correct prior signal/identity exploration or repeated historical reuse.',
                               'Eligibility conditions on future observed endpoints; missingness need not be random.',
                               'Missingness grids are algebraic assumptions, not imputed returns or identified all-event effects.',
                               'Canonical source assumptions inherited; no bid/ask, costs, borrow, path-risk or production claim.']}
    receipt['output_csvs'] = [{'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(output.glob('*.csv'))]
    (output/'robustness_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    make_report(receipt, overview_rows, output/'REPORT.md')
    print(json.dumps({'decision':receipt['decision'], 'primary_family14_positive_cells':receipt['primary_family14_positive_cells'],
                      'all_four_family56_positive_cells':receipt['all_four_family56_positive_cells']},indent=2))
    return receipt

def fmt(x: Any) -> str:
    return 'UNQUANTIFIED' if x is None else f'{x:+.3f}'

def make_report(receipt: dict, overview: list[dict], path: Path) -> None:
    lines = ['# R1_A endpoint dependence / selection robustness', '',
             'Decision: `'+receipt['decision']+'`', '',
             'Retrospective inference on already observed means. NOT new independent confirmation, causal proof, or live profitability.', '',
             'Freeze commit: `'+FREEZE_COMMIT+'`; code commit: `'+receipt['code_commit']+'`; run: `'+str(receipt['github_run_id'])+'`.', '',
             '## Primary 20-trading-day calendar-exposure specification', '',
             'The graph connects any event/control paths sharing a calendar block, including cross-role shared controls. Means and per-horizon samples are unchanged. Intervals use an approximate graph sandwich with an IID-SE floor and a heuristic t reference; displayed family correction covers 14 contrasts only.', '',
             '| ETF | h | n | Increment bp | SE bp | Pointwise 95% interval | 14-family interval | Positive in all four 56-family checks |',
             '|---|---:|---:|---:|---:|---|---|---|']
    for r in overview:
        lines.append(f"| {r['carrier']} | {r['horizon']} | {r['n_observed']} | {fmt(r['mean_increment_bp'])} | {fmt(r['primary_se_bp'])} | [{fmt(r['primary_point_lo_bp'])}, {fmt(r['primary_point_hi_bp'])}] | [{fmt(r['primary_family14_lo_bp'])}, {fmt(r['primary_family14_hi_bp'])}] | {r['all_four_family56_positive']} |")
    lines += ['', 'Primary-family positive cells: `'+json.dumps(receipt['primary_family14_positive_cells'])+'`.',
              'All-four/56-family positive cells: `'+json.dumps(receipt['all_four_family56_positive_cells'])+'`.', '',
              'No positive adjusted lower bound means insufficient evidence under that check, NOT proof the effect is zero or negative.', '',
              '## Influence / concentration checks (descriptive, not substitute winners)', '',
              '| ETF | h | Distinct controls | Max reuse | Equal-control increment bp | Clock-disjoint n | Clock-disjoint increment bp | Minimum leave-year-out increment bp |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in overview:
        lines.append(f"| {r['carrier']} | {r['horizon']} | {r['unique_controls']} | {r['maximum_control_reuse']} | {fmt(r['control_equal_weight_increment_bp'])} | {r['clock_disjoint_n']} | {fmt(r['clock_disjoint_increment_bp'])} | {fmt(r['leave_year_out_min_increment_bp'])} |")
    lines += ['', 'The disjoint subset is selected on ALL original clocks before endpoint eligibility, not by return. It does not guarantee independence from serial dependence. All leave-year-out results and 56 inference rows remain in the receipt.', '',
              '## Missing-outcome tipping points (NOT estimates)', '',
              'Let missing ETF-minus-index mean residual differ from the observed mean residual by gamma. Only as a sensitivity assumption: all-pair mean = full-index mean + observed residual mean + missing_fraction*gamma. No missing ETF return is filled. Pooled and each-year gamma grids [-100,-50,-25,-10,-5,0,5,10,25,50,100] bp are all retained.', '',
              '| ETF | h | Missing ETF paired mean needed for zero, pooled bp | Residual gamma needed for zero, pooled bp |',
              '|---|---:|---:|---:|']
    for r in overview:
        lines.append(f"| {r['carrier']} | {r['horizon']} | {fmt(r['missing_etf_mean_to_zero_pooled_bp'])} | {fmt(r['gamma_to_zero_pooled_bp'])} |")
    lines += ['', 'A tipping point is not evidence about actual missing outcomes or a validated plausible range. No unrestricted all-event mean sign is identified when outcomes are missing.', '', '## Boundaries', '']
    lines += ['- '+s for s in receipt['limitations']]
    lines += ['', 'Old full-path and endpoint receipts are untouched; no failed common-primary cohort has been opened. No horizon selected. `BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.', '',
              'Method references and exact formulas are in `docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json`.']
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--output',type=Path)
    a=p.parse_args(); root=a.root.resolve()
    run(root,a.output or root/'docs/ops/evidence/r1a_endpoint_robustness_20260912')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
