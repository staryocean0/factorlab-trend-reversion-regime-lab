"""Post-measurement source-schema audit. No new return, lead-lag or repair test.

The original schema inspection exposed fill/eligibility/as-of fields. Inspect
those fields and existing zero-volume/clock anomalies, without editing the
original freeze, masks or receipt. A vendor's asserted eligibility is not
independent exchange verification. Ingestion time is not a live availability claim.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from research.etf_index_measurability.audit import (
    MAPS,PACK,YEARS,FREEZE,sha,checked_path,index_clock,etf_clock,validity,dump,require,assert_blob,
)
FIELDS=('causal_flat_fill','high_frequency_analysis_eligible','source_minute_count',
        'source_kind','signal_price_view','fill_price_view','data_contract','export_frequency',
        'dataset_version','export_view_id')


def run(root,output):
    require(not output.exists(),'fresh output required')
    f=json.loads((root/FREEZE).read_text())
    for path,blob in f['source_guards'].items(): assert_blob(root/path,blob)
    m=json.loads((root/'data/manifest.json').read_text())
    flags=[]; clocks=[]; examples=[]; sources=[]
    for carrier,symbol in MAPS.items():
        em=json.loads((root/PACK/(carrier+'.json')).read_text())
        etf={int(s['path'].split('_')[-1].split('.')[0]):s for s in em['files']}
        for y in YEARS:
            spec=next(s for s in m['files'] if s['symbol']==symbol and s['frequency']=='1m' and s['year']==y)
            path=checked_path(root,spec); columns=pq.read_schema(path).names
            chosen=['symbol','timestamp','trading_day']+[c for c in FIELDS+('available_at','ingested_at') if c in columns]
            ix=pd.read_parquet(path,columns=chosen); times=index_clock(ix)
            sources.append({'path':spec['path'],'sha256':sha(path),'columns_read':chosen})
            for field in FIELDS:
                counts=ix[field].astype(str).value_counts(dropna=False).sort_index() if field in ix else pd.Series({'FIELD_ABSENT':len(ix)})
                for value,n in counts.items(): flags.append({'symbol':symbol,'year':y,'field':field,'value':str(value),'rows':int(n)})
            for field in ('available_at','ingested_at'):
                if field in ix:
                    s=ix[field].astype(str)
                    flags.append({'symbol':symbol,'year':y,'field':field+'_first_and_last','value':json.dumps([s.iloc[0],s.iloc[-1]]),'rows':len(s)})
            ep=checked_path(root,etf[y]); tape=pd.read_csv(ep,dtype={'symbol':str}); tape.index=etf_clock(tape.timestamp)
            missing=times[~times.isin(tape.index)]; extra=tape.index[~tape.index.isin(times)]
            for kind,stamps in [('MISSING_ETF_LABEL',missing),('EXTRA_ETF_LABEL',extra)]:
                q=pd.DataFrame({'day':stamps.strftime('%Y-%m-%d'),'clock':stamps.strftime('%H:%M')})
                for day,g in q.groupby('day',sort=True):
                    clocks.append({'carrier':carrier,'year':y,'kind':kind,'day':day,'rows':len(g),'first_clock':g.clock.min(),'last_clock':g.clock.max()})
            valid,v,p=validity(tape)
            nonflat=valid&(v==0)&~np.isclose(p[:,1],p[:,2],rtol=0,atol=1e-12)
            # Fixed earliest three examples per carrier-year, never ranked by returns.
            for row in tape.loc[nonflat].sort_index().head(3).itertuples():
                examples.append({'carrier':carrier,'year':y,'timestamp':str(row.Index),'open':row.open,'high':row.high,'low':row.low,'close':row.close,'volume':row.volume})
    output.mkdir(parents=True)
    pd.DataFrame(flags).to_csv(output/'index_source_flags.csv',index=False)
    pd.DataFrame(clocks,columns=['carrier','year','kind','day','rows','first_clock','last_clock']).to_csv(output/'daily_clock_anomalies.csv',index=False)
    pd.DataFrame(examples,columns=['carrier','year','timestamp','open','high','low','close','volume']).to_csv(output/'earliest_nonflat_zero_volume_examples.csv',index=False)
    r={'schema_id':'factorlab_etf_measurement_source_supplement@1.0',
       'role':'POST_MEASUREMENT_METADATA_AND_ROW_QUALITY_INSPECTION_NOT_A_NEW_REVERSION_EXPERIMENT',
       'reason':'Initial schema exposed fill/analysis-eligibility/as-of fields; original summaries are not revised.',
       'original_measurement_receipt_sha256':sha(root/'docs/ops/evidence/etf_index_measurability_20260912/receipt.json'),
       'sources':sources,'row_counts':{'flag_rows':len(flags),'clock_anomaly_days':len(clocks),'zero_volume_examples':len(examples)},
       'original_source_bytes_changed':False,'original_measurement_masks_changed':False,
       'new_returns_or_signals_computed':False,'R1A_disposition_unchanged':True,
       'BLACKBOX_query_count':3,'production_authority':False,'fresh_oos':False,
       'files':[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.iterdir())]}
    dump(output/'receipt.json',r)
    print(json.dumps({'row_counts':r['row_counts'],'flag_values':flags},ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); run(a.root.resolve(),a.output.resolve())
