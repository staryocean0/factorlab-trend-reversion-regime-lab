"""Protect immutable local-delivery results using public data only."""
import json
from pathlib import Path
from research.r1a_carrier_transport.audit_public_delivery import (
    BASE, LOCAL, PAIRS, FREEZE, sha, read_csv, compare_json, verify_ledger,
)
from research.r1a_carrier_transport.transport import summarize

ROOT=Path(__file__).resolve().parents[1]


def test_delivered_public_hashes_and_scope():
    receipt=json.loads((ROOT/LOCAL/'transport_receipt.json').read_text())
    assert receipt['decision']=='PARTIAL_CARRIER_TRANSPORT'
    assert receipt['carriers']['512100.SH']['ETF_outcomes_read'] is False
    assert receipt['BLACKBOX_query_count']==3
    assert receipt['production_authority'] is False
    assert sha(ROOT/FREEZE)==receipt['freeze_sha256']
    assert sha(ROOT/PAIRS)==receipt['matched_pairs_sha256']
    for spec in receipt['evidence_files']:
        path=ROOT/LOCAL/spec['path']
        if spec['path']=='frozen_index_clock_anchors.csv':
            path=ROOT/BASE/spec['path']
        assert path.stat().st_size==spec['bytes']
        assert sha(path)==spec['sha256']


def test_delivered_pairs_algebra_and_all_summary_fields():
    receipt=json.loads((ROOT/LOCAL/'transport_receipt.json').read_text())
    pairs=read_csv(ROOT/PAIRS)
    pairs=pairs.loc[(pairs.cell=='R1_A') & (pairs.symbol=='000688.SH')].copy()
    pairs['pair_id']=pairs.symbol.astype(str)+':R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
    ledger=read_csv(ROOT/LOCAL/'588000.SH_transport.csv')
    coverage=read_csv(ROOT/LOCAL/'588000.SH_coverage.csv')
    checks=verify_ledger(ledger,coverage,pairs)
    assert checks['frozen_pairs']==1802 and checks['complete_pairs']==1791
    assert checks['ledger_rows']==12537
    assert compare_json(summarize(ledger),receipt['carriers']['588000.SH']['summary'])==2128
