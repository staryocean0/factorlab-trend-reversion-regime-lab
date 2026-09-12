"""Synthetic method boundaries; no new real-market alpha calculation."""
import inspect
import math
import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from research.r1a_method_calibration import study as m


def group_dates(n_per_year=20):
    days = [f'{year}-06-03' for year in range(2021, 2026) for _ in range(n_per_year)]
    return pd.DataFrame({col: [d+'T10:00:00+08:00' for d in days] for col in (
        'event_entry_timestamp', 'event_exit_timestamp', 'control_entry_timestamp', 'control_exit_timestamp')})


def synthetic_design():
    n, g = 100, 50
    members = [{i % g, (i+7) % g} for i in range(n)]
    inc = m.binary_incidence(members, g)
    unsigned = sparse.diags(np.full(n, 1/math.sqrt(2))) @ inc
    signed = unsigned.copy().tocsr()
    groups, info = m.group_operator(group_dates())
    op, signs = m.prior.meat_operator(members)
    return {'id': 'synthetic', 'n': n, 'sd': 3., 'historical_se': .5, 'lambda': .3,
            'incidence': inc, 'unsigned': unsigned, 'signed': signed,
            'primitive': sparse.eye(n, format='csr'), 'groups': groups, 'group_info': info,
            'operator': op, 'signs': signs, 'occupied': g, 'kernel': m.bartlett_kernel(g, 6),
            'pair_positions': np.arange(n)}


@pytest.mark.parametrize('g,lags', [(1, 0), (5, 0), (5, 2), (61, 6)])
def test_bartlett_positive_semidefinite_and_diagonal(g, lags):
    k = m.bartlett_kernel(g, lags)
    assert np.allclose(k, k.T) and np.array_equal(np.diag(k), np.ones(g))
    assert np.linalg.eigvalsh(k).min() > -1e-10
    if g > lags+1:
        assert k[0, lags+1] == 0


@pytest.mark.parametrize('g,lags', [(0, 6), (3, -1)])
def test_invalid_kernel_rejected(g, lags):
    with pytest.raises(ValueError): m.bartlett_kernel(g, lags)


def test_incidence_keeps_empty_calendar_blocks():
    h = m.binary_incidence([{0, 2}, {2}], 5).toarray()
    assert h.shape == (2, 5)
    assert np.array_equal(h[:, 1], [0, 0]) and np.array_equal(h[:, 4], [0, 0])


def test_bad_incidence_block_rejected():
    with pytest.raises(ValueError): m.binary_incidence([{0}, {5}], 5)


def test_signed_roles_cancel_on_same_calendar_exposure():
    bounds = np.array([[0, 2, 0, 2], [20, 20, 40, 40]])
    load = m.signed_calendar_loads(bounds, np.array([1, -1]), 3).toarray()
    assert np.array_equal(load[0], [0., 0., 0.])
    assert np.isclose(load[1, 1], -1/math.sqrt(2))
    assert np.isclose(load[1, 2], 1/math.sqrt(2))


def test_signed_paths_include_all_boundary_blocks():
    load = m.signed_calendar_loads(np.array([[19, 20, 40, 40]]), np.array([1]), 3).toarray()
    assert np.allclose(load, [[.5, .5, -1/math.sqrt(2)]])


def test_group_operator_excludes_cross_role_year_leakage():
    a = group_dates(); a.loc[0, 'control_exit_timestamp'] = '2022-01-04T10:00:00+08:00'
    op, info = m.group_operator(a)
    assert info['excluded_cross_year'] == 1 and info['group_counts']['2021'] == 19
    assert np.allclose(op.sum(axis=1), 1) and op[:, 0].nnz == 0


def test_groups_are_equal_period_not_pair_weighted():
    a = group_dates(); a = pd.concat([a, a.iloc[-20:]], ignore_index=True)
    op, info = m.group_operator(a)
    y = np.r_[np.zeros(80), np.ones(40)*10]
    assert np.isclose((op @ y).mean(), 2)
    assert not np.isclose((op @ y).mean(), y.mean())
    assert info['available']


def test_group_small_sample_abstains():
    _, info = m.group_operator(group_dates(9))
    assert info['available'] is False


def test_hac_matches_dense_incidence_quadratic():
    d = synthetic_design(); rng = np.random.default_rng(2)
    y = rng.normal(size=(100, 4)); u = y-y.mean(axis=0)
    h = d['incidence'].toarray(); k = d['kernel']
    quadratic = np.einsum('ij,ij->j', u, (h @ k @ h.T) @ u)/100**2*(100/99)*(50/49)
    iid = (u*u).sum(axis=0)/(100*99)
    assert np.allclose(m.hac_variance(y, d['incidence'], k, 50), np.maximum(quadratic, iid))


def test_translation_changes_means_not_standard_errors():
    d = synthetic_design(); y = np.random.default_rng(3).normal(size=(100, 8))
    a = m.estimates(y, d, .02); b = m.estimates(y+4., d, .02)
    for key in m.METHODS:
        assert np.allclose(b[key][0]-a[key][0], 4.)
        assert np.allclose(a[key][1], b[key][1])
        assert np.array_equal(a[key][2], b[key][2])


