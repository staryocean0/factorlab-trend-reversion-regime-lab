"""Finite source accounting, not a return study. Raw input files are immutable.

Only the fixed 2025-12-01 observations enter calculations. Decimal arithmetic
keeps quantity and conditional notional discrepancies visible without fitted
unit factors or numerical pass tolerances. The interval view is offline-only.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left, bisect_right
from collections import Counter
import csv
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

DAY = '2025-12-01'
PACK = 'data/etf_microstructure_sample_20251201_v1'
LEGACY = 'data/r1a_carrier_prices/cloud_pack_v1'
FREEZE = 'docs/governance/ETF_DAY_RECONCILIATION_FREEZE@1.0.json'
FREEZE_SHA = '89f65e51a9b89fea160ad4f305392afa651986d3482bcc8c4f77831994830bd3'
MANIFEST_SHA = '559963188f9b2f858f8255e7f107496288f8e2ed884f81a762584ef249853360'
YEAR_PINS = {'512100': ('d600155e41f23b63d64d73c035f919f68bcd7ed3b93f48e401f310f312fdea73',3930936), '588000': ('08839ca0242ddd57a3b84305abb9670ca1b8055d2bd33ce59768bd84af97b14a',3984249)}
CONVENTIONS = ('[t-60s,t)', '(t-60s,t]', '[t,t+60s)', '(t,t+60s]')
PHASES = {'continuous_am': ('09:30:00','11:30:00'), 'continuous_pm': ('13:00:00','14:57:00')}
ZERO = Decimal(0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dec(value):
    require(value is not None and value != '', 'missing numeric field')
    x = Decimal(str(value))
    require(x.is_finite(), 'nonfinite numeric field')
    return x


def clock(value):
    """ETF product's naive Shanghai source label; no generic Z exception."""
    t = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    require(t.tzinfo is None and t.date().isoformat() == DAY, 'wrong source clock/day')
    return t


def at(value):
    return datetime.fromisoformat(DAY+'T'+value)


def phase_at(t):
    return next((p for p,(a,b) in PHASES.items() if at(a) <= t < at(b)), None)


def legacy_clock(value):
    t = datetime.fromisoformat(value)
    require(t.tzinfo is not None, 'legacy CSV must explicitly carry timezone')
    t = t.astimezone(ZoneInfo('Asia/Shanghai')).replace(tzinfo=None)
    require(t.date().isoformat() == DAY, 'legacy day changed')
    return t


class TickTape:
    def __init__(self, rows):
        self.rows = rows
        self.times = [clock(r['market_observed_at']) for r in rows]
        require(self.times == sorted(self.times), 'tick ordering changed')
        require([r['trade_seq'] for r in rows] == list(range(len(rows))), 'tick sequence changed')
        self.quantities, self.notionals = [ZERO], [ZERO]
        for r in rows:
            q, p = dec(r['volume']), dec(r['price_x10000'])
            require(q > 0 and p > 0, 'nonpositive tick; no silent filtering')
            self.quantities.append(self.quantities[-1]+q)
            self.notionals.append(self.notionals[-1]+p*q/Decimal(10000))

    def bounds(self, left, right, right_closed=False):
        lo = (bisect_right if right_closed else bisect_left)(self.times,left)
        hi = (bisect_right if right_closed else bisect_left)(self.times,right)
        return lo, hi

    def bar(self, left, right, right_closed=False):
        lo, hi = self.bounds(left,right,right_closed)
        prices = [r['price_x10000'] for r in self.rows[lo:hi]]
        ohlc = [prices[0],max(prices),min(prices),prices[-1]] if prices else [None]*4
        return {'tick_rows':hi-lo, 'tick_volume_raw':self.quantities[hi]-self.quantities[lo],
                **dict(zip(('tick_open_x10000','tick_high_x10000','tick_low_x10000','tick_close_x10000'),ohlc)),
                'left_exact_tick_rows':bisect_right(self.times,left)-bisect_left(self.times,left),
                'right_exact_tick_rows':bisect_right(self.times,right)-bisect_left(self.times,right)}


