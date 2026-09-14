"""Repository consistency gate; never fit models or compute market outcomes.

--render synchronizes managed documentation from REPOSITORY_STATE.json.
--check validates the Git index, current worktree text, source syntax, local
imports, workflow contracts, and baseline preservation. Historical source
snapshots are deliberately not rewritten or treated as current instructions.

A small set of current product documents is status-managed rather than
body-generated: their scientific status block still comes from the repository
state, while the roadmap/API/product body may evolve milestone by milestone.
"""
from __future__ import annotations
import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote

STATE = 'docs/REPOSITORY_STATE.json'
BASELINE = 'docs/maintenance/BASELINE_COMPONENTS.json'
AUTO_WORKFLOW = '.github/workflows/repository-consistency.yml'

STATUS_ONLY_DOCUMENTS = frozenset({
    'README.md',
    'CONTINUE_HERE.md',
    'docs/WHITEPAPER.md',
})
CURRENT_PRODUCT_DOCUMENTS = frozenset({
    'CHANGELOG.md',
    'docs/ROADMAP.md',
    'docs/API_CONTRACT.md',
    'docs/API_EXAMPLES.md',
    'docs/API_GAP_ANALYSIS.md',
    'docs/RELEASE.md',
    'docs/THREE_BUCKET_BASELINE.md',
})
_STATUS_PATTERN = re.compile(
    r'<!-- GENERATED: edit docs/REPOSITORY_STATE\.json, then --render -->'
    r'.*?'
    r'<!-- END GENERATED STATUS -->',
    re.DOTALL,
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def git_index(root: Path) -> dict[str, dict[str, str]]:
    out = subprocess.check_output(['git', 'ls-files', '-s', '-z'], cwd=root)
    entries = {}
    for line in out.split(b'\0'):
        if not line:
            continue
        meta, raw_name = line.split(b'\t', 1)
        mode, sha, stage = meta.decode().split()
        require(stage == '0', 'unmerged index entry')
        entries[raw_name.decode()] = {'mode': mode, 'git_blob': sha}
    return entries


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def status_block(path: str, state: dict) -> str:
    ref = os.path.relpath(STATE, str(PurePosixPath(path).parent))
    report = os.path.relpath(state['latest_review'], str(PurePosixPath(path).parent))
    return '\n'.join([
        '<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->',
        '> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。',
        '> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。',
        '> `BLACKBOX_query_count=' + str(state['BLACKBOX_query_count']) + '`；'
        '`production_authority=' + str(state['production_authority']).lower() + '`；'
        '`fresh_oos=' + str(state['fresh_oos']).lower() + '`。',
        '> 机器状态：`' + state['scientific_status'] + '`。',
        '> [状态源](' + ref + ') · [最新研究解释](' + report + ')',
        '<!-- END GENERATED STATUS -->',
    ])


def status_only_text(path: str, text: str, state: dict) -> str:
    replacement = status_block(path, state)
    if _STATUS_PATTERN.search(text):
        rendered = _STATUS_PATTERN.sub(replacement, text, count=1)
        return rendered if rendered.endswith('\n') else rendered + '\n'
    lines = text.splitlines()
    title = lines[0] if lines and lines[0].startswith('#') else '# ' + Path(path).stem
    suffix = '\n'.join(lines[1:]).strip() if lines else ''
    return title + '\n\n' + replacement + ('\n\n' + suffix if suffix else '') + '\n'


def local_target(path: str, target: str) -> str | None:
    if re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#)', target):
        return None
    target = unquote(target.split('#', 1)[0].split('?', 1)[0])
    if not target:
        return None
    require(not target.startswith('/'), 'absolute local documentation link: ' + target)
    resolved = os.path.normpath(str(PurePosixPath(path).parent / target)).replace(os.sep, '/')
    require(resolved != '..' and not resolved.startswith('../'), 'documentation link escapes repo')
    return resolved


def lifecycle(path: str, state: dict) -> str:
    if path in state['generated_documents'] or path == STATE:
        return 'CURRENT_GENERATED_AUTHORITY'
    if path in CURRENT_PRODUCT_DOCUMENTS:
        return 'CURRENT_PRODUCT_DOCUMENTATION'
    if path.startswith('docs/archive/'):
        return 'ARCHIVED_HISTORICAL_SOURCE'
    if path.startswith('data/'):
        return 'PRESERVED_SOURCE_NOT_NEW_ADMISSION'
    if path.startswith('docs/ops/evidence/'):
        return 'PRESERVED_EVIDENCE'
    if path.startswith('docs/research/'):
        return 'PRESERVED_RESEARCH_SNAPSHOT'
    if path.startswith('docs/governance/'):
        return 'FROZEN_OR_DISPOSITION_CONTRACT'
    if path.startswith('research/'):
        module = path.split('/')[1]
        require(module in state['modules'], 'unregistered research module: ' + module)
        return state['modules'][module]['status']
    if path.startswith('tests/'):
        return 'REGRESSION_TEST'
    if path.startswith(('src/', 'shared/')):
        return 'SUPPORT_CODE_NOT_PRODUCTION'
    if path.startswith('.github/workflows/'):
        require(path == AUTO_WORKFLOW or path in state['manual_workflows'], 'unregistered workflow: ' + path)
        return 'AUTOMATIC_CONSISTENCY_GATE' if path == AUTO_WORKFLOW else 'EXPLICIT_REPLAY_ONLY'
    if path.startswith(('scripts/', 'docs/maintenance/', '.codex/')):
        return 'CURRENT_MAINTENANCE_TOOLING'
    if path in {'pyproject.toml', '.gitignore', '.gitattributes', 'docs/infrastructure_manifest.json'}:
        return 'CURRENT_PACKAGE_METADATA'
    raise ValueError('unclassified tracked file: ' + path)


def validate_authority(state: dict, disposition: dict, receipt: dict, consumer: dict) -> None:
    require(state['r1a_status'] == disposition['status'], 'R1_A disposition mismatch')
    require(state['scientific_status'] == receipt['decision'], 'latest scientific receipt mismatch')
    for obj in (state, disposition, receipt):
        require(obj['production_authority'] is False, 'production status drift')
        require(obj['fresh_oos'] is False, 'OOS status drift')
        require(obj['BLACKBOX_query_count'] == 3, 'BLACKBOX counter drift')
    require(state['active_empirical_candidate'] is None and disposition['active_empirical_candidate'] is None,
            'new candidate needs explicit governance revision')
    require(state['new_local_transfer_required'] is False, 'stale local transfer state')
    require(disposition['automatic_continuation_authorized'] is False, 'automatic study continuation drift')
    require(consumer['production_authority'] is False and consumer['exact_realtime_asof'] is False,
            'consumer realtime authority drift')


def check_preservation(entries: dict, baseline: dict) -> tuple[int, int]:
    mutable = set(baseline['modified_baseline_paths'])
    preserved = 0
    for path, spec in baseline['entries'].items():
        if path not in mutable:
            require(entries.get(path) == spec, 'protected baseline file changed or removed: ' + path)
            preserved += 1
        else:
            archived = baseline['archive_prefix'] + '/' + path
            require(entries.get(archived) == spec, 'missing/nonidentical archive copy: ' + path)
    for path in baseline['removed_active_paths']:
        require(path not in entries, 'retired active path reintroduced: ' + path)
    return preserved, len(mutable)


def check_links(root: Path, entries: dict[str, dict[str, str]]) -> int:
    checked = 0
    pattern = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
    for path in entries:
        if not path.endswith('.md'):
            continue
        text = (root / path).read_text(encoding='utf-8')
        for target in pattern.findall(text):
            local = local_target(path, target)
            if local is None:
                continue
            require(local in entries, 'broken local documentation link: ' + path + ' -> ' + target)
            checked += 1
    return checked


def check_python(root: Path, entries: dict[str, dict[str, str]]) -> int:
    count = 0
    for path in entries:
        if not path.endswith('.py'):
            continue
        ast.parse((root / path).read_text(encoding='utf-8'), filename=path)
        count += 1
    return count


def check(root: Path) -> dict:
    state = json.loads((root / STATE).read_text(encoding='utf-8'))
    baseline = json.loads((root / BASELINE).read_text(encoding='utf-8'))
    entries = git_index(root)
    names = set(entries)
    require(AUTO_WORKFLOW in names, 'missing automatic consistency workflow')
    protected, mutable = check_preservation(entries, baseline)
    role_counts = Counter(lifecycle(path, state) for path in names)
    for path in STATUS_ONLY_DOCUMENTS:
        require(path in names, 'missing status-managed product document: ' + path)
        current = (root / path).read_text(encoding='utf-8')
        require(status_only_text(path, current, state) == current,
                'status-managed product document is stale: ' + path)
    links = check_links(root, entries)
    python_count = check_python(root, entries)
    disposition = json.loads((root / 'docs/governance/R1A_DISPOSITION.json').read_text(encoding='utf-8'))
    receipt = json.loads((root / 'docs/ops/evidence/etf_day_reconciliation_20260912/receipt.json').read_text(encoding='utf-8'))
    consumer = json.loads((root / 'docs/governance/ETF_SOURCE_LABEL_CONSUMER_V1_20260912.json').read_text(encoding='utf-8'))
    validate_authority(state, disposition, receipt, consumer)
    result = {
        'status': 'REPOSITORY_CONSISTENCY_PASS_NOT_RESEARCH_CERTIFICATION',
        'tracked_files': len(names),
        'baseline_files': len(baseline['entries']),
        'protected_baseline_files_unchanged': protected,
        'archived_pre_cleanup_copies': mutable,
        'generated_documents': len(state['generated_documents']),
        'current_local_links_checked': links,
        'python_files_parsed': python_count,
        'test_files_registered': sorted(path for path in names if path.startswith('tests/') and path.endswith('.py')),
        'research_modules': len(state['modules']),
        'workflow_files_checked': sum(path.startswith('.github/workflows/') for path in names),
        'lifecycle_counts': dict(sorted(role_counts.items())),
        'new_market_outcomes_computed': False,
        'source_semantics_certified': False,
    }
    return result


def render(root: Path) -> None:
    state = json.loads((root / STATE).read_text(encoding='utf-8'))
    for path, text in state['generated_documents'].items():
        (root / path).write_text(text, encoding='utf-8')
    for path in STATUS_ONLY_DOCUMENTS:
        current = (root / path).read_text(encoding='utf-8')
        (root / path).write_text(status_only_text(path, current, state), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.render:
        render(root)
    if args.check:
        result = check(root)
        text = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            Path(args.output).write_text(text, encoding='utf-8')
        print(text)
    if not args.check and not args.render:
        parser.error('choose --check and/or --render')


if __name__ == '__main__':
    main()
