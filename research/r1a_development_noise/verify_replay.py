"""Verify a fresh Development accounting replay, preserving original evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.r1a_development_noise.study import guard, require, sha

REFERENCE_BLOB = '2a92d3cafce7ceb1b970ef58ef7114024c367f4a'
ATOL, RTOL = 1e-8, 1e-10


def compare(a, b, path='root'):
    if isinstance(a, dict):
        require(isinstance(b, dict) and a.keys()==b.keys(), 'keys: '+path)
        for k in a:
            compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        require(isinstance(b,list) and len(a)==len(b),'list: '+path)
        for i,(x,y) in enumerate(zip(a,b)):
            compare(x,y,path+f'[{i}]')
    elif isinstance(a,float):
        require(isinstance(b,(int,float)) and not isinstance(b,bool) and np.isfinite([a,b]).all() and np.isclose(a,b,atol=ATOL,rtol=RTOL),'float: '+path)
    else:
        require(type(a) is type(b) and a==b,'exact: '+path)


def table(old:Path,new:Path) -> dict:
    dtype={'symbol':str,'calendar_year':str,'pair_id':str,'day':str}
    a=pd.read_csv(old,dtype=dtype); b=pd.read_csv(new,dtype=dtype)
    require(a.shape==b.shape and list(a.columns)==list(b.columns),'table structure: '+old.name)
    deltas={}
    for col in a:
        require(a[col].isna().equals(b[col].isna()),'missing mask: '+col)
        valid=a[col].notna()
        x,y=a.loc[valid,col],b.loc[valid,col]
        if pd.api.types.is_float_dtype(a[col]):
            require(pd.api.types.is_numeric_dtype(b[col]),'numeric schema: '+col)
            require(np.isfinite(x).all() and np.isfinite(y).all(),'nonfinite: '+col)
            require(np.allclose(x,y,atol=ATOL,rtol=RTOL),'numeric difference: '+col)
            deltas[col]=float(np.max(np.abs(x.to_numpy(float)-y.to_numpy(float)))) if len(x) else 0.
        else:
            require(x.equals(y),'discrete/text mismatch: '+col)
    return {'path':old.name,'rows':len(a),'columns':len(a.columns),'byte_identical':sha(old)==sha(new),
            'maximum_float_differences':deltas,'discrete_and_missing_masks_exact':True}


def audit(reference:Path,replay:Path) -> dict:
    guard(reference/'noise_receipt.json',REFERENCE_BLOB)
    a=json.loads((reference/'noise_receipt.json').read_text()); b=json.loads((replay/'noise_receipt.json').read_text())
    for k in ['decision','baseline_commit','freeze_commit','freeze_sha256','sources','cohorts','pooled_signed',
              'signed_clock_accounting','table_rows','post2020_price_files_read','ETF_price_files_read',
              'validation_pairs_modified','new_significance_tests','horizon_selected','causal_noise_components_identified',
              'BLACKBOX_query_count','production_authority','fresh_oos','confirmation_protocol_frozen','confirmation_clock_started']:
        compare(a[k],b[k],k)
    require([x['path'] for x in a['files']]==[x['path'] for x in b['files']],'file list drift')
    rows=[]
    for spec in a['files']:
        name=spec['path']; require(Path(name).name==name,'invalid evidence path')
        old=reference/name; new=replay/name
        require(sha(old)==spec['sha256'] and old.stat().st_size==spec['bytes'],'changed sealed reference')
        rows.append(table(old,new))
    return {'decision':'DEVELOPMENT_NOISE_REPLAY_VERIFIED_NOT_NEW_ALPHA',
            'reference_receipt_blob':REFERENCE_BLOB,'tables':rows,'float_atol':ATOL,'float_rtol':RTOL,
            'post2020_prices_read':False,'production_authority':False}


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--reference',type=Path,required=True); ap.add_argument('--replay',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); out=audit(args.reference,args.replay)
    args.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'decision':out['decision'],'tables':len(out['tables']),
                      'byte_identical_tables':sum(x['byte_identical'] for x in out['tables'])},indent=2))


if __name__=='__main__':
    main()
