import csv
import json
from pathlib import Path
import pytest
from research.r1a_method_calibration import replay_audit as a


def write(path, value='1.0', count='5', flag='False', key='x', missing=''):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['id','count','flag','value','optional'])
        w.writeheader(); w.writerow({'id':key,'count':count,'flag':flag,'value':value,'optional':missing})


def test_small_float_difference_reported_not_concealed(tmp_path):
    old, new = tmp_path/'a.csv', tmp_path/'b.csv'
    write(old); write(new,value='1.000000000000001')
    r = a.compare_csv(old,new,['id'],{'value','optional'})
    assert r['pass'] and not r['byte_identical']
    assert r['float_columns']['value']['different_numeric_cells'] == 1
    assert float(r['float_columns']['value']['max_absolute_difference']) == 1e-15
    assert not any(r['exact_column_mismatches'].values())


@pytest.mark.parametrize('change', [{'count':'6'}, {'flag':'True'}, {'value':'1.00001'}, {'missing':'0'}])
def test_substantive_or_discrete_changes_fail(tmp_path,change):
    old,new = tmp_path/'a.csv',tmp_path/'b.csv'
    write(old); write(new,**change)
    r=a.compare_csv(old,new,['id'],{'value','optional'})
    assert not r['pass']


def test_discrete_numeric_strings_are_exact_even_tiny_difference(tmp_path):
    old,new=tmp_path/'a.csv',tmp_path/'b.csv'
    write(old,count='5'); write(new,count='5.000000000000001')
    assert not a.compare_csv(old,new,['id'],{'value','optional'})['pass']


def test_key_change_and_duplicate_keys_fail(tmp_path):
    old,new=tmp_path/'a.csv',tmp_path/'b.csv'
    write(old); write(new,key='y')
    with pytest.raises(a.ReplayError,match='identities'): a.compare_csv(old,new,['id'],{'value','optional'})
    write(new)
    with old.open('a') as f: f.write('x,5,False,1.0,\n')
    with new.open('a') as f: f.write('x,5,False,1.0,\n')
    with pytest.raises(a.ReplayError,match='duplicate'): a.compare_csv(old,new,['id'],{'value','optional'})


@pytest.mark.parametrize('value',['nan','inf','-Infinity','not-a-number'])
def test_nonfinite_and_invalid_float_rejected(tmp_path,value):
    old,new=tmp_path/'a.csv',tmp_path/'b.csv'
    write(old); write(new,value=value)
    with pytest.raises(a.ReplayError): a.compare_csv(old,new,['id'],{'value','optional'})


def test_schema_and_row_count_guard(tmp_path):
    old,new=tmp_path/'a.csv',tmp_path/'b.csv'
    write(old); new.write_text('id,count,value\nx,5,1\n')
    with pytest.raises(a.ReplayError): a.compare_csv(old,new,['id'],{'value','optional'})


def test_json_types_counts_and_booleans_strict():
    a.compare_json_tight({'x':1.000000000000001,'n':3,'flag':False},{'x':1.,'n':3,'flag':False})
    for actual,expected in [(4,3),(3.,3),(True,1),(False,True),(1.001,1.)]:
        with pytest.raises(a.ReplayError): a.compare_json_tight(actual,expected)


def test_reference_receipt_cannot_be_rewritten(tmp_path):
    old,new=tmp_path/'old',tmp_path/'new'; old.mkdir(); new.mkdir()
    (old/'method_receipt.json').write_text('{}')
    with pytest.raises(a.ReplayError,match='immutable'): a.audit(old,new,tmp_path/'out.json')


def test_source_hashes_and_exact_method_count_comparisons():
    root=Path(__file__).resolve().parents[1]
    source=root/'docs/ops/evidence/r1a_method_calibration_20260912'
    r=json.loads((source/'method_receipt.json').read_text())
    for spec in r['output_csvs']:
        file=source/spec['path']
        assert a.sha(file)==spec['sha256']
        keys,fl=a.CONFIG[spec['path']]
        got=a.compare_csv(file,file,keys,fl)
        assert got['pass'] and got['byte_identical']
        assert not any(got['exact_column_mismatches'].values())
    assert 'null_rejections' not in a.CELL_FLOATS
    assert 'seed' not in a.CELL_FLOATS
    assert 'severe_size_warning' not in a.CELL_FLOATS
