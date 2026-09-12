"""Fixed nested ridge forecasts; no matching, p-values or strategy execution."""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

CONTINUOUS = ('parent_abs_drift', 'parent_efficiency', 'log1p_parent_age_bars', 'local_vol_30_over_240')
HORIZONS = (1, 5, 15, 30, 60, 120, 240)
RIDGE = 0.001


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def raw_features(frame: pd.DataFrame, enhanced: bool = False) -> tuple[np.ndarray, list[str]]:
    names = list(CONTINUOUS) + ['parent_direction']
    x = frame[names].to_numpy(float)
    require(np.isfinite(x).all(), 'nonfinite parent feature')
    require(frame.parent_direction.isin([-1, 1]).all(), 'invalid direction')
    clock = frame.info_clock_bucket.to_numpy(float)
    require(np.isfinite(clock).all() and np.equal(clock, np.floor(clock)).all(), 'invalid clock')
    require(((clock >= 19) & (clock <= 30)).all(), 'clock outside fixed exchange buckets')
    x = np.column_stack([x] + [(clock == k).astype(float) for k in range(20, 31)])
    names += ['info_clock_' + str(k) for k in range(20, 31)]
    if enhanced:
        flag = frame.is_event.to_numpy(float)
        require(np.isin(flag, [0, 1]).all(), 'invalid R1_A flag')
        x = np.column_stack([x, flag]); names += ['R1_A']
    return x, names


@dataclass(frozen=True)
class RidgeFit:
    center: np.ndarray
    scale: np.ndarray
    beta: np.ndarray
    intercept: float
    condition_number: float

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, float)
        require(x.ndim == 2 and x.shape[1] == len(self.beta) and np.isfinite(x).all(), 'bad prediction features')
        return self.intercept + ((x-self.center)/self.scale) @ self.beta


def fit_ridge(x: np.ndarray, y: np.ndarray) -> RidgeFit:
    x, y = np.asarray(x, float), np.asarray(y, float)
    require(x.ndim == 2 and y.ndim == 1 and len(x) == len(y) and len(y) > 0, 'bad fit shape')
    require(np.isfinite(x).all() and np.isfinite(y).all(), 'nonfinite training data')
    center = x.mean(axis=0); scale = x.std(axis=0, ddof=0)
    scale = np.where(scale > 0, scale, 1.)
    z = (x-center)/scale; intercept = float(y.mean())
    gram = z.T @ z / len(y) + RIDGE*np.eye(z.shape[1])
    beta = np.linalg.solve(gram, z.T @ (y-intercept) / len(y))
    require(np.isfinite(beta).all(), 'ridge solution nonfinite')
    return RidgeFit(center, scale, beta, intercept, float(np.linalg.cond(gram)))


def training_mask(frame: pd.DataFrame, horizon: int, cutoff: int) -> np.ndarray:
    require(horizon in HORIZONS, 'unfrozen horizon')
    e = frame.entry_idx.to_numpy(int)
    require((e >= 1).all(), 'invalid entry indices')
    return e + horizon <= cutoff


def target(frame: pd.DataFrame, prices: np.ndarray, horizon: int) -> np.ndarray:
    e = frame.entry_idx.to_numpy(int); d = frame.parent_direction.to_numpy(int)
    require((e >= 1).all() and (e+horizon < len(prices)).all(), 'target outside price scope')
    a, b = prices[e], prices[e+horizon]
    require(np.isfinite(a).all() and np.isfinite(b).all() and (a > 0).all() and (b > 0).all(), 'bad target prices')
    return d * (b/a-1) * 10000.


