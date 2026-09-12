import pandas as pd
import pytest
from research.etf_index_measurability.verify_replay import compare_summary,compare_pooled,ATOL


def sample():
    return pd.DataFrame([{'carrier':'512100.SH','index_symbol':'000852.SH','period':'2021',
      'index_records':'58320','eligible_comparisons':'52068','positive_volume_coverage':'0.944787379972565',
      'gap_abs_bp_p95':'13.9305370653474'}])


def test_same_reference_is_unchanged():
    a=sample(); assert compare_summary(a,a.copy())==[]


def test_tiny_quantile_difference_is_disclosed():
    a=sample(); b=a.copy(); b.loc[0,'gap_abs_bp_p95']='13.930537065347401'
    result=compare_summary(a,b)
    assert len(result)==1 and result[0]['column']=='gap_abs_bp_p95'
    assert result[0]['absolute_difference'] <= ATOL


@pytest.mark.parametrize('field,value',[
 ('carrier','588000.SH'),('period','2022'),('index_records','58319'),
 ('eligible_comparisons','52069'),('positive_volume_coverage','0.944787379972566'),
 ('gap_abs_bp_p95','13.9306'),('gap_abs_bp_p95',''),('gap_abs_bp_p95','nan'),
])
def test_material_discrete_fraction_or_missingness_change_rejected(field,value):
    a=sample(); b=a.copy(); b.loc[0,field]=value
    with pytest.raises(ValueError): compare_summary(a,b)


def test_row_and_column_sets_not_relaxed():
    a=sample()
    with pytest.raises(ValueError): compare_summary(a,a.iloc[0:0])
    with pytest.raises(ValueError): compare_summary(a,a[a.columns[::-1]])


def test_json_counts_are_not_tolerated():
    a=[{'carrier':'512100.SH','index_records':58320,'gap_abs_bp_p95':13.9305370653474}]
    b=[dict(a[0],gap_abs_bp_p95=13.930537065347401)]
    assert len(compare_pooled(a,b))==1
    with pytest.raises(ValueError): compare_pooled(a,[dict(a[0],index_records=58321)])