class RestrictedSourceView:
    """A fail-closed consumer overlay, not a mutation or upstream repair.

The latest event is inspected even when invalid. An older valid state never
substitutes for a newer invalid one. Future checkpoints are never backfilled.
"""
    def __init__(self, rows):
        self.rows, self.dispositions = rows, []
        self.times = [clock(r['valid_from']) for r in rows]
        require(self.times == sorted(set(self.times)), 'duplicate/unordered quote labels')
        require([r['event_seq'] for r in rows] == list(range(len(rows))), 'quote sequence changed')
        initialized, previous_phase = False, None
        for r,start in zip(rows,self.times):
            require(start == clock(r['market_observed_at']), 'valid_from differs from observed label')
            p = r['session_phase']
            if p != previous_phase:
                initialized = False
            if r['is_checkpoint']:
                initialized = True
            previous_phase = p
            end = None if r['valid_until'] is None else clock(r['valid_until'])
            effective = None
            if end is None:
                reason = 'UNKNOWN_END'
            elif end <= start:
                reason = 'REVERSED_OR_EMPTY'
            elif p not in PHASES or phase_at(start) != p:
                reason = 'OUTSIDE_CONTINUOUS_SCOPE'
            elif not initialized:
                reason = 'NO_SAME_PHASE_CHECKPOINT'
            else:
                b,a = dec(r['bid_price_x10000_1']),dec(r['ask_price_x10000_1'])
                bs,az = dec(r['bid_size_1']),dec(r['ask_size_1'])
                if not (0 < b <= a and bs > 0 and az > 0):
                    reason = 'INVALID_BBO'
                else:
                    effective = min(end,at(PHASES[p][1]))
                    reason = 'USABLE_RESTRICTED_SOURCE_LABEL' if effective > start else 'EMPTY_AFTER_PHASE_CLIP'
            self.dispositions.append({'event_seq':r['event_seq'],'session_phase':p,'raw_valid_from':str(start),
              'raw_valid_until':str(end) if end else '', 'consumer_end':str(effective) if effective else '',
              'phase_end_clipped':effective is not None and effective != end,'disposition':reason})

    def lookup(self,t):
        p = phase_at(t)
        if p is None:
            return None
        j = bisect_right(self.times,t)-1
        if j < 0:
            return None
        d = self.dispositions[j]
        if d['disposition'] != 'USABLE_RESTRICTED_SOURCE_LABEL' or d['session_phase'] != p:
            return None
        return j if t < clock(d['consumer_end']) else None


def quote_accounting(code,quotes,tape):
    result=[]
    for q in quotes:
        t=clock(q['market_observed_at']); before=bisect_left(tape.times,t); through=bisect_right(tape.times,t)
        lp=tape.rows[through-1]['price_x10000'] if through else None
        dv=dec(q['cum_volume'])-tape.quantities[through]
        db=dec(q['cum_volume'])-tape.quantities[before]
        da=dec(q['cum_amount'])-tape.notionals[through]
        result.append({'carrier':code,'event_seq':q['event_seq'],'session_phase':q['session_phase'],'source_label':str(t),
          'quote_cum_volume_raw':dec(q['cum_volume']),'tick_cum_before_raw':tape.quantities[before],
          'tick_cum_through_raw':tape.quantities[through],'quantity_difference_through_raw':dv,
          'quantity_difference_before_raw':db,'ticks_exactly_at_quote_label':through-before,
          'quote_last_price_x10000':q['last_price_x10000'],'last_tick_price_x10000':lp,
          'last_price_equal':q['last_price_x10000']==lp if lp is not None else '',
          'last_tick_label':str(tape.times[through-1]) if through else '',
          'last_tick_tie_count':through-bisect_left(tape.times,tape.times[through-1]) if through else 0,
          'quote_cum_amount_raw':dec(q['cum_amount']),'conditional_price_times_quantity':tape.notionals[through],
          'conditional_amount_difference':da})
    return result


def quote_summaries(rows):
    out=[]
    for code in ('512100','588000'):
        rr=[r for r in rows if r['carrier']==code]
        for p in ['ALL']+sorted({r['session_phase'] for r in rr}):
            g=[r for r in rr if p=='ALL' or r['session_phase']==p]
            dif=[r['quantity_difference_through_raw'] for r in g]
            out.append({'carrier':code,'phase':p,'quote_events':len(g),
              'quantity_equal_through':sum(v==0 for v in dif),'quantity_equal_before':sum(r['quantity_difference_before_raw']==0 for r in g),
              'quote_quantity_ahead':sum(v>0 for v in dif),'quote_quantity_behind':sum(v<0 for v in dif),
              'max_absolute_quantity_gap_raw':max(map(abs,dif)),
              'price_comparable_events':sum(r['last_price_equal']!='' for r in g),
              'last_price_equal_events':sum(r['last_price_equal'] is True for r in g),
              'max_absolute_conditional_amount_gap':max(abs(r['conditional_amount_difference']) for r in g),
              'last_quantity_difference_raw':g[-1]['quantity_difference_through_raw'],
              'last_conditional_amount_difference':g[-1]['conditional_amount_difference']})
    return out


