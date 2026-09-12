"""Fixed-day source field/clock audit, not fair-value or trading research.

Only the six already delivered 2025-12-01 Parquet files are read. Source interval
coverage is an offline property: time since last state change is NOT quote age,
latency, or proof that no intervening source snapshot is missing. No PnL, returns,
lead-lag estimation, optimal clock shift, missing-data fill or date search.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

PACK = 'data/etf_microstructure_sample_20251201_v1'
DAY = '2025-12-01'
DELIVERY = '6004b42b1a6d68e13ec602126292a3709d474b70'
MANIFEST_BLOB = 'b7ccaca6bb0ae712922dd81cb84acd0e334d7847'
PAIRS = (('512100','000852'),('588000','000688'))
SESSIONS = (('continuous_am','09:30:00','11:30:00'),('continuous_pm','13:00:00','14:57:00'))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False, default=str)+'\n', encoding='utf-8')


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    columns = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader(); writer.writerows(rows)


def moment(clock: str) -> datetime:
    return datetime.fromisoformat(DAY+'T'+clock)


def decode_raw(value: str, day: str = DAY) -> datetime:
    """This delivered L2/tick product's HHmmssSSS, not a general ISO parser."""
    s=str(value)
    require(s.isascii() and s.isdigit() and 1<=len(s)<=9,'invalid raw observation clock')
    n=int(s); h=n//10000000; m=n//100000%100; sec=n//1000%100; ms=n%1000
    require(0<=h<24 and 0<=m<60 and 0<=sec<60,'out-of-range source observation time')
    return datetime.fromisoformat(day).replace(hour=h,minute=m,second=sec,microsecond=ms*1000)


def index_label(row: dict) -> datetime:
    """Source-specific index serializer appends Z to a naive observation label."""
    s=row['observation_datetime']
    require(isinstance(s,str) and s.endswith('Z'),'unexpected index label encoding')
    t=datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ')
    require(t.date().isoformat()==DAY and t.strftime('%H:%M:%S')==row['observation_time'],'index clock/day disagreement')
    return t


def continuous_phase(t: datetime) -> str | None:
    # Half-open interior windows declared for this audit. Auction/close endpoints
    # are retained in source diagnostics but never carried into these windows.
    for name,start,end in SESSIONS:
        if moment(start)<=t<moment(end): return name
    return None


def good_bbo(row: dict) -> bool:
    vals=[row.get(c) for c in ('bid_price_x10000_1','ask_price_x10000_1','bid_size_1','ask_size_1')]
    if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in vals): return False
    return vals[0]<=vals[1]


def quote_lookup(rows: list[dict], times: list[datetime], t: datetime) -> tuple[int | None,str]:
    phase=continuous_phase(t)
    if phase is None: return None,'outside_continuous_window'
    k=bisect.bisect_right(times,t)-1
    if k<0: return None,'before_first_quote'
    row=rows[k]
    if row['session_phase']!=phase: return None,'no_same_session_state'
    if not row['valid_from']<=t<row['valid_until']: return None,'outside_declared_valid_interval'
    if not good_bbo(row): return None,'invalid_bbo'
    return k,'covered_source_label_only'


def histogram(values) -> str:
    return json.dumps(dict(sorted(Counter(str(v) for v in values).items())),ensure_ascii=False)


def order_violations(row: dict, side: str) -> bool:
    active=[row[f'{side}_price_x10000_{i}'] for i in range(1,11)]
    active=[v for v in active if v is not None and v>0]
    if side=='ask': return any(b<a for a,b in zip(active,active[1:]))
    return any(b>a for a,b in zip(active,active[1:]))


