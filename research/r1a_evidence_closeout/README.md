# Existing R1_A evidence closeout

Current disposition: **R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED**.

This module audits already-saved evidence. It does not fit models, regenerate events, load raw market files, compute new strategy returns, repair missing quotes or open new confirmation data. A successful audit is not a new independent experiment or alpha confirmation.

Read:

- `docs/research/R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md`
- `docs/governance/R1A_EVIDENCE_CLOSEOUT_FREEZE@1.0.json`
- `docs/governance/R1A_PRICE_RESEARCH_DISPOSITION_20260912.json`
- `docs/ops/evidence/r1a_evidence_closeout_20260912/receipt.json`

## Reproduce

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_evidence_closeout.py tests/test_evidence_closeout_retained.py
PYTHONPATH=src:. python research/r1a_evidence_closeout/audit.py --output /tmp/r1a-evidence-closeout-new
PYTHONPATH=src:. python research/r1a_evidence_closeout/verify_replay.py \
  --reference docs/ops/evidence/r1a_evidence_closeout_20260912 \
  --replay /tmp/r1a-evidence-closeout-new \
  --output /tmp/r1a-evidence-closeout-replay.json
```

All output paths must be fresh. Never overwrite reference receipts. The nine cross-study reports and original Development identity file are pinned by Git blob identity. The eight forecast CSVs are verified against their original immutable receipt. The explicit report registry is a human-reviewed semantic map, not a new automatic proof of historical claims.

## Arithmetic and limits

With `e=y-parent_prediction` and `g=enhanced_prediction-parent_prediction`, the stored loss difference is exactly `2*e*g-g*g`.

In each fixed group, MSE equals the squared average residual plus the variance of centered residuals (`ddof=0`). The pooled decomposition is not the same as the event-count-weighted within-year decomposition; the between-year term is retained. This is finite-sample accounting, not repeated-training bias/variance estimation, identified market noise, event ranking evidence or an attainable correction using unknown future group means.

The enhanced R1_A indicator is constant on event rows inside each annual fold. It therefore provides a fold-level event offset, while the original simultaneous fit also changes shared coefficients. Stored centered intercept/scales are respected. The shared-refit remainder is defined by an identity, not a causal effect.

No observation is dropped. Report all seven horizons, all years, both directions and all year-by-direction groups. Loss gains use bp squared; they are never converted to bp of trading alpha. Small relative MSE improvement alone does not imply economic irrelevance.

## What completion means

The retained forecast arithmetic and identities agree within the declared tolerance; no material discrepancy was found in that scope. This is not an independent raw-source check or full code audit of every previous study. Source semantics, benchmark weakness, inferential calibration and historical reuse are not solved by this module.

Reserve the CURRENT price formulation and stop automatic active development. Preserve original mechanism records and all old studies; the wider research project is not terminated. A later materially different question or reproducible error requires explicit authorization, clear data role, budget and stop condition. No automatic model, feature, horizon, matching or option rescue follows this closeout.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_clock_started=false`.
