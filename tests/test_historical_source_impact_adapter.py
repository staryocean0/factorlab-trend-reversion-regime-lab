"""Compatibility-view guards, without loading historical market data."""
import hashlib
from pathlib import Path
import pytest
from scripts.verify_historical_source_impact import (
    METADATA, RETIRED_WORKFLOW, metadata_eligible, safe_path, verify_bytes,
)


def specification(raw):
    return {'path':'data/example.csv','bytes':str(len(raw)),
            'sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}


def test_exact_original_hashes_required():
    raw=b'original';s=specification(raw);verify_bytes(raw,s)
    with pytest.raises(ValueError):verify_bytes(b'tampered',s)


@pytest.mark.parametrize('field',['bytes','sha256','git_blob_sha1'])
def test_each_identity_channel_checked(field):
    raw=b'original';s=specification(raw);s[field]='999' if field=='bytes' else '0'*64
    with pytest.raises(ValueError):verify_bytes(raw,s)


@pytest.mark.parametrize('path',['data/market/1m/raw.parquet','research/study.py','docs/governance/freeze.json','docs/ops/evidence/result.csv'])
def test_scientific_inputs_never_get_metadata_fallback(path):
    assert not metadata_eligible(path,b'changed',b'original')


def test_docstring_only_init_is_explicitly_allowed():
    assert metadata_eligible('src/regime_lab/__init__.py',b'"""new documentation"""',b'"""old documentation"""')
    with pytest.raises(ValueError):
        metadata_eligible('src/regime_lab/__init__.py',b'"""new"""\nvalue=1',b'"""old"""')


def test_only_known_retired_workflow_may_be_missing():
    assert metadata_eligible(RETIRED_WORKFLOW,None,b'on: old')
    with pytest.raises(ValueError):
        metadata_eligible('.github/workflows/r1a-control-design.yml',None,b'on: old')
    assert len(METADATA)==7


def test_temp_view_rejects_path_escape_and_symlink(tmp_path):
    assert safe_path(tmp_path,'docs/a.json')==tmp_path/'docs/a.json'
    for p in ('../outside','/absolute'):
        with pytest.raises(ValueError):safe_path(tmp_path,p)
    (tmp_path/'link').symlink_to(tmp_path/'actual')
    with pytest.raises(ValueError):safe_path(tmp_path,'link')
