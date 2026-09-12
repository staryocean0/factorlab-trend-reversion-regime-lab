"""Bounded public-repository data-role inventory. NEVER load candidate prices.

A new filename/year is not an unseen-sample certificate. This audit cannot
establish private/local/cognitive exposure or accept a confirmation data role.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

REPOS=('factorlab-trend-reversion-regime-lab','factorlab-star50-filter-lab',
       'factorlab-two-wave-strategy-lab','factorlab-overnight-open-lab',
       'factorlab-multifactor-stock-lab')
SAFE_KEYS={'path','symbol','symbols','frequency','year','first_day','last_day','start_date',
           'end_date','date_min','date_max','min_day','max_day','role','data_role','usage_role',
           'source','provider','consumed','is_holdout','fresh_oos','start','end','source_id',
           'window','period','dataset_version','schema','schema_id','holdout','quarantine',
           'first_timestamp','last_timestamp','2026_included','new_source_identity'}
TARGETS=('000852','000688','512100','588000')
OUTCOME_KEYS=re.compile(r'(?i)(pnl|profit|sharpe|return|performance|outcome|summary|metrics|results|events)')


def metadata_path(path: str, size: int) -> bool:
    return (size<=500000 and path.endswith('.json') and
            (path.startswith('data/') or path.startswith('docs/governance/')) and
            bool(re.search(r'(?i)(manifest|data.?role|usage|quarantine|holdout|data.?split|data.?access)',Path(path).name)) and
            not bool(OUTCOME_KEYS.search(Path(path).name)))


def select_metadata(obj, context: str='root') -> list[dict]:
    """Keep identity/window/role scalars; strip outcome subtrees and all raw values."""
    out=[]
    if isinstance(obj,dict):
        item={'json_location':context}
        for k,v in obj.items():
            if k in SAFE_KEYS and not isinstance(v,dict) and (not isinstance(v,list) or all(isinstance(z,(str,int,bool,float)) or z is None for z in v)):
                item[k]=v
        if len(item)>1: out.append(item)
        for k,v in obj.items():
            if isinstance(v,(dict,list)) and not OUTCOME_KEYS.search(k):
                out.extend(select_metadata(v,context+'.'+k))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            if isinstance(v,(dict,list)): out.extend(select_metadata(v,context+f'[{i}]'))
    return out


def get_json(url: str, max_bytes: int=12000000):
    if not url.startswith('https://api.github.com/repos/staryocean0/'):
        raise ValueError('outside approved public repository API scope')
    headers={'User-Agent':'FactorLab-confirmation-metadata-audit','Accept':'application/vnd.github+json'}
    token=os.environ.get('GITHUB_TOKEN')
    if token: headers['Authorization']='Bearer '+token
    with urlopen(Request(url,headers=headers),timeout=25) as response:
        raw=response.read(max_bytes+1)
        if len(raw)>max_bytes: raise ValueError('metadata response byte budget exceeded')
        return json.loads(raw),hashlib.sha256(raw).hexdigest()


def audit_repo(repo: str) -> dict:
    base='https://api.github.com/repos/staryocean0/'+repo
    info={'repository':'staryocean0/'+repo,'candidate_price_bytes_read':False,
          'candidate_strategy_outcomes_read':False,'fresh_role':'UNKNOWN_NOT_ADMITTED'}
    try:
        tree,tree_hash=get_json(base+'/git/trees/main?recursive=1')
        blobs=[x for x in tree.get('tree',[]) if x['type']=='blob' and x.get('mode')!='120000']
        candidates=[{'path':x['path'],'git_blob_sha1':x['sha'],'bytes':x.get('size'),
                     'target_named':any(s in x['path'] for s in TARGETS)}
                    for x in blobs if x['path'].startswith('data/') and '2026' in x['path'] and
                    re.search(r'\.(csv|parquet|feather|zip|gz)$',x['path'],re.I)]
        eligible=[x for x in blobs if metadata_path(x['path'],x.get('size',0))]
        # Fixed ordering: root manifest, 2026/role declarations, other manifests.
        eligible.sort(key=lambda x:(0 if x['path']=='data/manifest.json' else 1 if re.search(r'2026|role|usage|holdout|quarantine',x['path'],re.I) else 2,x['path']))
        picked=eligible[:12]
        info.update({'tree_sha':tree.get('sha'),'tree_response_sha256':tree_hash,
                     'tree_truncated':bool(tree.get('truncated')),'data_file_count':sum(x['path'].startswith('data/') for x in blobs),
                     '2026_named_price_candidates':candidates,'metadata_candidate_count':len(eligible),
                     'metadata_read_limit':12,'metadata_limit_hit':len(eligible)>12,'metadata_files':[]})
        for x in picked:
            record={'path':x['path'],'git_blob_sha1':x['sha'],'bytes':x.get('size')}
            try:
                blob,_=get_json(base+'/git/blobs/'+x['sha'],max_bytes=1000000)
                if blob.get('encoding')!='base64': raise ValueError('unexpected metadata encoding')
                raw=base64.b64decode(blob['content'])
                actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                if actual!=x['sha']: raise ValueError('metadata Git blob mismatch')
                safe=select_metadata(json.loads(raw))
                record.update({'status':'METADATA_ONLY_READ','sha256':hashlib.sha256(raw).hexdigest(),
                               'safe_metadata':safe})
            except Exception as exc:
                record.update({'status':'METADATA_UNAVAILABLE','error_type':type(exc).__name__})
            info['metadata_files'].append(record)
        branches,bhash=get_json(base+'/branches?per_page=100')
        info['branch_names_inspected_only']=[b['name'] for b in branches]
        info['branch_list_first_page_limit_hit']=len(branches)==100
        info['branch_response_sha256']=bhash
        info['status']='BOUNDED_METADATA_INVENTORY_COMPLETED'
    except Exception as exc:
        info.update({'status':'INVENTORY_UNAVAILABLE','error_type':type(exc).__name__})
    return info


def audit(root: Path,output: Path) -> dict:
    if output.exists(): raise ValueError('new audit output directory required')
    output.mkdir(parents=True)
    local=root/'data/manifest.json'; local_raw=local.read_bytes()
    with ThreadPoolExecutor(max_workers=3) as pool:
        repos=list(pool.map(audit_repo,REPOS))
    local_items=select_metadata(json.loads(local_raw))
    candidates=[]
    for repo in repos:
        for x in repo.get('2026_named_price_candidates',[]):
            candidates.append({'repository':repo['repository'],**x})
    receipt={'schema_id':'factorlab_r1a_confirmation_data_role_audit@1.0',
             'observed_at_utc':datetime.now(timezone.utc).isoformat(),
             'decision':'NO_QUALIFIED_CONFIRMATION_PACKAGE_ESTABLISHED_BY_BOUNDED_AUDIT',
             'current_manifest_sha256':hashlib.sha256(local_raw).hexdigest(),
             'current_manifest_metadata':local_items,'repositories':repos,
             '2026_candidate_price_path_count':len(candidates),'2026_candidate_paths':candidates,
             '2026_role':'UNKNOWN_NOT_ADMITTED','qualified_confirmation_packages':[],
             'prospective_design':'A later final confirmation freeze and explicit data admission are required. This audit does not start a prospective clock.',
             'reason':'Metadata availability is not a complete exposure history. No sufficient frozen-unused/source-admitted primary index+ETF package is established here. Local/private usage and uninspected branches/artifacts remain outside scope.',
             'existing_history':'2015-2025 previously consumed; may estimate nuisance/noise, not relabeled fresh.',
             'candidate_price_bytes_read':False,'candidate_strategy_outcomes_read':False,
             'general_data_absence_claimed':False,'confirmation_protocol_frozen':False,
             'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False}
    (output/'data_role_audit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Confirmation data-role audit — metadata only','',
           '`NO_QUALIFIED_CONFIRMATION_PACKAGE_ESTABLISHED_BY_BOUNDED_AUDIT`','',
           'No 2026 price or strategy-outcome files were read. A filename/date is not a holdout certificate. This is a bounded metadata inventory, not proof that no data exists anywhere.','',
           '| Repository | Inventory status | 2026-named price paths | Metadata reads / candidates |',
           '|---|---|---:|---:|']
    for r in repos:
        lines.append(f"| {r['repository']} | {r['status']} | {len(r.get('2026_named_price_candidates',[]))} | {len(r.get('metadata_files',[]))}/{r.get('metadata_candidate_count',0)} |")
    lines+=['','All tree/blob hashes, inspected branches (names only), metadata path limits and safe role/window records are preserved in data_role_audit.json.',
            '', '2026 role remains UNKNOWN_NOT_ADMITTED. Another repository\'s use does not automatically prove contamination of R1_A, but neither a different repository nor absence of a usage log certifies non-exposure. A paired source package and an exposure declaration must be reviewed before any confirmation outcomes are read.',
            '', 'Future observations can be prospective only relative to the later finalized design. No confirmation clock, live collection or automation was started. No additional transfer of the already delivered 2021-2025 pack is requested.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'decision':receipt['decision'],'candidate_paths':len(candidates),'repositories':[{k:r[k] for k in ('repository','status','fresh_role')} for r in repos]},indent=2))
    return receipt


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); audit(args.root.resolve(),args.output)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
