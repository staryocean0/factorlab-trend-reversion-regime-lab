"""Method-only serial calibration on frozen nuisance geometry, NOT real alpha.

No market OHLC columns, ETF return ledgers, 2026 files, or external APIs are read.
Every simulation rule is frozen; no simulation result changes a method parameter.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import sparse
from scipy.stats import norm, t as student_t
from research.r1a_confirmation_feasibility import study as prior
from research.r1a_endpoint_robustness import study as rb

BASELINE = 'a4b86fc4c0a8a0d8cf18f5d92dac6998b6602e74'
FREEZE = 'docs/governance/R1A_METHOD_CALIBRATION_FREEZE@1.0.json'
FREEZE_COMMIT = '3032c6567b15c7df705f09101d63ba1caeadd4d1'
NOISE = 'docs/ops/evidence/r1a_confirmation_feasibility_20260912/planning/historical_noise_NOT_new_tests.csv'
LAYERS = ('INDEX_ALL_FROZEN_PAIRS', 'ETF_OBSERVED_ENDPOINTS')
MODELS = ('IID_GAUSSIAN', 'BLOCK_GAUSSIAN_RHO0', 'BLOCK_GAUSSIAN_RHO06',
          'BLOCK_GAUSSIAN_RHO09', 'BLOCK_T5_RHO06',
          'HETEROSKEDASTIC_BLOCK_RHO06', 'SIGNED_LEG_REUSE_RHO06')
METHODS = ('GRAPH_T_BASELINE', 'EXPOSURE_SCORE_HAC6', 'FIVE_YEAR_GROUP_T',
           'ORACLE_MEAN_NORMAL_REFERENCE')
EFFECTS = (2, 4, 6)
REPS, BATCH, SEED, BURN = 2000, 100, 2026091207, 256
YEAR_NAMES = tuple(str(y) for y in range(2021, 2026))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def digest(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def bartlett_kernel(g: int, lags: int = 6) -> np.ndarray:
    require(g > 0 and lags >= 0, 'invalid kernel size')
    distance = np.abs(np.arange(g)[:, None]-np.arange(g)[None, :])
    return np.maximum(1-distance/(lags+1), 0.)


def binary_incidence(members: list[set[int]], g: int) -> sparse.csr_matrix:
    rr, cc = [], []
    require(len(members) > 1 and all(len(s) for s in members), 'empty exposure set')
    for i, group in enumerate(members):
        for b in sorted(group):
            require(0 <= b < g, 'block outside calendar')
            rr.append(i); cc.append(b)
    return sparse.csr_matrix((np.ones(len(rr)), (rr, cc)), shape=(len(members), g))


def signed_calendar_loads(bounds: np.ndarray, directions: np.ndarray, g: int) -> sparse.csr_matrix:
    require(bounds.shape == (len(directions), 4), 'invalid signed bounds')
    require(np.isin(directions, [-1, 1]).all(), 'invalid direction')
    rr, cc, vv = [], [], []
    for i, (e0, e1, c0, c1) in enumerate(bounds.astype(int)):
        require(0 <= e0 <= e1 and 0 <= c0 <= c1, 'reversed signed bounds')
        for a, b, sign in ((e0, e1, 1), (c0, c1, -1)):
            blocks = list(range(a//20, b//20+1))
            for block in blocks:
                rr.append(i); cc.append(block)
                vv.append(sign*directions[i]/math.sqrt(2*len(blocks)))
    matrix = sparse.csr_matrix((vv, (rr, cc)), shape=(len(bounds), g))
    matrix.eliminate_zeros()
    return matrix


def group_operator(availability: pd.DataFrame) -> tuple[sparse.csr_matrix, dict]:
    columns = ['event_entry_timestamp', 'event_exit_timestamp',
               'control_entry_timestamp', 'control_exit_timestamp']
    years = np.column_stack([availability[c].astype(str).str[:4].to_numpy() for c in columns])
    rr, cc, vv, counts = [], [], [], {}
    for group, year in enumerate(YEAR_NAMES):
        ids = np.flatnonzero(np.all(years == year, axis=1))
        counts[year] = len(ids)
        if len(ids):
            rr.extend([group]*len(ids)); cc.extend(ids.tolist()); vv.extend([1/len(ids)]*len(ids))
    return sparse.csr_matrix((vv, (rr, cc)), shape=(5, len(availability))), {
        'group_counts': counts, 'included': sum(counts.values()),
        'excluded_cross_year': len(availability)-sum(counts.values()),
        'available': all(n >= 10 for n in counts.values()),
        'estimand': 'equal_calendar_year_mean_not_original_pair_weighted_mean',
    }


def hac_variance(y: np.ndarray, incidence: sparse.csr_matrix, kernel: np.ndarray,
                 occupied: int) -> np.ndarray:
    n = y.shape[0]
    require(n > 1 and occupied > 1 and y.shape[0] == incidence.shape[0], 'invalid HAC geometry')
    u = y-y.mean(axis=0)
    scores = incidence.T @ u
    raw = np.einsum('ij,ij->j', scores, kernel @ scores)/(n*n)
    raw *= n/(n-1)*occupied/(occupied-1)
    require(np.min(raw) >= -1e-8, 'PSD score quadratic became materially negative')
    iid = np.sum(u*u, axis=0)/(n*(n-1))
    return np.maximum(np.maximum(raw, 0.), iid)


def estimates(y: np.ndarray, design: dict, oracle_var: float) -> dict:
    n, r = y.shape; avg = y.mean(axis=0); g = design['occupied']
    old_se, old_valid = prior.simulate_standard_errors(y, design['operator'], design['signs'], g)
    hv = hac_variance(y, design['incidence'], design['kernel'], g)
    hs = np.sqrt(hv); hv_ok = (n >= 30) & (g >= 30) & np.isfinite(hs) & (hs > 0)
    grouped = design['groups'] @ y
    group_mean = grouped.mean(axis=0)
    group_se = grouped.std(axis=0, ddof=1)/math.sqrt(5)
    group_ok = design['group_info']['available'] & np.isfinite(group_se) & (group_se > 0)
    require(oracle_var > 0 and np.isfinite(oracle_var), 'invalid oracle variance')
    return {
        METHODS[0]: (avg, old_se, old_valid, min(n-1, g-1)),
        METHODS[1]: (avg, hs, hv_ok, min(n-1, g-1)),
        METHODS[2]: (group_mean, group_se, group_ok, 4),
        METHODS[3]: (avg, np.full(r, math.sqrt(oracle_var)), np.ones(r, bool), None),
    }


def critical(df: int | None, family: int) -> float:
    require(family >= 1, 'invalid family')
    p = 1-.05/(2*family)
    return float(norm.ppf(p) if df is None else student_t.ppf(p, df))


def fitted_lambda(unsigned: sparse.csr_matrix, sd: float, se: float) -> tuple[float, float]:
    n = unsigned.shape[0]; loads = np.asarray(unsigned.sum(axis=0)).ravel()
    c = float(loads @ loads)
    raw = (n*n*se*se/(sd*sd)-n)/(c-n) if c > n else 0.
    return float(np.clip(raw, 0., .95)), float(raw)


def random_blocks(rng: np.random.Generator, g: int, r: int, rho: float,
                  heavy: bool = False) -> np.ndarray:
    require(0 <= rho < 1 and g > 0 and r > 0, 'invalid AR setup')
    size = (g+BURN, r)
    innovations = rng.standard_t(5, size=size)*math.sqrt(3/5) if heavy else rng.standard_normal(size)
    values = innovations.copy()
    for i in range(1, len(values)):
        values[i] = rho*values[i-1]+math.sqrt(1-rho*rho)*innovations[i]
    return values[BURN:]


def dgp_parameters(design: dict, model: str, covariance: np.ndarray) -> dict:
    require(model in MODELS, 'unfrozen DGP')
    signed = model == 'SIGNED_LEG_REUSE_RHO06'
    load = design['signed'] if signed else design['unsigned']
    lam = 0. if model == 'IID_GAUSSIAN' else design['lambda']
    p = design['primitive'] if signed else None
    load_dense = load.toarray()
    factor_row_var = np.einsum('ij,ij->i', load_dense @ covariance, load_dense)
    idio_row_var = np.asarray(p.multiply(p).sum(axis=1)).ravel() if signed else np.ones(design['n'])
    total_average_var = float(((1-lam)*idio_row_var+lam*factor_row_var).mean())
    require(total_average_var > 0, 'degenerate synthetic DGP')
    scale = design['sd']/math.sqrt(total_average_var)
    a = np.asarray(load.sum(axis=0)).ravel()
    idio_sum_var = float(np.square(np.asarray(p.sum(axis=0)).ravel()).sum()) if signed else float(design['n'])
    oracle = scale*scale*((1-lam)*idio_sum_var+lam*float(a @ covariance @ a))/(design['n']**2)
    return {'load': load, 'lambda': lam, 'scale': scale, 'oracle_var': oracle,
            'average_marginal_variance': scale*scale*total_average_var}


def make_y(design: dict, model: str, params: dict, eps_pairs: np.ndarray,
           eps_clocks: np.ndarray | None, blocks: np.ndarray) -> np.ndarray:
    if model == 'SIGNED_LEG_REUSE_RHO06':
        require(eps_clocks is not None, 'missing shared clock innovations')
        errors = design['primitive'] @ eps_clocks
    else:
        errors = eps_pairs[design['pair_positions']]
    lam = params['lambda']
    return params['scale']*(math.sqrt(1-lam)*errors+math.sqrt(lam)*(params['load'] @ blocks))


def load_inputs(root: Path) -> tuple[list[dict], dict]:
    """Only source geometry, calendar columns, and already disclosed scales."""
    contract = json.loads((root/FREEZE).read_text())
    require(contract['baseline_commit'] == BASELINE and contract['status'] == 'FROZEN_BEFORE_METHOD_SIMULATIONS', 'freeze drift')
    sim = contract['simulation']
    require(sim['models'] == list(MODELS) and sim['repetitions_per_model'] == REPS and sim['seed'] == SEED, 'simulation drift')
    require(sim['batch_size'] == BATCH and sim['burn_in_blocks'] == BURN and sim['effects_bp_assumed'] == list(EFFECTS), 'budget drift')
    require(list(contract['methods']) == list(METHODS) and contract['designs']['horizons'] == list(rb.HORIZONS), 'method drift')
    require(not contract['confirmation_outcomes_authorized'] and not contract['production_authority'] and contract['BLACKBOX_query_count'] == 3, 'authority drift')
    inputs = contract['inputs']
    for path, key in ((rb.PAIRS, 'pairs_blob_sha1'), (rb.OLD+'/endpoint_receipt.json', 'endpoint_receipt_blob_sha1'),
                      (NOISE, 'noise_blob_sha1'), ('data/manifest.json', 'index_manifest_blob_sha1')):
        rb.blob_guard(root/path, inputs[key])
    manifest = json.loads((root/'data/manifest.json').read_text())
    calendar, verified = set(), []
    parts = [x for x in manifest['files'] if x['symbol'] == '000852.SH' and x['frequency'] == '1m' and 2021 <= x['year'] <= 2025]
    require(len(parts) == 5, 'expected exactly five calendar partitions')
    for spec in parts:
        rel = Path(spec['path']); path = (root/rel).resolve()
        require(path.is_relative_to(root.resolve()) and str(rel).startswith('data/market/1m/000852.SH/'), 'calendar path escape')
        require(digest(path) == spec['sha256'] and path.stat().st_size == spec['bytes'], 'calendar byte identity changed')
        frame = pq.read_table(path, columns=['trading_day']).to_pandas()
        require(len(frame) == spec['rows'], 'calendar row count changed')
        calendar.update(frame.trading_day.astype(str).tolist())
        verified.append({'path': str(rel), 'sha256': spec['sha256'], 'columns_read': ['trading_day']})
    days = sorted(calendar)
    require(len(days) == 1212 and days[0][:4] == '2021' and days[-1][:4] == '2025', 'unexpected historical clock')
    day_map = {day: i for i, day in enumerate(days)}; g = (len(days)-1)//20+1
    pairs = pd.read_csv(root/rb.PAIRS)
    pairs = pairs.loc[pairs.cell == 'R1_A'].copy().reset_index(drop=True)
    pairs['pair_id'] = pairs.symbol.astype(str)+':R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
    require(not pairs.pair_id.duplicated().any(), 'duplicate pair identity')
    pairs['_position'] = np.arange(len(pairs))
    nodes = sorted({(p.symbol, int(i)) for p in pairs.itertuples() for i in (p.event_entry_idx, p.control_entry_idx)})
    node_map = {node: i for i, node in enumerate(nodes)}
    noise = pd.read_csv(root/NOISE)
    noise = noise.loc[noise.spec == 'L20_shift0']
    require(len(noise) == 28 and noise.observed_mean_used_as_true_effect.eq(False).all(), 'invalid disclosed nuisance table')
    receipt = json.loads((root/rb.OLD/'endpoint_receipt.json').read_text())
    specs = {x['path']: x for x in receipt['evidence_files']}
    designs = []
    for symbol, carrier in rb.MAP.items():
        original = pairs.loc[pairs.symbol == symbol].reset_index(drop=True)
        require(len(original) == rb.COUNTS[symbol], 'original pair counts changed')
        name = carrier+'_endpoint_availability.csv'; path = root/rb.OLD/name
        require(digest(path) == specs[name]['sha256'] and path.stat().st_size == specs[name]['bytes'], 'availability identity changed')
        av = pd.read_csv(path)
        require(not av.duplicated(['pair_id', 'horizon']).any(), 'duplicate availability')
        for h in rb.HORIZONS:
            a_all = av.loc[av.horizon == h].set_index('pair_id').loc[original.pair_id].reset_index()
            require(a_all.eligible.isin([True, False]).all(), 'invalid eligibility')
            for layer in LAYERS:
                mask = np.ones(len(original), bool) if layer == LAYERS[0] else a_all.eligible.to_numpy(bool)
                p = original.loc[mask].reset_index(drop=True); a = a_all.loc[mask].reset_index(drop=True)
                require(np.array_equal(p.pair_id, a.pair_id), 'geometry misalignment')
                bounds = rb._bounds(a, day_map)
                memberships = rb.block_memberships(bounds, 20, 0)
                incidence = binary_incidence(memberships, g)
                unsigned = sparse.diags(1/np.sqrt(np.asarray(incidence.sum(axis=1)).ravel())) @ incidence
                signed_load = signed_calendar_loads(bounds, p.parent_direction.to_numpy(int), g)
                positions_e = np.array([node_map[(symbol, int(i))] for i in p.event_entry_idx])
                positions_c = np.array([node_map[(symbol, int(i))] for i in p.control_entry_idx])
                directions = p.parent_direction.to_numpy(float)
                primitive = sparse.csr_matrix((np.r_[directions, -directions]/math.sqrt(2),
                    (np.r_[np.arange(len(p)), np.arange(len(p))], np.r_[positions_e, positions_c])),
                    shape=(len(p), len(nodes)))
                primitive.eliminate_zeros()
                info = noise.loc[(noise.layer == layer) & (noise.index_symbol == symbol) & (noise.horizon == h)]
                require(len(info) == 1 and int(info.iloc[0].historical_pairs) == len(p), 'nuisance design mismatch')
                sd = float(info.iloc[0].marginal_SD_bp); se = float(info.iloc[0].historical_SE_bp)
                lam, raw_lam = fitted_lambda(unsigned, sd, se)
                operator, signs = prior.meat_operator(memberships)
                groups, group_info = group_operator(a)
                design = {'id': f'{layer}:{carrier}:{h}', 'layer': layer, 'index_symbol': symbol,
                          'carrier': carrier, 'horizon': h, 'n': len(p), 'sd': sd, 'historical_se': se,
                          'lambda': lam, 'lambda_unclipped': raw_lam, 'incidence': incidence,
                          'unsigned': unsigned, 'signed': signed_load, 'primitive': primitive,
                          'operator': operator, 'signs': signs, 'occupied': len(set().union(*memberships)),
                          'kernel': bartlett_kernel(g, 6), 'groups': groups, 'group_info': group_info,
                          'pair_positions': p['_position'].to_numpy(int)}
                designs.append(design)
    require(len(designs) == 28, 'design count mismatch')
    return designs, {'calendar_days': len(days), 'calendar_blocks': g, 'pair_universe': len(pairs),
                     'entry_clock_universe': len(nodes), 'calendar_files': verified,
                     'noise_sha256': digest(root/NOISE), 'pair_sha256': digest(root/rb.PAIRS),
                     'availability_files': [{'path': k, **specs[k]} for k in specs if k.endswith('_availability.csv')],
                     'return_ledger_files_read': [], 'OHLC_columns_read': [], 'new_data_files_read': []}


def simulate(designs: list[dict], universe: dict, repetitions: int = REPS) -> tuple[pd.DataFrame, pd.DataFrame]:
    require(repetitions > 0, 'simulation repetition count')
    g = universe['calendar_blocks']; n_pairs = universe['pair_universe']; n_clocks = universe['entry_clock_universe']
    rows, family_rows = [], []
    for model_no, model in enumerate(MODELS):
        rho = .9 if model.endswith('RHO09') else .6 if model.endswith('RHO06') else 0.
        heavy = model == 'BLOCK_T5_RHO06'
        covariance = rho**np.abs(np.arange(g)[:, None]-np.arange(g)[None, :]) if rho else np.eye(g)
        block_scale = np.ones(g)
        if model == 'HETEROSKEDASTIC_BLOCK_RHO06':
            block_scale[g//2:] = 2.
        covariance = covariance*block_scale[:, None]*block_scale[None, :]
        parameters = {d['id']: dgp_parameters(d, model, covariance) for d in designs}
        counts = {(d['id'], method): {'valid': 0, 'reject': 0, 'reject14': 0, 'se_sum': 0.,
                  'width14_sum': 0., 'power': {delta: 0 for delta in EFFECTS}} for d in designs for method in METHODS}
        joint = {(method, family): {'reject': 0, 'complete': 0} for method in METHODS for family in LAYERS+('COMBINED_28',)}
        rng = np.random.default_rng(SEED+model_no*1000003)
        for start in range(0, repetitions, BATCH):
            r = min(BATCH, repetitions-start)
            eps = rng.standard_t(5, size=(n_pairs, r))*math.sqrt(3/5) if heavy else rng.standard_normal((n_pairs, r))
            clocks = rng.standard_normal((n_clocks, r)) if model == 'SIGNED_LEG_REUSE_RHO06' else None
            blocks = random_blocks(rng, g, r, rho, heavy)*block_scale[:, None]
            union = {key: np.zeros(r, bool) for key in joint}
            complete = {key: np.ones(r, bool) for key in joint}
            for d in designs:
                params = parameters[d['id']]
                y = make_y(d, model, params, eps, clocks, blocks)
                for method, (mean, se, valid, df) in estimates(y, d, params['oracle_var']).items():
                    valid = np.asarray(valid, bool) & np.isfinite(mean) & np.isfinite(se) & (se > 0)
                    statistic = np.divide(mean, se, out=np.zeros(r), where=valid)
                    c1, c14, c28 = (critical(df, size) for size in (1, 14, 28))
                    counter = counts[(d['id'], method)]
                    counter['valid'] += int(valid.sum())
                    counter['reject'] += int((valid & (np.abs(statistic) > c1)).sum())
                    counter['reject14'] += int((valid & (np.abs(statistic) > c14)).sum())
                    counter['se_sum'] += float(se[valid].sum())
                    counter['width14_sum'] += float((2*c14*se[valid]).sum())
                    for delta in EFFECTS:
                        counter['power'][delta] += int((valid & (mean+delta > c14*se)).sum())
                    for family, cutoff in ((d['layer'], c14), ('COMBINED_28', c28)):
                        key = (method, family)
                        union[key] |= valid & (np.abs(statistic) > cutoff)
                        complete[key] &= valid
            for key in joint:
                joint[key]['reject'] += int(union[key].sum())
                joint[key]['complete'] += int(complete[key].sum())
        for d in designs:
            params = parameters[d['id']]
            for method in METHODS:
                c = counts[(d['id'], method)]; lo, hi = prior.wilson(c['reject'], repetitions)
                row = {k: d[k] for k in ('id', 'layer', 'index_symbol', 'carrier', 'horizon', 'n')}
                row.update({'DGP_ASSUMED': model, 'method': method, 'repetitions': repetitions,
                            'seed': SEED+model_no*1000003, 'rho_ASSUMED': rho, 'lambda_nuisance': params['lambda'],
                            'marginal_SD_target_bp': d['sd'], 'oracle_mean_SE_under_DGP_bp': math.sqrt(params['oracle_var']),
                            'null_rejections': c['reject'], 'null_rejection_rate': c['reject']/repetitions,
                            'null_MC95_lo': lo, 'null_MC95_hi': hi, 'severe_size_warning': bool(lo > .075),
                            'valid_fraction': c['valid']/repetitions, 'invalid_replicates': repetitions-c['valid'],
                            'mean_reported_SE_bp': c['se_sum']/c['valid'] if c['valid'] else None,
                            'mean_family14_interval_width_bp': c['width14_sum']/c['valid'] if c['valid'] else None,
                            'marginal_family14_rejections': c['reject14'],
                            'reference_not_deployable': method == METHODS[3],
                            'estimand': 'equal_year_mean' if method == METHODS[2] else 'pair_weighted_mean'})
                for delta in EFFECTS:
                    power_lo, power_hi = prior.wilson(c['power'][delta], repetitions)
                    row[f'power_positive_family14_effect{delta}bp_ASSUMED'] = c['power'][delta]/repetitions
                    row[f'power_effect{delta}_MC95_lo'] = power_lo
                    row[f'power_effect{delta}_MC95_hi'] = power_hi
                rows.append(row)
        for (method, family), c in joint.items():
            lo, hi = prior.wilson(c['reject'], repetitions)
            family_rows.append({'DGP_ASSUMED': model, 'method': method, 'family': family,
                                'family_size': 28 if family == 'COMBINED_28' else 14,
                                'repetitions': repetitions, 'joint_rejections': c['reject'],
                                'joint_rejection_rate': c['reject']/repetitions, 'MC95_lo': lo, 'MC95_hi': hi,
                                'severe_size_warning': bool(lo > .075),
                                'complete_quantification_fraction': c['complete']/repetitions,
                                'shared_calendar_and_pair_shocks': True})
        print('Completed fixed synthetic model:', model, flush=True)
    return pd.DataFrame(rows), pd.DataFrame(family_rows)


def control_variance_ratio(k: float, rho: float) -> float:
    require(k >= 1 and 0 <= rho <= 1, 'invalid control scenario')
    return (1+rho+(1-rho)/k)/2


def efficiency(designs: list[dict], days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for d in designs:
        for effect in EFFECTS:
            for family in (1, 14):
                needed = days*(d['historical_se']/effect)**2*(norm.ppf(1-.05/(2*family))+norm.ppf(.8))**2
                for budget in (243, 486):
                    ratio = budget/needed
                    rows.append({k: d[k] for k in ('layer', 'index_symbol', 'carrier', 'horizon')} | {
                        'effect_bp_ASSUMED': effect, 'family_size': family, 'target_power': .8,
                        'budget_trading_days': budget, 'prior_required_days_CONDITIONAL': float(needed),
                        'required_variance_ratio': float(ratio), 'required_variance_reduction': float(max(0., 1-ratio)),
                        'required_information_multiplier': float(1/ratio),
                        'balanced_independent_controls_limit_ratio': .5,
                        'infinite_controls_sufficient_in_balanced_model': bool(ratio >= .5),
                        'measured_R_squared': False, 'real_matching_changed': False})
    controls = [{'K_controls': 'infinity' if math.isinf(k) else str(int(k)), 'control_error_correlation_ASSUMED': rho,
                 'variance_ratio_balanced_model': control_variance_ratio(k, rho),
                 'information_multiplier_balanced_model': 1/control_variance_ratio(k, rho),
                 'empirical_R1A_decomposition': False}
                for k in (1., 2., 5., 10., math.inf) for rho in (0., .25, .5, .75)]
    return pd.DataFrame(rows), pd.DataFrame(controls)


def method_screen(cells: pd.DataFrame, families: pd.DataFrame) -> dict:
    result = {}
    for method in METHODS:
        c = cells.loc[cells.method == method]; f = families.loc[families.method == method]
        require(len(c) > 0 and len(f) > 0, 'empty method screen')
        passed = bool(not c.severe_size_warning.any() and c.valid_fraction.ge(.99).all()
                      and f.MC95_hi.le(.075).all() and f.complete_quantification_fraction.ge(.99).all())
        result[method] = {'severe_marginal_cells': int(c.severe_size_warning.sum()),
                          'severe_family_cells': int(f.severe_size_warning.sum()),
                          'minimum_valid_fraction': float(c.valid_fraction.min()),
                          'maximum_joint_MC95_hi': float(f.MC95_hi.max()),
                          'minimum_complete_family_fraction': float(f.complete_quantification_fraction.min()),
                          'limited_simulation_screen_pass': passed if method != METHODS[3] else False,
                          'oracle_reference_only': method == METHODS[3],
                          'real_market_validity_proved': False, 'production_authorized': False}
    return result


def run(root: Path, output: Path) -> dict:
    require(not output.exists(), 'fresh output directory required; preserve prior evidence')
    designs, inputs = load_inputs(root)
    cells, families = simulate(designs, inputs)
    budget, controls = efficiency(designs, inputs['calendar_days'])
    output.mkdir(parents=True)
    tables = {'all_method_DGP_design_cells.csv': cells, 'joint_family_null_checks.csv': families,
              'information_budget_NOT_commitment.csv': budget, 'multiple_control_bounds_ASSUMPTIONS.csv': controls}
    for name, frame in tables.items():
        frame.to_csv(output/name, index=False)
    summary = method_screen(cells, families)
    geometry = [{k: d[k] for k in ('id', 'layer', 'carrier', 'horizon', 'n', 'sd', 'historical_se',
                                  'lambda', 'lambda_unclipped', 'occupied', 'group_info')} for d in designs]
    result = {'schema_id': 'factorlab_r1a_method_calibration_receipt@1.0',
              'decision': 'BOUNDED_SYNTHETIC_METHOD_REVIEW_COMPLETED_NO_CONFIRMATION_AUTHORITY',
              'baseline_commit': BASELINE, 'freeze_commit': FREEZE_COMMIT, 'freeze_sha256': digest(root/FREEZE),
              'code_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              'github_run_id': os.environ.get('GITHUB_RUN_ID'), 'seed': SEED,
              'joint_model_replicates': REPS*len(MODELS), 'synthetic_design_datasets': REPS*len(MODELS)*len(designs),
              'design_count': len(designs), 'method_count': len(METHODS), 'inputs': inputs, 'geometry': geometry,
              'method_screen': summary, 'table_rows': {k: len(v) for k, v in tables.items()},
              'output_csvs': [{'path': name, 'sha256': digest(output/name), 'bytes': (output/name).stat().st_size} for name in tables],
              'methods_clearing_limited_screen': [m for m, v in summary.items() if v['limited_simulation_screen_pass']],
              'real_R1A_means_retested': False, 'new_price_data_read': False, 'horizon_selected': False,
              'real_matching_changed': False, 'missing_outcomes_imputed': False,
              'BLACKBOX_query_count': 3, 'production_authority': False, 'fresh_oos': False,
              'confirmation_protocol_frozen': False, 'confirmation_clock_started': False,
              'interpretation': 'Synthetic-size/power and assumption-based information accounting only. No real alpha, causal or prospective validity certificate. The oracle is not a deployable method; equal-year and pair-weighted estimands are different.'}
    write_json(output/'method_receipt.json', result)
    lines = ['# R1_A bounded method calibration and information review', '',
             'Decision: `'+result['decision']+'`.', '',
             f'Freeze `{FREEZE_COMMIT}`; code `{result["code_commit"]}`; Actions `{result["github_run_id"]}`.', '',
             'All outcomes below are synthetic; the actual R1_A means were not retested. Seven predeclared DGPs, 28 designs and 2,000 shared-family replicates per DGP. No 2026 data, market OHLC columns or return ledgers read.', '',
             '## Fixed method screen', '',
             '| Method | Severe marginal cells | Severe family cells | Max joint MC upper | Screen pass |',
             '|---|---:|---:|---:|---|']
    for m, v in summary.items():
        lines.append(f'| {m} | {v["severe_marginal_cells"]} | {v["severe_family_cells"]} | {v["maximum_joint_MC95_hi"]:.2%} | {v["limited_simulation_screen_pass"]} |')
    lines += ['', 'The known-covariance oracle is never eligible for the screen. Passing a finite simulation screen would not establish market validity.', '',
              '## Nominal 5% pointwise null rejection ranges across 28 designs', '',
              '| Model | Method | Minimum | Maximum |', '|---|---|---:|---:|']
    for (model, method), f in cells.groupby(['DGP_ASSUMED', 'method'], sort=False):
        lines.append(f'| {model} | {method} | {f.null_rejection_rate.min():.2%} | {f.null_rejection_rate.max():.2%} |')
    lines += ['', '## Joint familywise false rejection', '',
              '| Model | Method | Index family14 | ETF family14 | Combined family28 |', '|---|---|---:|---:|---:|']
    for model in MODELS:
        for method in METHODS:
            f = families.loc[(families.DGP_ASSUMED == model) & (families.method == method)].set_index('family')
            lines.append(f'| {model} | {method} | {f.loc[LAYERS[0], "joint_rejection_rate"]:.2%} | {f.loc[LAYERS[1], "joint_rejection_rate"]:.2%} | {f.loc["COMBINED_28", "joint_rejection_rate"]:.2%} |')
    lines += ['', '## Information efficiency: illustrative CSI1000 index locations, not selected horizons', '',
              '| h | Assumed effect bp | One-year required noise reduction | Needed information multiple | Infinite balanced independent controls enough? |',
              '|---:|---:|---:|---:|---|']
    selected = budget.loc[(budget.layer == LAYERS[0]) & (budget.index_symbol == '000852.SH') &
                          budget.horizon.isin([15, 30]) & (budget.family_size == 14) & (budget.budget_trading_days == 243)]
    for row in selected.itertuples():
        lines.append(f'| {row.horizon} | {row.effect_bp_ASSUMED} | {row.required_variance_reduction:.2%} | {row.required_information_multiplier:.2f} | {row.infinite_controls_sufficient_in_balanced_model} |')
    lines += ['', 'In the explicit equal-variance independent-event/control model, infinitely many independent controls can remove at most half of paired noise (2x information). Correlated controls reduce that benefit. This is not a measured universal bound. Required reductions inherit the old planning assumptions and are not attained R-squared values.', '',
              '## Limits and stopping rule', '',
              'The exposure-score HAC is a duplicated-incidence adaptation, not a plug-in validity theorem. Group t relies on approximately independent group estimates and changes the target to equal-year means when effects differ. The oracle knows the simulated covariance and is unavailable in practice. Cross-block AR, heavy-tail, heteroskedastic and signed/reused-leg cases are stipulated scenarios, not fitted market truth.', '',
              'Joint shocks are explicitly shared across horizons and layers; one stylized family dependence is tested, not every possible dependence. Abstentions and complete-family quantification are recorded. No bandwidth/group/DGP/seed/threshold was changed based on results.', '',
              'The bounded method sweep ends here. No method is applied to historic R1_A means, no failed common-primary cohort is opened, and no prospective data are spent. Historical research conclusions and all old freezes remain unchanged.', '',
              '`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root.resolve(), args.output.resolve())
    print(json.dumps({'decision': result['decision'], 'method_screen': result['method_screen'],
                      'table_rows': result['table_rows']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