def interval_scope(left,right,right_closed):
    for p,(a,b) in PHASES.items():
        if at(a) <= left and (right < at(b) if right_closed else right <= at(b)):
            return p
    return 'OUTSIDE_COMPLETE_CONTINUOUS_MINUTE'


def minute_accounting(code,legacy,tape):
    out=[]
    for r in legacy:
        t=legacy_clock(r['timestamp'])
        old=[dec(r[c])*Decimal(10000) for c in ('open','high','low','close')]
        for convention in CONVENTIONS:
            past='t-60s' in convention; rc=convention.startswith('(')
            left,right=(t-timedelta(minutes=1),t) if past else (t,t+timedelta(minutes=1))
            scope=interval_scope(left,right,rc)
            b=tape.bar(left,right,rc)
            prices=[b[c] for c in ('tick_open_x10000','tick_high_x10000','tick_low_x10000','tick_close_x10000')]
            eq=[o==dec(p) if p is not None else '' for o,p in zip(old,prices)]
            out.append({'carrier':code,'legacy_label':r['timestamp'],'convention':convention,'scope':scope,
              'left_label':str(left),'right_label':str(right),'legacy_volume_raw':dec(r['volume']),
              **{'legacy_'+c:r[c] for c in ('open','high','low','close')},**b,
              'volume_equal_without_unit_conversion':dec(r['volume'])==b['tick_volume_raw'],
              'legacy_minus_tick_volume_raw':dec(r['volume'])-b['tick_volume_raw'],
              **dict(zip(('open_equal_declared_scale','high_equal_declared_scale','low_equal_declared_scale','close_equal_declared_scale'),eq)),
              'all_ohlc_equal_declared_scale':all(v is True for v in eq) if b['tick_rows'] else '',
              'legacy_zero_nonflat':dec(r['volume'])==0 and dec(r['high'])!=dec(r['low'])})
    return out


def minute_summaries(rows):
    out=[]
    for code in ('512100','588000'):
        for c in CONVENTIONS:
            g=[r for r in rows if r['carrier']==code and r['convention']==c]
            usable=[r for r in g if r['scope']!='OUTSIDE_COMPLETE_CONTINUOUS_MINUTE']
            printed=[r for r in usable if r['tick_rows']]
            out.append({'carrier':code,'convention':c,'all_legacy_rows':len(g),'complete_continuous_minutes':len(usable),
              'boundary_scope_rows':len(g)-len(usable),'with_recorded_ticks':len(printed),
              'without_recorded_ticks':len(usable)-len(printed),
              'all_ohlc_equal_declared_scale':sum(r['all_ohlc_equal_declared_scale'] is True for r in printed),
              'close_equal_declared_scale':sum(r['close_equal_declared_scale'] is True for r in printed),
              'volume_equal_without_conversion':sum(r['volume_equal_without_unit_conversion'] for r in usable),
              'ohlc_and_volume_equal':sum(r['all_ohlc_equal_declared_scale'] is True and r['volume_equal_without_unit_conversion'] for r in usable),
              'legacy_zero_nonflat':sum(r['legacy_zero_nonflat'] for r in usable),
              'legacy_zero_nonflat_with_ticks':sum(r['legacy_zero_nonflat'] and r['tick_rows']>0 for r in usable),
              'tick_sum_raw':sum((r['tick_volume_raw'] for r in usable),ZERO),
              'legacy_sum_raw':sum((r['legacy_volume_raw'] for r in usable),ZERO)})
    return out


def write_csv(path,rows):
    require(bool(rows),'empty output table')
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str,allow_nan=False)+'\n',encoding='utf-8')


