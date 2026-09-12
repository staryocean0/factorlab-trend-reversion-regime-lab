"""Read-only replay comparison with exact counts and bounded quantile rounding.

Initial main replay 34672587870 reproduced source identities/counts but failed a
whole-file byte comparison on measurement_summary.csv. Do not rerun until a
preferred CPU happens to match, round original data, or replace original tables.
Only the sixteen computed quantile columns may differ by at most 1e-10 in their
reported units. Every differing cell is recorded; identities, counts, fractions,
source bytes, scope flags and all other evidence files remain exact.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import pandas as pd

REFERENCE_RECEIPT_SHA = 'b1e7e37a553dd6aa6c6d4afce9430f0cf51596e3be16e4bbbb84b071832c1738'
ATOL = 1e-10
QUANTILES = {p+'_p'+str(q) for p in ('gap_abs_bp','tick_bp','gap_reference_ticks','etf_minute_range_bp') for q in (50,90,95,99)}


def require(ok,message):
    if not ok: raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_summary(reference,replay):
    require(list(reference.columns)==list(replay.columns) and reference.shape==replay.shape,'summary schema/order/size changed')
    require({'carrier','index_symbol','period'} <= set(reference),'missing summary identity')
    require(not reference[['carrier','period']].duplicated().any(),'duplicate summary identity')
    changes=[]
    for col in reference:
        a=reference[col].astype(str).tolist(); b=replay[col].astype(str).tolist()
        for row,(x,y) in enumerate(zip(a,b)):
            if x==y: continue
            require(col in QUANTILES,'exact summary field changed: '+col)
            require(x!='' and y!='','quantile missingness changed')
            xf,yf=float(x),float(y)
            require(math.isfinite(xf) and math.isfinite(yf),'nonfinite quantile difference')
            error=abs(xf-yf)
            require(error <= ATOL,'quantile discrepancy exceeds rounding bound: '+col)
            changes.append({'carrier':str(reference.iloc[row]['carrier']),'period':str(reference.iloc[row]['period']),
                            'column':col,'reference':x,'replay':y,'absolute_difference':error})
    return changes


def compare_pooled(a,b):
    require(len(a)==len(b),'pooled size changed')
    changes=[]
    for x,y in zip(a,b):
        require(x.keys()==y.keys(),'pooled keys changed')
        for k in x:
            if x[k]==y[k]: continue
            require(k in QUANTILES and x[k] is not None and y[k] is not None,'pooled exact field changed: '+k)
            error=abs(float(x[k])-float(y[k]))
            require(math.isfinite(error) and error <= ATOL,'pooled quantile changed beyond bound')
            changes.append({'carrier':x['carrier'],'field':k,'reference':x[k],'replay':y[k],'absolute_difference':error})
    return changes


def verify(reference,replay,output):
    require(reference.resolve()!=replay.resolve(),'reference cannot be replay output')
    require(not output.exists(),'new audit output required')
    require(sha(reference/'receipt.json')==REFERENCE_RECEIPT_SHA,'original receipt changed')
    a=json.loads((reference/'receipt.json').read_text()); b=json.loads((replay/'receipt.json').read_text())
    require(a.keys()==b.keys(),'receipt schema changed')
    for key in a:
        if key not in {'code_commit','files','pooled'}:
            require(a[key]==b[key],'receipt scope/decision changed: '+key)
    pooled=compare_pooled(a['pooled'],b['pooled'])
    specs={s['path']:s for s in b['files']}
    require(set(specs)=={s['path'] for s in a['files']},'evidence file set changed')
    reports=[]
    for s in a['files']:
        old,new=reference/s['path'],replay/s['path']; t=specs[s['path']]
        require(old.stat().st_size==s['bytes'] and sha(old)==s['sha256'],'original evidence changed')
        require(new.stat().st_size==t['bytes'] and sha(new)==t['sha256'],'replay file/receipt mismatch')
        identical=sha(new)==s['sha256']; changes=[]
        if not identical:
            require(s['path']=='measurement_summary.csv','nonquantile evidence bytes changed: '+s['path'])
            x=pd.read_csv(old,dtype=str,keep_default_na=False); y=pd.read_csv(new,dtype=str,keep_default_na=False)
            require(len(x)==132,'original summary groups changed')
            changes=compare_summary(x,y)
        reports.append({'path':s['path'],'byte_identical':identical,'quantile_cell_differences':changes})
    result={'status':'PASS_EXACT_DISCRETE_BOUNDED_QUANTILE_REPLAY_NOT_NEW_EVIDENCE',
            'original_reference_receipt_sha256':sha(reference/'receipt.json'),'replay_receipt_sha256':sha(replay/'receipt.json'),
            'quantile_absolute_tolerance':ATOL,'quantile_columns':sorted(QUANTILES),
            'all_other_fields_exact':True,'reference_overwritten':False,'pooled_quantile_differences':pooled,'files':reports}
    all_diffs=pooled+[c for report in reports for c in report['quantile_cell_differences']]
    result['max_absolute_quantile_difference']=max((r['absolute_difference'] for r in all_diffs),default=0.)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',type=Path,required=True); p.add_argument('--replay',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); verify(a.reference,a.replay,a.output)
