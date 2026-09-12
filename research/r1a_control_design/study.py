"""Development-only control design. Never evaluate newly assigned returns."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from research.r1a_control_design.core import (
    FEATURES, HORIZONS, STAGES, IDENTITY, SPAN, CALIPER,
    allocate, coverage_balance, make_geometry, adjudicate, require,
)

BASELINE='02717cb0844d17bb572a2a5d4ace9fa92c8dd5b8'
FREEZE_COMMIT='6ebbb80e93cd0e5d783438c41f6fe310381a3e68'
FREEZE='docs/governance/R1A_CAUSAL_CONTROL_DESIGN_FREEZE@1.0.json'
PAIRS='docs/ops/evidence/r1a_development_noise_20260912/development_pairs.csv'
SCOPES={'000852.SH':('2015-01-05','2020-12-31'), '000688.SH':('2020-07-23','2020-12-31')}
COUNTS={'000852.SH':1752,'000688.SH':156}
GUARDS={
 PAIRS:'d4d06d136fab527e3717575517be50acbe56e542',
 'data/manifest.json':'a1935d30326dc9306dc23cdb309ac463114e2a2a',
 'research/index_price_validity/core.py':'a03bb31ea7f9f883187e6ad26e53df8ad86f4285',
 'research/r1_incremental_alpha_attribution/core.py':'73c4eaad108e9c56ad5af84a562e89442c192f13',
 'research/r1a_development_noise/study.py':'c603a25b068f206832e32305f406dde869eaf390',
 'docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json':'9a3d24da0a1d829d2d604219dedf72a1d49a7a18',
}


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_inputs(root:Path)->dict:
    for name,expected in GUARDS.items():
        data=(root/name).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(actual==expected,'pinned source changed: '+name)
    f=json.loads((root/FREEZE).read_text())
    require(f['baseline_commit']==BASELINE and f['status']=='FROZEN_BEFORE_NEW_ALLOCATION_AND_OUTCOMES','freeze identity drift')
    require(f['BLACKBOX_query_count']==3 and not f['production_authority'] and not f['horizon_selected'],'authority drift')
    require({s:(x['start'],x['end']) for s,x in f['scopes'].items()}==SCOPES,'scope drift')
    return f


def allowed_tables(events,controls,symbol):
    events=events.loc[events.cell=='R1_A'].copy()
    controls=controls.loc[controls.cell=='R1_A'].copy()
    events['symbol']=symbol; controls['symbol']=symbol
    events=events.rename(columns={'event_day':'day'})
    controls=controls.rename(columns={'control_day':'day'})
    cols=list(IDENTITY)+list(FEATURES)
    return events[cols].copy(),controls[cols].copy()


def verify_event_identity(events,old):
    e=events.sort_values('entry_idx').reset_index(drop=True)
    o=old.sort_values('event_entry_idx').reset_index(drop=True)
    require(np.array_equal(e.entry_idx.to_numpy(int),o.event_entry_idx.to_numpy(int)),'original event universe changed')
    for col in ('parent_direction','clock_bucket'):
        require(np.array_equal(e[col].to_numpy(int),o[col].to_numpy(int)),'event identity differs: '+col)
    require(e.day.tolist()==o.event_day.astype(str).tolist(),'event dates differ')
    for feature in FEATURES:
        # Original public feature ledger was serialized to twelve significant digits.
        require(np.allclose(e[feature],o['event_'+feature],rtol=2e-10,atol=2e-12),'recompiled causal feature differs: '+feature)


def render(receipt,coverage,balance,geometry):
    out=['# R1_A event-time control allocation — design only','',receipt['decision'],'',
         'No newly assigned event/control returns, p-values or noise estimates were calculated. Original event denominators and old ledgers are preserved.',
         '', '| Symbol | Stage | Original events | Matched | Coverage | No past stratum | Outside caliper | Interval blocked |',
         '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in coverage.loc[coverage.group=='POOLED'].itertuples():
        out.append(f'| {r.symbol} | {r.stage} | {r.original_events} | {r.matched_events} | {100*r.coverage:.2f}% | {r.no_mature_exact} | {r.no_caliper_support} | {r.interval_blocked} |')
    out.extend(['','## Primary design decisions',''])
    for s,v in receipt['symbols'].items():
        out.append(f"- {s}: {v['decision']}; reasons {v['failure_reasons']}; coverage groups {v['failed_coverage_groups']}; balance groups {v['failed_balance_groups']}.")
    out.extend(['','## All primary coverage groups','', '| Symbol | Group | Denominator | Matched | Coverage | Required | Balance pass |',
                '|---|---|---:|---:|---:|---|---|'])
    for r in coverage.loc[coverage.stage==STAGES[2]].itertuples():
        out.append(f'| {r.symbol} | {r.group} | {r.original_events} | {r.matched_events} | {100*r.coverage:.2f}% | {r.gate_required} | {r.balance_pass} |')
    out.extend(['','## Interpretation limits','',
      'Only PAST_CALIPER_EXCLUSIVE is the proposed design. The other two stages diagnose where availability is lost; they are not alternatives selected after failure.',
      'PAST_CALIPER coverage is an upper bound on per-event admissibility under these exact past/year/stratum/scaling/caliper rules before interval competition. A greedy allocation failure is NOT proof that every allocator fails.',
      'The 0.5 prefix-scale caliper, 80% coverage and 0.1 balance limits are predeclared project-specific screening criteria, not statistical significance or proof of exchangeability. All observed covariate variance ratios are also reported.',
      'A control needs its entire 240-bar path to have ended by the event information cutoff. Normalization uses the same-year matured control prefix only. Outcomes of those controls are not read by the allocator.',
      'The historical feature compiler reuses the existing structural event engine, which uses close prices and structural first passage internally. This is not a claim of never loading post-event price rows; no NEW allocation return is evaluated.',
      'Unit-incidence energies describe repeated clock use, not actual simple-return variance, realized noise reduction or independent information. Cross-pair event/control exposures may remain.',
      'The fixed terminal-complete Development cohort is not fresh OOS, an online event-admission specification, or an identified full-population causal contrast. Missing matches stay visible, never zero-imputed.',
      'CSI1000 is primary; STAR50 2020 is short context only. No ETFs, post2020 prices or 2026 candidate outcomes entered this study.',
      'No signal/threshold/horizon change, no new significance test, no production promotion. Stop after this fixed screen; do not retune failed design settings.',
      '', 'BLACKBOX_query_count=3; production_authority=false; fresh_oos=false.'])
    return '\n'.join(out)+'\n'


def run(root:Path,output:Path)->dict:
    require(not output.exists(),'fresh output directory required')
    frozen=check_inputs(root)
    # Import only after source identity checks. This compiler is the original one.
    from research.r1a_development_noise.study import load_development
    from research.r1_incremental_alpha_attribution.core import build_r1_events_and_controls
    old=pd.read_csv(root/PAIRS,dtype={'calendar_year':str})
    require(set(old.cell)=={'R1_A'},'wrong event cell')
    contract=json.loads((root/'docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json').read_text())
    manifest=json.loads((root/'data/manifest.json').read_text())
    allocations=[]; scalings=[]; sources=[]; clocks={}; pools={}; compiled_events=[]
    for symbol,(start,end) in SCOPES.items():
        tape,files=load_development(root,symbol,manifest); sources.extend(files)
        print('Compiling causal feature stream, not new returns:',symbol,flush=True)
        ev,co=build_r1_events_and_controls(tape.close.to_numpy(float),tape.trading_day.to_numpy(str),tape.time,
                 contract['directional_change_thresholds'],contract['r1_vol_reference'],start,end,max_horizon=SPAN)
        ev,co=allowed_tables(ev,co,symbol)
        base=old.loc[old.symbol==symbol]
        require(len(base)==COUNTS[symbol] and len(ev)==COUNTS[symbol],'denominator mismatch')
        verify_event_identity(ev,base)
        # Event outcome/resolve fields are stripped. Future prices are not passed on.
        codes,dates=pd.factorize(tape.trading_day,sort=True)
        clocks[symbol]=codes
        pools[symbol]={'original_events':len(ev),'candidate_controls':len(co),'observed_index_rows':len(tape),
                       'trading_days':len(dates),'event_identity_and_feature_reconstruction_pass':True,
                       'original_role':frozen['scopes'][symbol]['role']}
        del tape
        print('Allocating from identity/covariate-only tables:',symbol,flush=True)
        ledger,norm=allocate(ev,co)
        allocations.append(ledger); scalings.append(norm); compiled_events.append(ev)
    ledger=pd.concat(allocations,ignore_index=True)
    require(len(ledger)==sum(COUNTS.values())*len(STAGES),'some events silently dropped')
    coverage,balance=coverage_balance(ledger)
    geo=make_geometry(ledger,old,clocks)
    decisions=adjudicate(ledger,coverage)
    for info in decisions.values():
        require('IMPLEMENTATION_CONTRACT_VIOLATION' not in info['failure_reasons'],'implementation failed constraints')
    frames={'allocation_ledger':ledger,'prefix_scaling_audit':pd.concat(scalings,ignore_index=True),
            'coverage_by_group':coverage,'covariate_balance':balance,'unit_incidence_geometry_NOT_realized_variance':geo,
            'compiled_event_features':pd.concat(compiled_events,ignore_index=True)}
    output.mkdir(parents=True)
    for name,frame in frames.items():
        frame.to_csv(output/(name+'.csv'),index=False,float_format='%.12g')
    receipt={'schema_id':'factorlab_r1a_control_design_receipt@1.0',
        'decision':'CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES',
        'baseline_commit':BASELINE,'freeze_commit':FREEZE_COMMIT,'freeze_sha256':sha(root/FREEZE),
        'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'github_run_id':os.environ.get('GITHUB_RUN_ID'),'sources':sources,'input_blobs':GUARDS,
        'pools':pools,'symbols':decisions,'table_rows':{k+'.csv':len(v) for k,v in frames.items()},
        'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.glob('*.csv'))],
        'new_allocation_outcomes_read':False,'new_significance_tests':False,'noise_reduction_demonstrated':False,
        'old_pairs_modified':False,'post2020_price_files_read':[],'caliper_tuned':False,
        'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
        'confirmation_protocol_frozen':False,'confirmation_clock_started':False,'horizon_selected':False}
    (output/'design_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (output/'REPORT.md').write_text(render(receipt,coverage,balance,geo))
    print(json.dumps({'decision':receipt['decision'],'symbols':decisions,'table_rows':receipt['table_rows']},indent=2))
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(args.root.resolve(),args.output.resolve())


if __name__=='__main__':
    main()
