import json
from pathlib import Path
import numpy as np
import pandas as pd
from research.r1a_method_calibration import study as m

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/ops/evidence/r1a_method_calibration_20260912'


def receipt():
    return json.loads((EVIDENCE/'method_receipt.json').read_text())


def test_method_inputs_and_outputs_are_sealed():
    r = receipt()
    assert r['freeze_commit'] == m.FREEZE_COMMIT
    assert r['freeze_sha256'] == m.digest(ROOT/m.FREEZE)
    assert r['synthetic_design_datasets'] == 392000
    assert r['joint_model_replicates'] == 14000
    assert r['design_count'] == 28 and r['method_count'] == 4
    assert r['inputs']['OHLC_columns_read'] == []
    assert r['inputs']['return_ledger_files_read'] == []
    assert r['inputs']['new_data_files_read'] == []
    assert all(x['columns_read'] == ['trading_day'] for x in r['inputs']['calendar_files'])
    for s in r['output_csvs']:
        path = EVIDENCE/s['path']
        assert path.is_file() and path.stat().st_size == s['bytes']
        assert m.digest(path) == s['sha256']
        assert len(pd.read_csv(path)) == r['table_rows'][s['path']]


def test_every_fixed_design_method_and_DGP_retained():
    cells = pd.read_csv(EVIDENCE/'all_method_DGP_design_cells.csv')
    assert len(cells) == 784
    assert not cells.duplicated(['id', 'DGP_ASSUMED', 'method']).any()
    assert set(cells.method) == set(m.METHODS)
    assert set(cells.DGP_ASSUMED) == set(m.MODELS)
    assert set(cells.horizon) == set(m.rb.HORIZONS)
    assert cells.groupby(['DGP_ASSUMED', 'method']).size().eq(28).all()
    assert cells.repetitions.eq(2000).all()
    assert np.allclose(cells.null_rejection_rate, cells.null_rejections/2000)
    assert np.array_equal(cells.severe_size_warning, cells.null_MC95_lo > .075)
    assert np.allclose(cells.valid_fraction, 1-cells.invalid_replicates/2000)
    power = cells[[f'power_positive_family14_effect{x}bp_ASSUMED' for x in (2, 4, 6)]].to_numpy()
    assert ((power >= 0) & (power <= 1)).all()
    assert (np.diff(power, axis=1) >= -1e-12).all()


def test_family_union_is_real_joint_count_not_marginal_sum():
    f = pd.read_csv(EVIDENCE/'joint_family_null_checks.csv')
    assert len(f) == 84 and not f.duplicated(['DGP_ASSUMED', 'method', 'family']).any()
    assert set(f.family) == set(m.LAYERS+('COMBINED_28',))
    assert f.shared_calendar_and_pair_shocks.eq(True).all()
    assert np.allclose(f.joint_rejection_rate, f.joint_rejections/2000)
    assert np.array_equal(f.severe_size_warning, f.MC95_lo > .075)
    assert np.array_equal(f.family_size, np.where(f.family == 'COMBINED_28', 28, 14))


def test_retained_screen_does_not_promote_failed_methods_or_oracle():
    cells = pd.read_csv(EVIDENCE/'all_method_DGP_design_cells.csv')
    families = pd.read_csv(EVIDENCE/'joint_family_null_checks.csv')
    screen = m.method_screen(cells, families)
    stored = receipt()['method_screen']
    for key in m.METHODS:
        assert screen[key]['severe_marginal_cells'] == stored[key]['severe_marginal_cells']
        assert screen[key]['severe_family_cells'] == stored[key]['severe_family_cells']
        assert screen[key]['limited_simulation_screen_pass'] == stored[key]['limited_simulation_screen_pass']
        assert not stored[key]['real_market_validity_proved']
        assert not stored[key]['production_authorized']
    assert receipt()['methods_clearing_limited_screen'] == []
    assert stored['FIVE_YEAR_GROUP_T']['severe_family_cells'] == 0
    assert stored['FIVE_YEAR_GROUP_T']['severe_marginal_cells'] > 0
    assert stored['ORACLE_MEAN_NORMAL_REFERENCE']['oracle_reference_only'] is True


def test_efficiency_bound_not_claimed_as_empirical_R_squared():
    b = pd.read_csv(EVIDENCE/'information_budget_NOT_commitment.csv')
    c = pd.read_csv(EVIDENCE/'multiple_control_bounds_ASSUMPTIONS.csv')
    assert len(b) == 336 and len(c) == 20
    assert b.measured_R_squared.eq(False).all() and b.real_matching_changed.eq(False).all()
    assert c.empirical_R1A_decomposition.eq(False).all()
    assert np.allclose(b.required_variance_ratio, b.budget_trading_days/b.prior_required_days_CONDITIONAL)
    assert np.allclose(b.required_variance_reduction, np.maximum(0, 1-b.required_variance_ratio))
    assert np.allclose(b.required_information_multiplier, 1/b.required_variance_ratio)
    pure = c.loc[(c.K_controls == 'infinity') & (c.control_error_correlation_ASSUMED == 0)]
    assert pure.variance_ratio_balanced_model.item() == .5
    primary = b.loc[(b.layer == 'INDEX_ALL_FROZEN_PAIRS') & (b.index_symbol == '000852.SH') &
                    (b.family_size == 14) & (b.budget_trading_days == 243) & (b.effect_bp_ASSUMED == 4)]
    assert primary.loc[primary.horizon == 15, 'required_variance_reduction'].item() > .94
    assert primary.loc[primary.horizon == 30, 'required_variance_reduction'].item() > .98


def test_no_confirmation_or_historical_significance_retest():
    r = receipt()
    assert r['BLACKBOX_query_count'] == 3
    for key in ('real_R1A_means_retested', 'new_price_data_read', 'horizon_selected', 'real_matching_changed',
                'missing_outcomes_imputed', 'production_authority', 'fresh_oos',
                'confirmation_protocol_frozen', 'confirmation_clock_started'):
        assert r[key] is False
