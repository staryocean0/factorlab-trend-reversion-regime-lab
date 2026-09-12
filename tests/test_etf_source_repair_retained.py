import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/ops/evidence/etf_source_repair_20260912'


def test_decisive_scope_and_counts_retained():
    r=json.loads((EV/'receipt.json').read_text())
    assert r['original_frozen_pairs']==3098
    assert r['endpoint_pair_horizon_rows']==21686
    assert r['existing_published_return_rows_checked']==46594
    assert r['endpoint_membership_changes']==0
    assert r['new_model_fits']==0 and not r['new_return_population_opened']
    assert not r['full_source_qualification_complete'] and r['R1A_reserve_unchanged']


def test_effective_action_csv_excludes_cancelled_proposal():
    f=pd.read_csv(ROOT/'data/etf_source_actions_v2/512100.SH_actions.csv')
    assert f.ex_date.tolist()==['2022-09-02','2025-01-15']
    assert f.event_type.tolist()==['share_consolidation','cash_distribution']
    assert len(pd.read_csv(ROOT/'data/etf_source_actions_v2/588000.SH_actions.csv'))==0


def test_new_action_tables_match_decisive_known_action_files():
    for carrier in ('512100.SH','588000.SH'):
        assert (ROOT/f'data/etf_source_actions_v2/{carrier}_actions.csv').read_bytes()==(EV/f'{carrier}_known_actions_v2.csv').read_bytes()


def test_membership_and_reason_changes_are_not_conflated():
    x=pd.read_csv(EV/'endpoint_impact_summary.csv')
    assert not x.membership_changed.any()
    assert x.reason_changed.sum()==3
    assert x.crossing_previously_included.sum()==0


def test_all_original_horizons_and_carriers_retained():
    x=pd.read_csv(EV/'published_result_impact.csv')
    assert set(x.carrier)=={'512100.SH','588000.SH'}
    assert set(x.horizon)=={1,5,15,30,60,120,240}
    assert len(x)==112 and (x.old_n==x.new_n).all()
    assert (x.filter(like='_mean_change_bp')==0).all().all()


def test_source_contract_remains_explicitly_partial():
    m=json.loads((ROOT/'data/etf_source_actions_v2/manifest.json').read_text())
    assert not m['full_source_qualification_complete']
    assert not m['microstructure_research_admitted']
    assert m['raw_prices_modified'] is False
    for s in m['known_action_files']:
        p=ROOT/s['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
        assert p.stat().st_size==s['bytes']
