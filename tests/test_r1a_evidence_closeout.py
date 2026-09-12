import ast
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.r1a_evidence_closeout.audit import (
    decompose, annual_partition, blob, close, groups, HORIZONS, YEARS,
    parameter_accounting, validate_prediction_rows,
)


@pytest.mark.parametrize('n',[1,2,7,101])
def test_all_exact_decompositions(n):
    r=np.random.default_rng(20260912+n)
    y=r.normal(2,50,n);p0=r.normal(0,4,n);p1=p0+r.normal(-1,2,n)
    x=decompose(y,p0,p1)
    assert np.isclose(x['mean_loss_improvement_bp2'],np.mean((y-p0)**2-(y-p1)**2))
    assert np.isclose(x['mean_loss_improvement_bp2'],x['bias_square_reduction_bp2']+x['centered_error_variance_reduction_bp2'])
    assert x['max_identity_error_bp2']<1e-7


def test_downward_adjustment_can_help_without_positive_alpha():
    x=decompose([-2.,-2.],[4.,4.],[0.,0.])
    assert x['adjustment_mean_bp']<0 and x['target_mean_bp']<0
    assert x['mean_loss_improvement_bp2']==32
    assert x['centered_error_variance_reduction_bp2']==0


def test_constant_shift_cannot_improve_within_group_centered_error():
    y=np.array([-8.,1.,20.,-1.]);p=np.array([3.,1.,-4.,2.])
    x=decompose(y,p,p+2.)
    assert abs(x['centered_error_variance_reduction_bp2'])<1e-12


def test_worse_correction_is_not_clipped():
    x=decompose([0.,0.],[0.,0.],[1.,1.])
    assert x['mean_loss_improvement_bp2']==-1
    assert x['bias_square_reduction_bp2']==-1
    assert x['relative_mse_reduction'] is None


def test_group_specific_constant_correction_changes_pooled_variance():
    f=pd.DataFrame({'info_year':[2016,2016,2017,2017],
                    'target_bp':[-2.,0.,0.,2.],
                    'parent_prediction_bp':[1.,1.,-1.,-1.],
                    'enhanced_prediction_bp':[-1.,-1.,1.,1.]})
    p=decompose(f.target_bp,f.parent_prediction_bp,f.enhanced_prediction_bp)
    x=annual_partition(f,p)
    assert x['weighted_within_year_centered_error_variance_reduction_bp2']==0
    assert x['pooled_centered_error_variance_reduction_bp2']>0
    assert x['weighted_within_year_bias_square_reduction_bp2']==x['total_gain_bp2']


def test_year_partition_uses_counts_not_equal_year_weight():
    f=pd.DataFrame({'info_year':[2016,2016,2016,2017],
                    'target_bp':[0.,0.,0.,0.],
                    'parent_prediction_bp':[2.,2.,2.,0.],
                    'enhanced_prediction_bp':[0.,0.,0.,1.]})
    x=annual_partition(f,decompose(f.target_bp,f.parent_prediction_bp,f.enhanced_prediction_bp))
    assert x['total_gain_bp2']==(3*4-1)/4


@pytest.mark.parametrize('y,p0,p1',[([],[],[]),([1,2],[0],[1,2]),([np.nan],[0],[0]),([1],[np.inf],[0]),([[1]],[[0]],[[0]])])
def test_invalid_vectors_fail_closed(y,p0,p1):
    with pytest.raises(ValueError):decompose(y,p0,p1)


def test_no_fit_or_price_pipeline_imports():
    from research.r1a_evidence_closeout import audit
    tree=ast.parse(Path(audit.__file__).read_text())
    banned={'fit','fit_ridge','generate_events','load_market_data','load_development','read_parquet'}
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
            assert name not in banned
        if isinstance(node,ast.ImportFrom):
            assert not (node.module or '').startswith(('research.r1a_walkforward_prediction','research.index_price_validity','regime_lab','sklearn'))


def test_group_registry_has_all_years_and_sides():
    f=pd.DataFrame([{'info_year':y,'parent_direction':d} for y in YEARS for d in [-1,1]])
    g=list(groups(f))
    assert len(g)==18 and len(set(x[0] for x in g))==18
    assert all(len(x)>0 for _,x in g)
    assert HORIZONS==(1,5,15,30,60,120,240)


def test_git_blob_guard_formula():
    assert blob(b'')=='e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
    assert blob(b'a')!=blob(b'b')


def test_close_refuses_material_discrepancy_or_nan():
    with pytest.raises(ValueError):close([1],[2],'fake')
    with pytest.raises(ValueError):close([np.nan],[np.nan],'fake')


def test_shared_refit_remainder_not_mislabeled_as_flag_effect():
    rows=[]
    for model in ['parent','parent_plus_R1A']:
        for feature in ['intercept']+['x'+str(k) for k in range(16)]:
            rows.append({'year':2016,'horizon':15,'model':model,'feature':feature,'center':0.,'scale':1.,'coefficient_raw':0.,'coefficient_standardized':0.})
    rows.append({'year':2016,'horizon':15,'model':'parent_plus_R1A','feature':'R1_A','center':.25,'scale':.5,'coefficient_raw':4.,'coefficient_standardized':2.})
    forecasts=pd.DataFrame({'info_year':[2016,2016],'horizon':[15,15],'parent_prediction_bp':[0.,1.],'enhanced_prediction_bp':[5.,4.]})
    x=parameter_accounting(pd.DataFrame(rows),forecasts).iloc[0]
    assert x.centered_indicator_term_at_event_bp==3.
    assert x.mean_total_prediction_adjustment_bp==4.
    assert x.mean_shared_feature_refit_remainder_bp==1.


def test_material_parameter_normalization_error_rejected():
    # Shape violation is refused before any coefficient interpretation.
    p=pd.DataFrame({'year':[2016],'horizon':[15],'model':['parent'],'feature':['intercept'],
                    'center':[0.],'scale':[1.],'coefficient_raw':[1.],'coefficient_standardized':[2.]})
    f=pd.DataFrame({'info_year':[2016],'horizon':[15],'parent_prediction_bp':[0.],'enhanced_prediction_bp':[0.]})
    with pytest.raises(ValueError):parameter_accounting(p,f)


def test_small_mse_percentage_is_not_economic_zero():
    # Pure algebra toy example, not an extra market experiment.
    variance=55.**2;mu=3.
    assert 0.0029 < mu**2/(variance+mu**2) < 0.0031
