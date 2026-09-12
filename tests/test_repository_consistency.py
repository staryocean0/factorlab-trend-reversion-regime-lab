"""Synthetic maintenance tests; no source prices or fitting are needed."""
from copy import deepcopy
import importlib
from pathlib import Path
import pytest
from scripts.repository_consistency import (
    AUTO_WORKFLOW, blob, check_preservation, check_workflow, document_text,
    lifecycle, local_target, validate_authority,
)


def state():
    return {'scientific_status': 'DONE', 'r1a_status': 'RESERVED', 'BLACKBOX_query_count': 3,
            'production_authority': False, 'fresh_oos': False, 'active_empirical_candidate': None,
            'new_local_transfer_required': False, 'latest_review': 'docs/research/review.md',
            'generated_documents': {'README.md': '# Hi'}, 'manual_workflows': ['.github/workflows/replay.yml'],
            'modules': {'example': {'status': 'REPLAY_ONLY'}}}


def authorities():
    s=state(); d=dict(s, status='RESERVED', automatic_continuation_authorized=False)
    r=dict(s, decision='DONE'); c={'production_authority':False,'exact_realtime_asof':False}
    return s,d,r,c


def test_authority_consistent():
    validate_authority(*authorities())


@pytest.mark.parametrize('key,value',[('production_authority',True),('fresh_oos',True),('BLACKBOX_query_count',4),('new_local_transfer_required',True),('active_empirical_candidate','new'),('r1a_status','PASS'),('scientific_status','PASS')])
def test_reject_authority_drift(key,value):
    s,d,r,c=authorities();s[key]=value
    with pytest.raises(ValueError):validate_authority(s,d,r,c)


def test_state_change_changes_rendered_document():
    a=state();b=deepcopy(a);b['scientific_status']='OTHER'
    assert document_text('README.md','# Hi\nBody',a)!=document_text('README.md','# Hi\nBody',b)
    assert '../REPOSITORY_STATE.json' in document_text('docs/research/README.md','# X',a)


@pytest.mark.parametrize('target',['../../escape.md','/absolute/path'])
def test_document_links_cannot_escape(target):
    with pytest.raises(ValueError):local_target('README.md',target)


def test_local_and_external_links():
    assert local_target('docs/TESTING.md','../README.md#head')=='README.md'
    assert local_target('README.md','https://example.com') is None
    assert local_target('README.md','#section') is None


def test_unregistered_module_and_file_fail():
    with pytest.raises(ValueError):lifecycle('research/new/study.py',state())
    with pytest.raises(ValueError):lifecycle('mystery.txt',state())
    assert lifecycle('data/raw.csv',state())=='PRESERVED_SOURCE_NOT_NEW_ADMISSION'
    assert lifecycle('docs/archive/old.py',state())=='ARCHIVED_HISTORICAL_SOURCE'


def baseline_fixture():
    spec={'mode':'100644','git_blob':'abc'}
    b={'entries':{'data/raw.csv':spec,'README.md':spec},'modified_baseline_paths':['README.md'],
       'archive_prefix':'docs/archive/baseline','removed_active_paths':['docs/seed_manifest.json']}
    e={'data/raw.csv':spec,'docs/archive/baseline/README.md':spec,'README.md':{'mode':'100644','git_blob':'new'}}
    return e,b


def test_originals_preserved_and_mutable_document_archived():
    e,b=baseline_fixture();assert check_preservation(e,b)==(1,1)


@pytest.mark.parametrize('path',['data/raw.csv','docs/archive/baseline/README.md'])
def test_original_or_archive_modification_rejected(path):
    e,b=baseline_fixture();e[path]={'mode':'100644','git_blob':'tampered'}
    with pytest.raises(ValueError):check_preservation(e,b)


def test_retired_manifest_reintroduction_rejected():
    e,b=baseline_fixture();e['docs/seed_manifest.json']={'mode':'100644','git_blob':'abc'}
    with pytest.raises(ValueError):check_preservation(e,b)


def workflow():
    return {'on':{'workflow_dispatch':'','workflow_call':''},'permissions':{'contents':'read'},
            'jobs':{'replay':{'timeout-minutes':'10','steps':[{'uses':'actions/checkout@v4','with':{'persist-credentials':'false'}}]}}}


def test_manual_workflow_accepted():
    check_workflow('.github/workflows/replay.yml',workflow(),set())


@pytest.mark.parametrize('bad',['write','push','credentials','git_push'])
def test_workflow_regressions_rejected(bad):
    w=workflow()
    if bad=='write':w['permissions']['contents']='write'
    elif bad=='push':w['on']['push']={}
    elif bad=='credentials':w['jobs']['replay']['steps'][0]['with']['persist-credentials']='true'
    else:w['jobs']['replay']['steps'].append({'run':'git push origin main'})
    with pytest.raises(ValueError):check_workflow('.github/workflows/replay.yml',w,set())


def test_reusable_target_must_exist():
    w={'on':{'push':{},'pull_request':{},'workflow_dispatch':{}},'permissions':{'contents':'read'},
       'jobs':{'all':{'uses':'./.github/workflows/missing.yml'}}}
    with pytest.raises(ValueError):check_workflow(AUTO_WORKFLOW,w,set())


def test_support_import_closure():
    root=Path(__file__).resolve().parents[1]
    for base in ('src','shared'):
        for p in sorted((root/base).rglob('*.py')):
            rel=p.relative_to(root/'src' if base=='src' else root)
            parts=list(rel.with_suffix('').parts)
            if parts[-1]=='__init__':parts.pop()
            importlib.import_module('.'.join(parts))


def test_git_blob_formula():
    assert blob(b'')=='e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
