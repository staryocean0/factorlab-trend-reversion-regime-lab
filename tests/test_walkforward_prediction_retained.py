import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.r1a_walkforward_prediction.core import HORIZONS, score, daily_accounting
from research.r1a_walkforward_prediction.verify_replay import compare_json

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/ops/evidence/r1a_walkforward_prediction_20260912'


def receipt():
    data=(EVIDENCE/'receipt.json').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert blob=='0bdf7738cd2a7e73bb20b85b8613dd2954ae488b'
    return json.loads(data)


def test_sealed_receipt_and_real_csv_bytes():
    r=receipt()
    for f in r['files']:
        p=EVIDENCE/f['path']
        assert p.stat().st_size==f['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
        assert len(pd.read_csv(p))==r['table_rows'][f['path']]
    assert r['original_events']==1752 and r['warmup_events']==645
    assert r['successful_fit_count']==70
    assert len(r['sources'])==6 and r['post2020_price_files_read']==[]
    assert not r['fresh_oos'] and not r['production_authority']


def test_all_event_denominators_and_warmup_remain_visible():
    cov=pd.read_csv(EVIDENCE/'all_original_event_coverage.csv')
    pred=pd.read_csv(EVIDENCE/'event_predictions.csv')
    assert len(cov)==1752*7 and len(pred)==1107*7
    for h in HORIZONS:
        a=cov.loc[cov.horizon==h]; b=pred.loc[pred.horizon==h]
        assert set(a.loc[a.status=='SCORED','entry_idx'])==set(b.entry_idx)
        assert (a.loc[a.status=='WARMUP_2015_NOT_SCORED','info_year']==2015).all()
        assert len(b)==1107 and int(b.outside_training_range.sum())==2
        assert int(b.outside_background_range.sum())==11
        assert (b.fit_cutoff_idx < b.info_idx).all()
        assert (b.exit_idx==b.entry_idx+h).all()
        assert (b.is_event==1).all()


def test_recompute_all_event_score_groups_from_forecast_ledger():
    f=pd.read_csv(EVIDENCE/'event_predictions.csv'); s=pd.read_csv(EVIDENCE/'scores.csv')
    for row in s.loc[s.scope=='EVENT'].to_dict('records'):
        x=f.loc[f.horizon==row['horizon']]
        group=row['group']
        if group.startswith('YEAR_'):
            x=x.loc[x.info_year==int(group.split('_')[1])]
        if group.endswith('LONG'): x=x.loc[x.parent_direction==1]
        elif group.endswith('SHORT'): x=x.loc[x.parent_direction==-1]
        actual=score(x)
        for k,v in actual.items():
            if v is None: assert pd.isna(row[k])
            elif isinstance(v,int): assert v==row[k]
            else: assert np.isclose(v,row[k],rtol=1e-11,atol=1e-8),(group,k)


def test_training_labels_and_price_prefixes_are_earlier():
    a=pd.read_csv(EVIDENCE/'fold_training_audit.csv')
    assert len(a)==35 and (a.status=='SCORED').all()
    assert (a.max_train_label_idx<=a.cutoff_idx).all()
    assert (a.train_event_n+a.train_background_n==a.train_n).all()
    p=pd.read_csv(EVIDENCE/'prefix_identity_audit.csv')
    assert len(p)==5 and p.identities_equal.all() and (p.max_feature_difference==0).all()


def test_daily_loss_ledger_reconciles_without_independence_claim():
    f=pd.read_csv(EVIDENCE/'event_predictions.csv'); old=pd.read_csv(EVIDENCE/'daily_loss_accounting.csv')
    new,_=daily_accounting(f,sorted(set(old.info_day)))
    assert old.n.tolist()==new.n.tolist()
    np.testing.assert_allclose(old.loss_sum_bp2,new.loss_sum_bp2,rtol=1e-10,atol=1e-7)
    assert (old.n==0).any()


def test_descriptive_flag_is_not_confirmation_or_best_horizon():
    r=receipt()
    assert [x['horizon'] for x in r['horizon_review']]==list(HORIZONS)
    sixty=next(x for x in r['horizon_review'] if x['horizon']==60)
    assert sixty['descriptive_consistency_NOT_significance']
    assert not sixty['enhanced_beats_zero_mse']
    assert not r['new_significance_test'] and not r['horizon_selected']
    assert not r['confirmation_protocol_frozen'] and not r['confirmation_clock_started']


def test_replay_comparison_does_not_tolerate_changed_counts_or_flags():
    with pytest.raises(AssertionError): compare_json({'n':1107},{'n':1108})
    with pytest.raises(AssertionError): compare_json({'flag':False},{'flag':True})
    with pytest.raises(AssertionError): compare_json({'p':1.},{'p':1.01})
