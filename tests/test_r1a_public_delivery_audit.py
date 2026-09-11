import copy
import numpy as np
import pandas as pd
import pytest
from research.r1a_carrier_transport.audit_public_delivery import (
    AuditError, HORIZONS, compare_json, verify_ledger,
)


def fixture():
    pairs = pd.DataFrame([{'pair_id':'p1','symbol':'000688.SH','event_day':'2023-01-04','control_day':'2023-02-01','side':'LONG','parent_direction':1}])
    coverage = pd.DataFrame([{'pair_id':'p1','eligible':True}])
    rows=[]
    for h in HORIZONS:
        e=h/10000; c=e/2; ie=e*0.8; ic=c*0.8
        rows.append({'pair_id':'p1','index_symbol':'000688.SH','event_day':'2023-01-04','control_day':'2023-02-01','side':'LONG','horizon':h,'etf_event':e,'etf_control':c,'etf_incremental':e-c,'index_event_same_sample':ie,'index_control_same_sample':ic,'index_incremental_same_sample':ie-ic,'event_tracking_residual':e-ie,'incremental_tracking_residual':(e-c)-(ie-ic),'etf_close_MFE':e,'etf_close_MAE':0.0})
    return pd.DataFrame(rows), coverage, pairs


def test_valid_seven_horizon_surface():
    ledger, coverage, pairs=fixture()
    result=verify_ledger(ledger,coverage,pairs)
    assert result['complete_pairs']==1 and result['ledger_rows']==7


@pytest.mark.parametrize('mutation', ['duplicate','missing_horizon','different_pair','wrong_side','algebra','nonfinite','extrema','coverage'])
def test_corrupted_evidence_rejected(mutation):
    ledger, coverage, pairs=fixture()
    if mutation=='duplicate': ledger=pd.concat([ledger,ledger.iloc[:1]],ignore_index=True)
    elif mutation=='missing_horizon': ledger=ledger.iloc[:-1].copy()
    elif mutation=='different_pair': ledger.loc[0,'pair_id']='other'
    elif mutation=='wrong_side': ledger.loc[0,'side']='SHORT'
    elif mutation=='algebra': ledger.loc[0,'etf_incremental']+=0.001
    elif mutation=='nonfinite': ledger.loc[0,'etf_event']=np.inf
    elif mutation=='extrema': ledger.loc[0,'etf_close_MAE']=0.1
    elif mutation=='coverage': coverage.loc[0,'eligible']=False
    with pytest.raises(AuditError): verify_ledger(ledger,coverage,pairs)


def test_json_roundoff_only():
    expected={'x':[1.5,2.5], 'flag':False, 'none':None}
    actual=copy.deepcopy(expected); actual['x'][0]+=1e-10
    assert compare_json(actual,expected)==4
    actual['x'][0]+=0.01
    with pytest.raises(AuditError): compare_json(actual,expected)


def test_json_boolean_not_integer_and_schema_not_subset():
    with pytest.raises(AuditError): compare_json({'ok':0},{'ok':False})
    with pytest.raises(AuditError): compare_json({'x':1,'extra':2},{'x':1})


def test_nested_extrema_must_be_monotonic():
    ledger,coverage,pairs=fixture()
    ledger.loc[0,'etf_close_MFE']=1.0
    with pytest.raises(AuditError,match='nested extrema'):
        verify_ledger(ledger,coverage,pairs)
