import copy
import pytest
from research.etf_source_repair.verify_legacy_inventory import inventory_for_paths, check_inventory, tree_paths


def test_each_inventory_is_checked_at_its_own_commit():
    old=['data/manifest.json','data/mo_quotes/2022.csv']
    new=old+['data/etf_source_actions_v2/manifest.json']
    check_inventory(inventory_for_paths(old),old)
    check_inventory(inventory_for_paths(new),new)
    with pytest.raises(ValueError): check_inventory(inventory_for_paths(old),new)
    with pytest.raises(ValueError): check_inventory(inventory_for_paths(new),old)


@pytest.mark.parametrize('field,value',[
    ('data_paths',99),('candidate_names_only',[]),('unrelated_file_contents_read',True),('limitation','changed')
])
def test_inventory_differences_are_not_silently_ignored(field,value):
    paths=['data/quote_x.csv','data/manifest.json']; obj=inventory_for_paths(paths)
    obj[field]=value
    with pytest.raises(ValueError): check_inventory(obj,paths)


def test_candidate_order_and_case_match_original_rule():
    paths=['data/IOPV/a.csv','data/price.csv','data/quotes/b.csv','data/basket.json']
    obj=inventory_for_paths(paths)
    assert obj['data_paths']==4
    assert obj['candidate_names_only']==[paths[0],paths[2],paths[3]]
    assert obj['unrelated_file_contents_read'] is False


@pytest.mark.parametrize('commit',['HEAD','main','bad','a'*39,'z'*40,'--all'])
def test_mutable_or_invalid_reference_rejected_without_git_access(tmp_path,commit):
    with pytest.raises(ValueError,match='immutable'): tree_paths(tmp_path,commit)
