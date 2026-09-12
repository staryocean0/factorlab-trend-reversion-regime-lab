"""Repository consistency gate; never fit models or compute market outcomes.

--render synchronizes managed documentation from REPOSITORY_STATE.json.
--check validates the Git index, current worktree text, source syntax, local
imports, workflow contracts, and baseline preservation. Historical source
snapshots are deliberately not rewritten or treated as current instructions.
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


def document_text(path: str, body: str, state: dict) -> str:
    title, _, rest = body.strip().partition('\n')
    ref = os.path.relpath(STATE, str(PurePosixPath(path).parent))
    report = os.path.relpath(state['latest_review'], str(PurePosixPath(path).parent))
    block = '\n'.join([
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
    return title + '\n\n' + block + '\n\n' + rest.strip() + '\n'


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


def check_workflow(path: str, obj: dict, names: set[str]) -> None:
    require(isinstance(obj, dict) and isinstance(obj.get('on'), dict), 'invalid workflow events: ' + path)
    require(obj.get('permissions') == {'contents': 'read'}, 'workflow must be read-only: ' + path)
    if path != AUTO_WORKFLOW:
        require(set(obj['on']) == {'workflow_dispatch', 'workflow_call'}, 'legacy auto-trigger drift: ' + path)
    else:
        require(set(obj['on']) == {'push', 'pull_request', 'workflow_dispatch'}, 'missing generic gate events')
    require(isinstance(obj.get('jobs'), dict) and obj['jobs'], 'empty workflow jobs')
    for job in obj['jobs'].values():
        if 'uses' in job:
            use = job['uses']
            require(use.startswith('./.github/workflows/'), 'unexpected external reusable workflow')
            require(use[2:] in names, 'reusable workflow target missing: ' + use)
        else:
            require('timeout-minutes' in job, 'missing workflow job timeout: ' + path)
        for step in job.get('steps', []):
            if str(step.get('uses', '')).startswith('actions/checkout@'):
                require(str(step.get('with', {}).get('persist-credentials', '')).lower() == 'false',
                        'checkout retains credentials: ' + path)
            run = str(step.get('run', ''))
            require(not re.search(r'\bgit\s+(?:push|commit)\b', run), 'replay may not write Git evidence: ' + path)


def check(root: Path) -> dict:
    import yaml
    state = json.loads((root / STATE).read_text(encoding='utf-8'))
    baseline = json.loads((root / BASELINE).read_text(encoding='utf-8'))
    entries = git_index(root)
    names = set(entries)
    require(len(baseline['entries']) == baseline['baseline_file_count'], 'baseline count mismatch')
    preserved, archived = check_preservation(entries, baseline)
    changes = set(subprocess.check_output(['git', 'diff', '--name-only'], cwd=root, text=True).splitlines())
    protected = set(baseline['entries']) - set(baseline['modified_baseline_paths'])
    require(not changes.intersection(protected), 'unstaged protected source changes')
    for path, spec in entries.items():
        require(spec['mode'] in {'100644', '100755'}, 'symlink/submodule not permitted: ' + path)
    role_counts = Counter(lifecycle(path, state) for path in names)
    for key in ('latest_review', 'latest_receipt', 'r1a_disposition', 'consumer_contract'):
        require(state[key] in names, 'missing authority target: ' + state[key])
    load = lambda path: json.loads((root / path).read_text(encoding='utf-8'))
    validate_authority(state, load(state['r1a_disposition']), load(state['latest_receipt']), load(state['consumer_contract']))
    doc_links = 0
    for path, body in state['generated_documents'].items():
        require(path in names, 'generated document not tracked: ' + path)
        wanted = document_text(path, body, state)
        require((root / path).read_text(encoding='utf-8') == wanted, 'generated document drift: ' + path)
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', wanted):
            rel = local_target(path, target)
            if rel is not None:
                require(rel in names or any(x.startswith(rel.rstrip('/') + '/') for x in names),
                        'broken current documentation link: ' + path + ' -> ' + rel)
                doc_links += 1
    actual_modules = {p.split('/')[1] for p in names if p.startswith('research/') and p.endswith('.py')}
    require(actual_modules == set(state['modules']), 'research component registry drift')
    for name, spec in state['modules'].items():
        require(spec['report'] in names and spec['workflow'] in names, 'module endpoint missing: ' + name)
        require('research/' + name + '/README.md' in names, 'missing lifecycle readme: ' + name)
    syntax_count = 0
    tests = []
    for path in sorted(names):
        if not path.endswith('.py') or not path.startswith(('src/', 'shared/', 'research/', 'tests/', 'scripts/')):
            continue
        tree = ast.parse((root / path).read_text(encoding='utf-8'), filename=path)
        syntax_count += 1
        if path.startswith('tests/test_'):
            tests.append(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and not node.level:
                if node.module.startswith(('factor_lab.', 'regime_lab.', 'shared.', 'research.', 'scripts.')):
                    modpath = node.module.replace('.', '/')
                    choices = {modpath + '.py', modpath + '/__init__.py', 'src/' + modpath + '.py', 'src/' + modpath + '/__init__.py'}
                    require(bool(choices.intersection(names)) or any(p.startswith(modpath + '/') for p in names),
                            'unresolved repository import: ' + path + ' -> ' + node.module)
    workflows = sorted(p for p in names if p.startswith('.github/workflows/') and p.endswith(('.yml', '.yaml')))
    require(set(workflows) == set(state['manual_workflows']) | {AUTO_WORKFLOW}, 'workflow registry drift')
    for path in workflows:
        check_workflow(path, yaml.load((root / path).read_text(), Loader=yaml.BaseLoader), names)
    infra = load('docs/infrastructure_manifest.json')
    listed = {x['path'] for x in infra['files']}
    actual = {p for p in names if p.startswith(('src/', 'shared/')) and p.endswith('.py')}
    require(actual == listed, 'infrastructure inventory membership drift')
    for spec in infra['files']:
        require(hashlib.sha256((root / spec['path']).read_bytes()).hexdigest() == spec['sha256'], 'infrastructure hash drift: ' + spec['path'])
    setup = (root / '.codex/cloud_setup.sh').read_text()
    require('scripts/validate_seed.py' not in setup and 'scripts/repository_consistency.py --check' in setup, 'setup invokes retired validator')
    return {'status': 'REPOSITORY_CONSISTENCY_PASS_NOT_RESEARCH_CERTIFICATION', 'tracked_files': len(names),
            'baseline_files': len(baseline['entries']), 'protected_baseline_files_unchanged': preserved,
            'archived_pre_cleanup_copies': archived, 'generated_documents': len(state['generated_documents']),
            'current_local_links_checked': doc_links, 'python_files_parsed': syntax_count, 'test_files_registered': tests,
            'research_modules': len(actual_modules), 'workflow_files_checked': len(workflows), 'lifecycle_counts': dict(sorted(role_counts.items())),
            'new_market_outcomes_computed': False, 'source_semantics_certified': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--render', action='store_true')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    if a.render:
        state = json.loads((root / STATE).read_text(encoding='utf-8'))
        for path, body in state['generated_documents'].items():
            target = (root / path).resolve()
            require(target.is_relative_to(root) and not (root / path).is_symlink(), 'unsafe generated document path')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(document_text(path, body, state), encoding='utf-8')
        print('Rendered', len(state['generated_documents']), 'documents; run --check after staging intended changes.')
        return
    result = check(root)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