def run(root: Path, output: Path) -> dict:
    import pyarrow.parquet as pq
    root=root.resolve(); pack=root/PACK
    require(not output.exists(),'fresh evidence directory required')
    raw=(pack/'manifest.json').read_bytes()
    require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==MANIFEST_BLOB,'delivery manifest identity changed')
    m=json.loads(raw)
    expected={f'{kind}/{code}_20251201.parquet' for kind,codes in (('quotes',('512100','588000')),('trades',('512100','588000')),('index_3s',('000852','000688'))) for code in codes}
    require(set(m['logical_files'])==expected,'six-file identity drift')
    require({str(p.relative_to(pack)) for p in pack.rglob('*.parquet')}==expected,'extra/missing raw parquet')
    tables={}; integrity=[]
    for name in sorted(expected):
        p=pack/name; spec=m['logical_files'][name]
        require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(pack.resolve()),'invalid source path')
        require(digest(p)==spec['sha256'] and p.stat().st_size==spec['bytes'],'file bytes changed '+name)
        table=pq.read_table(p); require(table.num_rows==spec['rows'],'row count changed '+name)
        rows=table.to_pylist(); code=name.split('/')[1].split('_')[0]
        require(all(r['trading_day']==DAY for r in rows),'out-of-day market rows')
        idcol='symbol' if name.startswith('index_3s') else 'instrument_id'
        require(all(r[idcol]==code+'.SH' for r in rows),'instrument mismatch')
        tables[name]=rows
        integrity.append({'path':name,**spec,'columns':table.num_columns})
    payload=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(pack.rglob('*')) if p.is_file()]
    phase_rows=[]; interval_issues=[]; quote_rows=[]; trade_rows=[]; index_rows=[]; lookup_rows=[]; boundary_rows=[]; anomaly=[]
    for code,idx in PAIRS:
        q=tables[f'quotes/{code}_20251201.parquet']; tr=tables[f'trades/{code}_20251201.parquet']; ix=tables[f'index_3s/{idx}_20251201.parquet']
        qt=[r['market_observed_at'] for r in q]; tt=[r['market_observed_at'] for r in tr]; it=[index_label(r) for r in ix]
        require(all(t.tzinfo is None for t in qt+tt),'unexpected aware L2/tick timestamps')
        require([r['event_seq'] for r in q]==list(range(len(q))),'quote sequence changed')
        require([r['trade_seq'] for r in tr]==list(range(len(tr))),'trade sequence changed')
        require(qt==sorted(qt) and len(set(qt))==len(qt),'quote clock unsorted/nonunique')
        require(tt==sorted(tt),'trade time not stable chronological')
        require(it==sorted(it),'index time unsorted')
        require(all(decode_raw(r['time_raw'])==r['market_observed_at'] for r in q+tr),'source-specific raw clock decode mismatch')
        require(all(r['valid_from']==r['market_observed_at'] for r in q),'valid_from disagrees with observation')
        require(all(r['valid_until']==qt[k+1] for k,r in enumerate(q[:-1])),'nonterminal interval endpoint changed')
        for k,r in enumerate(q):
            phase_start=k==0 or q[k-1]['session_phase']!=r['session_phase']
            require(r['is_checkpoint']==phase_start and r['update_type']==('checkpoint' if phase_start else 'delta'),'checkpoint phase mismatch')
            if r['valid_until']<=r['valid_from']:
                interval_issues.append({'carrier':code+'.SH','event_seq':r['event_seq'],'session_phase':r['session_phase'],'valid_from':r['valid_from'],'valid_until':r['valid_until'],'duration_ms':(r['valid_until']-r['valid_from']).total_seconds()*1000,'disposition':'RETAIN_RAW_DO_NOT_USE_AS_VALID_INTERVAL'})
        for phase in dict.fromkeys(r['session_phase'] for r in q):
            a=[r for r in q if r['session_phase']==phase]
            phase_rows.append({'carrier':code+'.SH','session_phase':phase,'rows':len(a),'checkpoints':sum(r['is_checkpoint'] for r in a),'first_time':a[0]['market_observed_at'],'last_time':a[-1]['market_observed_at'],'valid_bbo_rows':sum(good_bbo(r) for r in a),'locked_rows':sum(good_bbo(r) and r['bid_price_x10000_1']==r['ask_price_x10000_1'] for r in a),'crossed_positive_price_rows':sum((r['bid_price_x10000_1'] or 0)>(r['ask_price_x10000_1'] or 0)>0 for r in a),'invalid_intervals':sum(r['valid_until']<=r['valid_from'] for r in a),'ten_level_order_violations':sum(order_violations(r,'ask') or order_violations(r,'bid') for r in a)})
        cq=[r for r in q if continuous_phase(r['market_observed_at'])==r['session_phase']]
        quote_rows.append({'carrier':code+'.SH','records':len(q),'checkpoints':sum(r['is_checkpoint'] for r in q),'delta_rows':sum(not r['is_checkpoint'] for r in q),'first_time':qt[0],'last_time':qt[-1],'continuous_event_rows':len(cq),'continuous_valid_bbo_rows':sum(good_bbo(r) for r in cq),'continuous_ms_remainder_hist':histogram((t.hour*3600000+t.minute*60000+t.second*1000+t.microsecond//1000)%3000 for t in qt if continuous_phase(t)),'all_iopv_raw_zero':all(str(r['iopv_raw'])=='0' for r in q),'all_receipt_exact_pit_false':all(r['receipt_exact_pit'] is False for r in q),'reversed_or_empty_interval_rows':sum(r['valid_until']<=r['valid_from'] for r in q),'cum_volume_last_raw':q[-1]['cum_volume'],'source_kind':q[0]['source_kind'],'time_authority':q[0]['time_authority']})
        positive=[r for r in tr if r['volume'] is not None and r['volume']>0 and r['price_x10000'] is not None and r['price_x10000']>0]
        raw_ids=Counter(r['trade_seq_raw'] for r in tr)
        trade_rows.append({'carrier':code+'.SH','records':len(tr),'positive_price_quantity_rows':len(positive),'zero_quantity_rows':sum(r['volume']==0 for r in tr),'first_time':tt[0],'last_time':tt[-1],'unique_observation_times':len(set(tt)),'max_trades_same_timestamp':max(Counter(tt).values()),'duplicate_nonempty_trade_id_rows':sum(n-1 for k,n in raw_ids.items() if k and n>1),'trade_code_counts':histogram(r['trade_code'] for r in tr),'all_receipt_exact_pit_false':all(r['receipt_exact_pit'] is False for r in tr),'volume_sum_raw':sum(r['volume'] for r in tr if r['volume'] is not None),'currency_or_lot_unit_certified':False})
        gaps=[(b-a).total_seconds() for a,b in zip(it,it[1:])]
        index_rows.append({'symbol':idx+'.SH','records':len(ix),'first_time':it[0],'last_time':it[-1],'duplicate_observation_times':len(it)-len(set(it)),'interval_seconds_hist':histogram(gaps),'nonpositive_or_invalid_prices':sum(r['price'] is None or not math.isfinite(r['price']) or r['price']<=0 for r in ix),'null_volume_rows':sum(r['volume'] is None for r in ix),'timestamp_mode':histogram(r['timestamp_mode'] for r in ix),'exchange_publication_verified':False})
        quote_time_set=set(qt)
        for phase,lo,hi in SESSIONS:
            target=[t for t in it if moment(lo)<=t<moment(hi)]
            status=Counter(); ages=[]; max_interval=0.
            for t in target:
                k,why=quote_lookup(q,qt,t);status[why]+=1
                if k is not None:
                    ages.append((t-qt[k]).total_seconds())
                    max_interval=max(max_interval,(q[k]['valid_until']-q[k]['valid_from']).total_seconds())
            sorted_age=sorted(ages)
            lookup_rows.append({'carrier':code+'.SH','index_symbol':idx+'.SH','session_phase':phase,'observed_index_targets':len(target),'exact_quote_label_matches':sum(t in quote_time_set for t in target),'source_interval_valid_bbo_matches':len(ages),'unmatched_reasons':json.dumps({k:v for k,v in status.items() if k!='covered_source_label_only'},sort_keys=True),'max_seconds_since_state_change':max(ages,default=None),'median_seconds_since_state_change':sorted_age[len(sorted_age)//2] if sorted_age else None,'max_matched_declared_interval_seconds':max_interval,'not_exchange_quote_age':True})
        for clock in ('09:30:00','09:30:01','09:30:02','11:30:00','13:00:00','13:00:01','13:00:02','13:26:00','14:57:00','15:00:00','15:00:03'):
            t=moment(clock); k,why=quote_lookup(q,qt,t)
            boundary_rows.append({'carrier':code+'.SH','target_label':t,'status':why,'event_seq':q[k]['event_seq'] if k is not None else None,'state_start':qt[k] if k is not None else None,'state_end':q[k]['valid_until'] if k is not None else None})
        for lo,hi in (('13:25:00','13:26:00'),('13:26:00','13:27:00')):
            rows=[r for r in tr if moment(lo)<=r['market_observed_at']<moment(hi)]
            anomaly.append({'carrier':code+'.SH','label_interval_left_closed':lo,'label_interval_right_open':hi,'recorded_trade_rows':len(rows),'positive_price_quantity_rows':sum(r['volume'] is not None and r['volume']>0 and r['price_x10000'] is not None and r['price_x10000']>0 for r in rows),'volume_sum_raw_units':sum(r['volume'] for r in rows if r['volume'] is not None),'min_price_x10000_raw':min((r['price_x10000'] for r in rows if r['price_x10000'] is not None),default=None),'max_price_x10000_raw':max((r['price_x10000'] for r in rows if r['price_x10000'] is not None),default=None),'exact_left_boundary_trades':sum(r['market_observed_at']==moment(lo) for r in rows),'not_legacy_bar_reconstruction':True})
    output.mkdir(parents=True)
    for name,rows in [('file_integrity',integrity),('quote_summary',quote_rows),('quote_phase_audit',phase_rows),('invalid_quote_intervals',interval_issues),('trade_summary',trade_rows),('index_summary',index_rows),('index_quote_label_coverage',lookup_rows),('fixed_boundary_probes',boundary_rows),('anomaly_neighbourhood',anomaly)]:
        write_csv(output/(name+'.csv'),rows)
    write_json(output/'delivery_payload_hashes.json',payload)
    decision='DAY_FILES_VERIFIED_LABEL_REPLAY_RESTRICTED_REALTIME_AND_NAV_UNQUALIFIED'
    if interval_issues: decision+='__SOURCE_INTERVAL_DEFECT_FOUND'
    receipt={'schema_id':'factorlab_one_day_observation_review@1.0','decision':decision,'delivery_commit':DELIVERY,'manifest_sha256':digest(pack/'manifest.json'),'trading_day':DAY,'verified_parquet_files':len(integrity),'verified_market_rows':sum(x['rows'] for x in integrity),'verified_parquet_bytes':sum(x['bytes'] for x in integrity),'quotes':quote_rows,'trades':trade_rows,'indices':index_rows,'index_quote_label_coverage':lookup_rows,'invalid_intervals':interval_issues,'anomaly_neighbourhood':anomaly,'complete_vendor_archives_reproduced':False,'source_partition_hashes_independently_verified':False,'clock_shift_fitted':False,'zero_volume_cause_identified':False,'historical_units_certified':False,'exact_receipt_pit_qualified':False,'synchronized_economic_price_identified':False,'nav_premium_qualified':False,'old_prices_or_results_modified':False,'new_strategy_returns_computed':False,'new_model_fits':0,'R1A_reserve_unchanged':True,'post2025_market_rows_read':False,'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,'files':[{'path':p.name,'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(output.iterdir())]}
    write_json(output/'receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2,default=str))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.root,a.output)
