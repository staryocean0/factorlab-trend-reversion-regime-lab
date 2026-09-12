"""Read-only replay reconciliation: identities exact, floating differences audited."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

EXACT = {'entry_idx','info_idx','info_year','parent_direction','is_event','horizon','fit_cutoff_idx','exit_idx',
         'year','evaluation_year','cutoff_idx','max_train_label_idx','events_checked','n',
         'outside_training_range','outside_background_range','no_past_background_stratum','identities_equal'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compare_json(a,b,path='root'):
    if isinstance(a,dict):
        assert isinstance(b,dict) and set(a)==set(b),path
        for k in a: compare_json(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)): compare_json(x,y,f'{path}[{i}]')
    elif isinstance(a,float):
        assert np.isclose(a,b,rtol=1e-11,atol=1e-8), (path,a,b)
    else:
        assert type(a)==type(b) and a==b,(path,a,b)


def verify(reference:Path,replay:Path,output:Path):
    a=json.loads((reference/'receipt.json').read_text()); b=json.loads((replay/'receipt.json').read_text())
    for key in ('decision','baseline_commit','freeze_commit','freeze_sha256','sources','input_blobs',
                'original_events','training_population_rows','warmup_events','scored_event_horizon_rows',
                'successful_fit_count','horizon_review','prefix_identity_checks_pass','coverage_status_counts',
                'table_rows','post2020_price_files_read','ETF_price_files_read','new_matching','signal_refitted',
                'new_significance_test','horizon_selected','BLACKBOX_query_count','production_authority',
                'fresh_oos','confirmation_protocol_frozen','confirmation_clock_started'):
        compare_json(a[key],b[key],key)
    expected={x['path']:x for x in a['files']}; observed={x['path']:x for x in b['files']}
    assert set(expected)==set(observed)
    tables=[]
    for name,spec in expected.items():
        old,new=reference/name,replay/name
        assert sha(old)==spec['sha256'] and old.stat().st_size==spec['bytes'],name+' reference changed'
        assert sha(new)==observed[name]['sha256'] and new.stat().st_size==observed[name]['bytes'],name+' replay changed'
        x=pd.read_csv(old,dtype=str,keep_default_na=False); y=pd.read_csv(new,dtype=str,keep_default_na=False)
        assert x.shape==y.shape and list(x)==list(y),name
        column_diffs=[]
        for col in x:
            if col in EXACT or col.endswith('_n') or col.endswith('_idx'):
                assert x[col].equals(y[col]),(name,col)
                continue
            an=pd.to_numeric(x[col],errors='coerce'); bn=pd.to_numeric(y[col],errors='coerce')
            numeric=((x[col]=='')|an.notna()).all() and ((y[col]=='')|bn.notna()).all()
            if not numeric:
                assert x[col].equals(y[col]),(name,col)
                continue
            assert np.array_equal(an.isna(),bn.isna()),(name,col)
            mask=an.notna()
            assert np.allclose(an[mask],bn[mask],rtol=1e-11,atol=1e-8),(name,col)
            delta=float(np.max(np.abs(an[mask]-bn[mask]))) if mask.any() else 0.
            if delta: column_diffs.append({'column':col,'max_absolute_difference':delta})
        tables.append({'path':name,'rows':len(x),'byte_identical':sha(old)==sha(new),'continuous_differences':column_diffs})
    out={'status':'PASS_DETERMINISTIC_REPLAY_NOT_NEW_EVIDENCE','reference_receipt_sha256':sha(reference/'receipt.json'),
         'replay_receipt_sha256':sha(replay/'receipt.json'),'tables':tables,'original_evidence_overwritten':False}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',type=Path,required=True); p.add_argument('--replay',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); a=p.parse_args(); verify(a.reference,a.replay,a.output)
