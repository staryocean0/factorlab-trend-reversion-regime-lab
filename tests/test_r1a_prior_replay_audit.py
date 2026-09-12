import hashlib
import json
from pathlib import Path
import pytest
from research.r1a_method_calibration import prior_replay_audit as p
from research.r1a_method_calibration.replay_audit import ReplayError, compare_csv, sha

ROOT=Path(__file__).resolve().parents[1]
REFERENCES={
    'robustness': ROOT/'docs/ops/evidence/r1a_endpoint_robustness_20260912',
    'feasibility': ROOT/'docs/ops/evidence/r1a_confirmation_feasibility_20260912/planning',
}


@pytest.mark.parametrize('stage', list(REFERENCES))
def test_all_prior_reference_schemas_and_keys_are_strictly_comparable(stage):
    root=REFERENCES[stage]; s=p.STAGES[stage]
    raw=(root/s['receipt']).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==s['blob']
    r=json.loads(raw)
    assert {x['path'] for x in r[s['files_key']]}==set(s['keys'])
    for file in r[s['files_key']]:
        path=root/file['path']; keys=s['keys'][file['path']]
        assert sha(path)==file['sha256']
        floats=p.inferred_float_columns(path,keys)
        assert not set(keys)&floats
        result=compare_csv(path,path,keys,floats)
        assert result['pass'] and result['byte_identical']


def test_integer_boolean_and_key_columns_not_tolerated(tmp_path):
    f=tmp_path/'x.csv'
    f.write_text('id,n,seed,flag,value,gamma_bp\na,2000,44,False,1.25,-50.0\n')
    cols=p.inferred_float_columns(f,['id','gamma_bp'])
    assert cols=={'value'}


def test_modified_old_receipt_is_not_accepted(tmp_path):
    old=tmp_path/'old';new=tmp_path/'new';old.mkdir();new.mkdir()
    (old/'robustness_receipt.json').write_text('{}')
    with pytest.raises(ReplayError,match='pinned'):
        p.audit('robustness',old,new,tmp_path/'audit.json')
