"""Read-only retained impact regression, not another market experiment.

All scientific inputs remain current-byte exact. The one operational workflow
which must evolve is checked from its immutable baseline Git object, with the
current digest separately reported. No history or decisive result is replaced.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

EVIDENCE='docs/ops/evidence/etf_source_repair_20260912'
OVERLAY='docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json'
FREEZE='docs/governance/ETF_SOURCE_REPAIR_IMPACT_FREEZE@1.0.json'
BASE='ef18bf905e9e427153650d5538a996249bb6a901'
HISTORICAL_OPERATIONAL_INPUT='.github/workflows/etf-index-measurability.yml'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify(root: Path) -> dict:
    root=Path(root).resolve(); ev=root/EVIDENCE
    r=json.loads((ev/'receipt.json').read_text()); o=json.loads((root/OVERLAY).read_text())
    require(r['baseline_commit']==BASE,'baseline changed')
    require(digest(root/OVERLAY)==r['overlay_sha256'],'overlay changed')
    require(digest(root/FREEZE)==r['freeze_sha256'],'freeze changed')
    for s in r['files']:
        p=ev/s['path']; require(p.is_file() and p.stat().st_size==s['bytes'] and digest(p)==s['sha256'],'evidence changed '+s['path'])
    pins=pd.read_csv(ev/'pinned_input_integrity.csv'); operational=[]
    for s in pins.itertuples(index=False):
        p=root/s.path
        require(p.is_file() and not p.is_symlink(),'baseline input missing '+s.path)
        if s.path==HISTORICAL_OPERATIONAL_INPUT:
            raw=subprocess.check_output(['git','show',BASE+':'+s.path],cwd=root)
            operational.append({'path':s.path,'historical_commit':BASE,'historical_sha256':hashlib.sha256(raw).hexdigest(),'current_sha256':digest(p),'role':'operational workflow, not numerical/source input'})
        else:
            raw=p.read_bytes()
        require(len(raw)==s.bytes and hashlib.sha256(raw).hexdigest()==s.sha256,'baseline input changed '+s.path)
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob==s.git_blob_sha1,'baseline git identity changed '+s.path)
    require(len(operational)==1,'historical operational input not verified')
    w=pd.read_csv(ev/'endpoint_window_audit.csv',float_precision='round_trip')
    require(len(w)==21686 and not w.duplicated(['pair_id','horizon']).any(),'endpoint denominator/identity')
    require(set(w.horizon)=={1,5,15,30,60,120,240},'horizon changed')
    expected=np.zeros(len(w),bool)
    for carrier,spec in o['carriers'].items():
        for action in spec['known_effective_actions']:
            for leg in ('event','control'):
                en=w[leg+'_entry_timestamp'].str[:10]; ex=w[leg+'_exit_timestamp'].str[:10]
                expected |= w.carrier.eq(carrier).to_numpy() & (en<action['effective_date']).to_numpy() & (ex>=action['effective_date']).to_numpy()
    require(np.array_equal(w.new_eligible.to_numpy(),w.old_eligible.to_numpy() & ~expected),'incorrect revised eligibility')
    require(not w.membership_changed.any() and not (w.old_eligible!=w.new_eligible).any(),'unexpected changed cohort')
    require(int(w.new_action_crossing.sum())==3 and w.loc[w.new_action_crossing,'pair_id'].nunique()==2,'new action boundary counts')
    require(not w.loc[w.new_action_crossing,'old_eligible'].any(),'action crossed published cohort')
    require(not w.unit_bridge_crossing.any(),'unexpected pre/post resumed price bridge')
    require(int(w.reason_changed.sum())==3,'reason-only changes differ')
    x=pd.read_csv(ev/'published_result_impact.csv',float_precision='round_trip')
    require(len(x)==112 and x.old_n.equals(x.new_n),'published group denominator changed')
    delta=x.filter(like='_mean_change_bp').to_numpy(float)
    require(np.isfinite(delta).all() and (delta==0).all(),'published mean changed')
    full=pd.read_csv(ev/'full_path_impact_summary.csv')
    require(not full.membership_changed.any(),'full path membership changed')
    require(full.old_complete_paths.tolist()==[846,1791] and full.new_complete_paths.tolist()==[846,1791],'full path counts')
    require(full.full_path_originally_measured.tolist()==[False,True],'blocked primary outcomes opened')
    require(full.common_gate_after_known_patch.tolist()==[False,True],'common-cohort admission changed')
    m=pd.read_csv(ev/'intraday_measurement_impact.csv')
    require(len(m)==132 and (m.eligible_difference==0).all() and (m.max_preserved_gap_absolute_difference==0).all(),'intraday measurement changed')
    pooled=m.loc[m.period=='ALL']
    require(pooled.old_eligible.tolist()==[281354,288418],'intraday denominator changed')
    require(pooled.new_action_exclusions.tolist()==[476,0],'action reason accounting changed')
    d=pd.read_csv(ev/'calendar_boundary_audit.csv')
    aug=d.loc[(d.carrier=='512100.SH')&(d.day=='2022-08-03')].iloc[0]
    sep=d.loc[(d.carrier=='512100.SH')&(d.day=='2022-09-02')].iloc[0]
    require(aug.present_etf_labels==240 and not aug.confirmed_halt and not aug.confirmed_effective_action,'cancelled proposal incorrectly applied')
    require(sep.present_etf_labels==0 and sep.confirmed_halt,'suspension not retained')
    require(o['complete_corporate_action_calendar_certified'] is False and o['microstructure_source_admitted'] is False,'false full-source admission')
    data=root/'data/etf_source_actions_v2'; spec=json.loads((data/'manifest.json').read_text())
    require(spec['full_source_qualification_complete'] is False,'v2 falsely claims admission')
    require(spec['overlay_sha256']==r['overlay_sha256'],'v2 overlay link drift')
    for s in spec['known_action_files']:
        p=root/s['path']; require(p.stat().st_size==s['bytes'] and digest(p)==s['sha256'],'v2 action bytes differ')
        require(len(pd.read_csv(p))==s['rows'],'v2 action rows differ')
    require(r['new_model_fits']==0 and r['new_return_population_opened'] is False and r['original_source_bytes_modified'] is False,'scope breach')
    return {'status':'RETAINED_EVIDENCE_AND_BASELINE_INPUT_REGRESSION_PASS','pinned_inputs':len(pins),'current_scientific_and_other_inputs_exact':len(pins)-len(operational),'operational_inputs_verified_at_baseline':operational,'endpoint_windows':len(w),'published_groups':len(x),'intraday_groups':len(m),'new_model_fits':0,'new_market_experiment':False,'full_source_qualification_complete':False}


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); ap.add_argument('--output',type=Path)
    a=ap.parse_args(); result=verify(a.root)
    if a.output: a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
