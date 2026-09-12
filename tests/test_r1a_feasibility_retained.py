"""Reconcile retained feasibility; never treat planning as a new alpha test."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.r1a_confirmation_feasibility.study import sample_plan, budget_plan, MODELS

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'docs/ops/evidence/r1a_confirmation_feasibility_20260912'
PLAN = BASE/'planning'


def read(name):
    return pd.read_csv(PLAN/name, float_precision='round_trip')


def test_retained_receipt_scope_counts_and_hashes():
    r=json.loads((PLAN/'feasibility_receipt.json').read_text())
    freeze=ROOT/'docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json'
    assert hashlib.sha256(freeze.read_bytes()).hexdigest()==r['freeze_sha256']
    assert r['decision']=='FEASIBILITY_MEASURED_CONDITIONAL_NOT_CONFIRMATION'
    assert r['design_count']==28 and r['historical_trading_days']==1212
    assert r['simulated_samples']==224000 and r['BLACKBOX_query_count']==3
    for flag in ['new_confirmation_prices_read','new_significance_claim','horizon_selected',
                 'confirmation_protocol_frozen','confirmation_clock_started','unobserved_ETF_returns_imputed',
                 'production_authority','fresh_oos']:
        assert r[flag] is False
    expected={
        'historical_noise_NOT_new_tests.csv':112,
        'sample_size_scenarios_NOT_commitments.csv':2688,
        'fixed_budget_power_NOT_forecasts.csv':6720,
        'null_calibration_synthetic_DGPs.csv':112,
        'historical_pair_rates.csv':140,
    }
    assert r['table_rows']==expected
    for spec in r['files']:
        p=PLAN/spec['path']
        assert p.stat().st_size==spec['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256']
        assert len(read(spec['path']))==expected[spec['path']]


def test_every_sample_size_scenario_recomputes_from_noise_not_observed_mean():
    keys=['layer','index_symbol','carrier','horizon','spec']
    noise=read('historical_noise_NOT_new_tests.csv').set_index(keys)
    rows=read('sample_size_scenarios_NOT_commitments.csv')
    assert set(rows.family_size)=={1,7,14,28}
    assert set(rows.effect_bp_ASSUMED)=={2,4,6}
    assert set(rows.target_positive_detection)=={.8,.9}
    assert not rows.duplicated(keys+['family_size','effect_bp_ASSUMED','target_positive_detection']).any()
    for r in rows.to_dict('records'):
        n=noise.loc[tuple(r[k] for k in keys)]
        recomputed=sample_plan(n.historical_SE_bp,n.marginal_SD_bp,int(n.historical_pairs),
                              int(n.historical_trading_days),r['effect_bp_ASSUMED'],
                              r['target_positive_detection'],int(r['family_size']))
        assert r['required_trading_days_CONDITIONAL']==recomputed['required_trading_days_CONDITIONAL']
        assert r['expected_eligible_pairs_CONDITIONAL']==recomputed['expected_eligible_pairs_CONDITIONAL']
        assert r['equivalent_years_NOT_FORECAST']==pytest.approx(recomputed['equivalent_years_NOT_FORECAST'])
    assert noise.observed_mean_used_as_true_effect.eq(False).all()


def test_all_fixed_budgets_recompute_without_selecting_best_horizon():
    keys=['layer','index_symbol','carrier','horizon','spec']
    noise=read('historical_noise_NOT_new_tests.csv').set_index(keys)
    rows=read('fixed_budget_power_NOT_forecasts.csv')
    assert set(rows.horizon)=={1,5,15,30,60,120,240}
    assert set(rows.budget_trading_days)=={60,120,243,486,1215}
    for r in rows.to_dict('records'):
        n=noise.loc[tuple(r[k] for k in keys)]
        b=budget_plan(n.historical_SE_bp,int(n.historical_pairs),int(n.historical_trading_days),
                      int(r['budget_trading_days']),r['effect_bp_ASSUMED'],int(r['family_size']))
        assert r['positive_detection_probability_CONDITIONAL']==pytest.approx(b['positive_detection_probability_CONDITIONAL'],abs=1e-14)
        assert r['detectable_effect_80_bp_CONDITIONAL']==pytest.approx(b['detectable_effect_80_bp_CONDITIONAL'])


def test_calibration_records_all_models_and_invalid_replicates():
    c=read('null_calibration_synthetic_DGPs.csv')
    assert set(c.DGP_ASSUMED)==set(MODELS)
    assert c.groupby('DGP_ASSUMED').size().eq(28).all()
    assert c.repetitions.eq(2000).all()
    assert np.allclose(c.pointwise_rejection_rate,c.pointwise_rejections/c.repetitions)
    assert c.pointwise_rejections.ge(0).all()
    assert (c.pointwise_rejections+c.unquantified_replicates<=c.repetitions).all()
    assert not c.real_market_calibration_proved.any()
    assert not c.joint_family_error_simulated.any()
    assert np.array_equal(c.severe_size_warning.to_numpy(),(c.pointwise_MC95_lo>.075).to_numpy())


def test_new_data_role_not_promoted_by_filename_or_prior_use():
    r=json.loads((BASE/'data_role/data_role_audit.json').read_text())
    assert len(r['repositories'])==5
    assert r['qualified_confirmation_packages']==[]
    assert r['2026_role']=='UNKNOWN_NOT_ADMITTED'
    assert r['candidate_price_bytes_read'] is False
    assert r['candidate_strategy_outcomes_read'] is False
    c=json.loads((BASE/'data_role/csi1000_2026_candidate_review.json').read_text())
    assert c['instrument']=='000852.SH' and c['declared_trading_days']==154
    assert c['decision']=='KNOWN_REPEAT_USE_NOT_CERTIFIED_R1A_HOLDOUT'
    assert c['source_fresh_oos'] is False and c['R1A_specific_exposure_history']=='UNKNOWN'
    assert c['price_bytes_read'] is False and c['2026_strategy_outcomes_read'] is False
    assert c['copied_to_this_repository'] is False
