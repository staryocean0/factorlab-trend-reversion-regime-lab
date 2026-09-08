# K-line recognizer Markov filter v7 — result card

V7 modifies only recognizer A's internal causal state memory. Classifier, features and frozen benchmark are unchanged.

## Pre-2025 promotion decision

Markov promoted over v5: **False**

V5 frozen rolling-CV baseline:
- minimum transition F1: `0.179`
- maximum false transitions/day: `1.240`
- minimum balanced accuracy: `0.754`
- minimum macro F1: `0.756`

Best point-eligible Markov candidate before promotion gate:
- candidate: `markov_eta2_beta2`
- eta: `2`; beta: `2`
- minimum transition F1: `0.118`
- maximum false transitions/day: `2.095`
- minimum balanced accuracy: `0.774`
- minimum macro F1: `0.780`

No Markov candidate satisfied the preregistered pre-2025 promotion gate. V5 remains the active recognizer and no Markov 2025 diagnostic was used for model selection or rescue.

## Boundary

2025 was already consumed by earlier development and is diagnostic only. This is chart-state recognition research, not trading profitability or fresh OOS performance.
