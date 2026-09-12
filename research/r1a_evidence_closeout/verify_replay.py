"""Verify the existing-evidence audit without refitting or rewriting references."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from research.r1a_evidence_closeout.audit import sha, require

REFERENCE_SHA256='adb89b07da7221b63e75a41747e582991ab46f3738c0b6b75781e9dc35bc33f2'


def compare(reference: Path, replay: Path, output: Path) -> dict:
    require(reference.resolve()!=replay.resolve(),'reference and replay must differ')
    require(not output.exists(),'fresh audit output required')
    a=json.loads((reference/'receipt.json').read_text());b=json.loads((replay/'receipt.json').read_text())
    require(sha(reference/'receipt.json')==REFERENCE_SHA256,'sealed closeout receipt changed')
    for key in ['decision','baseline_commit','freeze_commit','freeze_sha256','source_registry_sha256',
                'original_forecast_receipt_sha256','new_model_fits','new_signal_generation','new_strategy_returns',
                'raw_market_files_read','new_significance_tests','original_events','warmup_events',
                'scored_events_each_horizon','audited_event_score_groups','reconciled_score_fields',
                'audited_parameter_rows','audited_prior_fit_records','audited_prior_prefix_records',
                'audit_discrepancy','table_rows','BLACKBOX_query_count','production_authority','fresh_oos',
                'confirmation_protocol_frozen','confirmation_clock_started','horizon_selected']:
        require(a[key]==b[key],'receipt drift '+key)
    result=[]
    for spec in a['files']:
        p=reference/spec['path'];q=replay/spec['path']
        require(sha(p)==spec['sha256'],'reference CSV changed')
        x=pd.read_csv(p);y=pd.read_csv(q)
        require(x.shape==y.shape and list(x.columns)==list(y.columns),'table shape drift')
        changes=[]
        for col in x.columns:
            require(x[col].isna().equals(y[col].isna()),'missingness drift '+col)
            if pd.api.types.is_float_dtype(x[col]):
                good=x[col].notna()
                u=x.loc[good,col].to_numpy();v=y.loc[good,col].to_numpy()
                require(np.allclose(u,v,rtol=1e-9,atol=1e-7),'numeric drift '+col)
                delta=float(np.max(np.abs(u-v))) if len(u) else 0.
                if delta:changes.append({'column':col,'maximum_absolute_difference':delta})
            else:
                require(x[col].fillna('<NA>').equals(y[col].fillna('<NA>')),'identity/discrete drift '+col)
        result.append({'path':spec['path'],'rows':len(x),'byte_identical':sha(p)==sha(q),'continuous_differences':changes})
    out={'status':'PASS_NO_FIT_REPLAY_NOT_NEW_RESEARCH','reference_receipt_sha256':sha(reference/'receipt.json'),
         'replay_receipt_sha256':sha(replay/'receipt.json'),'tables':result,'original_evidence_overwritten':False}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',type=Path,required=True);p.add_argument('--replay',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();compare(a.reference,a.replay,a.output)
