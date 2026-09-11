# R1_B post-backspread payoff-object theory review — 2026-09-11

Status: **NO NEW EMPIRICAL PAYOFF IDENTITY AUTHORIZED**

`BLACKBOX_query_count=3`  
`production_authority=false`

## Evidence boundary

Two materially distinct directional-option payoff objects have now been frozen before their own outcomes and executed on the same certified R1_B mechanism:

1. `R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT` — one long ATM directional option; final decision `FAIL_IDENTITY_CLOSED`.
2. `R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT` — one short ATM plus two adjacent OTM directional options; final decision `FAIL_IDENTITY_CLOSED`.

The first paid premium for simple convexity and produced a sparse positive right tail but a strongly negative typical event. The second independently changed the payoff geometry by financing part of the premium while retaining net tail convexity. It achieved 93.51% joint-fill coverage, but pooled mean was -376.61 CNY, all three voting years were negative, and only 2/12 voting quarters were positive.

The question now is not which option structure would have worked better historically. The question is whether any **independently motivated** next economic object remains that can be specified without using these realized option outcomes as a design surface.

## Theory review of nearby structures

### Another long strike / different DTE — not authorized

Choosing another strike distance, delta, or expiry after the ATM result would be exactly the strike/DTE rescue prohibited by the prior closeout. There is no mechanism-level evidence that identifies a particular option moneyness or expiry independently of the observed payoff.

### Another ratio or wider backspread — not authorized

The 1x2 adjacent-OTM structure was frozen specifically to test financing plus retained tail convexity without a width/ratio search. Moving to 1x3, 2x3, two strikes OTM, or any other width/ratio now would turn the observed option surface into an optimization grid. That is a rescue of the failed identity, not a new theory.

### Debit/credit vertical spreads — not authorized

A directional vertical would mainly choose how much of the already-tested convex tail to sell or cap in exchange for premium reduction. With no independent structural rule for the strike width, it is another ex-post payoff-shape tuning dimension.

### Calendar / diagonal spreads — theory not supported

A calendar or diagonal spread would primarily express relative theta / implied-volatility term structure. The certified R1_B mechanism concerns parent-trend restoration in the underlying path; there is no certified evidence linking R1_B to MO implied-volatility term structure. Opening this lane now would silently convert a restoration study into a volatility-term-structure strategy without a prior mechanism.

### Straddle / strangle — theory mismatch

R1_B supplies a frozen parent direction. A direction-agnostic long-volatility payoff discards certified information rather than representing it. It also increases gross premium exposure, contrary to the empirically observed typical-event premium burden. No independent theory supports this mapping.

### Short-volatility / short-convexity structures — theory mismatch and account risk

The unresolved R1_B evidence was a sparse large parent-aligned restoration tail. Selling that tail is not a faithful mapping of the certified mechanism. Short-option structures would additionally introduce materially different margin and tail-risk contracts, requiring a new risk mechanism rather than merely a new carrier.

### Dynamic delta/gamma trading — not currently a defined payoff identity

Delta-hedged option trading would test realized-versus-implied volatility and pathwise rehedging economics, not the certified directional restoration mechanism itself. It requires a separately frozen hedge instrument, executable hedge spreads/basis, rebalance clock, margin and transaction-cost model. No independent R1_B-to-volatility theory currently supplies those choices.

### Exotic barrier/digital claims — not an executable listed-object continuation

A digital or barrier payoff could represent structural restoration more directly in theory, but no admitted listed instrument in the current repository implements that payoff. Synthetic replication would reintroduce strike-grid, rebalance and execution choices and therefore requires a new program rather than another R1_B MO variant.

## Decision

`R1B_LISTED_DIRECTIONAL_OPTION_PAYOFF_PROGRAM_CLOSED_NO_NEW_EMPIRICAL_IDENTITY`

This decision does **not** claim that every possible option strategy is unprofitable. It says something narrower and scientifically important:

> after two independently frozen directional-convex payoff objects failed, no further nearby listed-MO structure can presently be specified from the certified R1_B mechanism without using already observed option outcomes to choose a new strike/ratio/DTE/volatility dimension.

Therefore no R1_B option v3/v4 is authorized. The correct current state is **no open empirical payoff identity**.

A future program may reopen only if it brings a genuinely external theory or economic need that determines the payoff object before reading the corresponding outcomes — for example a separately justified volatility-risk-premium mechanism, an account-level hedge/inventory problem, or a newly admitted instrument whose contractual payoff directly matches restoration. Such a restart requires a new freeze and explicit authority; it may not reuse the failed option outcomes to choose its parameters.

R1 and R2 mechanism certifications remain intact. The economic translation problem remains unresolved, not falsified at the mechanism level.
