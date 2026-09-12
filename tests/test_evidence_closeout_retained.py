import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.r1a_evidence_closeout.audit import HORIZONS, sha
from research.r1a_evidence_closeout.verify_replay import REFERENCE_SHA256

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/ops/evidence/r1a_evidence_closeout_20260912'


def test_retained_checksums_and_no_new_models():
    assert sha(E/'receipt.json')==REFERENCE_SHA256
    r=json.loads((E/'receipt.json').read_text())
    assert r['new_model_fits']==r['new_signal_generation']==r['new_strategy_returns']==0
    assert r['raw_market_files_read']==[] and not r['new_significance_tests']
    assert not r['production_authority'] and r['BLACKBOX_query_count']==3
    for spec in r['files']:assert sha(E/spec['path'])==spec['sha256']


@pytest.mark.parametrize('h',HORIZONS)
def test_every_horizon_reconciles_all_years_and_sides(h):
    f=pd.read_csv(E/'error_decomposition.csv');f=f[f.horizon==h]
    assert len(f)==18
    assert f[f.group=='POOLED'].n.item()==1107
    year=f[f.group.str.fullmatch('YEAR_[0-9]{4}')]
    assert year.n.sum()==1107 and len(year)==5
    p=pd.read_csv(E/'year_partition.csv');p=p[p.horizon==h].iloc[0]
    assert np.isclose(p.total_gain_bp2,(year.n*year.mean_loss_improvement_bp2).sum()/1107)
    assert np.isclose(p.total_gain_bp2,p.weighted_within_year_bias_square_reduction_bp2+p.weighted_within_year_centered_error_variance_reduction_bp2)
    # This protects the observed sign, not a new statistical significance assertion.
    assert p.weighted_within_year_centered_error_variance_reduction_bp2<0


def test_cross_study_targets_are_not_silently_pooled():
    f=pd.read_csv(E/'cross_study_evidence.csv')
    assert len(f)==10 and f.study.is_unique
    assert f.directly_comparable_to_forward_loss.sum()==1
    assert f.loc[f.directly_comparable_to_forward_loss,'study'].item()=='WALKFORWARD_PREDICTION'


def test_original_evidence_fields_and_parameter_sign_change_retained():
    f=pd.read_csv(E/'published_score_reconciliation.csv')
    assert len(f)==2268 and f.absolute_error.max()<1e-7
    p=pd.read_csv(E/'parameter_adjustment_accounting.csv')
    for h in [15,30]:
        g=p[p.horizon==h].sort_values('year')
        assert (g[g.year<2020].mean_total_prediction_adjustment_bp<0).all()
        assert g[g.year==2020].mean_total_prediction_adjustment_bp.item()>0