def run(root,output):
    import pyarrow.parquet as pq
    root,output=Path(root).resolve(),Path(output).resolve()
    require(not output.exists(),'fresh output required')
    require(digest(root/FREEZE)==FREEZE_SHA,'freeze changed')
    pack=root/PACK;require(digest(pack/'manifest.json')==MANIFEST_SHA,'delivery manifest changed')
    m=json.loads((pack/'manifest.json').read_text());records={};integrity=[]
    require(len(m['logical_files'])==6 and len(list(pack.rglob('*.parquet')))==6,'raw file set changed')
    for name,s in sorted(m['logical_files'].items()):
        p=pack/name;require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(pack),'source path')
        require(digest(p)==s['sha256'] and p.stat().st_size==s['bytes'],'raw bytes changed')
        table=pq.read_table(p);require(table.num_rows==s['rows'],'raw row count')
        rr=table.to_pylist();require(all(r['trading_day']==DAY for r in rr),'date scope')
        code=name.split('/')[1][:6]
        require(all(r['symbol']==code+'.SH' if name.startswith('index_3s/') else r['instrument_id']==code+'.SSE' and r['code']==code for r in rr),'instrument scope')
        records[name]=rr;integrity.append({'path':str(p.relative_to(root)),'sha256':s['sha256'],'bytes':s['bytes'],'file_rows':s['rows'],'calculation_rows':len(rr)})
    quote_rows=[];minute_rows=[];dispositions=[];targets=[];probes=[]
    for code,index in (('512100','000852'),('588000','000688')):
        p=root/LEGACY/'prices'/(code+'_2025.csv');hp,bp=YEAR_PINS[code]
        require(p.is_file() and not p.is_symlink() and digest(p)==hp and p.stat().st_size==bp,'legacy price bytes changed')
        # Both byte sizes come from the independently retained fixed-day intake.
        with p.open(newline='') as f:
            legacy=[r for r in csv.DictReader(f) if r['timestamp'].startswith(DAY)]
        require(len(legacy)==241 and all(r['symbol']==code+'.SH' for r in legacy),'legacy fixed-day denominator')
        require(len({r['timestamp'] for r in legacy})==len(legacy),'duplicate legacy minute')
        integrity.append({'path':str(p.relative_to(root)),'sha256':hp,'bytes':p.stat().st_size,'file_rows':58563,'calculation_rows':len(legacy)})
        q=records['quotes/'+code+'_20251201.parquet'];tape=TickTape(records['trades/'+code+'_20251201.parquet'])
        view=RestrictedSourceView(q)
        quote_rows.extend(quote_accounting(code,q,tape));minute_rows.extend(minute_accounting(code,legacy,tape))
        dispositions.extend({'carrier':code,**d} for d in view.dispositions)
        for r in records['index_3s/'+index+'_20251201.parquet']:
            # Product-specific documented serialization: append Z to naive source text.
            value=r['observation_datetime'];require(value.endswith('Z'),'index label encoding')
            ts=clock(value[:-1]);j=view.lookup(ts)
            targets.append({'carrier':code,'index_symbol':index,'index_label':value,'phase':phase_at(ts) or 'OUTSIDE_CONTINUOUS_SCOPE',
              'source_state_found':j is not None,'event_seq':q[j]['event_seq'] if j is not None else '',
              'live_asof_certified':False})
        for text in ('09:29:59.999','09:30:00','09:30:02','11:29:59.999','11:30:00','12:59:59.999','13:00:00','13:00:02','14:56:59.999','14:57:00','15:00:00','15:00:02','15:00:03'):
            j=view.lookup(at(text));probes.append({'carrier':code,'label':DAY+'T'+text,'event_seq':q[j]['event_seq'] if j is not None else '', 'state_found':j is not None})
    output.mkdir(parents=True)
    qs,ms=quote_summaries(quote_rows),minute_summaries(minute_rows)
    tables={'input_integrity.csv':integrity,'quote_tick_accounting.csv':quote_rows,'quote_tick_summary.csv':qs,
      'minute_boundary_accounting.csv':minute_rows,'minute_boundary_summary.csv':ms,'consumer_dispositions.csv':dispositions,
      'consumer_index_label_ledger.csv':targets,'consumer_boundary_probes.csv':probes}
    for name,rr in tables.items():write_csv(output/name,rr)
    r={'schema_id':'factorlab_etf_day_reconciliation@1.0','decision':'FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION',
      'baseline_commit':'677168d872adf7e36300cac1f2dca6c2c483f107','freeze_commit':'17d87322e4ca8bac4e1299d2c76a4b05b886c9bc','freeze_sha256':FREEZE_SHA,
      'day':DAY,'quote_events':len(quote_rows),'minute_scenario_rows':len(minute_rows),'legacy_day_rows':len(minute_rows)//4,
      'quote_summaries':qs,'minute_summaries':ms,'consumer_disposition_counts':dict(Counter(d['disposition'] for d in dispositions)),
      'raw_source_files_modified':False,'upstream_DataHub_code_patched':False,'consumer_overlay_only':True,
      'price_divisor_10000_is_declared_hypothesis':True,'quantity_unit_fitted':False,'bucket_convention_selected':False,
      'clock_shift_fitted':False,'vendor_bucket_certified':False,'live_receipt_time_certified':False,'nav_premium_qualified':False,
      'strategy_outcomes_computed':False,'new_model_fits':0,'post2025_market_rows_read':False,'R1A_reopened':False,
      'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
      'files':[{'path':p.name,'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(output.iterdir())]}
    dump(output/'receipt.json',r)
    print(json.dumps({k:r[k] for k in ('decision','quote_events','minute_scenario_rows','consumer_disposition_counts')},indent=2))
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.root,a.output)
