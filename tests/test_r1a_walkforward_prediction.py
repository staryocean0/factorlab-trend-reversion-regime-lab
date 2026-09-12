import numpy as np
import pandas as pd
import pytest
from research.r1a_walkforward_prediction.core import (
    CONTINUOUS, HORIZONS, RIDGE, raw_features, fit_ridge, training_mask,
    target, support_audit, prediction_rows, score, daily_accounting,
)


def fixture(n=240, seed=73):
    rng = np.random.default_rng(seed)
    f = pd.DataFrame(rng.normal(size=(n,4)), columns=CONTINUOUS)
    f['parent_direction'] = np.where(np.arange(n)%2, -1, 1)
    f['info_clock_bucket'] = np.where(np.arange(n)%3, 20, 19).astype(float)
    f['is_event'] = (np.arange(n)%5 == 0).astype(int)
    f['entry_idx'] = np.arange(n)+1; f['info_idx'] = f.entry_idx-1
    f['info_day'] = '2016-01-04'; f['info_year'] = 2016; f['entry_day'] = f.info_day
    return f


def test_only_added_feature_is_indicator():
    f=fixture(); x0,n0=raw_features(f); x1,n1=raw_features(f,True)
    np.testing.assert_array_equal(x0,x1[:,:-1]); assert n1==n0+['R1_A']
    assert x0.shape[1]==16 and x1.shape[1]==17


def test_no_severity_future_or_selected_control_feature():
    f=fixture(); x,_=raw_features(f,True)
    for name in ['severity','resolve_idx','future_return','control_entry_idx','structural_outcome']:
        f[name]=np.arange(len(f))*999999
    np.testing.assert_array_equal(x,raw_features(f,True)[0])


@pytest.mark.parametrize('col,value',[('parent_abs_drift',np.nan),('parent_efficiency',np.inf),('parent_direction',0),('info_clock_bucket',12),('info_clock_bucket',20.2),('is_event',2)])
def test_invalid_features_rejected(col,value):
    f=fixture(); f.loc[0,col]=value
    with pytest.raises(ValueError): raw_features(f,True)


def test_ridge_objective_and_intercept():
    x=np.arange(20.,dtype=float).reshape(10,2); y=np.arange(10.)*3+17
    model=fit_ridge(x,y); z=(x-model.center)/model.scale
    expected=np.linalg.solve(z.T@z/len(y)+RIDGE*np.eye(2),z.T@(y-y.mean())/len(y))
    np.testing.assert_allclose(model.beta,expected)
    assert model.intercept==y.mean()
    np.testing.assert_allclose(model.predict(x).mean(),y.mean())


def test_constant_column_does_not_fail_or_get_future_scale():
    x=np.column_stack([np.arange(30.),np.zeros(30)])
    model=fit_ridge(x,np.arange(30.))
    assert model.scale[1]==1 and model.beta[1]==0
    before=model.center.copy(); model.predict(np.array([[99999.,1.]]))
    np.testing.assert_array_equal(before,model.center)


@pytest.mark.parametrize('h',HORIZONS)
def test_only_completed_labels_enter_training(h):
    f=fixture(500); mask=training_mask(f,h,300)
    assert (f.loc[mask,'entry_idx']+h<=300).all()
    assert (f.loc[~mask,'entry_idx']+h>300).all()
    assert int(mask.sum())==300-h


def test_future_price_changes_do_not_change_fit():
    f=fixture(500); p=100*np.exp(np.arange(800)*.0001)
    train=f.loc[training_mask(f,30,300)]
    x,_=raw_features(train,True); y=target(train,p,30); a=fit_ridge(x,y)
    p[301:]*=np.linspace(2,7,len(p)-301)
    b=fit_ridge(x,target(train,p,30))
    np.testing.assert_array_equal(a.beta,b.beta)
    np.testing.assert_array_equal(a.center,b.center)


def test_synthetic_signal_increment_is_detected_without_search():
    train,test=fixture(2000,1),fixture(200,2)
    ytrain=3*train.parent_abs_drift.to_numpy()+5*train.is_event.to_numpy()
    ytest=3*test.parent_abs_drift.to_numpy()+5*test.is_event.to_numpy()
    p=[]
    for enhanced in [False,True]:
        model=fit_ridge(raw_features(train,enhanced)[0],ytrain)
        p.append(model.predict(raw_features(test,enhanced)[0]))
    rows=prediction_rows(test,ytest,p[0],p[1],float(ytrain.mean()))
    assert score(rows.loc[rows.is_event==1])['mean_loss_improvement_bp2']>10


def test_equal_predictions_have_exact_zero_improvement():
    f=fixture(); y=np.arange(len(f),dtype=float); p=y*.5
    r=prediction_rows(f,y,p,p,float(y.mean())); s=score(r)
    assert s['mean_loss_improvement_bp2']==0 and s['relative_mse_reduction']==0


def test_loss_units_and_sign_are_not_extra_return():
    f=fixture(2); y=np.array([2.,4.]); p0=np.zeros(2); p1=np.ones(2)
    s=score(prediction_rows(f,y,p0,p1,0))
    assert s['mean_loss_improvement_bp2']==5
    assert s['parent_mse_bp2']==10 and s['enhanced_mse_bp2']==5


def test_support_flags_do_not_drop_difficult_events():
    train,test=fixture(),fixture(5)
    test.loc[0,CONTINUOUS[0]]=1e9; test.loc[1,'info_clock_bucket']=30
    audit=support_audit(train,test)
    assert len(audit)==len(test) and audit.loc[0,'outside_training_range']
    assert audit.loc[1,'no_past_background_stratum']
    assert np.isnan(audit.loc[1,'nearest_background_distance'])
    m=fit_ridge(raw_features(train)[0],np.arange(len(train),dtype=float))
    assert np.isfinite(m.predict(raw_features(test)[0])).all()


def test_minute_target_uses_frozen_direction_and_horizon():
    f=fixture(2); p=100+np.arange(300,dtype=float)
    y=target(f,p,15)
    np.testing.assert_allclose(y,[15/101*1e4,-15/102*1e4])
    with pytest.raises(ValueError): target(f,p[:10],15)


def test_daily_reconstruction_retains_zero_event_days_and_all_horizons():
    f=fixture(5); r=prediction_rows(f,np.arange(5.),np.zeros(5),np.ones(5),0.)
    ledger=pd.concat([r.assign(horizon=h) for h in HORIZONS],ignore_index=True)
    cal=list(pd.date_range('2016-01-04',periods=80).strftime('%Y-%m-%d'))
    daily,lags=daily_accounting(ledger,cal)
    assert len(daily)==80*7 and len(lags)==35
    assert (daily.loc[daily.info_day!='2016-01-04','n']==0).all()
    assert daily.n.sum()==35
    np.testing.assert_allclose(daily.loss_sum_bp2.sum(),ledger.loss_improvement_bp2.sum())


def test_future_features_not_used_in_training_normalization():
    f=fixture(); train=f.iloc[:150]; x,_=raw_features(train,True)
    fit=fit_ridge(x,np.arange(len(train),dtype=float)); expected=fit.beta.copy()
    f.loc[150:,CONTINUOUS[0]]=1e8
    fit_again=fit_ridge(raw_features(f.iloc[:150],True)[0],np.arange(len(train),dtype=float))
    np.testing.assert_array_equal(expected,fit_again.beta)
