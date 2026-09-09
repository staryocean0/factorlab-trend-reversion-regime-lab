# K-line recognizer temporal-blend v11 — result card

V11 is a narrow local refinement of champion v10. Only blend alpha changes.

## Champion before v11

- version: `v10_temporal_blend`
- result commit: `723404633fccb0a52181d2090cadbca3114dcc67`
- min balanced accuracy: `0.755`
- min macro F1: `0.759`
- min transition F1: `0.198`
- max false transitions/day: `1.207`

## Pre-2025 decision

V11 promotion candidate found: **False**

Best local v11 candidate (used for contribution analysis only if not promoted):
- candidate: `v11_h6_a0.45`
- min balanced accuracy: `0.758`
- min macro F1: `0.762`
- min transition F1: `0.201`
- max false transitions/day: `1.165`

No v11 alpha passed the frozen champion noninferiority + material-improvement gate. V10 remains champion.

Champion update eligibility: **False**

Any useful local effect may still be considered for the Contribution Ledger in a separate governance action.

## Boundary

The runner does not modify champion or contribution authority files. 2025 is already-consumed evidence, not fresh OOS.
