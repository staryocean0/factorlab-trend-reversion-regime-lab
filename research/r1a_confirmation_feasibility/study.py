"""Power/resource planning and null calibration, NOT R1_A confirmation.

Only pinned 2015-2025 index bytes and previously observed ETF endpoint ledgers
are read. No signal refit, new market sample, imputation or observed-power claim.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import norm, t as student_t

from research.r1a_endpoint_robustness import study as rb

FREEZE = 'docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json'
FREEZE_COMMIT = '4c1b30995e02e00d335b83a050a45e9cb309d502'
BASELINE = '8b1cb1e69123712be3fbefb909ae382e2a1104c3'
EFFECTS = (2, 4, 6)
TARGETS = (.8, .9)
FAMILIES = (1, 7, 14, 28)
BUDGETS = (60, 120, 243, 486, 1215)
MODELS = ('IID_GAUSSIAN', 'SHARED_BLOCK_GAUSSIAN', 'SHARED_BLOCK_T5', 'OFF_GRAPH_AR1_0.6')
REPS, SEED = 2000, 20260912


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def sample_plan(se: float, sd: float, n: int, days: int, delta: float, power: float, family: int) -> dict:
    require(se > 0 and sd > 0 and n > 1 and days > 0 and delta > 0, 'invalid planning scales')
    require(0.5 < power < 1 and family >= 1, 'invalid planning probability/family')
    critical = float(norm.ppf(1-.05/(2*family)))
    multiplier = (critical+norm.ppf(power))**2
    needed_days = int(math.ceil(days*(se/delta)**2*multiplier))
    needed_pairs = int(math.ceil(n*needed_days/days))
    return {'effect_bp_ASSUMED': delta, 'target_positive_detection': power, 'family_size': family,
            'required_trading_days_CONDITIONAL': needed_days,
            'expected_eligible_pairs_CONDITIONAL': needed_pairs,
            'equivalent_years_NOT_FORECAST': float(needed_days/(days/5)),
            'independent_equivalent_n_required_NOT_actual_count': float(multiplier*(sd/delta)**2),
            'critical_z': critical, 'not_confirmatory_sample_size': True}


def budget_plan(se: float, n: int, days: int, budget: int, delta: float, family: int) -> dict:
    require(se > 0 and min(n, days, budget, delta, family) > 0, 'invalid budget')
    se_new = se*math.sqrt(days/budget)
    z = float(norm.ppf(1-.05/(2*family)))
    return {'budget_trading_days': budget, 'effect_bp_ASSUMED': delta, 'family_size': family,
            'expected_eligible_pairs_CONDITIONAL': float(n*budget/days),
            'positive_detection_probability_CONDITIONAL': float(norm.cdf(delta/se_new-z)),
            'detectable_effect_80_bp_CONDITIONAL': float((z+norm.ppf(.8))*se_new),
            'detectable_effect_90_bp_CONDITIONAL': float((z+norm.ppf(.9))*se_new)}


def meat_operator(members: list[set[int]]) -> tuple[sparse.csr_matrix, np.ndarray]:
    """Exact union-of-cliques quadratic, avoiding O(n^2 * simulations).

