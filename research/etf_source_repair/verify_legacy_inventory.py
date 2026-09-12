"""Separate evolving Git path metadata from frozen numerical measurement evidence.

Do not ignore an inventory difference: independently reconstruct BOTH path lists
from their receipts' immutable code commits. Preserve every old artifact/hash.
Numerical checks reuse the original exact/discrete and 1e-10 quantile rules.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path
import pandas as pd
from research.etf_index_measurability.verify_replay import (
    require, sha, compare_summary, compare_pooled, REFERENCE_RECEIPT_SHA, ATOL, QUANTILES,
)


def inventory_for_paths(paths):
    return {'data_paths':len(paths),
        'candidate_names_only':[p for p in paths if re.search(r'(?:iopv|nav|pcf|constituent|basket|bid|ask|quote|snapshot)',p,re.I)],
        'unrelated_file_contents_read':False,
        'limitation':'Path-name inventory does not exhaust unlabeled files or other repositories. MO quote names are not ETF quotes.'}


def check_inventory(observed, paths):
    require(observed==inventory_for_paths(paths),'inventory does not match its declared Git commit')


def tree_paths(root, commit):
    require(re.fullmatch(r'[0-9a-f]{40}',commit) is not None,'not an immutable commit')
    return subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','data'],cwd=root,text=True).splitlines()


def verify(root, reference, replay, output):
    root=Path(root).resolve(); reference=Path(reference); replay=Path(replay); output=Path(output)
    require(reference.resolve()!=replay.resolve() and not output.exists(),'fresh replay and audit output required')
    require(sha(reference/'receipt.json')==REFERENCE_RECEIPT_SHA,'original receipt modified')
    a=json.loads((reference/'receipt.json').read_text()); b=json.loads((replay/'receipt.json').read_text())
    require(a.keys()==b.keys(),'receipt schema changed')
    for key in a:
        if key not in {'code_commit','files','pooled'}:
            require(a[key]==b[key],'scope/decision changed '+key)
    pooled=compare_pooled(a['pooled'],b['pooled'])
    specs={s['path']:s for s in b['files']}
    require(set(specs)=={s['path'] for s in a['files']},'evidence file set changed')
    reports=[]; inventory_check=None
    for s in a['files']:
        old=reference/s['path']; new=replay/s['path']; t=specs[s['path']]
        require(old.stat().st_size==s['bytes'] and sha(old)==s['sha256'],'reference evidence changed')
        require(new.stat().st_size==t['bytes'] and sha(new)==t['sha256'],'replay receipt mismatch')
        identical=sha(new)==s['sha256']; changes=[]
        if s['path']=='data_path_inventory.json':
            old_paths=tree_paths(root,a['code_commit']); new_paths=tree_paths(root,b['code_commit'])
            check_inventory(json.loads(old.read_text()),old_paths)
            check_inventory(json.loads(new.read_text()),new_paths)
            inventory_check={'reference_commit':a['code_commit'],'replay_commit':b['code_commit'],
                'reference_data_paths':len(old_paths),'replay_data_paths':len(new_paths),
                'added_paths':sorted(set(new_paths)-set(old_paths)),
                'removed_paths':sorted(set(old_paths)-set(new_paths)),
                'both_inventories_independently_match_git':True,
                'inventory_is_filename_metadata_not_a_measurement_input':True}
        elif not identical:
            require(s['path']=='measurement_summary.csv','non-numerical evidence changed '+s['path'])
            x=pd.read_csv(old,dtype=str,keep_default_na=False); y=pd.read_csv(new,dtype=str,keep_default_na=False)
            require(len(x)==132,'group count changed'); changes=compare_summary(x,y)
        reports.append({'path':s['path'],'byte_identical':identical,'quantile_cell_differences':changes})
    require(inventory_check is not None,'inventory was not checked')
    result={'status':'EXACT_SCIENTIFIC_REPLAY_AND_COMMIT_SCOPED_INVENTORY_PASS',
        'reference_receipt_sha256':sha(reference/'receipt.json'),'replay_receipt_sha256':sha(replay/'receipt.json'),
        'quantile_absolute_tolerance':ATOL,'quantile_columns':sorted(QUANTILES),
        'all_discrete_measurements_and_scope_flags_exact':True,'original_evidence_overwritten':False,
        'inventory':inventory_check,'pooled_quantile_differences':pooled,'files':reports,
        'new_reversion_outcomes_opened':False}
    result['max_absolute_quantile_difference']=max([0.]+[x['absolute_difference'] for x in pooled]+[x['absolute_difference'] for f in reports for x in f['quantile_cell_differences']])
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--reference',type=Path,required=True); p.add_argument('--replay',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); verify(a.root,a.reference,a.replay,a.output)
