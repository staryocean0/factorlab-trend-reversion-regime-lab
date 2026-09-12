"""Strict replay comparison; immutable source/reference hashes stay exact.

Floating tolerances apply ONLY to listed computed float columns. Identities,
seeds, counts, categories, flags, row ordering and missing-value masks are exact.
No reference file, random seed, inference method or statistical gate is changed.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

ATOL = Decimal('1e-12')
RTOL = Decimal('1e-12')
REFERENCE_BLOB = 'd98e09fc84b0db513bfa7aca389244534b03ae16'
CELL_FLOATS = {
    'rho_ASSUMED', 'lambda_nuisance', 'marginal_SD_target_bp',
    'oracle_mean_SE_under_DGP_bp', 'null_rejection_rate', 'null_MC95_lo',
    'null_MC95_hi', 'valid_fraction', 'mean_reported_SE_bp',
    'mean_family14_interval_width_bp',
} | {f'power_positive_family14_effect{d}bp_ASSUMED' for d in (2, 4, 6)} | {
    f'power_effect{d}_MC95_{side}' for d in (2, 4, 6) for side in ('lo', 'hi')}
CONFIG = {
    'all_method_DGP_design_cells.csv': (['id', 'DGP_ASSUMED', 'method'], CELL_FLOATS),
    'joint_family_null_checks.csv': (
        ['DGP_ASSUMED', 'method', 'family'],
        {'joint_rejection_rate', 'MC95_lo', 'MC95_hi', 'complete_quantification_fraction'}),
    'information_budget_NOT_commitment.csv': (
        ['layer', 'index_symbol', 'horizon', 'effect_bp_ASSUMED', 'family_size', 'budget_trading_days'],
        {'target_power', 'prior_required_days_CONDITIONAL', 'required_variance_ratio',
         'required_variance_reduction', 'required_information_multiplier', 'balanced_independent_controls_limit_ratio'}),
    'multiple_control_bounds_ASSUMPTIONS.csv': (
        ['K_controls', 'control_error_correlation_ASSUMED'],
        {'variance_ratio_balanced_model', 'information_multiplier_balanced_model'}),
}


class ReplayError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ReplayError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        require(bool(columns) and len(columns) == len(set(columns)), 'invalid CSV header')
        rows = list(reader)
    require(all(set(row) == set(columns) and all(v is not None for v in row.values()) for row in rows), 'ragged CSV')
    return columns, rows


def compare_csv(reference: Path, replay: Path, keys: list[str], float_columns: set[str]) -> dict:
    ca, a = read_csv(reference); cb, b = read_csv(replay)
    require(ca == cb and len(a) == len(b), 'schema or row count changed: '+reference.name)
    require(set(keys) <= set(ca) and float_columns <= set(ca), 'unrecognized comparison schema')
    ka = [tuple(row[k] for k in keys) for row in a]
    kb = [tuple(row[k] for k in keys) for row in b]
    require(len(ka) == len(set(ka)) and len(kb) == len(set(kb)), 'duplicate keys')
    require(ka == kb, 'row identities/order changed')
    floats = {c: {'different_text_cells': 0, 'different_numeric_cells': 0,
                  'max_absolute_difference': Decimal(0), 'max_scaled_difference': Decimal(0),
                  'out_of_tolerance_cells': 0} for c in sorted(float_columns)}
    exact = {c: 0 for c in ca if c not in float_columns}
    missing_mask_errors = 0
    examples = []
    for row_number, (x, y) in enumerate(zip(a, b, strict=True), start=2):
        for c in ca:
            if c not in float_columns:
                if x[c] != y[c]:
                    exact[c] += 1
                    if len(examples) < 8:
                        examples.append({'row': row_number, 'column': c, 'reference': x[c], 'replay': y[c]})
                continue
            if (x[c] == '') != (y[c] == ''):
                missing_mask_errors += 1
                continue
            if x[c] == '':
                continue
            try:
                av, bv = Decimal(x[c]), Decimal(y[c])
            except InvalidOperation as exc:
                raise ReplayError('invalid float literal in '+c) from exc
            require(av.is_finite() and bv.is_finite(), 'nonfinite computed float in '+c)
            delta = abs(av-bv); scale = max(abs(av), abs(bv))
            allowed = ATOL+RTOL*scale
            f = floats[c]
            f['different_text_cells'] += int(x[c] != y[c])
            f['different_numeric_cells'] += int(av != bv)
            f['max_absolute_difference'] = max(f['max_absolute_difference'], delta)
            f['max_scaled_difference'] = max(f['max_scaled_difference'], delta/max(Decimal(1), scale))
            if delta > allowed:
                f['out_of_tolerance_cells'] += 1
                if len(examples) < 8:
                    examples.append({'row': row_number, 'column': c, 'reference': x[c], 'replay': y[c]})
    passed = (not any(exact.values()) and missing_mask_errors == 0
              and not any(f['out_of_tolerance_cells'] for f in floats.values()))
    return {'path': reference.name, 'rows': len(a), 'columns': len(ca),
            'reference_sha256': sha(reference), 'replay_sha256': sha(replay),
            'byte_identical': reference.read_bytes() == replay.read_bytes(),
            'exact_column_mismatches': exact, 'missing_mask_mismatches': missing_mask_errors,
            'float_columns': {k: {q: str(v) if isinstance(v, Decimal) else v for q, v in f.items()} for k, f in floats.items()},
            'mismatch_examples': examples, 'pass': passed}


def compare_json_tight(actual, expected, where='root') -> None:
    require(type(actual) is type(expected), 'JSON type changed: '+where)
    if isinstance(expected, dict):
        require(set(actual) == set(expected), 'JSON keys changed: '+where)
        for k in expected:
            compare_json_tight(actual[k], expected[k], where+'.'+k)
    elif isinstance(expected, list):
        require(len(actual) == len(expected), 'JSON length changed: '+where)
        for i, (a, b) in enumerate(zip(actual, expected, strict=True)):
            compare_json_tight(a, b, where+f'[{i}]')
    elif isinstance(expected, float):
        require(math.isfinite(actual) and math.isfinite(expected), 'nonfinite JSON float')
        require(math.isclose(actual, expected, rel_tol=float(RTOL), abs_tol=float(ATOL)), 'JSON numeric mismatch: '+where)
    else:
        require(actual == expected, 'JSON exact value changed: '+where)


def audit(reference: Path, replay: Path, output: Path) -> dict:
    require(reference.resolve() != replay.resolve(), 'independent replay path required')
    require(not output.exists(), 'new audit receipt path required')
    raw = (reference/'method_receipt.json').read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    require(blob == REFERENCE_BLOB, 'immutable reference receipt changed')
    original = json.loads(raw); fresh = json.loads((replay/'method_receipt.json').read_text())
    fields = ['decision','freeze_sha256','seed','joint_model_replicates','synthetic_design_datasets',
              'design_count','method_count','inputs','geometry','method_screen','table_rows',
              'methods_clearing_limited_screen','real_R1A_means_retested','new_price_data_read',
              'real_matching_changed','missing_outcomes_imputed','BLACKBOX_query_count',
              'production_authority','fresh_oos','confirmation_protocol_frozen','confirmation_clock_started',
              'horizon_selected','interpretation']
    for k in fields:
        compare_json_tight(fresh[k], original[k], k)
    old_files = {s['path']: s for s in original['output_csvs']}
    new_files = {s['path']: s for s in fresh['output_csvs']}
    require(set(old_files) == set(new_files) == set(CONFIG), 'output list changed')
    tables = []
    for name, (keys, floats) in CONFIG.items():
        for directory, specs in ((reference, old_files), (replay, new_files)):
            p = directory/name
            require(p.is_file() and sha(p) == specs[name]['sha256'] and p.stat().st_size == specs[name]['bytes'], 'receipt/file hash mismatch: '+name)
        tables.append(compare_csv(reference/name, replay/name, keys, floats))
    passed = all(t['pass'] for t in tables)
    result = {'schema_id': 'factorlab_r1a_method_replay_numeric_audit@1.0',
              'decision': 'REPLAY_EXACT_DISCRETE_AND_TIGHT_FLOAT_PASS' if passed else 'REPLAY_MISMATCH_FAIL',
              'initial_failed_run': 34663153780, 'audit_github_run_id': os.environ.get('GITHUB_RUN_ID'),
              'reference_code_commit': original['code_commit'], 'replay_code_commit': fresh['code_commit'],
              'reference_receipt_blob_sha1': REFERENCE_BLOB, 'reference_bytes_unchanged': True,
              'statistical_rules_changed': False, 'float_atol': str(ATOL), 'float_rtol': str(RTOL),
              'integer_counts_seeds_flags_and_identities_exact': True,
              'tables': tables, 'production_authority': False, 'fresh_oos': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--replay', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = audit(a.reference, a.replay, a.output)
    return 0 if result['decision'] == 'REPLAY_EXACT_DISCRETE_AND_TIGHT_FLOAT_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