def test_sparse_graph_estimator_is_old_estimator():
    d = synthetic_design(); y = np.random.default_rng(4).normal(size=(100, 4))
    members = [{i % 50, (i+7) % 50} for i in range(100)]
    got = m.estimates(y, d, .01)[m.METHODS[0]]
    for j in range(4):
        old = m.rb.graph_inference(y[:, j], members)
        if old['used_se_bp'] is None:
            assert not got[2][j]
        else:
            assert np.isclose(got[1][j], old['used_se_bp'])


def test_oracle_covariance_matches_dense_model():
    d = synthetic_design(); g = d['unsigned'].shape[1]
    cov = .6**np.abs(np.arange(g)[:, None]-np.arange(g)[None, :])
    params = m.dgp_parameters(d, 'BLOCK_GAUSSIAN_RHO06', cov)
    b = d['unsigned'].toarray(); lam = params['lambda']; scale = params['scale']
    sigma = scale**2*((1-lam)*np.eye(100)+lam*b @ cov @ b.T)
    assert np.isclose(params['oracle_var'], sigma.sum()/100**2)
    assert np.isclose(np.trace(sigma)/100, d['sd']**2)


def test_iid_oracle_and_target_marginal_variance():
    d = synthetic_design(); p = m.dgp_parameters(d, 'IID_GAUSSIAN', np.eye(50))
    assert p['lambda'] == 0 and np.isclose(p['oracle_var'], 9/100)
    assert np.isclose(p['average_marginal_variance'], 9)


def test_same_pair_shocks_are_shared_across_designs():
    d = synthetic_design(); p = m.dgp_parameters(d, 'IID_GAUSSIAN', np.eye(50))
    eps = np.random.default_rng(1).normal(size=(100, 3)); z = np.ones((50, 3))
    y = m.make_y(d, 'IID_GAUSSIAN', p, eps, None, z)
    assert np.array_equal(y, 3*eps)
    assert np.array_equal(y, m.make_y(d, 'IID_GAUSSIAN', p, eps, None, z))


def test_shared_clock_errors_respect_exact_control_reuse():
    d = synthetic_design(); d['primitive'] = sparse.csr_matrix(np.tile(np.r_[1., -1., np.zeros(98)], (100, 1)))
    p = m.dgp_parameters(d, 'SIGNED_LEG_REUSE_RHO06', np.eye(50))
    assert p['oracle_var'] > 0
    with pytest.raises(ValueError): m.make_y(d, 'SIGNED_LEG_REUSE_RHO06', p, np.zeros((100, 3)), None, np.zeros((50, 3)))


@pytest.mark.parametrize('rho,heavy', [(0., False), (.6, False), (.9, True)])
def test_AR_reproducible_and_finite(rho, heavy):
    a = m.random_blocks(np.random.default_rng(5), 8, 6, rho, heavy)
    b = m.random_blocks(np.random.default_rng(5), 8, 6, rho, heavy)
    assert a.shape == (8, 6) and np.isfinite(a).all() and np.array_equal(a, b)


def test_effect_detection_monotone_on_identical_draws():
    d = synthetic_design(); y = np.random.default_rng(7).normal(size=(100, 100))
    for mean, se, valid, df in m.estimates(y, d, .01).values():
        counts = [int((valid & (mean+delta > m.critical(df, 14)*se)).sum()) for delta in (0, 2, 4, 6)]
        assert counts == sorted(counts)


def test_larger_family_has_larger_critical_value():
    for df in (None, 4, 60):
        assert m.critical(df, 1) < m.critical(df, 14) < m.critical(df, 28)


def test_control_noise_limit_is_explicit_not_zero():
    assert m.control_variance_ratio(1, 0) == 1
    assert m.control_variance_ratio(math.inf, 0) == .5
    assert m.control_variance_ratio(5, 0) == .6
    assert m.control_variance_ratio(math.inf, .5) == .75


@pytest.mark.parametrize('k,rho', [(0, 0), (2, -1), (2, 1.1)])
def test_invalid_control_scenario_rejected(k, rho):
    with pytest.raises(ValueError): m.control_variance_ratio(k, rho)


def test_no_prices_or_return_ledgers_in_input_reader():
    source = inspect.getsource(m.load_inputs)
    assert "columns=['trading_day']" in source
    assert 'endpoint_returns.csv' not in source
    assert 'load_market_data(' not in source
    assert '.close' not in source
    assert 'urlopen' not in source and 'requests.' not in source


def test_screen_cannot_deploy_oracle_or_hide_invalidity():
    cells = pd.DataFrame([{'method': method, 'severe_size_warning': False, 'valid_fraction': 1.} for method in m.METHODS])
    families = pd.DataFrame([{'method': method, 'MC95_hi': .06, 'severe_size_warning': False,
                             'complete_quantification_fraction': 1.} for method in m.METHODS])
    screen = m.method_screen(cells, families)
    assert screen[m.METHODS[3]]['limited_simulation_screen_pass'] is False
    cells.loc[cells.method == m.METHODS[0], 'valid_fraction'] = .9
    assert m.method_screen(cells, families)[m.METHODS[0]]['limited_simulation_screen_pass'] is False


def test_existing_output_refused_before_data_access(tmp_path):
    with pytest.raises(ValueError, match='fresh output'):
        m.run(tmp_path, tmp_path)
