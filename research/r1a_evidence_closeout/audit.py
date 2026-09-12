"""Read-only reconciliation of existing evidence; NO model fit or market replay.

Inputs are an explicit pinned allowlist of pre-existing receipts/reports/ledgers.
All moments below use ddof=0 finite-sample accounting, never inference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

BASELINE = '23e5c2bacf2dd1c43c84843aac256f5f41891c43'
FREEZE = 'docs/governance/R1A_EVIDENCE_CLOSEOUT_FREEZE@1.0.json'
REGISTRY = 'research/r1a_evidence_closeout/source_registry.json'
FOLDER = 'docs/ops/evidence/r1a_walkforward_prediction_20260912'
DEV = 'docs/ops/evidence/r1a_development_noise_20260912/development_pairs.csv'
RECEIPT_BLOB = '0bdf7738cd2a7e73bb20b85b8613dd2954ae488b'
DEV_BLOB = 'd4d06d136fab527e3717575517be50acbe56e542'
HORIZONS = (1, 5, 15, 30, 60, 120, 240)
YEARS = (2016, 2017, 2018, 2019, 2020)
RTOL, ATOL = 1e-9, 1e-7


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def close(a, b, name: str) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    require(a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all(), 'invalid audit values: ' + name)
    require(np.allclose(a, b, rtol=RTOL, atol=ATOL), 'arithmetic discrepancy: ' + name)
    return float(np.max(np.abs(a-b))) if a.size else 0.0


def vectors(y, p0, p1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y, p0, p1 = (np.asarray(x, dtype=float) for x in (y, p0, p1))
    require(y.ndim == p0.ndim == p1.ndim == 1 and y.shape == p0.shape == p1.shape and len(y) > 0,
            'empty or mismatched prediction vectors')
    require(all(np.isfinite(x).all() for x in (y, p0, p1)), 'nonfinite forecasts')
    return y, p0, p1


def decompose(y, p0, p1) -> dict:
    y, p0, p1 = vectors(y, p0, p1)
    e, q, g = y-p0, y-p1, p1-p0
    loss = e*e-q*q
    alignment, cost = 2*np.mean(e*g), np.mean(g*g)
    bias = np.mean(e)**2 - np.mean(q)**2
    centered = np.var(e, ddof=0) - np.var(q, ddof=0)
    covariance = np.mean((e-e.mean())*(g-g.mean()))
    mean_gain = float(loss.mean())
    err = max(close(loss, 2*e*g-g*g, 'individual loss'),
              close(mean_gain, alignment-cost, 'alignment-cost'),
              close(mean_gain, bias+centered, 'bias plus centered'),
              close(centered, 2*covariance-np.var(g), 'centered covariance'),
              close(np.mean(e*e), np.mean(e)**2+np.var(e), 'parent MSE identity'),
              close(np.mean(q*q), np.mean(q)**2+np.var(q), 'enhanced MSE identity'))
    mse0, mse1 = float(np.mean(e*e)), float(np.mean(q*q))
    return {'n': len(y), 'target_mean_bp': float(y.mean()), 'target_median_bp': float(np.median(y)),
        'parent_mean_prediction_bp': float(p0.mean()), 'enhanced_mean_prediction_bp': float(p1.mean()),
        'adjustment_mean_bp': float(g.mean()), 'adjustment_median_bp': float(np.median(g)),
        'adjustment_sd_bp': float(g.std()), 'adjustment_positive_fraction': float((g>0).mean()),
        'parent_residual_mean_y_minus_prediction_bp': float(e.mean()),
        'enhanced_residual_mean_y_minus_prediction_bp': float(q.mean()),
        'parent_centered_error_var_bp2': float(e.var()), 'enhanced_centered_error_var_bp2': float(q.var()),
        'parent_mse_bp2': mse0, 'enhanced_mse_bp2': mse1,
        'parent_rmse_bp': float(np.sqrt(mse0)), 'enhanced_rmse_bp': float(np.sqrt(mse1)),
        'parent_mae_bp': float(np.abs(e).mean()), 'enhanced_mae_bp': float(np.abs(q).mean()),
        'mean_loss_improvement_bp2': mean_gain, 'median_loss_improvement_bp2': float(np.median(loss)),
        'positive_loss_improvement_fraction': float((loss>0).mean()),
        'relative_mse_reduction': mean_gain/mse0 if mse0 > 0 else None,
        'alignment_2_mean_e_g_bp2': float(alignment), 'adjustment_square_cost_bp2': float(cost),
        'bias_square_reduction_bp2': float(bias), 'centered_error_variance_reduction_bp2': float(centered),
        'zero_forecast_mse_bp2': float(np.mean(y*y)),
        'enhanced_gain_over_zero_bp2': float(np.mean(y*y)-mse1),
        'max_identity_error_bp2': err}


def groups(f: pd.DataFrame):
    yield 'POOLED', f
    for year in YEARS:
        yield 'YEAR_'+str(year), f.loc[f.info_year == year]
    for side, direction in (('LONG', 1), ('SHORT', -1)):
        yield side, f.loc[f.parent_direction == direction]
    for year in YEARS:
        for side, direction in (('LONG', 1), ('SHORT', -1)):
            yield 'YEAR_'+str(year)+'_'+side, f.loc[(f.info_year == year) & (f.parent_direction == direction)]


def validate_prediction_rows(f: pd.DataFrame) -> None:
    require(not f.duplicated(['entry_idx','horizon']).any(), 'duplicate forecast identities')
    require(f.parent_direction.isin([-1,1]).all() and f.is_event.eq(1).all(), 'wrong event/side population')
    require((f.info_idx == f.entry_idx-1).all(), 'information index mismatch')
    require((f.exit_idx == f.entry_idx+f.horizon).all(), 'horizon/exit mismatch')
    require((f.fit_cutoff_idx < f.info_idx).all(), 'forecast fitted after information time')
    require(f.info_year.isin(YEARS).all(), 'unapproved information year')
    require((f.info_day.astype(str).str[:4].astype(int) == f.info_year).all(), 'information calendar mismatch')
    y,p0,p1 = vectors(f.target_bp, f.parent_prediction_bp, f.enhanced_prediction_bp)
    close(f.parent_squared_error, (y-p0)**2, 'stored parent errors')
    close(f.enhanced_squared_error, (y-p1)**2, 'stored enhanced errors')
    close(f.loss_improvement_bp2, (y-p0)**2-(y-p1)**2, 'stored loss difference')


def annual_partition(frame: pd.DataFrame, pool: dict) -> dict:
    rows = [(len(g), decompose(g.target_bp,g.parent_prediction_bp,g.enhanced_prediction_bp))
            for _,g in frame.groupby('info_year',sort=True)]
    n = len(frame)
    wg = sum(k*x['mean_loss_improvement_bp2'] for k,x in rows)/n
    wb = sum(k*x['bias_square_reduction_bp2'] for k,x in rows)/n
    wc = sum(k*x['centered_error_variance_reduction_bp2'] for k,x in rows)/n
    close(wg, pool['mean_loss_improvement_bp2'], 'year-weighted gain')
    close(wb+wc, wg, 'year-weighted components')
    return {'n': n, 'total_gain_bp2': wg, 'weighted_within_year_bias_square_reduction_bp2': wb,
        'weighted_within_year_centered_error_variance_reduction_bp2': wc,
        'pooled_bias_square_reduction_bp2': pool['bias_square_reduction_bp2'],
        'pooled_centered_error_variance_reduction_bp2': pool['centered_error_variance_reduction_bp2'],
        'between_year_centered_error_variance_reduction_bp2': pool['centered_error_variance_reduction_bp2']-wc,
        'meaning': 'ex_post_finite_sample_accounting_not_attainable_bias_correction'}


def parameter_accounting(parameters: pd.DataFrame, forecasts: pd.DataFrame) -> pd.DataFrame:
    require(not parameters.duplicated(['year','horizon','model','feature']).any(), 'duplicate model parameter')
    rows = []
    for (year,h),f in forecasts.groupby(['info_year','horizon'],sort=True):
        block = parameters.loc[(parameters.year == year)&(parameters.horizon == h)]
        a = block.loc[block.model == 'parent'].set_index('feature')
        b = block.loc[block.model == 'parent_plus_R1A'].set_index('feature')
        require(len(a)==17 and len(b)==18 and set(b.index)-set(a.index)=={'R1_A'}, 'parameter feature drift')
        common = [k for k in a.index if k != 'intercept']
        for m in (a,b):
            require((m.scale > 0).all(), 'invalid stored feature scale')
            close(m.coefficient_raw*m.scale,m.coefficient_standardized,'coefficient normalization')
        close(a.loc[common,'center'],b.loc[common,'center'],'common centers')
        close(a.loc[common,'scale'],b.loc[common,'scale'],'common scales')
        intercept_delta = float(b.loc['intercept','coefficient_raw']-a.loc['intercept','coefficient_raw'])
        close(intercept_delta, 0., 'same-training intercept')
        flag=b.loc['R1_A']; direct=float(flag.coefficient_raw*(1-flag.center))
        g=(f.enhanced_prediction_bp-f.parent_prediction_bp).to_numpy(float)
        remainder=g-intercept_delta-direct
        rows.append({'year':int(year),'horizon':int(h),'n':len(f),
            'enhanced_indicator_raw_coefficient_bp':float(flag.coefficient_raw),
            'indicator_training_prevalence':float(flag.center),
            'centered_indicator_term_at_event_bp':direct,'centered_intercept_difference_bp':intercept_delta,
            'mean_total_prediction_adjustment_bp':float(g.mean()),
            'mean_shared_feature_refit_remainder_bp':float(remainder.mean()),
            'shared_feature_refit_remainder_sd_bp':float(remainder.std()),
            'shared_standardized_coefficient_change_l2':float(np.linalg.norm(b.loc[common,'coefficient_standardized']-a.loc[common,'coefficient_standardized'])),
            'interpretation':'identity_defined_remainder_not_independent_causal_indicator_effect'})
    return pd.DataFrame(rows)


def run(root: Path, output: Path) -> dict:
    require(not output.exists(), 'fresh output directory required')
    frozen=json.loads((root/FREEZE).read_text())
    require(frozen['baseline_commit']==BASELINE and frozen['forecast_scope']['horizons']==list(HORIZONS), 'freeze drift')
    require(frozen['BLACKBOX_query_count']==3 and not frozen['production_authority'], 'authority drift')
    registry=json.loads((root/REGISTRY).read_text())
    source_meta=[]
    for spec in registry['reports']:
        p=root/spec['path']; raw=p.read_bytes()
        require(blob(raw)==spec['git_blob_sha1'], 'report source changed: '+spec['path'])
        source_meta.append({'path':spec['path'],'git_blob_sha1':spec['git_blob_sha1'],'sha256':sha(p),'bytes':len(raw),'role':'retained_report_not_new_outcome'})
    parent=root/FOLDER; rp=parent/'receipt.json'; raw=rp.read_bytes()
    require(blob(raw)==RECEIPT_BLOB,'original forecast receipt changed')
    old=json.loads(raw); source_meta.append({'path':str(rp.relative_to(root)),'sha256':sha(rp),'bytes':len(raw),'role':'original_receipt'})
    frames={}
    require(set(frozen['sources']['forecast_csvs'])==set(x['path'] for x in old['files']), 'forecast allowlist drift')
    for spec in old['files']:
        name=spec['path']; require(Path(name).name==name and name.endswith('.csv'),'unsafe evidence path')
        p=parent/name
        require(sha(p)==spec['sha256'] and p.stat().st_size==spec['bytes'],'forecast evidence changed: '+name)
        f=pd.read_csv(p)
        require(len(f)==old['table_rows'][name],'source row count mismatch: '+name)
        frames[name]=f
        source_meta.append({'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size,'rows':len(f),'role':'sealed_forecast_evidence'})
    raw=(root/DEV).read_bytes(); require(blob(raw)==DEV_BLOB,'original Development identities changed')
    dev=pd.read_csv(root/DEV);dev=dev.loc[dev.symbol=='000852.SH']
    source_meta.append({'path':DEV,'sha256':sha(root/DEV),'bytes':len(raw),'role':'original_identity_metadata'})
    d=frames['event_predictions.csv']; coverage=frames['all_original_event_coverage.csv']
    validate_prediction_rows(d)
    require(len(dev)==1752 and not dev.event_entry_idx.duplicated().any(),'Development identity denominator')
    require(len(d)==7749 and len(coverage)==12264,'forecast/coverage denominator')
    expected_ids=set(dev.event_entry_idx.astype(int))
    identity_ids=None
    for h in HORIZONS:
        c=coverage.loc[coverage.horizon==h]; f=d.loc[d.horizon==h]
        require(len(c)==1752 and set(c.entry_idx)==expected_ids,'coverage changed original population')
        require(not c.entry_idx.duplicated().any(),'duplicate coverage event')
        require(c.status.value_counts().to_dict()=={'SCORED':1107,'WARMUP_2015_NOT_SCORED':645},'coverage status drift')
        require(set(c.loc[c.status=='WARMUP_2015_NOT_SCORED','info_year'])=={2015},'warmup relabeled')
        require(len(f)==1107 and set(f.entry_idx)==set(c.loc[c.status=='SCORED','entry_idx']),'scored event mismatch')
        cur=tuple(sorted(zip(f.entry_idx,f.parent_direction)))
        require(identity_ids is None or cur==identity_ids,'horizon sample identity drift');identity_ids=cur
    require(set(d.horizon)==set(HORIZONS),'extra horizon')
    folds=frames['fold_training_audit.csv']; require(len(folds)==35 and (folds.max_train_label_idx<=folds.cutoff_idx).all(),'maturity audit failed')
    require(folds.status.eq('SCORED').all() and (folds.train_n==folds.train_event_n+folds.train_background_n).all(),'fit audit counts')
    for r in folds.itertuples():
        f=d.loc[(d.info_year==r.year)&(d.horizon==r.horizon)]
        require(len(f)==r.test_event_n and f.fit_cutoff_idx.eq(r.cutoff_idx).all(),'fold identity/forecast cutoff')
    prefixes=frames['prefix_identity_audit.csv']; require(len(prefixes)==5 and prefixes.identities_equal.all() and prefixes.max_feature_difference.eq(0).all(),'inherited prefix audit')
    scored=frames['scores.csv']; comparisons=[]; parts=[]; annual=[]
    for h in HORIZONS:
        f=d.loc[d.horizon==h]
        for name,g in groups(f):
            q=decompose(g.target_bp,g.parent_prediction_bp,g.enhanced_prediction_bp)
            q['past_mean_forecast_mse_bp2']=float(np.mean((g.target_bp-g.past_mean_bp)**2))
            q['parent_mean_error_bp']=-q['parent_residual_mean_y_minus_prediction_bp']
            q['enhanced_mean_error_bp']=-q['enhanced_residual_mean_y_minus_prediction_bp']
            z=scored.loc[(scored.scope=='EVENT')&(scored.horizon==h)&(scored.group==name)]
            require(len(z)==1,'missing/duplicate stored score group '+name)
            ref=z.iloc[0];require(int(ref.n)==len(g),'score denominator')
            for col in sorted(set(q)&set(scored.columns)-{'n'}):
                err=close(q[col],float(ref[col]),'published EVENT score '+col)
                comparisons.append({'horizon':h,'group':name,'field':col,'absolute_error':err})
            parts.append({'horizon':h,'group':name,**q})
        pool=decompose(f.target_bp,f.parent_prediction_bp,f.enhanced_prediction_bp)
        annual.append({'horizon':h,**annual_partition(f,pool)})
    observation=d[['entry_idx','info_idx','info_day','info_year','parent_direction','horizon','target_bp','parent_prediction_bp','enhanced_prediction_bp']].copy()
    observation['parent_residual_bp']=d.target_bp-d.parent_prediction_bp
    observation['prediction_adjustment_bp']=d.enhanced_prediction_bp-d.parent_prediction_bp
    observation['alignment_bp2']=2*observation.parent_residual_bp*observation.prediction_adjustment_bp
    observation['adjustment_square_bp2']=observation.prediction_adjustment_bp**2
    observation['loss_gain_bp2']=observation.alignment_bp2-observation.adjustment_square_bp2
    daily=frames['daily_loss_accounting.csv']
    for h in HORIZONS:
        f=d.loc[d.horizon==h]; a=daily.loc[daily.horizon==h]
        require(len(a)==1218 and not a.info_day.duplicated().any(),'calendar denominator changed')
        by=f.groupby('info_day').agg(n=('entry_idx','size'),loss=('loss_improvement_bp2','sum'),p0=('parent_squared_error','sum'),p1=('enhanced_squared_error','sum')).reindex(a.info_day,fill_value=0)
        for oldcol,newcol in [('n','n'),('loss_sum_bp2','loss'),('parent_sse_bp2','p0'),('enhanced_sse_bp2','p1')]:
            close(a[oldcol].to_numpy(),by[newcol].to_numpy(),'daily '+oldcol)
    params=parameter_accounting(frames['model_parameters.csv'],d)
    output.mkdir(parents=True)
    tables={'observation_accounting':observation,'error_decomposition':pd.DataFrame(parts),
            'year_partition':pd.DataFrame(annual),'parameter_adjustment_accounting':params,
            'published_score_reconciliation':pd.DataFrame(comparisons),
            'cross_study_evidence':pd.DataFrame(registry['studies']),
            'source_integrity':pd.DataFrame(source_meta)}
    for name,f in tables.items(): f.to_csv(output/(name+'.csv'),index=False,float_format='%.15g')
    try: head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    except (OSError,subprocess.CalledProcessError): head=None
    receipt={'schema_id':'factorlab_r1a_evidence_closeout_receipt@1.0',
       'decision':'EVIDENCE_RECONCILIATION_COMPLETED_NO_NEW_ALPHA_TEST',
       'baseline_commit':BASELINE,'freeze_commit':'29bd543948f6de0f0860ecede71a10e78b9f31c8',
       'freeze_sha256':sha(root/FREEZE),'source_registry_sha256':sha(root/REGISTRY),
       'code_commit':head,'github_run_id':os.environ.get('GITHUB_RUN_ID'),
       'original_forecast_receipt_sha256':sha(rp),'new_model_fits':0,'new_signal_generation':0,
       'new_strategy_returns':0,'raw_market_files_read':[],'new_significance_tests':False,
       'original_events':1752,'warmup_events':645,'scored_events_each_horizon':1107,
       'audited_event_score_groups':126,'reconciled_score_fields':len(comparisons),
       'max_published_score_absolute_error':max(x['absolute_error'] for x in comparisons),
       'max_algebra_identity_error_bp2':max(x['max_identity_error_bp2'] for x in parts),
       'audited_parameter_rows':1225,'audited_prior_fit_records':35,'audited_prior_prefix_records':5,
       'audit_discrepancy':'NONE_DETECTED_WITHIN_PINNED_EVIDENCE_AND_ARITHMETIC_SCOPE',
       'audit_limit':'Not independent raw-source validation or a full signal-engine/model-specification correctness proof. Existing source and inferential limitations remain.',
       'year_partition':json.loads(pd.DataFrame(annual).to_json(orient='records',double_precision=15)),
       'table_rows':{k+'.csv':len(f) for k,f in tables.items()},
       'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.glob('*.csv'))],
       'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
       'confirmation_protocol_frozen':False,'confirmation_clock_started':False,'horizon_selected':False}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    text=['# R1_A existing-evidence reconciliation and error accounting','',receipt['decision'],'',
      'No model was fitted, no raw price loaded, no old result rewritten. Accounting is not another independent experiment.',
      '', '| h | mean gain bp^2 | within-year mean-bias-square reduction bp^2 | within-year centered-error variance reduction bp^2 |',
      '|---:|---:|---:|---:|']
    for r in annual: text.append(f"| {r['horizon']} | {r['total_gain_bp2']:.6f} | {r['weighted_within_year_bias_square_reduction_bp2']:.6f} | {r['weighted_within_year_centered_error_variance_reduction_bp2']:.6f} |")
    text.extend(['','Year contributions are weighted by the unchanged number of scored events, not equally weighted years.',
      'Pooled centering and within-year centering are different decompositions of the same total, not contradictory results.',
      'The added indicator is constant on event rows inside each annual fold. Shared coefficients were jointly refitted in the OLD experiment. The identity-defined remainder is not causal attribution.',
      'Ex-post bias removal is an explanatory accounting term, NOT a proposed deployable correction, new fitted intercept or noise reduction.',
      'Small MSE percentages alone do not establish economic insignificance; no gain is converted to trading bp.',
      'The absence of a detected arithmetic discrepancy does not close source-provenance, dependence, model adequacy or historical reuse limitations.',
      '', 'Program-level resource judgment is recorded separately in the closeout review. No automatic replacement model is authorized.'])
    (output/'REPORT.md').write_text('\n'.join(text)+'\n')
    print(json.dumps({k:receipt[k] for k in ['decision','new_model_fits','audited_event_score_groups','reconciled_score_fields','max_published_score_absolute_error','table_rows','year_partition']},indent=2))
    return receipt


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(args.root.resolve(),args.output.resolve())


if __name__=='__main__': main()