def support_audit(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Descriptive coordinate support, not a deletion rule or causal proof."""
    tx = train[list(CONTINUOUS)].to_numpy(float)
    qx = test[list(CONTINUOUS)].to_numpy(float)
    out = pd.DataFrame(index=test.index)
    lo, hi = tx.min(axis=0), tx.max(axis=0)
    out['outside_training_range'] = ((qx < lo) | (qx > hi)).any(axis=1)
    bg = train.loc[train.is_event == 0]
    require(len(bg) > 0, 'no background support')
    bx = bg[list(CONTINUOUS)].to_numpy(float)
    out['outside_background_range'] = ((qx < bx.min(axis=0)) | (qx > bx.max(axis=0))).any(axis=1)
    scale = tx.std(axis=0); scale = np.where(scale > 0, scale, 1.)
    out['no_past_background_stratum'] = False
    out['nearest_background_distance'] = np.nan
    out['past_background_stratum_n'] = 0
    groups = {key: g for key, g in bg.groupby(['parent_direction', 'info_clock_bucket'], sort=True)}
    for key, q in test.groupby(['parent_direction', 'info_clock_bucket'], sort=True):
        candidates = groups.get(key)
        if candidates is None:
            out.loc[q.index, 'no_past_background_stratum'] = True
            continue
        tree = cKDTree(candidates[list(CONTINUOUS)].to_numpy(float)/scale)
        distance, _ = tree.query(q[list(CONTINUOUS)].to_numpy(float)/scale, k=1, workers=1)
        out.loc[q.index, 'nearest_background_distance'] = distance
        out.loc[q.index, 'past_background_stratum_n'] = len(candidates)
    return out


def prediction_rows(frame: pd.DataFrame, y: np.ndarray, p0: np.ndarray, p1: np.ndarray, past_mean: float) -> pd.DataFrame:
    columns = ['entry_idx', 'info_idx', 'info_day', 'info_year', 'entry_day', 'parent_direction', 'is_event']
    out = frame[columns].copy()
    out['target_bp'] = y; out['parent_prediction_bp'] = p0
    out['enhanced_prediction_bp'] = p1; out['past_mean_bp'] = past_mean
    out['parent_squared_error'] = (y-p0)**2; out['enhanced_squared_error'] = (y-p1)**2
    out['loss_improvement_bp2'] = out.parent_squared_error - out.enhanced_squared_error
    algebra = 2*(p1-p0)*(y-p0)-(p1-p0)**2
    require(np.allclose(out.loss_improvement_bp2, algebra, rtol=1e-9, atol=1e-7), 'loss difference identity')
    return out


def score(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {'n': 0}
    y = frame.target_bp.to_numpy(float); p0 = frame.parent_prediction_bp.to_numpy(float)
    p1 = frame.enhanced_prediction_bp.to_numpy(float); gain = (y-p0)**2-(y-p1)**2
    b = float(np.mean((y-p0)**2)); a = float(np.mean((y-p1)**2))
    out = {'n': len(frame), 'target_mean_bp': float(y.mean()), 'target_median_bp': float(np.median(y)),
           'parent_mean_prediction_bp': float(p0.mean()), 'enhanced_mean_prediction_bp': float(p1.mean()),
           'parent_mse_bp2': b, 'enhanced_mse_bp2': a, 'parent_rmse_bp': math.sqrt(b), 'enhanced_rmse_bp': math.sqrt(a),
           'parent_mae_bp': float(np.mean(np.abs(y-p0))), 'enhanced_mae_bp': float(np.mean(np.abs(y-p1))),
           'parent_mean_error_bp': float((p0-y).mean()), 'enhanced_mean_error_bp': float((p1-y).mean()),
           'mean_loss_improvement_bp2': float(gain.mean()), 'median_loss_improvement_bp2': float(np.median(gain)),
           'relative_mse_reduction': 1-a/b if b > 0 else None,
           'positive_loss_improvement_fraction': float((gain > 0).mean()),
           'zero_forecast_mse_bp2': float(np.mean(y*y)),
           'past_mean_forecast_mse_bp2': float(np.mean((y-frame.past_mean_bp.to_numpy(float))**2))}
    if 'outside_training_range' in frame:
        for col in ('outside_training_range', 'outside_background_range', 'no_past_background_stratum'):
            out[col+'_fraction'] = float(frame[col].mean())
        d = frame.nearest_background_distance.dropna()
        out['nearest_background_distance_median'] = float(d.median()) if len(d) else None
        out['nearest_background_distance_p95'] = float(d.quantile(.95)) if len(d) else None
    return out


def daily_accounting(ledger: pd.DataFrame, calendar: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, lag_rows = [], []
    for h in HORIZONS:
        f = ledger.loc[ledger.horizon == h]
        g = f.groupby('info_day', sort=True).agg(n=('entry_idx', 'size'),
              loss_sum_bp2=('loss_improvement_bp2', 'sum'),
              parent_sse_bp2=('parent_squared_error', 'sum'), enhanced_sse_bp2=('enhanced_squared_error', 'sum'))
        g = g.reindex(calendar, fill_value=0).rename_axis('info_day').reset_index()
        g['horizon'] = h; rows.append(g)
        x = g.loss_sum_bp2.to_numpy(float); centered = x-x.mean(); q = np.sort(np.abs(x))[::-1]
        mass = q.sum()
        for lag in (0, 1, 5, 20, 60):
            product = np.mean(centered*centered) if lag == 0 else np.mean(centered[lag:]*centered[:-lag])
            lag_rows.append({'horizon': h, 'lag': lag, 'calendar_days': len(g),
                'centered_loss_cross_product_bp4': float(product),
                'top_1pct_absolute_daily_loss_share': float(q[:max(1, math.ceil(.01*len(q)))].sum()/mass) if mass > 0 else None,
                'top_5pct_absolute_daily_loss_share': float(q[:max(1, math.ceil(.05*len(q)))].sum()/mass) if mass > 0 else None})
        require(int(g.n.sum()) == len(f), 'daily event count mismatch')
        require(np.isclose(g.loss_sum_bp2.sum(), f.loss_improvement_bp2.sum(), rtol=1e-9, atol=1e-6), 'daily loss reconstruction')
    return pd.concat(rows, ignore_index=True), pd.DataFrame(lag_rows)
