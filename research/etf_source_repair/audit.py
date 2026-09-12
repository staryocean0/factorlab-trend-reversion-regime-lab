"""Versioned source correction; inspect original windows, never open a new strategy.

All legacy files read are checked against the baseline Git tree. Raw prices are
unchanged. Only existing published return rows may be reaggregated after applying
the ORIGINAL action exclusion; previously blocked outcome populations stay shut.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

BASE = 'ef18bf905e9e427153650d5538a996249bb6a901'
FREEZE = 'docs/governance/ETF_SOURCE_REPAIR_IMPACT_FREEZE@1.0.json'
OVERLAY = 'docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json'
PACK = 'data/r1a_carrier_prices/cloud_pack_v1'
EV = 'docs/ops/evidence'
EP = EV + '/r1a_endpoint_diagnostic_20260912'
FP = EV + '/r1a_carrier_transport_20260912_local'
H = (1,5,15,30,60,120,240)
MAP = {'000852.SH':'512100.SH','000688.SH':'588000.SH'}
COUNTS = {'000852.SH':1296,'000688.SH':1802}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


class Pinned:
    def __init__(self, root):
        self.root = Path(root).resolve()
        raw = subprocess.check_output(['git','ls-tree','-rz',BASE], cwd=self.root).decode()
        self.tree = {}
        for item in raw.split('\0'):
            if item:
                meta, name = item.split('\t',1)
                mode, kind, blob = meta.split()
                if kind == 'blob':
                    self.tree[name] = blob
        self.used = {}

    def file(self, rel):
        rel = str(rel); p = (self.root/rel).resolve()
        require(p.is_relative_to(self.root) and not (self.root/rel).is_symlink(), 'unsafe source path')
        require(rel in self.tree and p.is_file(), 'missing baseline input '+rel)
        raw = p.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == self.tree[rel], 'baseline input drift '+rel)
        self.used[rel] = {'path':rel,'git_blob_sha1':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        return p

    def json(self, rel):
        return json.loads(self.file(rel).read_text(encoding='utf-8'))

    def csv(self, rel):
        return pd.read_csv(self.file(rel))


def effective_actions(overlay, carrier):
    rows = overlay['carriers'][carrier]['known_effective_actions']
    require(all(r['status']=='CONFIRMED_ACTION' for r in rows),'unconfirmed action applied')
    dates = [r['effective_date'] for r in rows]
    require(len(dates)==len(set(dates)), 'duplicate effective dates')
    for d in dates:
        require('2021-01-01' <= d <= '2025-12-31','action outside audit window')
        require(pd.Timestamp(d).strftime('%Y-%m-%d')==d,'bad action date')
    return sorted(dates)


def crossing(entry, exit_, day):
    return (np.asarray(entry,dtype=str) < day) & (np.asarray(exit_,dtype=str) >= day)


def window_audit(old, new, actions):
    keys=['pair_id','horizon']
    require(not old.duplicated(keys).any() and not new.duplicated(keys).any(),'duplicate audit identity')
    pd.testing.assert_frame_equal(old[keys].reset_index(drop=True),new[keys].reset_index(drop=True))
    require(not (new.eligible & ~old.eligible).any(),'added action cannot create new sample')
    out=old.copy().rename(columns={'eligible':'old_eligible','reason':'old_reason'})
    out['new_eligible']=new.eligible.to_numpy()
    out['new_reason']=new.reason.to_numpy()
    out['membership_changed']=out.old_eligible != out.new_eligible
    out['reason_changed']=out.old_reason != out.new_reason
    out['new_action_crossing']=False
    out['unit_bridge_crossing']=False
    out['on_new_halt_endpoint']=False
    for a in actions:
        day=a['effective_date']; resume=a.get('first_resumed_trading_date')
        for leg in ('event','control'):
            en=out[leg+'_entry_timestamp'].str[:10]
            ex=out[leg+'_exit_timestamp'].str[:10]
            out['new_action_crossing'] |= crossing(en,ex,day)
            if resume:
                out['unit_bridge_crossing'] |= (en < day) & (ex >= resume)
                out['on_new_halt_endpoint'] |= ((en>=day)&(en<resume)) | ((ex>=day)&(ex<resume))
    return out


def read_index(pin, manifest, symbol):
    earlier=[s for s in manifest['files'] if s['symbol']==symbol and s['frequency']=='1m' and s['year']<2021]
    offset=sum(s['rows'] for s in earlier)
    specs=sorted([s for s in manifest['files'] if s['symbol']==symbol and s['frequency']=='1m' and 2021<=s['year']<=2025],key=lambda s:s['year'])
    require(len(specs)==5,'five index partitions required')
    frames=[]
    for s in specs:
        p=pin.file(s['path']); require(sha(p)==s['sha256'] and p.stat().st_size==s['bytes'],'index source mismatch')
        f=pd.read_parquet(p)
        require(len(f)==s['rows'] and f.symbol.eq(symbol).all(),'index count/symbol mismatch')
        frames.append(f)
    f=pd.concat(frames,ignore_index=True)
    f.index=pd.DatetimeIndex(pd.to_datetime(f.timestamp.astype(str).str[:19])).tz_localize('Asia/Shanghai')
    require(f.index.is_monotonic_increasing and not f.index.has_duplicates,'index clock order')
    require(f.index.strftime('%Y-%m-%d').tolist()==f.trading_day.astype(str).tolist(),'index day-label mismatch')
    require(f.index.year.min()==2021 and f.index.year.max()==2025,'index window leaked')
    return f,offset


def read_etf(pin, carrier):
    from research.r1a_carrier_transport.transport import validate_prices
    m=pin.json(PACK+'/'+carrier+'.json'); frames=[]
    for s in m['files']:
        p=pin.file(s['path'])
        require(sha(p)==s['sha256'] and p.stat().st_size==s['bytes'],'ETF source mismatch')
        f=pd.read_csv(p); require(len(f)==s['rows'],'ETF row mismatch'); frames.append(f)
    s=m['corporate_actions_file']; p=pin.file(s['path'])
    require(sha(p)==s['sha256'] and p.stat().st_size==s['bytes'],'old action identity mismatch')
    a=pd.read_csv(p); require(len(a)==s['rows'],'old action rows')
    # The old completeness boolean is NOT accepted as fresh source certification.
    return validate_prices(pd.concat(frames,ignore_index=True),carrier), sorted(a.ex_date.astype(str).tolist()), m


def group_masks(frame):
    yield 'ALL',np.ones(len(frame),bool)
    for y in range(2021,2026): yield str(y),frame.event_day.astype(str).str.startswith(str(y)).to_numpy()
    for s in ('LONG','SHORT'): yield s,frame.side.eq(s).to_numpy()


def published_impact(pin, availability, carrier, result_rows, output):
    from research.r1a_carrier_transport.endpoint_diagnostic import coverage_gate
    path=EP+'/'+carrier+'_endpoint_returns.csv'
    ledger=pin.csv(path)
    require(not ledger.duplicated(['pair_id','horizon']).any(),'duplicate published returns')
    cols=['etf_event','etf_control','etf_incremental']
    require(np.isfinite(ledger[cols]).all().all(),'nonfinite published return')
    require(np.allclose(ledger.etf_event-ledger.etf_control,ledger.etf_incremental,atol=1e-12,rtol=0),'published return identity')
    changed=[]
    for h in H:
        a=availability.loc[availability.horizon==h]
        old_ids=set(a.loc[a.old_eligible,'pair_id']); new_ids=set(a.loc[a.new_eligible,'pair_id'])
        old=ledger.loc[ledger.horizon==h]
        require(set(old.pair_id)==old_ids,'published cohort mismatch')
        gate_input=a[['pair_id','event_day','new_eligible']].rename(columns={'new_eligible':'eligible'})
        gate=coverage_gate(gate_input)
        new=old.loc[old.pair_id.isin(new_ids)]
        if new_ids!=old_ids:
            changed.append(new)
        for group,mask in group_masks(old):
            o=old.loc[mask]
            n=new.loc[new.pair_id.isin(o.pair_id)]
            row={'carrier':carrier,'study':'published_endpoint','horizon':h,'group':group,'old_n':len(o),'new_n':len(n),'gate_pass_after_known_patch':bool(gate['pass']),'membership_changed':len(o)!=len(n)}
            for col in cols:
                before=float(o[col].mean()*1e4) if len(o) else None
                after=float(n[col].mean()*1e4) if len(n) and gate['pass'] else None
                row[col+'_old_mean_bp']=before; row[col+'_new_mean_bp']=after
                row[col+'_mean_change_bp']=after-before if after is not None and before is not None else None
            result_rows.append(row)
    if changed:
        # Only reaggregation of ALREADY published rows; no missing/new return created.
        pd.concat(changed).to_csv(output/(carrier+'_changed_published_rows.csv'),index=False)
    return len(ledger)


def consumer_inventory(pin, output):
    tokens=('cloud_pack_v1','r1a_carrier_prices','endpoint_diagnostic','r1a_endpoint_diagnostic_20260912','etf_index_measurability')
    rows=[]
    for rel in sorted(pin.tree):
        if not rel.startswith(('research/','src/','scripts/','tests/','.github/')) or not rel.endswith(('.py','.yml','.yaml','.sh')):
            continue
        p=pin.root/rel
        if not p.is_file(): continue
        text=pin.file(rel).read_text(encoding='utf-8')
        for number,line in enumerate(text.splitlines(),1):
            hits=[t for t in tokens if t in line]
            if hits:
                rows.append({'path':rel,'line':number,'matched_tokens':';'.join(hits),'text':line.strip()[:500], 'scope':'textual_dependency_candidate_not_runtime_proof'})
    pd.DataFrame(rows,columns=['path','line','matched_tokens','text','scope']).to_csv(output/'consumer_reference_inventory.csv',index=False)
    return len(rows)


def run(root, output):
    from research.r1a_carrier_transport import endpoint_diagnostic as ep
    from research.r1a_carrier_transport import transport as tr
    from research.etf_index_measurability import audit as meas
    root=Path(root).resolve(); output=Path(output)
    require(not output.exists(),'new output directory required')
    pin=Pinned(root)
    for path in ('research/r1a_carrier_transport/transport.py','research/r1a_carrier_transport/endpoint_diagnostic.py','research/etf_index_measurability/audit.py'):
        pin.file(path)
    freeze=json.loads((root/FREEZE).read_text()); overlay=json.loads((root/OVERLAY).read_text())
    require(freeze['baseline_commit']==BASE and freeze['scope']['horizons']==list(H),'freeze scope drift')
    require(overlay['baseline_commit']==BASE and not overlay['complete_corporate_action_calendar_certified'] and not overlay['microstructure_source_admitted'],'false source promotion')
    manifest=pin.json('data/manifest.json')
    pairs=pin.csv(tr.PAIRS_PATH); pairs=pairs.loc[pairs.cell=='R1_A'].copy()
    pairs['pair_id']=pairs.symbol.astype(str)+':R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
    require(not pairs.pair_id.duplicated().any(),'original pair identity duplicate')
    local_receipt=pin.json(FP+'/transport_receipt.json')
    old_meas=pin.csv(EV+'/etf_index_measurability_20260912/measurement_summary.csv')
    output.mkdir(parents=True)
    summaries=[]; result_rows=[]; full_rows=[]; intraday_rows=[]; boundary_rows=[]; all_windows=[]; source_state=[]
    published_rows=0
    for symbol,carrier in MAP.items():
        index,offset=read_index(pin,manifest,symbol)
        tape,old_dates,m=read_etf(pin,carrier)
        new_dates=effective_actions(overlay,carrier)
        require(set(old_dates).issubset(new_dates),'old known event removed')
        new_actions=[a for a in overlay['carriers'][carrier]['known_effective_actions'] if a['effective_date'] not in old_dates]
        block=pairs.loc[pairs.symbol==symbol].copy(); require(len(block)==COUNTS[symbol],'pair count drift')
        for col in ('event_entry_idx','control_entry_idx'): block[col]=block[col]-offset
        old,_=ep.endpoint_availability(block,index.index,tape,old_dates)
        new,_=ep.endpoint_availability(block,index.index,tape,new_dates)
        saved=pin.csv(EP+'/'+carrier+'_endpoint_availability.csv')
        pd.testing.assert_frame_equal(old.reset_index(drop=True),saved.reset_index(drop=True),check_dtype=False,check_exact=True)
        windows=window_audit(old,new,new_actions); windows['carrier']=carrier; all_windows.append(windows)
        published_rows+=published_impact(pin,windows,carrier,result_rows,output)
        for h in H:
            w=windows.loc[windows.horizon==h]
            summaries.append({'carrier':carrier,'horizon':h,'original_pairs':len(w),'old_eligible':int(w.old_eligible.sum()),'new_eligible':int(w.new_eligible.sum()),'membership_changed':int(w.membership_changed.sum()),'reason_changed':int(w.reason_changed.sum()),'new_action_crossing':int(w.new_action_crossing.sum()),'crossing_previously_included':int((w.new_action_crossing&w.old_eligible).sum()),'unit_bridge_crossing':int(w.unit_bridge_crossing.sum()),'halt_endpoint':int(w.on_new_halt_endpoint.sum())})
        of,_,oc=tr.common_pairs(block,index.index,tape,old_dates)
        nf,_,nc=tr.common_pairs(block,index.index,tape,new_dates)
        if carrier=='588000.SH':
            pd.testing.assert_frame_equal(of,pin.csv(FP+'/'+carrier+'_coverage.csv'),check_dtype=False,check_exact=True)
            fl=pin.csv(FP+'/'+carrier+'_transport.csv')
            require(set(fl.pair_id)==set(of.loc[of.eligible,'pair_id']),'published full-path sample differs')
            require(of.eligible.equals(nf.eligible),'changed secondary full-path requires separate reaggregation')
            published_rows+=len(fl)
        common_old=old.groupby('pair_id',sort=True).eligible.all()
        common_new=new.groupby('pair_id',sort=True).eligible.all()
        cf=block[['pair_id','event_day']].copy(); cf['eligible']=cf.pair_id.map(common_new)
        cg=ep.coverage_gate(cf)
        if carrier=='588000.SH':
            cl=pin.csv(EP+'/'+carrier+'_common_endpoint_returns.csv')
            require(set(cl.pair_id)==set(common_old.index[common_old]),'published common sample differs')
            require(common_old.equals(common_new),'changed common secondary requires reaggregation')
            published_rows+=len(cl)
        full_rows.append({'carrier':carrier,'original_pairs':len(block),'old_complete_paths':int(of.eligible.sum()),'new_complete_paths':int(nf.eligible.sum()),'membership_changed':int((of.eligible!=nf.eligible).sum()),'reason_changed':int((of.reason!=nf.reason).sum()),'full_path_originally_measured':bool(local_receipt['carriers'][carrier]['ETF_outcomes_read']),'old_path_gate':oc['minimum_coverage_pass'],'new_path_gate':nc['minimum_coverage_pass'],'old_all_horizon_endpoint_common':int(common_old.sum()),'new_all_horizon_endpoint_common':int(common_new.sum()),'common_gate_after_known_patch':bool(cg['pass'])})
        fa=of.rename(columns={'eligible':'old_eligible','reason':'old_reason'}).copy(); fa['new_eligible']=nf.eligible; fa['new_reason']=nf.reason
        fa.to_csv(output/(carrier+'_full_path_audit.csv'),index=False)
        obs0=meas.observations(index,tape,old_dates); obs1=meas.observations(index,tape,new_dates)
        for period in ['ALL']+[str(y) for y in range(2021,2026)]+sorted(set(index.index.strftime('%Y-%m'))):
            mask=np.ones(len(index),bool) if period=='ALL' else np.asarray(index.index.strftime('%Y-%m-%d').str.startswith(period))
            s0=meas.summarize(obs0.loc[mask],carrier,symbol,period); s1=meas.summarize(obs1.loc[mask],carrier,symbol,period)
            prior=old_meas.loc[(old_meas.carrier==carrier)&(old_meas.period.astype(str)==period)]
            require(len(prior)==1 and int(prior.eligible_comparisons.iloc[0])==s0['eligible_comparisons'],'old minute comparator count drift')
            intraday_rows.append({'carrier':carrier,'period':period,'old_eligible':s0['eligible_comparisons'],'new_eligible':s1['eligible_comparisons'],'eligible_difference':s1['eligible_comparisons']-s0['eligible_comparisons'],'old_action_exclusions':s0['declared_action_day_comparisons'],'new_action_exclusions':s1['declared_action_day_comparisons'],'old_missing_endpoint_exclusions':s0['etf_endpoint_unavailable_comparisons'],'new_missing_endpoint_exclusions':s1['etf_endpoint_unavailable_comparisons'],'max_preserved_gap_absolute_difference':float(np.nanmax(np.abs(obs1.loc[mask,'gap_abs_bp'].to_numpy()-obs0.loc[mask,'gap_abs_bp'].to_numpy())))})
        for day in ('2022-08-02','2022-08-03','2022-08-04','2022-09-01','2022-09-02','2022-09-05','2025-01-14','2025-01-15'):
            t=index.index[index.index.strftime('%Y-%m-%d')==day]; aligned=tape.reindex(t); present=t.isin(tape.index)
            boundary_rows.append({'carrier':carrier,'day':day,'expected_index_labels':len(t),'present_etf_labels':int(present.sum()),'zero_volume':int((aligned.volume==0).sum()),'positive_volume':int((aligned.volume>0).sum()),'confirmed_effective_action':day in new_dates,'confirmed_halt':any(a['start_date']<=day<=a['end_date'] for a in overlay['carriers'][carrier]['known_suspensions']),'prices_reported':False})
        source_state.append({'carrier':carrier,'index':symbol,'old_completeness_boolean':m.get('corporate_actions_complete'),'effective_known_action_dates':new_dates,'global_completeness_certified':False,'on_clock_zero_nonflat':int(obs0.zero_nonflat_bar.sum()),'index_flat_fill_rows':int(index.causal_flat_fill.astype(bool).sum()) if 'causal_flat_fill' in index else None,'index_available_at_examples':sorted(set(index.available_at.astype(str).str[11:19])) if 'available_at' in index else []})
        refs={s['source_id']:s['url'] for s in overlay['sources']}
        actions=pd.DataFrame([{'symbol':carrier,'ex_date':a['effective_date'],'event_type':a['event_type'],'source_reference':refs[a['source_id']]} for a in overlay['carriers'][carrier]['known_effective_actions']],columns=['symbol','ex_date','event_type','source_reference'])
        actions.to_csv(output/(carrier+'_known_actions_v2.csv'),index=False)
    tables={'endpoint_window_audit.csv':pd.concat(all_windows,ignore_index=True),'endpoint_impact_summary.csv':pd.DataFrame(summaries),'published_result_impact.csv':pd.DataFrame(result_rows),'full_path_impact_summary.csv':pd.DataFrame(full_rows),'intraday_measurement_impact.csv':pd.DataFrame(intraday_rows),'calendar_boundary_audit.csv':pd.DataFrame(boundary_rows)}
    for name,table in tables.items(): table.to_csv(output/name,index=False,float_format='%.15g')
    hits=consumer_inventory(pin,output)
    source_report=pin.json(EV+'/r1a_carrier_source_audit_20260912/source_delivery_audit.json')
    pin.file('research/r1a_carrier_transport/export_datahub_lake.py')
    dump(output/'source_semantics_status.json',{'state':source_state,'local_audit_is_not_independent_exchange_verification':True,'upstream_dictionary_files_available_in_this_repo':[p for p in pin.tree if p.endswith(('canonical-bars-whitepaper.md','session_offset_contract.py'))],'local_source_audit_top_level_keys':sorted(source_report),'unresolved':['true units/placeholder/aggregation semantics of zero-volume nonflat bars','exchange publication versus canonical wall-clock labels','meaning of available_at=15:30','original index fill contract and raw observations','exhaustive action and suspension calendars'],'exporter_verified_behavior':'to_numeric only for volume; no scaling/rounding implemented; Z stripped then localized; keep-last dedup; action list hardcoded. This identifies implemented transformations, not correctness of upstream semantics.'})
    pd.DataFrame(list(pin.used.values())).sort_values('path').to_csv(output/'pinned_input_integrity.csv',index=False)
    changed=sum(x['membership_changed'] for x in summaries)
    receipt={'schema_id':'factorlab_etf_source_repair_impact_receipt@1.0','decision':'KNOWN_ACTION_REPAIRED_PUBLISHED_MEMBERSHIP_UNCHANGED_SOURCE_SEMANTICS_PENDING' if changed==0 else 'KNOWN_ACTION_REPAIRED_CHANGED_PUBLISHED_COHORTS_REAGGREGATED','baseline_commit':BASE,'freeze_sha256':sha(root/FREEZE),'overlay_sha256':sha(root/OVERLAY),'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'github_run_id':os.getenv('GITHUB_RUN_ID'),'endpoint':summaries,'full_path':full_rows,'intraday_pooled':[x for x in intraday_rows if x['period']=='ALL'],'pinned_input_files':len(pin.used),'original_frozen_pairs':len(pairs),'endpoint_pair_horizon_rows':sum(len(t) for t in all_windows),'existing_published_return_rows_checked':published_rows,'endpoint_membership_changes':changed,'consumer_text_hits':hits,'original_source_bytes_modified':False,'new_return_population_opened':False,'new_model_fits':0,'R1A_reserve_unchanged':True,'full_source_qualification_complete':False,'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.iterdir()) if p.is_file()]}
    dump(output/'receipt.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('decision','original_frozen_pairs','endpoint_pair_horizon_rows','endpoint_membership_changes','existing_published_return_rows_checked','intraday_pooled')},ensure_ascii=False,indent=2))
    return receipt


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); run(a.root,a.output)
