"""ETF/index minute-data measurability, NOT a premium or reversion backtest."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

FREEZE = 'docs/governance/ETF_INDEX_MEASURABILITY_FREEZE@1.0.json'
PACK = 'data/r1a_carrier_prices/cloud_pack_v1'
MAPS = {'512100.SH': '000852.SH', '588000.SH': '000688.SH'}
YEARS = tuple(range(2021, 2026))
TICK = .001
Q = (.5, .9, .95, .99)
DECISION = 'MEASUREMENT_SCREEN_COMPLETED_MICROSTRUCTURE_IDENTIFICATION_BLOCKED'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def assert_blob(path, expected):
    raw = Path(path).read_bytes()
    actual = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    require(actual == expected, 'pinned source changed: '+str(path))


def checked_path(root, spec):
    path = (root/spec['path']).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(), 'missing/escaping source')
    require(path.stat().st_size == spec['bytes'] and sha(path) == spec['sha256'], 'source hash/bytes mismatch')
    return path


def etf_clock(series):
    s = series.astype(str)
    require(s.str.contains(r'(?:Z|[+-]\d{2}:\d{2})$').all(), 'ETF canonical time must include timezone')
    x = pd.DatetimeIndex(pd.to_datetime(s, utc=True, format='mixed')).tz_convert('Asia/Shanghai')
    check_clock(x)
    return x


def index_clock(frame):
    # Source encoding follows the pinned existing reader, NOT ISO-Z reinterpretation.
    x = pd.DatetimeIndex(pd.to_datetime(frame.timestamp.astype(str).str[:19])).tz_localize('Asia/Shanghai')
    check_clock(x)
    require(np.array_equal(x.strftime('%Y-%m-%d'), frame.trading_day.astype(str)), 'index day/label mismatch')
    return x


def check_clock(x):
    require(not x.has_duplicates and not x.hasnans, 'duplicate/missing timestamp')
    require((x.second == 0).all() and (x.microsecond == 0).all() and (x.nanosecond == 0).all(), 'not minute label')
    require(np.isin(x.year, YEARS).all(), 'outside 2021-2025 scope')


def session(times):
    m = times.hour*60+times.minute
    return np.where((m >= 571)&(m <= 690), 1, np.where((m >= 781)&(m <= 900), 2, 0))


def consecutive(times):
    out = np.zeros(len(times), dtype=bool)
    if len(times) > 1:
        s = session(times)
        out[1:] = ((np.diff(times.asi8) == 60_000_000_000) &
                   (times.strftime('%Y-%m-%d')[1:] == times.strftime('%Y-%m-%d')[:-1]) &
                   (s[1:] == s[:-1]) & (s[1:] > 0))
    return out


def validity(frame):
    p = frame[['open','high','low','close']].apply(pd.to_numeric, errors='coerce').to_numpy(float)
    v = pd.to_numeric(frame.volume, errors='coerce').to_numpy(float)
    valid = np.isfinite(p).all(axis=1)&(p > 0).all(axis=1)&np.isfinite(v)&(v >= 0)
    valid &= (p[:,2] <= np.minimum(p[:,0],p[:,3])) & (p[:,1] >= np.maximum(p[:,0],p[:,3])) & (p[:,2] <= p[:,1])
    return valid, v, p


def grid_departures(p):
    ok = np.isfinite(p)&(p > 0)
    departures = np.zeros_like(ok, dtype=bool)
    departures[ok] = np.abs(p[ok]/TICK-np.rint(p[ok]/TICK)) > 1e-6
    return departures


def observations(index, tape, ex_dates):
    times = index.index
    require(times.is_monotonic_increasing and tape.index.is_monotonic_increasing, 'unsorted clock')
    joined = tape.reindex(times)  # no fill, nearest timestamp or row-offset substitution
    valid, volume, p = validity(joined)
    present = times.isin(tape.index)
    status = np.where(~present, 'MISSING', np.where(~valid, 'INVALID_OHLCV', np.where(volume == 0, 'ZERO_VOLUME', 'POSITIVE_VOLUME')))
    good = status == 'POSITIVE_VOLUME'
    ix = pd.to_numeric(index.close, errors='coerce').to_numpy(float)
    ixok = np.isfinite(ix)&(ix > 0)
    continuous = consecutive(times)
    prior_good = np.r_[False, good[:-1]]
    prior_ixok = np.r_[False, ixok[:-1]]
    action = np.isin(times.strftime('%Y-%m-%d'), ex_dates)
    reason = np.full(len(times), 'ELIGIBLE', dtype=object)
    reason[~continuous] = 'SESSION_OR_CLOCK_BOUNDARY'
    reason[continuous & (~ixok | ~prior_ixok)] = 'INVALID_INDEX_ENDPOINT'
    remaining = continuous & ixok & prior_ixok
    reason[remaining & action] = 'DECLARED_ACTION_DAY'
    reason[remaining & ~action & (~good | ~prior_good)] = 'ETF_ENDPOINT_UNAVAILABLE'
    eligible = reason == 'ELIGIBLE'
    require(not (eligible & (~good | ~prior_good | ~continuous | action)).any(), 'comparison eligibility contradiction')
    out = pd.DataFrame({'timestamp': times.astype(str), 'month': times.strftime('%Y-%m'), 'year': times.year,
                        'status': status, 'index_valid': ixok, 'action_day': action,
                        'comparison_status': reason, 'grid_departure': grid_departures(p).any(axis=1)}, index=times)
    flat = np.isclose(p[:,1],p[:,2],rtol=0,atol=1e-12)
    out['positive_flat_bar'] = good & flat
    out['zero_nonflat_bar'] = (status == 'ZERO_VOLUME') & ~flat
    out['range_bp'] = np.nan
    out.loc[good,'range_bp'] = 1e4*(p[good,1]-p[good,2])/p[good,3]
    for col in ('gap_abs_bp','tick_bp','gap_reference_ticks','close_unchanged'):
        out[col] = np.nan
    k = np.flatnonzero(eligible)
    e, e0, i, i0 = p[k,3], p[k-1,3], ix[k], ix[k-1]
    gap = np.abs(1e4*(np.log(e/e0)-np.log(i/i0)))
    tick = 1e4*TICK/e0
    out.loc[eligible,'gap_abs_bp'] = gap
    out.loc[eligible,'tick_bp'] = tick
    out.loc[eligible,'gap_reference_ticks'] = gap/tick
    out.loc[eligible,'close_unchanged'] = np.isclose(e,e0,rtol=0,atol=1e-12).astype(float)
    require(np.isfinite(out.loc[eligible,['gap_abs_bp','tick_bp','gap_reference_ticks']].to_numpy(float)).all(), 'nonfinite comparison')
    return out


def quantiles(values, prefix):
    x = np.asarray(values, float); x = x[np.isfinite(x)]
    return {prefix+'_p'+str(round(q*100)): float(np.quantile(x,q)) if len(x) else None for q in Q}


def summarize(frame, carrier, index_symbol, period):
    n = len(frame); eligible = frame.comparison_status == 'ELIGIBLE'; good = frame.status == 'POSITIVE_VOLUME'
    out = {'carrier': carrier, 'index_symbol': index_symbol, 'period': str(period), 'index_records': n}
    for st in ('MISSING','INVALID_OHLCV','ZERO_VOLUME','POSITIVE_VOLUME'):
        out[st.lower()+'_records'] = int((frame.status == st).sum())
    for st in ('SESSION_OR_CLOCK_BOUNDARY','INVALID_INDEX_ENDPOINT','DECLARED_ACTION_DAY','ETF_ENDPOINT_UNAVAILABLE','ELIGIBLE'):
        out[st.lower()+'_comparisons'] = int((frame.comparison_status == st).sum())
    require(sum(out[st.lower()+'_records'] for st in ('MISSING','INVALID_OHLCV','ZERO_VOLUME','POSITIVE_VOLUME')) == n, 'record count mismatch')
    require(sum(out[st.lower()+'_comparisons'] for st in ('SESSION_OR_CLOCK_BOUNDARY','INVALID_INDEX_ENDPOINT','DECLARED_ACTION_DAY','ETF_ENDPOINT_UNAVAILABLE','ELIGIBLE')) == n, 'comparison count mismatch')
    out.update(record_coverage=(n-out['missing_records'])/n if n else None,
               positive_volume_coverage=float(good.mean()) if n else None,
               invalid_index_records=int((~frame.index_valid).sum()),
               declared_action_records=int(frame.action_day.sum()),
               off_grid_ohlc_records=int(frame.grid_departure.sum()),
               zero_nonflat_records=int(frame.zero_nonflat_bar.sum()),
               positive_flat_bar_fraction=float(frame.loc[good,'positive_flat_bar'].mean()) if good.any() else None,
               positive_close_repeat_fraction=float(frame.loc[eligible,'close_unchanged'].mean()) if eligible.any() else None,
               gap_at_most_one_reference_tick_fraction=float((frame.loc[eligible,'gap_reference_ticks'] <= 1).mean()) if eligible.any() else None)
    for col in ('gap_abs_bp','tick_bp','gap_reference_ticks'):
        out.update(quantiles(frame.loc[eligible,col],col))
    out.update(quantiles(frame.loc[good,'range_bp'],'etf_minute_range_bp'))
    return out


def synthetic_equivalence():
    # Two distinct unobserved efficient-price processes produce the SAME observed bars.
    trades = np.array([[.999,1.001,.999],[1.001,.999,1.001],[.999,1.001,.999]], float)
    observed = np.column_stack([trades[:,0],trades.max(axis=1),trades.min(axis=1),trades[:,-1],np.full(3,300.)])
    flat_fair = np.ones_like(trades)
    moving_fair = trades.copy()
    # World A: trades alternate on quotes about a flat fair price. World B: trades at the moving fair price.
    require(not np.array_equal(flat_fair,moving_fair), 'latent paths must differ')
    return {'synthetic_only': True, 'same_observed_ohlcv': np.array_equal(observed,observed.copy()),
            'world_A_efficiency': 'flat fair value; +/-0.001 trade-price bounce',
            'world_B_efficiency': 'efficient price follows the prints; no trade-price noise',
            'world_A_fair_close': flat_fair[:,-1].tolist(), 'world_B_fair_close': moving_fair[:,-1].tolist(),
            'observed_ohlcv': observed.tolist(),
            'separate_reference_example': {'ETF_last': 1.001,'index_sample': 100.,
                 'interpretation_A': 'synchronous fair ETF value 1.000, ETF above it',
                 'interpretation_B': 'current fair ETF value 1.001, index sample reflects older fair value 1.000'},
            'conclusion': 'OHLCV and sampled index values alone do not identify trade noise versus efficient-price change or reference lag; this is not a claim about actual gap frequency.'}


def run(root, output):
    require(not output.exists(), 'use a fresh output directory; never overwrite evidence')
    freeze = json.loads((root/FREEZE).read_text())
    require(freeze['maps'] == MAPS and freeze['formulas']['reference_tick_cny'] == TICK, 'scope drift')
    require(not freeze['reversion_outcomes_authorized'] and not freeze['production_authority'], 'authority drift')
    for path, blob in freeze['source_guards'].items():
        assert_blob(root/path, blob)
    im = json.loads((root/'data/manifest.json').read_text())
    sources, summaries, clock_extras, capabilities = [], [], [], []
    for carrier, symbol in MAPS.items():
        manifest_path = root/PACK/(carrier+'.json'); m = json.loads(manifest_path.read_text())
        require(m['symbol'] == carrier and m['frequency'] == '1m' and m['price_basis'] == 'unadjusted_actual_traded_OHLC', 'carrier schema drift')
        require(m['research_use_authorized'] is True, 'missing research authorization')
        expected = [f'{PACK}/prices/{carrier[:6]}_{y}.csv' for y in YEARS]
        require(sorted(s['path'] for s in m['files']) == expected, 'carrier file scope changed')
        ep = []
        for spec in m['files']:
            p = checked_path(root,spec); f = pd.read_csv(p, dtype={'symbol':str})
            require(len(f) == spec['rows'] and set(f.symbol) == {carrier}, 'ETF row/identity mismatch')
            require({'symbol','timestamp','open','high','low','close','volume'} <= set(f), 'ETF schema incomplete')
            f.index = etf_clock(f.timestamp); ep.append(f)
            _, _, prices = validity(f)
            sources.append({**spec, 'kind':'ETF_OHLCV', 'symbol':carrier, 'columns':';'.join(f.columns), 'off_grid_values':int(grid_departures(prices).sum())})
        tape = pd.concat(ep).sort_index(); require(not tape.index.has_duplicates, 'duplicate combined ETF clock')
        spec = m['corporate_actions_file']; p = checked_path(root,spec)
        actions = pd.read_csv(p, dtype=str)
        require(len(actions) == spec['rows'] and {'symbol','ex_date','event_type','source_reference'} <= set(actions), 'action schema/rows')
        require(actions.empty or set(actions.symbol) == {carrier}, 'action identity')
        ex_dates = sorted(set(pd.to_datetime(actions.ex_date,format='%Y-%m-%d').dt.strftime('%Y-%m-%d')))
        sources.append({**spec,'kind':'DECLARED_ACTIONS','symbol':carrier,'columns':';'.join(actions.columns),'off_grid_values':0})
        ip = []; index_cols = set()
        selected = [s for s in im['files'] if s['symbol'] == symbol and s['frequency'] == '1m' and s['year'] in YEARS]
        require(sorted(s['year'] for s in selected) == list(YEARS), 'index partition scope')
        for spec in selected:
            p = checked_path(root,spec); cols = pq.read_schema(p).names; index_cols.update(cols)
            f = pd.read_parquet(p, columns=['symbol','timestamp','trading_day','close'])
            require(len(f) == spec['rows'] and set(f.symbol) == {symbol}, 'index rows/identity')
            f.index = index_clock(f); ip.append(f)
            sources.append({k:spec[k] for k in ('path','sha256','bytes','rows')} | {'kind':'INDEX_1M','symbol':symbol,'columns':';'.join(cols),'off_grid_values':0})
        index = pd.concat(ip).sort_index(); require(not index.index.has_duplicates, 'duplicate index clock')
        obs = observations(index,tape,ex_dates)
        summaries.append(summarize(obs,carrier,symbol,'ALL'))
        for y,g in obs.groupby('year',sort=True): summaries.append(summarize(g,carrier,symbol,y))
        for month,g in obs.groupby('month',sort=True): summaries.append(summarize(g,carrier,symbol,month))
        extra = tape.loc[~tape.index.isin(index.index)]
        if len(extra):
            extra = extra.assign(year=extra.index.year,clock=extra.index.strftime('%H:%M'))
            for (y,c),g in extra.groupby(['year','clock'],sort=True):
                clock_extras.append({'carrier':carrier,'year':int(y),'clock':c,'rows':len(g)})
        capabilities.append({'carrier':carrier,'index_symbol':symbol,'etf_columns':list(tape.columns),'index_columns':sorted(index_cols),
             'declared_action_ex_dates':ex_dates,'inherited_bar_label':m['bar_label'],
             'source_contract_status':'DECLARED_IN_PINNED_AUDIT_NOT_INDEPENDENT_EXCHANGE_MESSAGE_VERIFICATION',
             'synchronized_last_trade_asof':'NOT_ADMITTED', 'ETF_bid_ask_and_quote_age':'NOT_ADMITTED',
             'IOPV_or_basket_cash_valuation':'NOT_ADMITTED', 'index_constituent_asof':'NOT_ADMITTED',
             'can_report_label_clock_changes':bool((obs.comparison_status == 'ELIGIBLE').any()),
             'can_identify_efficient_price_repair':False,'true_NAV_premium_measured':False})
    output.mkdir(parents=True)
    pd.DataFrame(summaries).to_csv(output/'measurement_summary.csv',index=False,float_format='%.15g')
    pd.DataFrame(sources).to_csv(output/'source_files.csv',index=False)
    pd.DataFrame(clock_extras,columns=['carrier','year','clock','rows']).to_csv(output/'extra_clock_rows.csv',index=False)
    dump(output/'capabilities.json',capabilities)
    dump(output/'synthetic_nonidentification.json',synthetic_equivalence())
    # Only repository filenames. Never open an unrelated candidate data file.
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','--','data'],cwd=root,text=True).splitlines()
    named = [p for p in paths if re.search(r'(?:iopv|nav|pcf|constituent|basket|bid|ask|quote|snapshot)',p,re.I)]
    dump(output/'data_path_inventory.json',{'data_paths':len(paths),'candidate_names_only':named,
         'unrelated_file_contents_read':False,'limitation':'Path-name inventory does not exhaust unlabeled files or other repositories. MO quote names are not ETF quotes.'})
    receipt = {'schema_id':'factorlab_etf_index_measurability_receipt@1.0','decision':DECISION,
         'baseline_commit':freeze['baseline_commit'],'freeze_commit':'728e7e11b4750afd3048de18d8a7f910a257380a','freeze_sha256':sha(root/FREEZE),
         'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
         'source_files_verified':len(sources),'source_price_rows':sum(s['rows'] for s in sources if s['kind'] != 'DECLARED_ACTIONS'),
         'source_integrity_pass':True,'capabilities':capabilities,'pooled':[s for s in summaries if s['period'] == 'ALL'],
         'L0':'LABEL_CLOCK_DIAGNOSTICS_COMPLETE_CONDITIONAL_ON_SOURCE_SEMANTICS',
         'L1':'TIMED_QUOTES_AND_REFERENCE_DATA_NOT_ADMITTED; ECONOMIC_DEVIATION_NOT_IDENTIFIED',
         'L2':'REPAIR_RETURNS_LEADLAG_AND_EXECUTION_NOT_OPENED',
         'all_observed_gaps_artifacts_proven':False,'minimum_tick_is_spread_or_noise_bound':False,
         'new_model_fits':0,'R1A_events_read':False,'reversion_outcomes_read':False,'post2025_prices_read':False,
         'R1A_disposition_unchanged':True,'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
         'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.iterdir())]}
    dump(output/'receipt.json',receipt)
    print(json.dumps({'decision':DECISION,'pooled':receipt['pooled']},ensure_ascii=False,indent=2))
    return receipt


def verify(reference,replay):
    a=json.loads((reference/'receipt.json').read_text()); b=json.loads((replay/'receipt.json').read_text())
    for k in ('decision','freeze_sha256','source_files_verified','source_price_rows','L0','L1','L2','capabilities'):
        require(a[k] == b[k], 'replay mismatch '+k)
    for spec in a['files']:
        require(sha(reference/spec['path']) == spec['sha256'], 'reference evidence modified')
        require(sha(replay/spec['path']) == spec['sha256'], 'replay bytes differ '+spec['path'])
    print('PASS_DETERMINISTIC_MEASUREMENT_REPLAY_NOT_REVERSION_EVIDENCE')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--reference',type=Path)
    args=ap.parse_args(); run(args.root.resolve(),args.output.resolve())
    if args.reference: verify(args.reference,args.output)


if __name__ == '__main__': main()
