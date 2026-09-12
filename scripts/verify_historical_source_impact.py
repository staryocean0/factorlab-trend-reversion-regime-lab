"""Verify retained source-impact evidence without pinning current workflow prose.

The original scientific verifier is unchanged. Its seven purely operational or
module-docstring dependencies are read at the original pinned commit in a
throwaway compatibility directory. All other inputs come from CURRENT bytes
and must match the original receipt exactly. No workflow code is executed from
that directory and no original file is overwritten.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile

HISTORY = 'ef18bf905e9e427153650d5538a996249bb6a901'
EVIDENCE = 'docs/ops/evidence/etf_source_repair_20260912'
METADATA = frozenset({
    '.github/workflows/etf-index-measurability.yml',
    '.github/workflows/r1a-control-design.yml',
    '.github/workflows/r1a-development-noise-regression.yml',
    '.github/workflows/r1a-evidence-closeout.yml',
    '.github/workflows/r1a-walkforward-prediction.yml',
    '.github/workflows/r1b-mo-data-admission-gate.yml',
    'src/regime_lab/__init__.py',
})
RETIRED_WORKFLOW = '.github/workflows/r1b-mo-data-admission-gate.yml'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_path(root: Path, relative: str) -> Path:
    p = PurePosixPath(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'unsafe source path')
    candidate = root / relative
    require(candidate.resolve().is_relative_to(root.resolve()) and not candidate.is_symlink(), 'unsafe source target')
    return candidate


def verify_bytes(raw: bytes, spec: dict) -> None:
    require(len(raw) == int(spec['bytes']), 'pinned byte count: ' + spec['path'])
    require(hashlib.sha256(raw).hexdigest() == spec['sha256'], 'pinned SHA256: ' + spec['path'])
    actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(actual == spec['git_blob_sha1'], 'pinned Git identity: ' + spec['path'])


def metadata_eligible(path: str, current: bytes | None, historical: bytes) -> bool:
    if path not in METADATA:
        return False
    require(current is not None or path == RETIRED_WORKFLOW, 'current metadata unexpectedly missing')
    if path == 'src/regime_lab/__init__.py':
        for raw in (current, historical):
            tree = ast.parse(raw.decode('utf-8'))
            require(len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str),
                    'only module docstring may use historical metadata view')
    return True


def verify(root: Path) -> dict:
    from research.etf_source_repair import verify_retained as original
    root = root.resolve()
    require(original.BASE == HISTORY, 'original historical verifier changed')
    receipt = json.loads((root / EVIDENCE / 'receipt.json').read_text())
    pin_name = 'pinned_input_integrity.csv'
    pin_spec = next(s for s in receipt['files'] if s['path'] == pin_name)
    pin_bytes = (root / EVIDENCE / pin_name).read_bytes()
    require(len(pin_bytes) == pin_spec['bytes'] and hashlib.sha256(pin_bytes).hexdigest() == pin_spec['sha256'], 'pin ledger changed')
    with (root / EVIDENCE / pin_name).open(newline='') as f:
        pins = list(csv.DictReader(f))
    require(len({s['path'] for s in pins}) == len(pins), 'duplicate pinned source paths')
    metadata = []
    exact_current = 0
    before = {}
    # Inside root solely so the unmodified verifier's git-show discovers the
    # existing repository. No private data or checkout changes are introduced.
    with tempfile.TemporaryDirectory(prefix='.source-impact-compat-', dir=root) as tmp:
        view = Path(tmp)
        def put(path, raw):
            dest = safe_path(view, path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        for spec in pins:
            path = spec['path']
            p = safe_path(root, path)
            current = p.read_bytes() if p.is_file() else None
            before[path] = hashlib.sha256(current).hexdigest() if current is not None else None
            if path in METADATA:
                historical = subprocess.check_output(['git', 'show', HISTORY + ':' + path], cwd=root)
                require(metadata_eligible(path, current, historical), 'not operational metadata')
                raw = historical
                metadata.append({'path': path, 'historical_commit': HISTORY,
                                 'historical_sha256': hashlib.sha256(raw).hexdigest(),
                                 'current_sha256': before[path], 'current_path_retired': current is None})
            else:
                require(current is not None, 'current scientific input missing: ' + path)
                raw = current
                exact_current += 1
            verify_bytes(raw, spec)
            put(path, raw)
        require({s['path'] for s in metadata} == METADATA, 'operational input inventory drift')
        extras = [original.OVERLAY, original.FREEZE, EVIDENCE + '/receipt.json']
        extras += [EVIDENCE + '/' + s['path'] for s in receipt['files']]
        action_manifest = 'data/etf_source_actions_v2/manifest.json'
        action = json.loads((root / action_manifest).read_text())
        extras += [action_manifest] + [s['path'] for s in action['known_action_files']]
        for path in sorted(set(extras)):
            put(path, safe_path(root, path).read_bytes())
        result = original.verify(view)
    for path, sha in before.items():
        p = safe_path(root, path)
        actual = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        require(actual == sha, 'current file changed during compatibility verification: ' + path)
    return {'status': 'CURRENT_SCIENTIFIC_BYTES_AND_PINNED_OPERATIONAL_HISTORY_VERIFIED',
            'pinned_inputs': len(pins), 'current_nonoperational_inputs_exact': exact_current,
            'operational_metadata_at_original_commit': metadata,
            'original_verifier_result_in_compatibility_view': result,
            'original_result_counts_refer_to_compatibility_view_not_current_workflows': True,
            'original_verifier_modified': False, 'source_files_modified': False,
            'new_market_experiment': False, 'production_authority': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    text = json.dumps(verify(args.root), ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text)
