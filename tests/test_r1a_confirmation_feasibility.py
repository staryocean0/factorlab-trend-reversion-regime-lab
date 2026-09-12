import math
import numpy as np
import pytest
from scipy.stats import norm
from research.r1a_confirmation_feasibility.study import (
    sample_plan, budget_plan, meat_operator, simulate_standard_errors,
    wilson, incidence, calibration, MODELS,
)
from research.r1a_confirmation_feasibility.audit_data_roles import metadata_path, select_metadata, get_json
from research.r1a_endpoint_robustness.study import shared_adjacency, graph_inference


def test_power_formula_matches_fixed_known_normal_example():
    p=sample_plan(1.,10.,100,100,2.,.8,1)
    expected=math.ceil(100/4*(norm.ppf(.975)+norm.ppf(.8))**2)
    assert p['required_trading_days_CONDITIONAL']==expected
    assert p['expected_eligible_pairs_CONDITIONAL']==expected
    assert p['not_confirmatory_sample_size'] is True


def test_halving_effect_quadruples_information_requirement():
    p=sample_plan(2.,30.,200,243,4.,.8,14)
    q=sample_plan(2.,30.,200,243,2.,.8,14)
    assert abs(q['required_trading_days_CONDITIONAL']-4*p['required_trading_days_CONDITIONAL'])<=3


def test_more_stringent_family_and_power_increase_sample():
    base=sample_plan(2.,30.,200,243,4.,.8,1)['required_trading_days_CONDITIONAL']
    family=sample_plan(2.,30.,200,243,4.,.8,14)['required_trading_days_CONDITIONAL']
    higher=sample_plan(2.,30.,200,243,4.,.9,14)['required_trading_days_CONDITIONAL']
    assert base<family<higher


def test_required_budget_reaches_declared_positive_detection_probability():
    p=sample_plan(2.,30.,200,243,4.,.8,14)
    b=budget_plan(2.,200,243,p['required_trading_days_CONDITIONAL'],4.,14)
    assert b['positive_detection_probability_CONDITIONAL']>=.8
    assert b['detectable_effect_80_bp_CONDITIONAL']<=4.


def test_longer_budget_improves_power_without_changing_effect():
    a=budget_plan(2.,200,243,60,4.,14)
    b=budget_plan(2.,200,243,243,4.,14)
    assert a['positive_detection_probability_CONDITIONAL']<b['positive_detection_probability_CONDITIONAL']
    assert a['detectable_effect_80_bp_CONDITIONAL']>b['detectable_effect_80_bp_CONDITIONAL']


@pytest.mark.parametrize('se,delta,power,family',[(0,4,.8,14),(2,0,.8,14),(2,4,.4,14),(2,4,.8,0)])
def test_invalid_plans_rejected(se,delta,power,family):
    with pytest.raises(ValueError): sample_plan(se,30,200,243,delta,power,family)


def test_union_of_cliques_operator_counts_shared_multiple_blocks_once():
    members=[{0,1,2},{0,1,2},{1,3},{4},{2,4}]
    h,s=meat_operator(members)
    reconstructed=(h.T@h.multiply(s[:,None])).toarray()
    adjacency,_=shared_adjacency(members)
    np.testing.assert_array_equal(reconstructed,adjacency.astype(float))


def test_operator_handles_role_reversal_membership_identically():
    h,s=meat_operator([{0,2},{2,0},{1,3}])
    v=(h.T@h.multiply(s[:,None])).toarray()
    assert v[0,1]==1 and v[0,2]==0


def test_batched_simulation_estimator_matches_previous_frozen_graph_code():
    members=[{i%40,(i+1)%40} for i in range(80)]
    y=np.random.default_rng(81).normal(size=(80,8))
    h,s=meat_operator(members)
    se,valid=simulate_standard_errors(y,h,s,40)
    for i in range(8):
        old=graph_inference(y[:,i],members)
        assert bool(valid[i])==(old['used_se_bp'] is not None)
        if valid[i]: assert abs(se[i]-old['used_se_bp'])<1e-12


def test_global_common_shock_with_one_occupied_block_not_certified():
    members=[{0} for _ in range(40)]
    h,s=meat_operator(members)
    _,valid=simulate_standard_errors(np.ones((40,5)),h,s,1)
    assert not valid.any()


def test_incidence_row_has_unit_squared_norm():
    b=incidence([{0},{0,2},{1,3,5}])
    np.testing.assert_allclose(np.asarray(b.multiply(b).sum(axis=1)).ravel(),1.)
    assert b.shape[1]==6  # gaps in the full ordered block clock are preserved


def test_simulation_reproducible_and_all_scenarios_reported():
    members=[{i%40,(i+1)%40} for i in range(80)]
    a=calibration(members,10.,2.,123,repetitions=100)
    b=calibration(members,10.,2.,123,repetitions=100)
    assert a==b and tuple(x['DGP_ASSUMED'] for x in a)==MODELS
    assert all(x['repetitions']==100 and not x['real_market_calibration_proved'] for x in a)
    assert all(0<=x['pointwise_rejections']<=100 for x in a)
    assert a[-1]['oracle_mean_SE_under_DGP_bp']>a[1]['oracle_mean_SE_under_DGP_bp']


@pytest.mark.parametrize('k,n',[(0,100),(5,100),(100,100)])
def test_wilson_interval_contains_empirical_fraction(k,n):
    lo,hi=wilson(k,n)
    assert 0<=lo<=k/n<=hi<=1


@pytest.mark.parametrize('path',["data/2026/512100.csv","data/2026/000852.parquet","docs/ops/evidence/2026/returns.json","data/2026/outcome_manifest.json"])
def test_candidate_outcome_and_price_files_not_read_as_metadata(path):
    assert not metadata_path(path,100)


def test_metadata_paths_are_bounded_and_allowlisted():
    assert metadata_path('data/manifest.json',100)
    assert metadata_path('docs/governance/DATA_ROLE_2026.json',100)
    assert not metadata_path('data/manifest.json',500001)
    assert not metadata_path('private/manifest.json',100)


def test_outcome_subtrees_are_removed_from_role_inventory():
    obj={'schema':'metadata','symbol':'000852.SH','year':2026,'role':'UNKNOWN',
         'summary':{'return':123,'symbol':'SHOULD_NOT_SURVIVE'},'pnl':999,
         'files':[{'path':'data/2026.csv','first_day':'2026-01-01','last_day':'2026-06-30','close':42}]}
    safe=select_metadata(obj)
    assert safe[0]['role']=='UNKNOWN'
    assert 'SHOULD_NOT_SURVIVE' not in str(safe) and '999' not in str(safe) and '42' not in str(safe)
    assert any(x.get('path')=='data/2026.csv' for x in safe)


def test_metadata_api_refuses_nonrepository_or_secret_endpoints():
    with pytest.raises(ValueError): get_json('https://api.github.com/user')
    with pytest.raises(ValueError): get_json('https://example.com/private.csv')
