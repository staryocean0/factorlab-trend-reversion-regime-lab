"""Synthetic tests for acceptance auditing, not new signal outcomes."""
import numpy as np
import pandas as pd
import pytest

from research.r1a_carrier_transport.audit_public_delivery import AuditError
from research.r1a_carrier_transport.verify_cloud_replay import coverage_counts, compare_frames, verify


def test_recorded_zero_is_distinct_from_missing_and_invalid():
    t=pd.date_range('2021-01-04 09:31',periods=4,freq='min',tz='Asia/Shanghai')
    tape=pd.DataFrame({'open':[10.,10.,10.], 'high':[10.,10.,10.], 'low':[10.,10.,10.], 'close':[10.,10.,np.nan], 'volume':[100.,0.,50.]},index=t[:3])
    x=coverage_counts(t,tape)
    assert x['expected_minutes']==4 and x['present_minutes']==3
    assert x['recorded_zero_volume_minutes']==1 and x['positive_volume_minutes']==1
    assert x['invalid_present_minutes']==1 and x['missing_minutes']==1
    assert x['record_coverage']==.75 and x['positive_volume_coverage']==.25
    assert 'exchange_no_trade' not in x


def test_comparison_matches_keys_not_row_positions():
    a=pd.DataFrame({'pair_id':['b','a'],'horizon':[5,1],'value':[.02,.01],'side':['SHORT','LONG']})
    x=compare_frames(a,a.iloc[::-1],['pair_id','horizon'])
    assert x['rows']==2 and x['maximum_absolute_errors']['value']==0


def test_replay_rejects_numeric_difference():
    a=pd.DataFrame({'pair_id':['a'],'value':[.001]})
    b=a.copy(); b.loc[0,'value']+=1e-7
    with pytest.raises(AuditError,match='numeric replay mismatch'):
        compare_frames(a,b,['pair_id'])


def test_replay_rejects_changed_identity():
    a=pd.DataFrame({'pair_id':['a'],'value':[.001],'side':['LONG']})
    b=a.copy(); b.loc[0,'side']='SHORT'
    with pytest.raises(AuditError,match='identity/category'):
        compare_frames(a,b,['pair_id'])


def test_replay_rejects_duplicate_keys():
    a=pd.DataFrame({'pair_id':['a','a'],'value':[.001,.001]})
    with pytest.raises(AuditError,match='duplicate comparison keys'):
        compare_frames(a,a,['pair_id'])


def test_replay_rejects_nonfinite():
    a=pd.DataFrame({'pair_id':['a'],'value':[np.nan]})
    with pytest.raises(AuditError,match='nonfinite'):
        compare_frames(a,a,['pair_id'])


def test_acceptance_must_not_use_private_directory(tmp_path):
    (tmp_path/'data/r1a_carrier_prices/private').mkdir(parents=True)
    with pytest.raises(AuditError,match='WITHOUT private'):
        verify(tmp_path,tmp_path/'new_audit')


def test_preserves_existing_receipts(tmp_path):
    output=tmp_path/'old_audit'; output.mkdir()
    (output/'evidence').write_text('retain')
    with pytest.raises(AuditError,match='do not overwrite'):
        verify(tmp_path,output)
    assert (output/'evidence').read_text()=='retain'
