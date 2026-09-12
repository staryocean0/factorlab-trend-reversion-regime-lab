"""Apply strict value audits to older derived statistical tables, not raw data.

Each reference receipt is Git-blob pinned. Its CSV bytes must still match the
unchanged receipt. Only original floating-dtype non-key columns get the same
1e-12 replay tolerance; discrete columns, keys, ordering and missingness are exact.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import pandas as pd
from research.r1a_method_calibration.replay_audit import compare_csv, compare_json_tight, require, sha

STAGES = {
    'robustness': {
        'receipt': 'robustness_receipt.json', 'blob': 'b26e590a8d500cb56185d82dd4b4aeb3b461d21d',
        'files_key': 'output_csvs',
        'fields': ['decision','freeze_sha256','carriers','primary_family14_positive_cells','all_four_family56_positive_cells'],
        'keys': {
            'all_56_inference_cells.csv': ['carrier','horizon','spec'],
            'clock_disjoint_selection_audit.csv': ['carrier','horizon','pair_id'],
            'missing_residual_scenarios_NOT_ESTIMATES.csv': ['carrier','horizon','event_year','gamma_bp'],
            'robustness_overview.csv': ['carrier','horizon'],
        },
    },
    'feasibility': {
        'receipt': 'feasibility_receipt.json', 'blob': '6330d2437304052d4578966b2647dc5e925bd310',
        'files_key': 'files',
        'fields': ['decision','freeze_sha256','design_count','table_rows','historical_trading_days',
                   'primary_CSI1000_short_locations_NOT_selected','four_bp_budget_comparison_NOT_forecast',
                   'calibration_summary','simulated_samples','new_confirmation_prices_read','confirmation_protocol_frozen'],
        'keys': {
            'historical_noise_NOT_new_tests.csv': ['layer','index_symbol','horizon','spec'],
            'sample_size_scenarios_NOT_commitments.csv': ['layer','index_symbol','horizon','spec','effect_bp_ASSUMED','target_positive_detection','family_size'],
            'fixed_budget_power_NOT_forecasts.csv': ['layer','index_symbol','horizon','spec','budget_trading_days','effect_bp_ASSUMED','family_size'],
            'null_calibration_synthetic_DGPs.csv': ['layer','index_symbol','horizon','DGP_ASSUMED'],
            'historical_pair_rates.csv': ['layer','index_symbol','horizon','year'],
        },
    },
}


def inferred_float_columns(reference: Path, keys: list[str]) -> set[str]:
    frame = pd.read_csv(reference)
    return {c for c in frame if pd.api.types.is_float_dtype(frame[c]) and c not in keys}


def audit(stage: str, reference: Path, replay: Path, output: Path) -> dict:
    spec = STAGES[stage]
    require(not output.exists() and reference.resolve() != replay.resolve(), 'fresh audit/replay paths required')
    raw = (reference/spec['receipt']).read_bytes()
    got = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    require(got == spec['blob'], 'pinned historical receipt changed')
    a = json.loads(raw); b = json.loads((replay/spec['receipt']).read_text())
    for key in spec['fields']:
        compare_json_tight(b[key], a[key], key)
    old = {s['path']: s for s in a[spec['files_key']]}
    new = {s['path']: s for s in b[spec['files_key']]}
    require(set(old) == set(new) == set(spec['keys']), 'historical output list changed')
    tables = []
    for name, keys in spec['keys'].items():
        for directory, files in ((reference, old), (replay, new)):
            p = directory/name
            require(sha(p) == files[name]['sha256'], 'historical receipt/file hash mismatch')
            if 'bytes' in files[name]:
                require(p.stat().st_size == files[name]['bytes'], 'historical receipt/file size mismatch')
        floats = inferred_float_columns(reference/name, keys)
        tables.append(compare_csv(reference/name, replay/name, keys, floats))
    result = {'schema_id':'factorlab_prior_statistical_replay_value_audit@1.0', 'stage':stage,
              'decision':'REPLAY_EXACT_DISCRETE_AND_TIGHT_FLOAT_PASS' if all(t['pass'] for t in tables) else 'REPLAY_MISMATCH_FAIL',
              'github_run_id':os.environ.get('GITHUB_RUN_ID'),'reference_blob_sha1':spec['blob'],
              'reference_bytes_unchanged':True,'statistical_rules_changed':False,
              'float_atol':'1e-12','float_rtol':'1e-12','tables':tables,
              'production_authority':False,'fresh_oos':False}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=list(STAGES),required=True)
    p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--replay',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); result=audit(a.stage,a.reference,a.replay,a.output)
    return 0 if result['decision']=='REPLAY_EXACT_DISCRETE_AND_TIGHT_FLOAT_PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
