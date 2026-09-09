# R1/R2 migration into Trend–Reversion Regime Lab

Date: 2026-09-09.

## Placement correction

R1/R2 broad reversal research was first executed after `factorlab-overnight-open-lab` was mistakenly repurposed into a broad reversal / mean-reversion program. During cleanup, that package was temporarily migrated into `factorlab-star50-filter-lab`. That placement was also incorrect because STAR50's bounded role is causal volatility/risk-state research.

This commit moves the complete preserved R1/R2 package into `factorlab-trend-reversion-regime-lab`, where trend/reversion regime and reversal/mean-reversion research belongs.

## Mechanism identities

- **R1**: intact parent trend + lower-scale counter-move recovery. The parent trend supplies the normal-state anchor; the lower-scale move is tested as a temporary pullback rather than a parent-state reversal.
- **R2**: intact parent range + boundary overshoot / re-entry. The parent range supplies the normal-state anchor; the boundary break is tested as failed acceptance and re-entry rather than a true breakout.

## Preserved evidence and runnable entries

Full source package: `docs/archive/rmr_migrated_from_star50_20260909/`

Preserved runnable entries:
- `scripts/rmr_parent_state_legacy/run_rmr_stage1_common_probe.py`
- `scripts/rmr_parent_state_legacy/run_rmr_R1_reusable_dev_validation.py`
- `scripts/rmr_parent_state_legacy/certify_rmr_R1_reusable_blackbox.py`

These are migrated research artifacts, not newly validated against this repository's current data contract. Migration does not inherit or reopen any BLACKBOX authority and does not create production or trading authority.

`production_authority=false`.
