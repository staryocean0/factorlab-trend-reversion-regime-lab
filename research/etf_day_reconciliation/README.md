# Fixed-day source reconciliation v1

Scope: 2025-12-01 only. Read the freeze and `docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md`.

```bash
python -m pip install 'pyarrow>=19,<22'
python -m unittest discover -s tests -p 'test_etf_day_reconciliation*.py' -v
python research/etf_day_reconciliation/audit.py --output /tmp/etf-day-reconciliation-new
```

Requires the six delivered Parquet files, two original 2025 annual ETF CSVs and the freeze. Only the fixed day enters numeric calculations; full annual bytes are hash-checked. Prefer sparse checkout, not a complete data-repository clone. Always use a new output path.

The eight retained CSVs and receipt live at `docs/ops/evidence/etf_day_reconciliation_20260912/`. Every discrepancy is retained. Four minute conventions are accounting scenarios, not fitted alternatives. Decimal arithmetic avoids masking discrepancies with an arbitrary tolerance. A price divisor of 10000 is explicitly conditional on the delivered representation, not currency or quantity-unit certification.

`RestrictedSourceView(rows).lookup(source_label)` returns an index into original quote rows or None. It supports only the fixed-day continuous source-label contract. No fallback from a bad latest event, no carry from another phase, no future checkpoint, no extension of reversed terminal intervals. It uses offline validity metadata and is NOT a live receipt-time API. `dispositions` records rejected rows and separately clipped consumer ends. Original rows are not modified.

This does not patch DataHub, reconstruct missing vendor archives, certify old bar semantics, alter historical signals/results, or authorize prices/returns on new dates. R1_A remains reserved. The finite reconciliation is complete; there is no automatic follow-on model or clock-shift search.
