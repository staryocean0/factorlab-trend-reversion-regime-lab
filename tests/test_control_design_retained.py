from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from research.r1a_control_design.core import STAGES, FEATURES, SPAN, overlap_pairs
from research.r1a_control_design.study import sha
from research.r1a_control_design.verify_replay import compare_table, packing_implication

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'docs/ops/evidence/r1a_control_design_20260912'


def test_reference_files_match_decisive_receipt():
    r=json.loads((REF/'design_receipt.json').read_text())
    assert r['new_allocation_outcomes_read'] is False
    assert r['production_authority'] is False
    for spec in r['files']:
        assert sha(REF/spec['path'])==spec['sha256']


def test_complete_denominators_and_exact_nested_stage_losses():
    f=pd.read_csv(REF/'allocation_ledger.csv')
    expected={'000852.SH':[1645,414,241],'000688.SH':[122,27,17]}
    for symbol,counts in expected.items():
        groups=[f.loc[(f.symbol==symbol)&(f.stage==s)] for s in STAGES]
        assert len(set(len(g) for g in groups))==1
        assert [int(g.matched.sum()) for g in groups]==counts
        assert groups[0].event_entry_idx.tolist()==groups[1].event_entry_idx.tolist()==groups[2].event_entry_idx.tolist()
        g=groups[2];m=g.loc[g.matched]
        assert (m.control_entry_idx+SPAN<=m.information_cutoff_idx).all()
        assert overlap_pairs(m.control_entry_idx.to_numpy(int),SPAN)==0
        assert (m.maximum_scaled_gap<=.5).all()


def test_matching_balance_is_not_confused_with_event_population_retention():
    f=pd.read_csv(REF/'covariate_balance.csv')
    x=f.loc[(f.symbol=='000852.SH')&(f.stage==STAGES[2])&(f.group=='POOLED')]
    assert len(x)==4
    assert (x.matched_SMD.abs()<.02).all()
    assert (x.retention_shift_SMD.abs()>.30).all()
    assert not x.balance_pass.any()


def test_new_control_unit_exposure_is_disjoint_all_horizons():
    f=pd.read_csv(REF/'unit_incidence_geometry_NOT_realized_variance.csv')
    x=f.loc[(f.stage==STAGES[2])&(f.cohort=='NEW_ASSIGNMENT_SAME_EVENTS')]
    assert len(x)==14
    assert (x.maximum_exact_reuse==1).all()
    assert (x.control_inclusive_overlap_pairs==0).all()
    assert np.allclose(x.control_unit_energy_ratio_NOT_variance_effect,1)


def test_same_year_capacity_bound_is_an_implication_not_return_result():
    r=json.loads((REF/'design_receipt.json').read_text())
    p=packing_implication(r,pd.read_csv(REF/'coverage_by_group.csv'))
    c=next(x for x in p['symbols'] if x['symbol']=='000852.SH')
    assert c['optimistic_total_capacity_bound']==1230
    assert c['total_events']==1752
    assert c['coverage_upper_bound']<.80
    assert c['years'][0]['optimistic_capacity_bound']==242


def test_one_changed_assignment_fails_even_if_all_summary_numbers_same(tmp_path):
    a=tmp_path/'a.csv';b=tmp_path/'b.csv'
    a.write_text('event_entry_idx,control_entry_idx,distance\n1000,10,0.1\n')
    b.write_text('event_entry_idx,control_entry_idx,distance\n1000,11,0.1\n')
    with pytest.raises(ValueError,match='exact allocation'):
        compare_table(a,b)


def test_float_tolerance_does_not_admit_real_design_changes(tmp_path):
    a=tmp_path/'a.csv';b=tmp_path/'b.csv'
    a.write_text('event_entry_idx,distance\n1000,0.1\n')
    b.write_text('event_entry_idx,distance\n1000,0.100000000001\n')
    compare_table(a,b)
    b.write_text('event_entry_idx,distance\n1000,0.11\n')
    with pytest.raises(ValueError,match='tolerance'):
        compare_table(a,b)
