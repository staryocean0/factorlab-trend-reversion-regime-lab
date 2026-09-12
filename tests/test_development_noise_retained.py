import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.r1a_development_noise import study as s
from research.r1a_development_noise import verify_replay as v

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/ops/evidence/r1a_development_noise_20260912'


def receipt():
    return json.loads((EVIDENCE/'noise_receipt.json').read_text())


def test_sealed_inputs_and_no_new_sample():
    r=receipt(); s.guard(EVIDENCE/'noise_receipt.json',v.REFERENCE_BLOB)
    assert r['freeze_sha256']==s.sha(ROOT/s.FREEZE)
    assert r['freeze_commit']==s.FREEZE_COMMIT
    assert len(r['sources'])==7
    assert all(int(Path(x['path']).stem)<=2020 for x in r['sources'])
    assert r['post2020_price_files_read']==r['ETF_price_files_read']==[]
    assert r['BLACKBOX_query_count']==3
    assert not r['production_authority'] and not r['fresh_oos'] and not r['new_significance_tests']
    for spec in r['files']:
        p=EVIDENCE/spec['path']
        assert s.sha(p)==spec['sha256'] and p.stat().st_size==spec['bytes']


def test_cohort_is_development_not_old_validation():
    r=receipt()
    assert r['cohorts']['000852.SH']['matched_events']==1752
    assert r['cohorts']['000688.SH']['matched_events']==156
    assert r['cohorts']['000852.SH']['unique_controls']==1482
    p=pd.read_csv(EVIDENCE/'development_pairs.csv',dtype={'symbol':str})
    assert len(p)==1908 and not p.pair_id.duplicated().any()
    assert p.event_day.max()<='2020-12-31' and p.control_day.max()<='2020-12-31'
    assert p.pair_id.str.contains(':DEV_R1_A:').all()


def test_every_horizon_has_identical_pairs_and_exact_variance_identity():
    f=pd.read_csv(EVIDENCE/'development_leg_returns_NOT_confirmation.csv',dtype={'symbol':str})
    for symbol,g in f.groupby('symbol'):
        ids=set(g.loc[g.horizon==1,'pair_id'])
        for h in s.HORIZONS:
            x=g.loc[g.horizon==h]
            assert set(x.pair_id)==ids
            assert np.allclose(x.difference_bp,x.event_bp-x.control_bp,rtol=1e-9,atol=1e-7)
    m=pd.read_csv(EVIDENCE/'leg_variance.csv')
    assert np.allclose(m.difference_var_bp2,m.event_var_bp2+m.control_var_bp2-2*m.event_control_cov_bp2,rtol=1e-9,atol=1e-6)


def test_retained_stratum_identity_and_calendar_identity():
    f=pd.read_csv(EVIDENCE/'stratum_covariance.csv')
    for _,g in f.groupby(['symbol','horizon']):
        g=g.set_index('component')
        for c in ['event_var_bp2','control_var_bp2','difference_var_bp2','event_control_cov_bp2']:
            assert np.isclose(g.loc['TOTAL',c],g.loc['WITHIN',c]+g.loc['BETWEEN',c],rtol=1e-9,atol=1e-7)
    d=pd.read_csv(EVIDENCE/'calendar_contributions_NOT_strategy_backtest.csv')
    assert np.allclose(d.difference_contribution_bp,d.event_contribution_bp-d.control_contribution_bp,rtol=1e-9,atol=1e-7)


def test_retained_calendar_day_denominator_includes_zeros():
    d=pd.read_csv(EVIDENCE/'calendar_contributions_NOT_strategy_backtest.csv',dtype={'symbol':str})
    for (symbol,h,view),g in d.groupby(['symbol','horizon','view']):
        assert len(g)==(1462 if symbol=='000852.SH' else 110)
        assert not g.day.duplicated().any()
    assert len(d)==22008


def test_comparator_accepts_only_small_float_difference():
    v.compare({'n':1752,'variance':100.},{'n':1752,'variance':100.+1e-10})
    with pytest.raises(ValueError): v.compare({'n':1752},{'n':1753})
    with pytest.raises(ValueError): v.compare({'variance':100.},{'variance':100.01})
    with pytest.raises(ValueError): v.compare({'authority':False},{'authority':True})
    with pytest.raises(ValueError): v.compare({'variance':float('nan')},{'variance':float('nan')})


def test_table_comparator_rejects_row_and_missing_mask_changes(tmp_path):
    a=tmp_path/'a.csv'; b=tmp_path/'b.csv'
    pd.DataFrame({'pair_id':['p1','p2'],'n':[1,2],'variance':[1.,2.]}).to_csv(a,index=False)
    pd.DataFrame({'pair_id':['p2','p1'],'n':[1,2],'variance':[1.,2.]}).to_csv(b,index=False)
    with pytest.raises(ValueError): v.table(a,b)
    pd.DataFrame({'pair_id':['p1','p2'],'n':[1,2],'variance':[1.,np.nan]}).to_csv(b,index=False)
    with pytest.raises(ValueError): v.table(a,b)
