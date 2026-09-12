"""Read-only replay verification; never replace decisive design evidence."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import pandas as pd
from research.r1a_control_design.core import FEATURES, require
from research.r1a_control_design.study import sha

REFERENCE_BLOB='d68ab9df9780866c1d9b11da5d8d8bb93ef5ae5b'
FLOAT_COLS=set(FEATURES)|{prefix+f for prefix in ('event_','control_','center_','scale_') for f in FEATURES}|{
 'distance','maximum_scaled_gap','coverage','original_event_SD','matched_SMD','retention_shift_SMD',
 'matched_event_control_variance_ratio','control_unit_energy_ratio_NOT_variance_effect',
 'unit_covariance_cancellation_NOT_observed_noise','control_calendar_HHI_unit_incidence','largest_control_day_unit_share'}


def compare_table(reference:Path,replay:Path)->dict:
    a=pd.read_csv(reference,dtype=str,keep_default_na=False)
    b=pd.read_csv(replay,dtype=str,keep_default_na=False)
    require(list(a.columns)==list(b.columns) and a.shape==b.shape,'table schema/row mismatch: '+reference.name)
    floats={}; exact=[]
    for col in a:
        if col not in FLOAT_COLS:
            require(a[col].equals(b[col]),'exact allocation/count/status mismatch: '+reference.name+':'+col)
            exact.append(col);continue
        require((a[col]=='').equals(b[col]==''),'missing mask mismatch: '+col)
        count=0;error=Decimal(0)
        for x,y in zip(a[col],b[col]):
            if x=='':continue
            try: dx,dy=Decimal(x),Decimal(y)
            except InvalidOperation as exc:raise ValueError('invalid numeric value: '+col) from exc
            require(dx.is_finite() and dy.is_finite(),'nonfinite numeric value: '+col)
            diff=abs(dx-dy);limit=Decimal('1e-10')+Decimal('1e-10')*max(abs(dx),abs(dy))
            require(diff<=limit,'float mismatch beyond tolerance: '+col)
            count+=int(x!=y);error=max(error,diff)
        floats[col]={'different_text_cells':count,'maximum_absolute_error':str(error)}
    return {'file':reference.name,'rows':len(a),'columns':len(a.columns),'byte_identical':sha(reference)==sha(replay),
            'exact_columns':exact,'float_columns':floats}


def packing_implication(receipt:dict,coverage:pd.DataFrame)->dict:
    """Analytical upper bound implied by the frozen same-year inclusive cap.

Not an optimized allocation, a new statistical gate, or a new source-data read.
Even the bound ignores quality, exact strata and event-time availability.
"""
    out=[]
    for symbol in receipt['pools']:
        entries=[]
        for source in receipt['sources']:
            p=Path(source['path'])
            if p.parent.name!=symbol:continue
            year=p.stem
            match=coverage.loc[(coverage.symbol==symbol)&(coverage.stage=='PAST_CALIPER_EXCLUSIVE')&(coverage.group=='YEAR_'+year)]
            require(len(match)==1,'year count unavailable')
            n=int(match.original_events.iloc[0]);bars=int(source['rows'])
            bound=min(n,bars//241)
            entries.append({'year':year,'original_events':n,'price_rows':bars,'optimistic_capacity_bound':bound})
        total=sum(x['original_events'] for x in entries);cap=sum(x['optimistic_capacity_bound'] for x in entries)
        out.append({'symbol':symbol,'years':entries,'total_events':total,'optimistic_total_capacity_bound':cap,
                    'coverage_upper_bound':cap/total})
    return {'formula':'sum_year min(event_count_year, floor(price_rows_year/241))',
            'assumptions':'Same calendar year; entire inclusive [c,c+240] price interval matures before event cutoff; no shared price observation between controls.',
            'postrun_analytical_implication_not_a_changed_gate':True,'symbols':out}


def verify(reference:Path,replay:Path,output:Path)->dict:
    raw=(reference/'design_receipt.json').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    require(blob==REFERENCE_BLOB,'decisive receipt changed')
    a=json.loads(raw);b=json.loads((replay/'design_receipt.json').read_text())
    for key in ('decision','baseline_commit','freeze_commit','freeze_sha256','sources','input_blobs','pools','symbols','table_rows',
                'new_allocation_outcomes_read','new_significance_tests','noise_reduction_demonstrated','old_pairs_modified',
                'post2020_price_files_read','caliper_tuned','BLACKBOX_query_count','production_authority','fresh_oos',
                'confirmation_protocol_frozen','confirmation_clock_started','horizon_selected'):
        require(a[key]==b[key],'receipt decision/input mismatch: '+key)
    require(b['new_allocation_outcomes_read'] is False,'outcomes were opened')
    tables=[]
    for spec in a['files']:
        p=reference/spec['path']
        require(p.stat().st_size==spec['bytes'] and sha(p)==spec['sha256'],'reference bytes changed: '+p.name)
        tables.append(compare_table(p,replay/p.name))
    result={'decision':'CONTROL_DESIGN_REPLAY_EXACT_IDENTITIES_AND_BOUNDED_FLOAT_PASS',
            'reference_receipt_blob_sha1':REFERENCE_BLOB,'reference_unchanged':True,'tables':tables,
            'packing_implication':packing_implication(a,pd.read_csv(reference/'coverage_by_group.csv')),
            'new_outcomes_read':False,'production_authority':False}
    require(not output.exists(),'do not overwrite audit')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'decision':result['decision'],'byte_identical_tables':sum(x['byte_identical'] for x in tables),
                      'packing_implication':result['packing_implication']},indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',type=Path,required=True);p.add_argument('--replay',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();verify(args.reference,args.replay,args.output)
