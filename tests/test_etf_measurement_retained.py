import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/ops/evidence'


def test_all_reference_hashes_and_domains():
    for folder in ('etf_index_measurability_20260912','etf_index_measurability_source_20260912'):
        r=json.loads((BASE/folder/'receipt.json').read_text())
        for s in r['files']:
            p=BASE/folder/s['path']; assert p.stat().st_size==s['bytes']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
        assert r['BLACKBOX_query_count']==3 and not r['production_authority']


def test_all_periods_and_accounting_retained():
    f=pd.read_csv(BASE/'etf_index_measurability_20260912/measurement_summary.csv')
    assert len(f)==132 and f.groupby('carrier').size().eq(66).all()
    assert not f[['carrier','period']].duplicated().any()
    rows=['missing_records','invalid_ohlcv_records','zero_volume_records','positive_volume_records']
    assert np.array_equal(f[rows].sum(axis=1),f.index_records)
    cols=['session_or_clock_boundary_comparisons','invalid_index_endpoint_comparisons','declared_action_day_comparisons','etf_endpoint_unavailable_comparisons','eligible_comparisons']
    assert np.array_equal(f[cols].sum(axis=1),f.index_records)
    assert (f.gap_at_most_one_reference_tick_fraction.between(0,1)).all()


def test_missing_day_is_suspension_not_automatic_imputation():
    f=pd.read_csv(BASE/'etf_index_measurability_source_20260912/daily_clock_anomalies.csv')
    x=f[f.kind=='MISSING_ETF_LABEL']
    assert len(x)==1 and x.day.item()=='2022-09-02' and x.rows.item()==240
    assert x.carrier.item()=='512100.SH'


def test_verified_action_omission_is_advisory_not_silent_rewrite():
    a=json.loads((ROOT/'docs/governance/ETF_SOURCE_QUALITY_ADVISORY_20260912.json').read_text())
    c=a['corporate_action_omission']
    assert c['consolidation_and_suspension_date']=='2022-09-02'
    assert c['new_shares_per_old_share']==0.36555
    p=ROOT/c['old_actions_file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==c['old_file_sha256']
    assert '2022-09-02' not in set(pd.read_csv(p).ex_date)
    assert not a['reversion_outcomes_opened']


def test_fill_counts_and_no_claim_of_independence():
    f=pd.read_csv(BASE/'etf_index_measurability_source_20260912/index_source_flags.csv')
    x=f[(f.field=='causal_flat_fill')&(f.value=='True')].groupby('symbol').rows.sum()
    assert x.to_dict()=={'000688.SH':1220,'000852.SH':1215}
    r=json.loads((BASE/'etf_index_measurability_20260912/receipt.json').read_text())
    assert not r['all_observed_gaps_artifacts_proven']
    assert not r['minimum_tick_is_spread_or_noise_bound']
    assert not r['reversion_outcomes_read'] and not r['R1A_events_read']


def test_governance_and_original_R1A_scope_preserved():
    r=json.loads((ROOT/'docs/governance/R1A_PRICE_RESEARCH_DISPOSITION_20260912.json').read_text())
    assert r['status']=='R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED'
    assert r['active_empirical_candidate'] is None
