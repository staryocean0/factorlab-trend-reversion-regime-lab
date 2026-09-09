# K-line recognizer low-weight persistence-prior v13 — result card

V13 integrates only the audited v7 persistence contribution into champion v10 as a one-step weak probability prior. No recursive Markov posterior or Markov decoder is used.

## Champion before v13

- version: `v10_temporal_blend`
- result commit: `723404633fccb0a52181d2090cadbca3114dcc67`
- min balanced accuracy: `0.755`
- min macro F1: `0.759`
- min transition F1: `0.198`
- max false transitions/day: `1.207`

## Pre-2025 decision

V13 promotion candidate found: **False**

Best local v13 candidate:
- candidate: `persistence_rho0.05`
- rho: `0.05`
- min balanced accuracy: `0.757`
- min macro F1: `0.761`
- min transition F1: `0.199`
- max false transitions/day: `1.231`

No v13 rho passed the frozen v10 noninferiority + material-improvement gate. V10 remains champion.

Champion update eligibility: **False**

## Boundary

Runner cannot mutate champion/contribution authority. 2025 is consumed evidence, not fresh OOS.
