"""Regression of the completed diagnostic, not another research selection."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.r1a_carrier_transport.endpoint_diagnostic import HORIZONS, coverage_gate, summarize, sha
from research.r1a_carrier_transport.audit_public_delivery import compare_json

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/ops/evidence/r1a_endpoint_diagnostic_20260912'


def receipt():
    return json.loads((EVIDENCE/'endpoint_receipt.json').read_text())


def test_frozen_diagnostic_scope_and_original_full_path_freeze():
    r=receipt()
    assert r['decision']=='ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE'
    assert r['measured_carrier_horizons']==14
    assert r['old_full_path_status']=='PARTIAL_CARRIER_TRANSPORT_UNCHANGED'
    assert r['BLACKBOX_query_count']==3
    for name in ('production_authority','fresh_oos','horizon_selected','signal_refitted','control_rematched','new_significance_test','formal_causal_inference','path_risk_measured'):
        assert r[name] is False
    assert sha(ROOT/'docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json')=='7c3b08847a873132df36c97b4c8c8e84c251c4b9c56568260ffbbb90ce99142b'
    for spec in r['evidence_files']:
        path=EVIDENCE/spec['path']
        assert path.stat().st_size==spec['bytes']
        assert sha(path)==spec['sha256']


@pytest.mark.parametrize('carrier',['512100.SH','588000.SH'])
def test_retained_samples_returns_and_all_summaries(carrier):
    info=receipt()['carriers'][carrier]
    a=pd.read_csv(EVIDENCE/(carrier+'_endpoint_availability.csv'))
    ledger=pd.read_csv(EVIDENCE/(carrier+'_endpoint_returns.csv'),float_precision='round_trip')
    assert not a.duplicated(['pair_id','horizon']).any()
    assert not ledger.duplicated(['pair_id','horizon']).any()
    assert set(ledger.horizon)==set(HORIZONS)
    assert not any('MFE' in c or 'MAE' in c for c in ledger.columns)
    for h in HORIZONS:
        block=a.loc[a.horizon==h]
        y=ledger.loc[ledger.horizon==h]
        assert set(y.pair_id)==set(block.loc[block.eligible,'pair_id'])
        assert block.groupby('pair_id').size().eq(1).all()
        compare_json(coverage_gate(block),info['horizons'][str(h)]['gate'])
        compare_json(summarize(y),info['horizons'][str(h)]['summary'])
    identities={'etf_incremental':ledger.etf_event-ledger.etf_control,
                'index_incremental':ledger.index_event-ledger.index_control,
                'event_tracking_residual':ledger.etf_event-ledger.index_event,
                'incremental_tracking_residual':ledger.etf_incremental-ledger.index_incremental}
    for name, expected in identities.items():
        assert np.max(np.abs(ledger[name]-expected))<1e-12


def test_insufficient_primary_common_sample_is_not_opened():
    r=receipt()['carriers']
    primary=r['512100.SH']['common_endpoint_sensitivity']
    assert primary['gate']['pass'] is False
    assert primary['gate']['outcomes_measured'] is False
    assert primary['horizons']=={}
    assert not (EVIDENCE/'512100.SH_common_endpoint_returns.csv').exists()
    secondary=r['588000.SH']['common_endpoint_sensitivity']
    assert secondary['gate']['outcomes_measured'] is True
    assert (EVIDENCE/'588000.SH_common_endpoint_returns.csv').is_file()
