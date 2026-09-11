"""Audit b656b4b public delivery evidence, not a new empirical experiment.

No private ETF tape is read. Checks hashes, original pair identity, all horizons,
return algebra, full receipt summaries, and index comparators on pinned data.
Original local results and prior freezes are never overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from research.r1a_carrier_transport.transport import HORIZONS, summarize

DELIVERY = 'b656b4b8cda266800b33a374d5a5c98360c51837'
BASE = 'docs/ops/evidence/r1a_carrier_transport_20260912'
LOCAL = BASE + '_local'
PAIRS = 'docs/ops/evidence/r1_incremental_alpha_20260911/matched_pairs.csv'
FREEZE = 'docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json'

class AuditError(ValueError):
    """Public evidence is inconsistent; no research promotion is allowed."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compare_json(actual, expected, path='root') -> int:
    """Tolerate only floating-point roundoff, not schema/boolean changes."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), f'{path}: keys differ')
        return sum(compare_json(actual[k], expected[k], path+'.'+k) for k in expected)
    if isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), f'{path}: list differs')
        return sum(compare_json(a,b,path+f'[{i}]') for i,(a,b) in enumerate(zip(actual,expected)))
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        require(actual == expected and type(actual) is type(expected), f'{path}: literal differs')
    elif isinstance(expected, (int, float)):
        require(isinstance(actual, (int, float, np.number)) and not isinstance(actual, bool), f'{path}: not numeric')
        require(math.isfinite(float(actual)) and math.isclose(float(actual),float(expected),rel_tol=1e-10,abs_tol=1e-8), f'{path}: numeric mismatch {actual} vs {expected}')
    else:
        require(actual == expected, f'{path}: differs')
    return 1

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision='round_trip')

def verify_ledger(ledger: pd.DataFrame, coverage: pd.DataFrame, pairs: pd.DataFrame) -> dict:
    require(not ledger.empty and not coverage.empty and not pairs.empty, 'empty evidence')
    require(not pairs.pair_id.duplicated().any(), 'duplicate frozen pair')
    require(not coverage.pair_id.duplicated().any(), 'duplicate coverage pair')
    require(set(coverage.pair_id) == set(pairs.pair_id), 'coverage denominator changed')
    require(coverage.eligible.isin([True,False]).all(), 'invalid eligible flags')
    accepted = set(coverage.loc[coverage.eligible, 'pair_id'])
    require(set(ledger.pair_id) == accepted, 'ledger/common sample mismatch')
    require(not ledger.duplicated(['pair_id','horizon']).any(), 'duplicate pair/horizon')
    require(set(ledger.horizon) == set(HORIZONS), 'horizon drift')
    require(ledger.groupby('pair_id').horizon.nunique().eq(len(HORIZONS)).all(), 'incomplete horizon surface')
    require(len(ledger) == len(accepted)*len(HORIZONS), 'unexpected row count')
    p = pairs.set_index('pair_id').loc[ledger.pair_id]
    for col in ('event_day','control_day','side'):
        require(np.array_equal(ledger[col].astype(str).to_numpy(), p[col].astype(str).to_numpy()), 'frozen '+col+' changed')
    require(np.array_equal(ledger.index_symbol.to_numpy(),p.symbol.to_numpy()), 'index symbol changed')
    require(np.array_equal(p.side.to_numpy(),np.where(p.parent_direction.to_numpy()==1,'LONG','SHORT')), 'side/direction mismatch')
    numeric = ['etf_event','etf_control','etf_incremental','index_event_same_sample','index_control_same_sample','index_incremental_same_sample','event_tracking_residual','incremental_tracking_residual','etf_close_MFE','etf_close_MAE']
    require(np.isfinite(ledger[numeric].to_numpy(float)).all(), 'nonfinite ledger')
    identities = {
        'etf_incremental': ledger.etf_event-ledger.etf_control,
        'index_incremental_same_sample': ledger.index_event_same_sample-ledger.index_control_same_sample,
        'event_tracking_residual': ledger.etf_event-ledger.index_event_same_sample,
        'incremental_tracking_residual': ledger.etf_incremental-ledger.index_incremental_same_sample,
    }
    errors = {}
    for col, value in identities.items():
        errors[col] = float(np.abs(ledger[col]-value).max())
        require(errors[col] <= 1e-12, col+' algebra mismatch')
    require((ledger.etf_close_MFE >= -1e-12).all() and (ledger.etf_close_MAE <= 1e-12).all(), 'zero-at-entry extrema violated')
    require((ledger.etf_close_MFE+1e-12 >= ledger.etf_event).all() and (ledger.etf_close_MAE-1e-12 <= ledger.etf_event).all(), 'endpoint outside extrema')
    for col,sign in [('etf_close_MFE',1),('etf_close_MAE',-1)]:
        for _, group in ledger.groupby('pair_id',sort=False):
            require((np.diff(group.sort_values('horizon')[col].to_numpy())*sign >= -1e-12).all(), 'nested extrema inconsistent')
    return {'frozen_pairs':len(pairs),'complete_pairs':len(accepted),'ledger_rows':len(ledger),'all_horizons_preserved':True,'maximum_algebra_errors':errors}

def audit(root: Path, output: Path) -> dict:
    require(not output.exists(), 'output already exists; preserve past evidence')
    local = root/LOCAL
    receipt = json.loads((local/'transport_receipt.json').read_text())
    require(receipt['decision']=='PARTIAL_CARRIER_TRANSPORT', 'delivery status changed')
    require(receipt['BLACKBOX_query_count']==3, 'BLACKBOX changed')
    for flag in ['production_authority','fresh_oos','horizon_selected','signal_refitted','control_rematched','option_outcomes_read','formal_causal_inference']:
        require(receipt[flag] is False, 'scope changed: '+flag)
    require(sha(root/FREEZE)==receipt['freeze_sha256'], 'freeze hash mismatch')
    require(sha(root/PAIRS)==receipt['matched_pairs_sha256'], 'pair hash mismatch')
    require(sha(root/'data/manifest.json')==receipt['input_index_manifest_sha256'], 'index manifest hash mismatch')
    checked = []
    for spec in receipt['evidence_files']:
        name = spec['path']; require(Path(name).name==name, 'unsafe evidence path')
        path = local/name
        if not path.exists() and name=='frozen_index_clock_anchors.csv':
            path=root/BASE/name  # shared immutable anchor, not silently regenerated
        require(path.is_file(), 'missing receipt evidence: '+name)
        require(path.stat().st_size==spec['bytes'] and sha(path)==spec['sha256'], 'evidence hash/size differs: '+name)
        checked.append({'path':str(path.relative_to(root)),'sha256':sha(path),'bytes':path.stat().st_size})
    pairs=read_csv(root/PAIRS)
    pairs=pairs.loc[(pairs.cell=='R1_A') & (pairs.symbol=='000688.SH')].copy()
    pairs['pair_id']=pairs.symbol.astype(str)+':R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
    coverage=read_csv(local/'588000.SH_coverage.csv')
    ledger=read_csv(local/'588000.SH_transport.csv')
    checks=verify_ledger(ledger,coverage,pairs)
    info=receipt['carriers']['588000.SH']
    require(info['ETF_outcomes_read'] is True and info['admission']['status']=='PASS_DATA_ADMISSION_ONLY', 'local carrier state differs')
    computed=summarize(ledger)
    summary_leaves=compare_json(computed,info['summary'],'summary')
    sample=info['common_sample']
    require(checks['complete_pairs']==sample['complete_pairs'] and checks['frozen_pairs']==sample['frozen_pairs'], 'sample count differs')
    rates={'pooled':float(coverage.eligible.mean())}
    for y in range(2021,2026):
        rows=coverage.loc[coverage.event_day.str.startswith(str(y))]
        rates[str(y)]=float(rows.eligible.mean())
    compare_json(rates,sample['coverage'],'coverage')
    compare_json({str(k):int(v) for k,v in coverage.reason.value_counts().items()},sample['reasons'],'reasons')
    # Recompute INDEX returns from original minute bytes, not from stored returns.
    from regime_lab.market_data import load_market_data
    index=load_market_data('000688.SH','1m','2020-07-23','2025-12-31',root=root)
    require(len(index)==info['index_rows_verified'], 'index row count mismatch')
    aligned=pairs.set_index('pair_id').loc[ledger.pair_id]
    e=aligned.event_entry_idx.to_numpy(int); c=aligned.control_entry_idx.to_numpy(int)
    h=ledger.horizon.to_numpy(int); d=aligned.parent_direction.to_numpy(int)
    prices=index.close.to_numpy(float)
    index_errors={}
    for col,starts in [('index_event_same_sample',e),('index_control_same_sample',c)]:
        expected=d*(prices[starts+h]/prices[starts]-1)
        err=float(np.max(np.abs(expected-ledger[col].to_numpy(float))))
        require(err<=1e-12, 'raw index comparator mismatch: '+col); index_errors[col]=err
    manifests={}; raw_missing=[]
    export=json.loads((local/'datahub_lake_export_receipt.json').read_text())
    for carrier in ('512100.SH','588000.SH'):
        path=root/'data/r1a_carrier_prices'/(carrier+'.json'); m=json.loads(path.read_text())
        require(sha(path)==export['carriers'][carrier]['manifest_sha256'], 'export manifest hash mismatch')
        compare_json(m['files'],export['carriers'][carrier]['files'],'manifest.files')
        compare_json(m['corporate_actions_file'],export['carriers'][carrier]['corporate_actions_file'],'manifest.actions')
        for spec in m['files']+[m['corporate_actions_file']]:
            if not (root/spec['path']).is_file(): raw_missing.append(spec['path'])
        manifests[carrier]={'sha256':sha(path),'declared_price_rows':sum(x['rows'] for x in m['files'])}
    require(sha(root/BASE/'datahub_lake_export_receipt.json')==sha(local/'datahub_lake_export_receipt.json'), 'two export receipt copies disagree')
    primary=receipt['carriers']['512100.SH']
    require(primary['ETF_outcomes_read'] is False, 'blocked primary outcomes opened')
    prefix='INSUFFICIENT_CARRIER_MINUTE_COVERAGE '
    require(primary['reason'].startswith(prefix), 'primary blocker changed')
    primary_rates=json.loads(primary['reason'][len(prefix):])
    require(primary_rates['2021'] < 0.95, 'reported primary gate contradicts rates')
    table=[]
    for h in HORIZONS:
        x=computed[str(h)]; pooled=x['pooled']
        table.append({'horizon':h,'n':pooled['n'],'ETF_event_bp':pooled['etf_event']['mean_bp'],'index_event_bp':pooled['index_event_same_sample']['mean_bp'],'ETF_increment_bp':pooled['etf_incremental']['mean_bp'],'index_increment_bp':pooled['index_incremental_same_sample']['mean_bp'],'event_tracking_residual_bp':pooled['event_tracking_residual']['mean_bp'],'increment_tracking_residual_bp':pooled['incremental_tracking_residual']['mean_bp'],'correlation':pooled['event_price_return_correlation'],'event_median_bp':pooled['etf_event']['median_bp'],'event_positive_fraction':pooled['etf_event']['positive_fraction'],'LONG_increment_bp':x['sides']['LONG']['etf_incremental']['mean_bp'],'SHORT_increment_bp':x['sides']['SHORT']['etf_incremental']['mean_bp'],'positive_increment_years':sum(v['etf_incremental']['mean_bp']>0 for v in x['years'].values())})
    out={'schema_id':'factorlab_r1a_public_delivery_audit@1.0','decision':'PUBLIC_LEDGER_AUDIT_PASS_RAW_ETF_REPLAY_NOT_PERFORMED','delivery_commit':DELIVERY,'audit_code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'local_receipt_sha256':sha(local/'transport_receipt.json'),'verified_public_files':checked,'ledger_checks':checks,'summary_leaves_verified':summary_leaves,'index_recomputed_from_verified_minute_bytes':True,'index_maximum_errors':index_errors,'raw_ETF_prices_read':False,'raw_ETF_replay_independently_reproduced':False,'raw_files_missing_in_this_checkout':raw_missing,'manifests':manifests,'primary_minute_coverage':primary_rates,'coverage_gate_unchanged':0.95,'secondary_common_pair_coverage':rates,'seven_horizon_summary':table,'research_state':'PARTIAL_CARRIER_TRANSPORT','horizon_selected':False,'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,'source_audit_remaining':['Raw source-to-canonical verification requires private bytes; hashes in a manifest are not the bytes themselves.','Exporter interprets Z-suffixed strings as Shanghai wall-clock under its source claim; upstream dictionary/provenance is not independently verified by this public-ledger audit.','Exporter drops duplicate timestamps keeping the last row without a before/after duplicate-count receipt; occurrence or nonoccurrence in this delivery cannot be established here.','Corporate-action completeness is asserted in local manifests; this audit does not independently establish the complete source ledger.'],'interpretation':'Arithmetic and retained evidence audit only. No new significance, causal, independent-OOS, horizon-selection or execution-profitability claim.'}
    output.mkdir(parents=True)
    (output/'audit_receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['# R1_A local delivery — cloud evidence audit','',f'Delivery commit: `{DELIVERY}`','',f"Decision: `{out['decision']}`",'', 'This audit recalculates the public ledger summaries and index comparators. It does not rerun private ETF price generation, independently approve upstream source semantics, or open the blocked primary carrier.', '',f"588000.SH: {checks['complete_pairs']}/{checks['frozen_pairs']} complete pairs; {checks['ledger_rows']} rows; {summary_leaves} summary leaves verified.",'','| Index bars | n | ETF event bp | Index event bp | ETF increment bp | Index increment bp | Return correlation |','|---:|---:|---:|---:|---:|---:|---:|']
    for x in table:
        lines.append(f"| {x['horizon']} | {x['n']} | {x['ETF_event_bp']:+.3f} | {x['index_event_bp']:+.3f} | {x['ETF_increment_bp']:+.3f} | {x['index_increment_bp']:+.3f} | {x['correlation']:.4f} |")
    lines+=['','512100.SH remains unmeasured: 2021 valid-minute coverage is '+f"{primary_rates['2021']:.6%}"+' versus frozen 95%. No year exclusion, zero-volume fill, carrier switch or gate relaxation is performed.','', 'All seven horizons are reported. The secondary carrier does not replace primary CSI1000 evidence. Close-price synthetic returns are not bid/ask execution profits.','', '## Remaining source-level checks','']
    lines += ['- '+x for x in out['source_audit_remaining']]
    lines+=['','`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    return out

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); root=args.root.resolve()
    result=audit(root,args.output or root/'docs/ops/evidence/r1a_carrier_cloud_audit_20260912')
    print(json.dumps({'decision':result['decision'],'ledger_checks':result['ledger_checks'],'seven_horizon_summary':result['seven_horizon_summary']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
