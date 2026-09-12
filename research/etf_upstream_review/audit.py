"""Read-only qualification of delivered source excerpts and fixed samples.

No price-pack reload, return experiment, provider access or new time correction.
The upstream repositories and missing vendor archives are not authenticated here.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
import re
import runpy
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PACK = 'data/etf_upstream_evidence_v1'
DELIVERY = '7bc9f893cf045e07479f251a8aa3a7c7e012d52a'
MANIFEST_SHA = 'f6cd653ecd01a6483bff1ef5a1e776eed64986b6785d8bb9371453577f95ca57'
DATASET = 'bars_cn_a_1m_raw_canonical_4ceca170a851'
FROZEN_SHA = '5ea3c8cbd95a9ffdba907fbbc4f5b765a68fb5b80117c0ccc0504f27f1a0f163'
OVERLAY_SHA = '164ad91cdb4b787475374e56c278008f31fb677d7e092a194308c9cfe2ed3b26'


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def checked_file(root: Path, spec: dict) -> Path:
    path = root / spec['path']
    require(not path.is_symlink(), 'symlink delivery')
    require(path.resolve().is_relative_to((root/PACK).resolve()), 'path escapes pack')
    require(path.is_file(), 'missing delivery: '+spec['path'])
    require(path.stat().st_size == spec['bytes'] and digest(path) == spec['sha256'], 'delivery hash/bytes changed: '+spec['path'])
    return path


def legacy_bar_time(value: str, dataset: str) -> datetime:
    # This exception is ONLY for the delivered fixed legacy contract.
    require(dataset == DATASET, 'unqualified dataset: do not strip Z generically')
    require(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00Z', value) is not None, 'not a legacy minute label')
    return datetime.fromisoformat(value[:-1]).replace(tzinfo=ZoneInfo('Asia/Shanghai'))


def verify_excerpt(full: str, excerpt: str) -> int:
    lines = full.splitlines()
    matches = list(re.finditer(r'^# ---- [^\n]+:(\d+)-(\d+) ----\n', excerpt, re.M))
    require(bool(matches), 'missing excerpt provenance')
    for i, match in enumerate(matches):
        lo, hi = map(int, match.groups())
        end = matches[i+1].start() if i+1 < len(matches) else len(excerpt)
        actual = excerpt[match.end():end].rstrip('\n')
        expected = '\n'.join(lines[lo-1:hi]).rstrip('\n')
        require(0 < lo <= hi <= len(lines) and actual == expected, 'excerpt line range mismatch')
    return len(matches)


def compare_anomalies(pack: Path) -> list[dict]:
    base = pack/'02_raw_anomaly_samples'
    require(digest(base/'frozen_examples.csv') == FROZEN_SHA, 'frozen examples changed')
    frozen = csv_rows(base/'frozen_examples.csv')
    canonical = read_json(base/'lake_4ceca_upstream_rows.json')
    imported = read_json(base/'baidu_fund_1m_history_rows.json')
    flat = csv_rows(base/'lake_4ceca_upstream_rows.csv')
    require(len(frozen) == len(canonical) == len(imported) == len(flat) == 20, 'sample denominator')
    def keyed(rows, key):
        out = {key(r): r for r in rows}
        require(len(out) == len(rows), 'duplicate sample identity')
        return out
    c = keyed(canonical, lambda r: (r['carrier'], r['frozen_example_timestamp']))
    h = keyed(imported, lambda r: (r['symbol'], r['timestamp']))
    f = keyed(flat, lambda r: (r['carrier'], r['timestamp']))
    expected = {(r['carrier'], r['timestamp']) for r in frozen}
    require(len(expected) == 20 and set(c) == expected and set(f) == {(r['carrier'],r['timestamp']) for r in canonical}, 'sample set mismatch')
    output = []
    for original in frozen:
        key = (original['carrier'], original['timestamp']); row = c[key]; flatrow = f[(row['carrier'], row['timestamp'])]
        source = h[(row['symbol'], row['timestamp'])]
        require(source['found'] == 1, 'nonunique history match')
        prior = source['record']
        underlying = {k:v for k,v in row.items() if k not in {'carrier','frozen_example_timestamp'}}
        require(underlying.keys() == prior.keys(), 'upstream field mismatch')
        differences = [k for k in underlying if underlying[k] != prior[k]]
        require(differences == ['dataset_version'], 'history differs beyond container identity')
        stamp = legacy_bar_time(row['timestamp'], row['dataset_version'])
        require(stamp == datetime.fromisoformat(original['timestamp']), 'label decoding mismatch')
        require('2021-01-01' <= row['trading_day'] <= '2025-12-31', 'unexpected market-date sample')
        for col in ('open','high','low','close','volume'):
            require(float(original[col]) == row[col] == float(flatrow[col]), 'sample value changed: '+col)
        require(row['high'] > row['low'] and row['volume'] == row['amount'] == 0, 'expected raw anomaly')
        require(row['available_at'] == row['ingested_at'] == '2026-06-26T15:00:39.908240+00:00', 'sample ingestion mismatch')
        require(row['source_kind'] == 'baidu_netdisk_etf_archive', 'source identity')
        require(datetime.fromisoformat(row['available_at']).utcoffset().total_seconds() == 0, 'ingestion is not bar wall-clock')
        # CSV and JSON are two encodings of the same supplied records, not independent vendors.
        for col in flatrow:
            value = row[col]
            if value is not None and col not in ('open','high','low','close','volume','amount'):
                require(flatrow[col] == str(value), 'CSV/JSON field mismatch: '+col)
        require(float(flatrow['amount']) == 0, 'amount mismatch')
        output.append({'carrier':key[0], 'legacy_label':row['timestamp'], 'decoded_shanghai':stamp.isoformat(),
                       'decoded_utc':stamp.astimezone(timezone.utc).isoformat(), 'history_only_difference':'dataset_version',
                       'recorded_volume':0, 'recorded_amount':0, 'archive_to_csv_ohlcv_match':True,
                       'vendor_original_available':False, 'exchange_no_trade_proven':False})
    return output


def source_function_probe(pack: Path) -> dict:
    # Reviewed, hash-pinned pure contract file; not the full DataHub application.
    module = runpy.run_path(str(pack/'01_timestamp_semantics/session_offset_contract.py'))
    normalize = module['normalize_session_offset_request']
    require(normalize(frequency='1m').uses_official_contract, '1m default')
    blocked = 0
    for args in ({'session_offset_minutes':1}, {'close_anchor':'11:30'}):
        try:
            normalize(frequency='1m', **args)
        except ValueError:
            blocked += 1
    require(blocked == 2, '1m offset/noon anchor unexpectedly accepted')
    # Extract only the two reviewed scalar minute-label functions, no DB calls.
    tree = ast.parse((pack/'03_index_processing/transactions_service_derive_minute.py').read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'_minute_label','_format_minute'}]
    require(len(selected) == 2, 'label function source missing')
    scope = {}; exec(compile(ast.Module(body=selected,type_ignores=[]), '<delivered-label-functions>', 'exec'), scope)
    cases = {'09:25:00':'09:31','09:30:00':'09:31','09:31:00':'09:32','11:30:00':'11:30','12:00:00':None,'13:00:00':'13:01','14:59:30':'15:00','15:00:03':'15:00'}
    for value, expected in cases.items():
        require(scope['_minute_label'](value) == expected, 'label boundary changed')
    # Synthetic values exercise the delivered prior-close rule. Supply a three-slot
    # test calendar; this is not a reconstruction of omitted production settings.
    text = (pack/'03_index_processing/export_v3_causal_flat_fill.py').read_text()
    defs = [n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='densify_one_minute_rows']
    require(len(defs)==1, 'fill function missing')
    env = {'Any':Any,'defaultdict':defaultdict,'deepcopy':deepcopy,
           'EXPECTED_CLOCKS':{'1m_official':('09:31','09:32','09:33')},
           'KNOWN_SHORT_DAYS':set(),'MAX_ELIGIBLE_MISSING_MINUTES':3,
           '_max_consecutive_missing':lambda x:len(x)}
    exec(compile(ast.Module(body=defs,type_ignores=[]),'<delivered-fill-function>','exec'),env)
    def record(clock,price):
        return {'symbol':'TEST','trading_day':'2021-01-04','timestamp':'2021-01-04T'+clock+':00Z',
                'open':price,'high':price,'low':price,'close':price,'volume':1,'amount':1,
                'available_at':'2021-01-04T15:30:00+08:00','source_kind':'synthetic'}
    for later in (5.,500.):
        rows=env['densify_one_minute_rows']([record('09:31',10.),record('09:33',later)])
        require(rows[1]['close']==10. and rows[1]['causal_flat_fill'] is True,'future close used in fill')
        require(rows[1]['available_at']==rows[1]['timestamp'],'fill availability construction changed')
    rejected=False
    try: env['densify_one_minute_rows']([record('09:33',5.)])
    except ValueError: rejected=True
    require(rejected,'leading gap without prior accepted')
    return {'raw_1m_offset_rejections':blocked,'scalar_index_label_cases':len(cases),
            'synthetic_prior_close_causality_check':True,'leading_gap_rejected':True,
            'full_index_aggregation_replayed':False,'production_configuration_reconstructed':False}


def index_sample_audit(pack: Path) -> list[dict]:
    records = read_json(pack/'03_index_processing/index_1m_observed_and_fill_samples.json')
    flat = csv_rows(pack/'03_index_processing/index_1m_observed_and_fill_samples.csv')
    require(len(records)==len(flat)==8,'index sample count')
    rows=[]
    for r,f in zip(records,flat):
        require((r['symbol'],r['timestamp'])==(f['symbol'],f['timestamp']),'index sample identities')
        require(r['timestamp'][:10] in {'2021-01-04','2021-01-05'},'index sample date')
        filled=r['causal_flat_fill']
        require(type(filled) is bool and f['causal_flat_fill']==str(filled),'fill flag')
        for col in ('open','high','low','close','amount'):
            require(r[col]==float(f[col]),'index CSV/JSON numeric mismatch')
        if filled:
            require(r['open']==r['high']==r['low']==r['close'] and r['volume']==r['amount']==0,'fill form')
            require(r['available_at']==r['timestamp'],'fill availability is legacy label')
            channel='SYNTHETIC_BAR_LABEL_NOT_VERIFIED_PUBLICATION'
        else:
            require(r['available_at']==r['trading_day']+'T15:30:00+08:00','observed availability differs')
            channel='PRODUCER_ASSIGNED_END_OF_DAY_NOT_VERIFIED_PUBLICATION'
        require(f['available_at']==r['available_at'],'index availability CSV/JSON')
        rows.append({'symbol':r['symbol'],'bar_label':r['timestamp'],'causal_flat_fill':filled,
                     'raw_available_at':r['available_at'],'channel_interpretation':channel,
                     'realtime_available_proven':False})
    inputs=read_json(pack/'03_index_processing/index_3s_input_000852_20210104_0930.json')
    require(len(inputs)==8 and all(r['symbol']=='000852.SH' and r['trading_day']=='2021-01-04' for r in inputs),'3s sample identity')
    require([r['observation_time'] for r in inputs]==[f'09:30:{s:02d}' for s in range(0,24,3)],'3s sample clock')
    return rows


def run(root: Path, output: Path) -> dict:
    root=root.resolve(); pack=root/PACK
    require(not output.exists(),'fresh output directory required')
    require(digest(pack/'manifest.json')==MANIFEST_SHA,'manifest identity changed')
    m=read_json(pack/'manifest.json'); specs=m['delivered_files']
    require(len(specs)==35 and len({s['path'] for s in specs})==35,'delivery file inventory')
    for spec in specs: checked_file(root,spec)
    actual={str(p.relative_to(root)) for p in pack.rglob('*') if p.is_file()}
    require(actual=={s['path'] for s in specs}|{PACK+'/manifest.json'},'unlisted pack file')
    full_map={'docs/modules/history/canonical-bars-whitepaper.md':'canonical-bars-whitepaper.md',
              'src/datahub/storage/query/session_offset_contract.py':'session_offset_contract.py',
              'docs/contracts/consumption_cards/cn_a_1m_4ceca_identity_time.md':'cn_a_1m_4ceca_identity_time.md'}
    for upstream,local in full_map.items():
        spec=m['source_repositories']['unified_datahub']['files'][upstream]
        p=pack/'01_timestamp_semantics'/local
        require(digest(p)==spec['sha256'] and p.stat().st_size==spec['bytes'],'upstream full-file copy mismatch')
    sections=0
    for full,excerpt in [('canonical-bars-whitepaper.md','canonical-bars-whitepaper_section5.md'),('session_offset_contract.py','session_offset_contract_1m_and_buckets.py')]:
        sections+=verify_excerpt((pack/'01_timestamp_semantics'/full).read_text(),(pack/'01_timestamp_semantics'/excerpt).read_text())
    anomalies=compare_anomalies(pack); probes=source_function_probe(pack); index=index_sample_audit(pack)
    require(digest(pack/'04_corporate_actions/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json')==OVERLAY_SHA,'known overlay changed')
    actions=read_json(pack/'04_corporate_actions/etf_source_actions_v2_manifest.json')
    require(actions['full_source_qualification_complete'] is False and actions['microstructure_research_admitted'] is False,'source admission falsely upgraded')
    inventory=read_json(pack/'05_microstructure_inventory/inventory.json')
    rows=[]
    for channel in inventory['channels']:
        for product in channel['products']:
            rows.append({'question':channel['question'],'dataset':product['dataset'],
                         'status':'LOCAL_INVENTORY_DECLARATION_NOT_DELIVERED_QUOTES_OR_PUBLICATION_PROOF',
                         'inspected_day_declared':product.get('inspected_without_2026_quotes',product.get('inspected_day'))})
    result={'schema_id':'factorlab_etf_upstream_cloud_review@1.0',
            'decision':'UPSTREAM_EXPLANATION_PARTIALLY_VERIFIED_ONE_DAY_QUOTE_DELIVERY_PENDING',
            'delivery_commit':DELIVERY,'manifest_sha256':MANIFEST_SHA,'verified_payload_files':len(specs),
            'verified_payload_bytes':sum(s['bytes'] for s in specs),'full_upstream_copies_hash_checked':len(full_map),
            'excerpt_sections_matched_to_delivered_fulltext':sections,'anomaly_rows_verified':len(anomalies),
            'anomaly_history_matches':20,'dataset_identity_only_differences':20,
            'index_sample_rows':len(index),'index_observed_rows':sum(not r['causal_flat_fill'] for r in index),
            'index_filled_rows':sum(r['causal_flat_fill'] for r in index),'index_3s_rows':8,'source_function_probes':probes,
            'legacy_label_decoding_supported_for_fixed_source':True,'native_ETF_trade_bucket_verified':False,
            'volume_unit':'UNRESOLVED_CONFLICT_SHARES_VS_CATALOG_LOTS_LIMITED_SCOPE',
            'volume_zero_cause':'UNKNOWN_BELOW_IMPORTED_ARCHIVE_LAYER',
            'shared_upstream_not_independent_sources':True,'source_repositories_independently_authenticated':False,
            'archive_vendor_originals_available':False,'exchange_publication_times_verified':False,
            'available_at_homogeneous_realtime_field':False,'corporate_action_complete':False,
            'quote_trade_inventory_only':True,'quoted_product_start_is_instrument_start':False,
            'new_quote_prices_read':False,'post2025_candidate_prices_read':False,
            'post2025_source_metadata_and_action_rows_present':True,'return_population_opened':False,
            'new_model_fits':0,'R1A_reserve_unchanged':True,'production_authority':False,'fresh_oos':False,
            'BLACKBOX_query_count':3,'old_values_or_manifests_modified':False}
    output.mkdir(parents=True)
    for name,data in [('anomaly_comparison.csv',anomalies),('index_time_channels.csv',index),('inventory_assessment.csv',rows)]:
        with (output/name).open('w',encoding='utf-8',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
    result['files']=[{'path':p.name,'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(output.glob('*.csv'))]
    (output/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); print(json.dumps(run(args.root,args.output),ensure_ascii=False,indent=2))
