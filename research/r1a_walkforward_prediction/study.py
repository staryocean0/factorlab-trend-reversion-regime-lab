"""One fixed parent-vs-parent+R1_A forward diagnostic, original Development only."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from research.r1a_walkforward_prediction.core import (
    CONTINUOUS, HORIZONS, RIDGE, require, raw_features, fit_ridge, training_mask,
    target, support_audit, prediction_rows, score, daily_accounting,
)

BASELINE = '442ed108de35e6bc3b9765b203b0c98b4353a20d'
FREEZE_COMMIT = '606d25933debcdb986fb19b4489e5c61407b52b3'
FREEZE = 'docs/governance/R1A_WALKFORWARD_PREDICTION_FREEZE@1.0.json'
REFERENCE = 'docs/ops/evidence/r1a_development_noise_20260912/development_pairs.csv'
YEARS = (2016, 2017, 2018, 2019, 2020)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def prefix_check(tape: pd.DataFrame, events: pd.DataFrame, thresholds: dict, vol_ref: float, cutoff: int) -> dict:
    """Rebuild only known events/features from prices ending at a fold boundary."""
    from research.index_price_validity.core import detect_waves, r1_events
    from research.r1_incremental_alpha_attribution.core import _parent_state, rolling_vol_ratio
    p = tape.close.to_numpy(float)[:cutoff+1]; days = tape.trading_day.to_numpy(str)[:cutoff+1]
    lower = detect_waves(p, thresholds['S1']); parent = detect_waves(p, thresholds['S2'])
    rows = r1_events(p, days, lower, parent, vol_ref, 'R1_A')
    confirms = [w.confirm_idx for w in parent]; cache = {}; vr = rolling_vol_ratio(p); found = []
    for row in rows.itertuples(index=False):
        e = int(row.confirm_idx)+1
        if e > cutoff:
            continue
        state = _parent_state(e-1, parent, confirms, p, cache)
        if state is None or state['parent_direction'] != int(row.signal_dir) or not np.isfinite(vr[e-1]):
            continue
        found.append({'entry_idx': e, 'parent_direction': int(row.signal_dir),
                      **{f: state[f] for f in CONTINUOUS[:-1]}, CONTINUOUS[-1]: vr[e-1]})
    rebuilt = pd.DataFrame(found).sort_values('entry_idx').reset_index(drop=True)
    original = events.loc[events.entry_idx <= cutoff].sort_values('entry_idx').reset_index(drop=True)
    require(rebuilt.entry_idx.tolist() == original.entry_idx.tolist(), 'prefix event identity changed')
    cols = ['parent_direction']+list(CONTINUOUS)
    error = float(np.max(np.abs(rebuilt[cols].to_numpy(float)-original[cols].to_numpy(float))))
    require(np.allclose(rebuilt[cols], original[cols], atol=1e-12, rtol=1e-12), 'prefix feature changed')
    return {'cutoff_idx': cutoff, 'cutoff_time': tape.time.iloc[cutoff].isoformat(),
            'events_checked': len(rebuilt), 'identities_equal': True, 'max_feature_difference': error}


def compile_population(root: Path, frozen: dict):
    from research.r1a_development_noise.study import load_development, guard
    from research.r1_incremental_alpha_attribution.core import build_r1_events_and_controls
    for path, blob in frozen['source_guards'].items():
        guard(root/path, blob)
    manifest = json.loads((root/'data/manifest.json').read_text())
    tape, sources = load_development(root, '000852.SH', manifest)
    require(len(sources) == 6 and all('/000852.SH/' in s['path'] for s in sources), 'source boundary')
    definition = json.loads((root/'docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json').read_text())
    events, background = build_r1_events_and_controls(tape.close.to_numpy(float), tape.trading_day.to_numpy(str),
        tape.time, definition['directional_change_thresholds'], definition['r1_vol_reference'], '2015-01-05', '2020-12-31', max_horizon=240)
    events = events.loc[events.cell == 'R1_A'].copy().sort_values('entry_idx').reset_index(drop=True)
    background = background.loc[background.cell == 'R1_A'].copy()
    ref = pd.read_csv(root/REFERENCE); ref = ref.loc[ref.symbol == '000852.SH'].sort_values('event_entry_idx')
    require(len(events) == len(ref) == 1752 and len(background) == 144733, 'original population count changed')
    require(events.entry_idx.tolist() == ref.event_entry_idx.tolist(), 'original event identity changed')
    require(np.array_equal(events.parent_direction, ref.parent_direction), 'original event direction changed')
    require(np.allclose(events[list(CONTINUOUS)], ref[['event_'+f for f in CONTINUOUS]], rtol=2e-10, atol=2e-11), 'original event features changed')
    events['is_event'] = 1; background['is_event'] = 0
    cols = ['entry_idx', 'parent_direction', 'is_event']+list(CONTINUOUS)
    population = pd.concat([events[cols], background[cols]], ignore_index=True).sort_values('entry_idx').reset_index(drop=True)
    require(not population.entry_idx.duplicated().any(), 'duplicate training observation')
    population['info_idx'] = population.entry_idx-1
    it = pd.DatetimeIndex(tape.time.iloc[population.info_idx.to_numpy(int)])
    population['info_day'] = it.strftime('%Y-%m-%d'); population['info_year'] = it.year
    population['info_clock_bucket'] = (it.hour*60+it.minute)//30
    population['entry_day'] = tape.trading_day.iloc[population.entry_idx.to_numpy(int)].to_numpy(str)
    return tape, population, sources, definition


def score_groups(frame: pd.DataFrame, scope: str, h: int) -> list[dict]:
    groups = [('POOLED', frame)]
    groups += [('YEAR_'+str(y), frame.loc[frame.info_year == y]) for y in YEARS]
    groups += [(side, frame.loc[frame.parent_direction == d]) for side, d in [('LONG', 1), ('SHORT', -1)]]
    groups += [('YEAR_'+str(y)+'_'+side, frame.loc[(frame.info_year == y) & (frame.parent_direction == d)])
               for y in YEARS for side, d in [('LONG', 1), ('SHORT', -1)]]
    return [{'scope': scope, 'horizon': h, 'group': name, **score(f)} for name, f in groups]


def run(root: Path, output: Path) -> dict:
    require(not output.exists(), 'fresh output directory required')
    frozen = json.loads((root/FREEZE).read_text())
    require(frozen['baseline_commit'] == BASELINE and frozen['status'] == 'FROZEN_BEFORE_NEW_FORECAST_FITS_AND_SCORES', 'wrong freeze')
    require(frozen['scope']['horizons'] == list(HORIZONS) and frozen['models']['lambda'] == RIDGE, 'model contract drift')
    require(frozen['timing']['evaluation_information_years'] == list(YEARS), 'fold drift')
    require(frozen['BLACKBOX_query_count'] == 3 and not frozen['production_authority'], 'authority drift')
    tape, population, sources, definition = compile_population(root, frozen)
    px = tape.close.to_numpy(float); original_events = population.loc[population.is_event == 1].copy()
    output.mkdir(parents=True)
    forecasts, contexts, audits, parameters, prefixes, coverage = [], [], [], [], [], []
    for h in HORIZONS:
        cov = original_events[['entry_idx', 'info_idx', 'info_day', 'info_year', 'entry_day', 'parent_direction']].copy()
        cov['horizon'] = h; cov['status'] = np.where(cov.info_year == 2015, 'WARMUP_2015_NOT_SCORED', 'PENDING')
        coverage.append(cov)
    cover = pd.concat(coverage, ignore_index=True)
    for year in YEARS:
        cutoff = int(np.flatnonzero(tape.trading_day.to_numpy(str) >= f'{year}-01-01')[0])-1
        prefixes.append({'evaluation_year': year, **prefix_check(tape, original_events,
            definition['directional_change_thresholds'], definition['r1_vol_reference'], cutoff)})
        test = population.loc[population.info_year == year].copy()
        print('Forward information year:', year, 'event rows:', int(test.is_event.sum()), flush=True)
        for h in HORIZONS:
            train = population.loc[training_mask(population, h, cutoff)].copy()
            event_n = int(train.is_event.sum()); background_n = len(train)-event_n
            audit = {'year': year, 'horizon': h, 'cutoff_idx': cutoff, 'cutoff_time': tape.time.iloc[cutoff].isoformat(),
                'train_n': len(train), 'train_event_n': event_n, 'train_background_n': background_n,
                'test_event_n': int(test.is_event.sum()), 'test_background_n': int((test.is_event == 0).sum()),
                'max_train_label_idx': int((train.entry_idx+h).max()) if len(train) else -1,
                'train_identity_sha256': hashlib.sha256(train[['entry_idx', 'is_event']].to_csv(index=False).encode()).hexdigest()}
            cmask = (cover.info_year == year) & (cover.horizon == h)
            if len(train) < 1000 or event_n < 20 or background_n < 20:
                audit['status'] = 'INSUFFICIENT_TRAINING'; audits.append(audit)
                cover.loc[cmask, 'status'] = audit['status']; continue
            require(audit['max_train_label_idx'] <= cutoff < int(test.info_idx.min()), 'train label leakage')
            ytrain = target(train, px, h)
            models = []
            try:
                for enhanced in (False, True):
                    x, names = raw_features(train, enhanced); fit = fit_ridge(x, ytrain)
                    xt, _ = raw_features(test, enhanced); prediction = fit.predict(xt)
                    models.append((fit, prediction)); model = 'parent_plus_R1A' if enhanced else 'parent'
                    parameters.append({'year': year, 'horizon': h, 'model': model, 'feature': 'intercept',
                        'center': 0., 'scale': 1., 'coefficient_standardized': fit.intercept, 'coefficient_raw': fit.intercept})
                    for j, name in enumerate(names):
                        parameters.append({'year': year, 'horizon': h, 'model': model, 'feature': name,
                            'center': fit.center[j], 'scale': fit.scale[j], 'coefficient_standardized': fit.beta[j],
                            'coefficient_raw': fit.beta[j]/fit.scale[j]})
                    audit[model+'_condition_number'] = fit.condition_number
            except np.linalg.LinAlgError as exc:
                audit['status'] = 'FIT_FAILED_'+type(exc).__name__; audits.append(audit)
                cover.loc[cmask, 'status'] = audit['status']; continue
            # Realized test labels are requested only AFTER both predictions exist.
            pred = prediction_rows(test, target(test, px, h), models[0][1], models[1][1], float(ytrain.mean()))
            pred['horizon'] = h; pred['fit_cutoff_idx'] = cutoff
            pred['entry_time'] = [tape.time.iloc[e].isoformat() for e in pred.entry_idx]
            pred['exit_idx'] = pred.entry_idx+h
            pred['exit_time'] = [tape.time.iloc[e+h].isoformat() for e in pred.entry_idx]
            ep = pred.loc[pred.is_event == 1].copy(); support = support_audit(train, test.loc[test.is_event == 1])
            ep = ep.join(support); forecasts.append(ep)
            contexts.append(pred.loc[pred.is_event == 0].copy())
            audit['status'] = 'SCORED'; audits.append(audit); cover.loc[cmask, 'status'] = 'SCORED'
    require(not (cover.status == 'PENDING').any(), 'unaccounted original event')
    require(bool(forecasts), 'no evaluable fold')
    ledger = pd.concat(forecasts, ignore_index=True).sort_values(['horizon', 'entry_idx']).reset_index(drop=True)
    context = pd.concat(contexts, ignore_index=True)
    require(not ledger[['horizon', 'entry_idx']].duplicated().any(), 'duplicate event score')
    require(int((cover.status == 'SCORED').sum()) == len(ledger), 'coverage reconciliation')
    scores = pd.DataFrame([row for h in HORIZONS for scope, f in [('EVENT', ledger), ('NON_EVENT_CONTEXT', context)]
                          for row in score_groups(f.loc[f.horizon == h], scope, h)])
    calendar = sorted(set(tape.loc[tape.trading_day >= '2016-01-01', 'trading_day'].astype(str)))
    daily, lags = daily_accounting(ledger, calendar)
    tables = {'all_original_event_coverage': cover, 'event_predictions': ledger, 'scores': scores,
        'daily_loss_accounting': daily, 'loss_lag_products': lags, 'fold_training_audit': pd.DataFrame(audits),
        'model_parameters': pd.DataFrame(parameters), 'prefix_identity_audit': pd.DataFrame(prefixes)}
    for name, f in tables.items():
        f.to_csv(output/(name+'.csv'), index=False, float_format='%.15g')
    horizon_reviews = []
    for h in HORIZONS:
        s = scores.loc[(scores.scope == 'EVENT') & (scores.horizon == h)]
        pooled = s.loc[s.group == 'POOLED'].iloc[0]
        annual = s.loc[s.group.isin(['YEAR_'+str(y) for y in YEARS])]
        sides = s.loc[s.group.isin(['LONG', 'SHORT'])]
        good = int((annual.mean_loss_improvement_bp2 > 0).sum())
        horizon_reviews.append({'horizon': h, 'scored_events': int(pooled.n),
            'mean_loss_improvement_bp2': float(pooled.mean_loss_improvement_bp2),
            'relative_mse_reduction': float(pooled.relative_mse_reduction), 'positive_years': good,
            'both_sides_positive': bool((sides.mean_loss_improvement_bp2 > 0).all()),
            'enhanced_beats_zero_mse': bool(pooled.enhanced_mse_bp2 < pooled.zero_forecast_mse_bp2),
            'enhanced_beats_past_mean_mse': bool(pooled.enhanced_mse_bp2 < pooled.past_mean_forecast_mse_bp2),
            'descriptive_consistency_NOT_significance': bool(pooled.mean_loss_improvement_bp2 > 0 and good >= 4 and (sides.mean_loss_improvement_bp2 > 0).all())})
    receipt = {'schema_id': 'factorlab_r1a_walkforward_prediction_receipt@1.0',
        'decision': 'WALKFORWARD_PREDICTION_DIAGNOSTIC_COMPLETED_NO_CONFIRMATION_AUTHORITY',
        'baseline_commit': BASELINE, 'freeze_commit': FREEZE_COMMIT, 'freeze_sha256': sha(root/FREEZE),
        'code_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'github_run_id': os.environ.get('GITHUB_RUN_ID'), 'sources': sources, 'input_blobs': frozen['source_guards'],
        'original_events': len(original_events), 'training_population_rows': len(population),
        'warmup_events': int((original_events.info_year == 2015).sum()),
        'scored_event_horizon_rows': len(ledger), 'successful_fit_count': 2*sum(x['status'] == 'SCORED' for x in audits),
        'horizon_review': horizon_reviews, 'prefix_identity_checks_pass': True,
        'coverage_status_counts': {str(k): int(v) for k, v in cover.status.value_counts().items()},
        'files': [{'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(output.glob('*.csv'))],
        'table_rows': {k+'.csv': len(f) for k, f in tables.items()},
        'post2020_price_files_read': [], 'ETF_price_files_read': [], 'new_matching': False,
        'signal_refitted': False, 'new_significance_test': False, 'horizon_selected': False,
        'BLACKBOX_query_count': 3, 'production_authority': False, 'fresh_oos': False,
        'confirmation_protocol_frozen': False, 'confirmation_clock_started': False}
    write_json(output/'receipt.json', receipt)
    report = ['# R1_A parent-baseline walk-forward prediction diagnostic', '', receipt['decision'], '',
        'Original CSI1000 Development only. Annual expanding fits, 2015 warm-up, information years 2016-2020 scored.',
        'Loss reduction is prediction-error improvement in bp^2, NOT extra trading return in bp. No calibrated significance or fresh-OOS claim.', '',
        '| h | Events | Parent RMSE bp | Enhanced RMSE bp | MSE improvement bp^2 | Relative MSE change | Positive years | Both sides + |',
        '|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in horizon_reviews:
        q = scores.loc[(scores.scope == 'EVENT') & (scores.group == 'POOLED') & (scores.horizon == r['horizon'])].iloc[0]
        report.append(f"| {r['horizon']} | {int(q.n)} | {q.parent_rmse_bp:.4f} | {q.enhanced_rmse_bp:.4f} | {r['mean_loss_improvement_bp2']:+.4f} | {100*r['relative_mse_reduction']:+.4f}% | {r['positive_years']}/5 | {r['both_sides_positive']} |")
    report += ['', '## Limits', '',
        'Both models are simple linear ridge on the same event/background mixture; the added indicator is only a global event-location term, not a nonlinear or interaction search.',
        'Support flags never delete events. Coordinate ranges/nearest distances are not joint-support or exchangeability certificates.',
        'The original event cohort has a terminal 240-bar completeness condition. Warm-up and unscored folds remain explicit; this is not all historical events or prospective admission.',
        'Daily loss accounting retains overlaps and zero-event days. It is not an IID SE, a trading equity curve or a causal comparison.',
        'Check zero/past-mean benchmark errors and yearly/side results before interpreting any relative gain. A weak parent model can make enhancement comparisons misleading.',
        'No post2020/ETF/2026 prices were read. Existing selected-pair failures, source bytes and old results are unchanged.',
        'No automatic refit, new candidate, execution experiment, confirmation clock or horizon selection follows this report.']
    (output/'REPORT.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps({'decision': receipt['decision'], 'warmup_events': receipt['warmup_events'], 'fit_count': receipt['successful_fit_count'], 'horizons': horizon_reviews}, indent=2))
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
