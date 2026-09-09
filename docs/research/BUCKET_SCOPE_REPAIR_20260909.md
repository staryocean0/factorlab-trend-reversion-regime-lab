# Bucket scope repair — 2026-09-09

## Correct three-bucket split

| Repository | Current authority |
|---|---|
| `factorlab-star50-filter-lab` | bottom-layer K-line volatility/risk attributes; Unsafe/Recovering/HighVol state measurement and causal risk-state switching |
| `factorlab-trend-reversion-regime-lab` | real reversal / mean-reversion strategy research, including R1/R2 and their historical MR/REV lineage |
| `factorlab-two-wave-strategy-lab` | causal parent-structure/state recognition: range vs uptrend vs downtrend, based on completed same-scale wave structure |

## Repairs affecting this repository

- R1/R2 had already been correctly migrated here from earlier mistaken placements. They stay here.
- The broad original regime seed text remains historical context only.
- `kline-recognizer` v1-v13 was developed on research branches here by mistake. Those branches/results are not deleted. Their key authority/result package is copied to the Two-Wave repository as supporting state-classification evidence.
- No future generic range/up/down recognizer work should continue in this bucket unless the owner explicitly changes the split again.

This repair changes current scope, not historical evidence.

`production_authority=false`.