1[Si intersects Sj] = sum_{nonempty T subset Si intersection Sj} (-1)^(|T|+1).
This is only an algebraic acceleration of the already frozen adjacency rule.
"""
    require(len(members) > 1 and all(0 < len(s) <= 12 for s in members), 'invalid memberships')
    subset_ids: dict[tuple[int, ...], int] = {}
    rr, cc, signs = [], [], []
    for i, group in enumerate(members):
        for size in range(1, len(group)+1):
            for subset in itertools.combinations(sorted(group), size):
                if subset not in subset_ids:
                    subset_ids[subset] = len(subset_ids)
                    signs.append(1. if size % 2 else -1.)
                rr.append(subset_ids[subset]); cc.append(i)
    h = sparse.csr_matrix((np.ones(len(rr)), (rr,cc)), shape=(len(subset_ids),len(members)))
    return h, np.asarray(signs)


def simulate_standard_errors(y: np.ndarray, h: sparse.csr_matrix, signs: np.ndarray, g: int) -> tuple[np.ndarray, np.ndarray]:
    require(y.ndim == 2 and y.shape[0] == h.shape[1] and np.isfinite(y).all(), 'simulation shape')
    n = len(y); u = y-y.mean(axis=0)
    summed = h @ u
    meat = np.sum(signs[:,None]*summed*summed, axis=0)
    raw = meat/(n*n)*(n/(n-1))*(g/(g-1)) if g > 1 else np.full(y.shape[1],np.nan)
    iid = np.sum(u*u,axis=0)/(n*(n-1))
    valid = (n >= 30) & (g >= 30) & np.isfinite(raw) & (raw > 0)
    se = np.sqrt(np.maximum(raw,iid), where=np.maximum(raw,iid)>=0,
                 out=np.full_like(raw,np.nan))
    return se, valid


def wilson(k: int, n: int) -> tuple[float,float]:
    require(0 <= k <= n and n > 0, 'invalid binomial count')
    z = float(norm.ppf(.975)); p=k/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return (0. if k == 0 else max(0.,center-half)), (1. if k == n else min(1.,center+half))


def incidence(members: list[set[int]]) -> sparse.csr_matrix:
    """Unsigned outcome-level random effects: an illustrative DGP, not market truth."""
    rr, cc, vv = [], [], []
    require(all(min(s)>=0 for s in members), 'negative block id')
    for i,s in enumerate(members):
        for b in sorted(s):
            rr.append(i); cc.append(b); vv.append(1/math.sqrt(len(s)))
    return sparse.csr_matrix((vv,(rr,cc)),shape=(len(members),max(max(s) for s in members)+1))


def calibration(members: list[set[int]], sd: float, historical_se: float,
                seed: int, repetitions: int = REPS) -> list[dict]:
    n=len(members); b=incidence(members); h,signs=meat_operator(members)
    occupied=len(set().union(*members)); gfull=b.shape[1]
    require(sd > 0 and historical_se > 0, 'invalid calibration noise')
    loads=np.asarray(b.sum(axis=0)).ravel(); c=float(loads@loads)
    raw_lam=(n*n*historical_se**2/sd**2-n)/(c-n) if c>n else 0.
    fitted=float(np.clip(raw_lam,0.,.95))
    rows=[]
    for model_index,model in enumerate(MODELS):
        lam=0. if model=='IID_GAUSSIAN' else fitted
        rho=.6 if model=='OFF_GRAPH_AR1_0.6' else 0.
        cov=np.power(rho,np.abs(np.arange(gfull)[:,None]-np.arange(gfull)[None,:])) if rho else np.eye(gfull)
        oracle_var=sd*sd*((1-lam)/n+lam*float(loads@cov@loads)/(n*n))
        rng=np.random.default_rng(seed+model_index*1000003)
        invalid=reject5=reject14=0
        df=min(n-1,occupied-1)
        z5=float(student_t.ppf(.975,df)); z14=float(student_t.ppf(1-.05/28,df))
        for start in range(0,repetitions,100):
            r=min(100,repetitions-start)
            if model=='SHARED_BLOCK_T5':
                eps=rng.standard_t(5,size=(n,r))*math.sqrt(3/5)
                z=rng.standard_t(5,size=(gfull,r))*math.sqrt(3/5)
            else:
                eps=rng.standard_normal((n,r)); z=rng.standard_normal((gfull,r))
            if rho:
                for j in range(1,gfull):
                    z[j]=rho*z[j-1]+math.sqrt(1-rho*rho)*z[j]
            y=sd*(math.sqrt(1-lam)*eps+math.sqrt(lam)*(b@z))
            se,valid=simulate_standard_errors(y,h,signs,occupied)
            statistic=np.divide(np.abs(y.mean(axis=0)),se,out=np.zeros(r),where=valid)
            invalid+=int((~valid).sum())
            reject5+=int((valid & (statistic>z5)).sum())
            reject14+=int((valid & (statistic>z14)).sum())
        lo,hi=wilson(reject5,repetitions); l14,u14=wilson(reject14,repetitions)
        rows.append({'DGP_ASSUMED':model,'repetitions':repetitions,'seed':seed+model_index*1000003,
                     'lambda':lam,'lambda_unclipped':raw_lam,'lambda_clipped':bool(raw_lam<0 or raw_lam>.95),
                     'oracle_mean_SE_under_DGP_bp':math.sqrt(oracle_var),
                     'matched_independent_block_SE_bp':sd*math.sqrt((1-lam)/n+lam*c/(n*n)),
                     'historical_target_SE_bp':historical_se,'occupied_blocks':occupied,
                     'pointwise_nominal_alpha':.05,'pointwise_rejections':reject5,
                     'pointwise_rejection_rate':reject5/repetitions,'pointwise_MC95_lo':lo,'pointwise_MC95_hi':hi,
                     'marginal_family14_nominal_alpha':.05/14,'marginal_family14_rejections':reject14,
                     'marginal_family14_rejection_rate':reject14/repetitions,
                     'marginal_family14_MC95_lo':l14,'marginal_family14_MC95_hi':u14,
                     'unquantified_replicates':invalid,'unquantified_fraction':invalid/repetitions,
                     'severe_size_warning':bool(lo>.075),'real_market_calibration_proved':False,
                     'joint_family_error_simulated':False})
    return rows


def safe_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient='records',double_precision=15))


def run(root: Path, output: Path) -> dict:
    from regime_lab.market_data import load_market_data
    require(not output.exists(),'fresh output directory required')
    contract=json.loads((root/FREEZE).read_text())
    require(contract['baseline_commit']==BASELINE and contract['status']=='FROZEN_BEFORE_FEASIBILITY_CALCULATIONS','wrong freeze')
    require(contract['power']['true_effect_scenarios_bp']==list(EFFECTS) and contract['power']['families']==list(FAMILIES),'power scope drift')
    require(contract['power']['fixed_budgets_trading_days']==list(BUDGETS),'budget drift')
    require(contract['null_calibration']['simulation_models']==list(MODELS) and contract['null_calibration']['repetitions_per_design_per_DGP']==REPS,'simulation scope drift')
    require(contract['BLACKBOX_query_count']==3 and not contract['production_authority'] and not contract['new_confirmatory_outcomes_authorized'],'authority drift')
    rb.blob_guard(root/rb.PAIRS,'95191091d1a26c360c3efb5ae2d5be9cf194211d')
    rb.blob_guard(root/'data/manifest.json','a1935d30326dc9306dc23cdb309ac463114e2a2a')
    rb.blob_guard(root/rb.OLD/'endpoint_receipt.json','89f188522ddd657c8957ec2b85f8d0b57892143b')
    rb.blob_guard(root/'research/r1a_endpoint_robustness/study.py','83ffef4087fb73a09aaf46271d3c06353d6d354a')
    previous=json.loads((root/rb.OLD/'endpoint_receipt.json').read_text())
    for spec in previous['evidence_files']:
        p=root/rb.OLD/spec['path']
        require(Path(spec['path']).name==spec['path'] and rb.sha(p)==spec['sha256'] and p.stat().st_size==spec['bytes'],'changed historical endpoint file')
    pairs=rb.read_csv(root/rb.PAIRS)
    pairs=pairs.loc[pairs.cell=='R1_A'].copy()
    pairs['pair_id']=pairs.symbol.astype(str)+':R1_A:'+pairs.event_entry_idx.astype(str)+':'+pairs.control_entry_idx.astype(str)
    require(not pairs.pair_id.duplicated().any(),'duplicate frozen pair')
    noise_rows=[]; sample_rows=[]; budget_rows=[]; calibration_rows=[]; rate_rows=[]
    design_no=0
    for symbol,carrier in rb.MAP.items():
        p=pairs.loc[pairs.symbol==symbol].reset_index(drop=True)
        require(len(p)==rb.COUNTS[symbol],'pair counts changed')
        ix=load_market_data(symbol,'1m','2015-01-05' if symbol=='000852.SH' else '2020-07-23','2025-12-31',root=root)
        times=pd.DatetimeIndex(ix.market_time_shanghai)
        require(times.max().strftime('%Y-%m-%d')<='2025-12-31','new price sample prohibited')
        if symbol=='000852.SH':
            calendar=sorted(set(times[times.year>=2021].strftime('%Y-%m-%d')))
            day_map={d:i for i,d in enumerate(calendar)}; days=len(calendar)
        a=rb.read_csv(root/rb.OLD/(carrier+'_endpoint_availability.csv'))
        ledger=rb.read_csv(root/rb.OLD/(carrier+'_endpoint_returns.csv'))
        require(not a.duplicated(['pair_id','horizon']).any() and not ledger.duplicated(['pair_id','horizon']).any(),'duplicated endpoints')
        px=ix.close.to_numpy(float); e=p.event_entry_idx.to_numpy(int); c=p.control_entry_idx.to_numpy(int); d=p.parent_direction.to_numpy(int)
        for horizon in rb.HORIZONS:
            av=a.loc[a.horizon==horizon].set_index('pair_id').loc[p.pair_id].reset_index()
            require(set(av.pair_id)==set(p.pair_id),'availability changed')
            bounds=rb._bounds(av,day_map)
            full_index=d*(px[e+horizon]/px[e]-px[c+horizon]/px[c])*1e4
            require(np.isfinite(full_index).all(),'invalid old index returns')
            obs=av.eligible.to_numpy(bool)
            le=ledger.loc[ledger.horizon==horizon].set_index('pair_id').loc[p.loc[obs,'pair_id']].reset_index()
            require(len(le)==int(obs.sum()),'ETF count changed')
            require(np.allclose(le.index_incremental.to_numpy()*1e4,full_index[obs],atol=1e-8,rtol=0),'index comparator drift')
            require(np.allclose(le.etf_event-le.etf_control,le.etf_incremental,atol=1e-12,rtol=0),'ETF identity drift')
            for layer,values,bb,dates in [('INDEX_ALL_FROZEN_PAIRS',full_index,bounds,p.event_day),
                                         ('ETF_OBSERVED_ENDPOINTS',le.etf_incremental.to_numpy()*1e4,bounds[obs],p.loc[obs,'event_day'])]:
                design_no+=1
                sd=float(np.std(values,ddof=1))
                base={'layer':layer,'index_symbol':symbol,'carrier':carrier,'horizon':horizon,
                      'historical_pairs':len(values),'historical_trading_days':days}
                for year in rb.YEARS:
                    ny=int(dates.astype(str).str.startswith(year).sum()); dy=sum(x.startswith(year) for x in calendar)
                    rate_rows.append({**base,'year':year,'year_pairs':ny,'year_trading_days':dy,'pairs_per_day':ny/dy})
                for length,shift in rb.SPECS:
                    memberships=rb.block_memberships(bb,length,shift)
                    # Centering preserves the variance and deliberately discards the historical mean.
                    est=rb.graph_inference(values-values.mean(),memberships)
                    se=est['used_se_bp']
                    row={**base,'spec':f'L{length}_shift{shift}','marginal_SD_bp':sd,'historical_SE_bp':se,
                         'IID_SE_bp':sd/math.sqrt(len(values)),'occupied_blocks':est['occupied_blocks'],
                         'graph_status':est['inference_status'],'observed_mean_used_as_true_effect':False,
                         'design_effect_APPROX':float(len(values)*se*se/(sd*sd)) if se else None,
                         'noise_equivalent_independent_n_NOT_count':float(sd*sd/(se*se)) if se else None}
                    noise_rows.append(row)
                    if se is None:
                        continue
                    for family in FAMILIES:
                        for effect in EFFECTS:
                            for target in TARGETS:
                                sample_rows.append({**base,'spec':row['spec'],**sample_plan(se,sd,len(values),days,effect,target,family)})
                            for budget in BUDGETS:
                                budget_rows.append({**base,'spec':row['spec'],**budget_plan(se,len(values),days,budget,effect,family)})
                    if (length,shift)==(20,0):
                        print('CALIBRATING',layer,symbol,horizon,flush=True)
                        calibration_rows += [{**base,**x} for x in calibration(memberships,sd,se,SEED+design_no*10007)]
    require(design_no==28,'missing fixed design')
    output.mkdir(parents=True)
    tables={'historical_noise_NOT_new_tests.csv':pd.DataFrame(noise_rows),
            'sample_size_scenarios_NOT_commitments.csv':pd.DataFrame(sample_rows),
            'fixed_budget_power_NOT_forecasts.csv':pd.DataFrame(budget_rows),
            'null_calibration_synthetic_DGPs.csv':pd.DataFrame(calibration_rows),
            'historical_pair_rates.csv':pd.DataFrame(rate_rows)}
    for name,table in tables.items(): table.to_csv(output/name,index=False)
    required=tables['sample_size_scenarios_NOT_commitments.csv']
    focus=required.loc[(required.spec=='L20_shift0') & (required.family_size==14) & (required.target_positive_detection==.8) & (required.index_symbol=='000852.SH') & required.horizon.isin([15,30])]
    budget=tables['fixed_budget_power_NOT_forecasts.csv']
    focus_budget=budget.loc[(budget.spec=='L20_shift0') & (budget.family_size==14) & (budget.index_symbol=='000852.SH') & budget.horizon.isin([15,30]) & (budget.effect_bp_ASSUMED==4)]
    cal=tables['null_calibration_synthetic_DGPs.csv']
    cal_summary=[]
    for model in MODELS:
        part=cal.loc[cal.DGP_ASSUMED==model]
        cal_summary.append({'model':model,'design_count':len(part),
                            'rejection_rate_min':float(part.pointwise_rejection_rate.min()),
                            'rejection_rate_max':float(part.pointwise_rejection_rate.max()),
                            'severe_size_warnings':int(part.severe_size_warning.sum()),
                            'invalid_replicates':int(part.unquantified_replicates.sum())})
    receipt={'schema_id':'factorlab_r1a_confirmation_feasibility_receipt@1.0',
             'decision':'FEASIBILITY_MEASURED_CONDITIONAL_NOT_CONFIRMATION',
             'freeze_commit':FREEZE_COMMIT,'freeze_sha256':rb.sha(root/FREEZE),
             'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
             'github_run_id':os.environ.get('GITHUB_RUN_ID'),
             'design_count':design_no,'table_rows':{k:len(v) for k,v in tables.items()},
             'noise_window':'2021-2025 original frozen pairs','historical_trading_days':days,
             'primary_CSI1000_short_locations_NOT_selected':safe_records(focus),
             'four_bp_budget_comparison_NOT_forecast':safe_records(focus_budget),
             'calibration_summary':cal_summary,'simulated_samples':int(cal.repetitions.sum()),
             'new_confirmation_prices_read':False,'new_significance_claim':False,'horizon_selected':False,
             'confirmation_protocol_frozen':False,'confirmation_clock_started':False,
             'unobserved_ETF_returns_imputed':False,'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
             'interpretation':'Conditional power at inherited noise/matching/eligibility; not assurance, not all-event ETF power, not a forecast of stable decades-long markets. Null simulations do not prove real-market calibration.',
             'files':[{'path':name,'sha256':rb.sha(output/name),'bytes':(output/name).stat().st_size} for name in tables]}
    write_json(output/'feasibility_receipt.json',receipt)
    lines=['# R1_A confirmation feasibility — conditional planning only','',
           'No new confirmation sample or empirical significance claim. All 28 index/ETF/horizon designs and four variance specifications are retained.',
           '', '## CSI1000 illustration: 80% positive detection, 14-comparison interval, primary variance',
           '', '| Layer | bars | Assumed effect bp | Required trading days | Expected pairs | Information-equivalent years, NOT forecast |',
           '|---|---:|---:|---:|---:|---:|']
    for r in focus.to_dict('records'):
        lines.append(f"| {r['layer']} | {r['horizon']} | {r['effect_bp_ASSUMED']} | {r['required_trading_days_CONDITIONAL']} | {r['expected_eligible_pairs_CONDITIONAL']} | {r['equivalent_years_NOT_FORECAST']:.2f} |")
    lines += ['', 'Required horizons are NOT chosen from this table. 2/4/6bp are assumptions, not historical effect estimates or economic profit hurdles. Years scale the historical pair/noise rate and must not be sold as a real-world completion schedule.',
              '', '## Null calibration of the previous approximate graph/t estimator',
              '', '| Assumed model | Designs | Marginal 5% rejection range | Severe warnings (MC lower bound >7.5%) |',
              '|---|---:|---|---:|']
    for r in cal_summary:
        lines.append(f"| {r['model']} | {r['design_count']} | {r['rejection_rate_min']:.2%} to {r['rejection_rate_max']:.2%} | {r['severe_size_warnings']} |")
    lines += ['', 'These simulations use the historical exposure geometry but imposed random-effect models. They do not identify the true DGP. Correlated block shocks intentionally violate the assumed off-graph independence. Invalid-variance replicates are reported and cannot reject. Marginal Bonferroni tests were simulated; joint familywise error was NOT simulated.',
              '', '## Deliverables and remaining boundary',
              '', 'All sample-size scenarios (families 1/7/14/28, target 80%/90%), fixed 60/120/243/486/1215-day power, index-versus-ETF noise, annual pair rates and 2000-repetition null diagnostics are separate CSVs. The pointwise and smaller-family alternatives are explanatory, not a chosen new test.',
              '', 'Data-role audit is separate. A later confirmation needs qualified data, a finalized missingness/observation contract, and an adequately justified inferential method. Neither the 95%/80% old gates nor failed common-primary ETF sample was changed. No new data transfer, live trading, options or BLACKBOX query is authorized.',
              '', 'Sources and exact planning/DGP formulas: docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json.',
              '', '`production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'decision':receipt['decision'],'designs':design_no,'calibration':cal_summary},indent=2))
    return receipt


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); run(args.root.resolve(),args.output)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
