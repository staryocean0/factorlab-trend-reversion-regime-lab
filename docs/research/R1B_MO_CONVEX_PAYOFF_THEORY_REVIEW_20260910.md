# R1_B MO convex-payoff / instrument-theory review — 2026-09-10

Identity under review: `rmr_R1B_MO_convex_impulse_mapping_v1`

Status: **THEORY ACCEPTED; SUPERSEDED FOR NEXT ACTION BY PRE-EXECUTION FREEZE 2026-09-11**

Current machine freeze: `docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json`. Empirical outcome test remains unauthorized.

Production authority: `false`

## 1. Authority chain

The current repository owns two separately certified reversal / mean-reversion mechanisms:

- R1: intact trend parent + lower-scale counter-move recovery;
- R2: intact range parent + boundary overshoot / re-entry.

The following economic/synthesis identities are already closed and must not be reopened by tuning:

- R1 immediate structural first-passage economic family;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- unified parent-state router v1;
- R1_B `rmr_R1B_temporal_impulse_completion_v1`.

The mechanism-to-execution diagnostic and the R1_B DEV temporal test established a specific unresolved economic shape: R1_B contains delayed parent-trend restoration information, but the tested causal linear index payoff has a right-tail-heavy distribution and does not provide a broadly positive event-level translation. This review does not alter those results or their gates.

R5-B1 was separately closed on 2026-09-10 after its preregistered limited diagnostic failed the monotonic anti-persistence-shape gate. It provides no authority for this identity.

## 2. Theory question

The question is not whether entry, exit, cost, probability threshold, wave scale, or hold horizon can be retuned.

The question is:

> If R1_B restoration is a delayed, right-tail-heavy parent-trend impulse, is a bounded-loss convex claim on the same CSI1000 underlying a more faithful economic payoff object than another linear index exposure?

This is an instrument/payoff hypothesis, not a new mechanism-discovery hypothesis.

## 3. Why a linear IM futures mapping is not promoted

CFFEX CSI1000 index futures (`IM`) are direct CSI1000 linear exposure. Their use would introduce real basis, margin, spread, and fee mechanics, but the payoff remains approximately affine in the underlying price path.

That is not a sufficiently independent response to the key R1_B failure: the closed causal temporal candidate had positive mean but negative median and low win rate. Merely replacing the index reference by another linear instrument would primarily test transaction-cost/basis differences and risks becoming a cost rescue of the closed family.

Therefore `IM` is **not** the next empirical identity under this review.

## 4. Promoted payoff theory: long directional MO option

CFFEX CSI1000 index options (`MO`) are directly written on the CSI1000 index, have a RMB 100 per index-point multiplier, are European, and are cash settled.

The materially new payoff object is a **long directional option**:

- intact upward S3 parent -> long MO call;
- intact downward S3 parent -> long MO put.

The causal event clock remains R1_B. The option does not change the R1_B event definition, S2/S3 thresholds, parent-integrity mechanism, direction, or causal completion/failure clock.

The theoretical reason to test a long option is structural:

- a long option bounds the loss to paid premium plus execution costs;
- its payoff is convex in a sufficiently large move in the selected direction;
- this is materially different from the already-closed linear payoff family;
- it is therefore capable, in principle, of representing a rare-large-restoration component without pretending that the typical linear event became profitable.

This is only a theory. Theta, implied-volatility premium, bid/ask spread, and adverse option repricing can fully erase the benefit. Those terms must be measured rather than assumed away.

## 5. Literature role

The literature is used only to support the *type of economic object*, not to claim this R1_B implementation works.

- Fung & Hsieh (2001), “The Risk in Hedge Fund Strategies: Theory and Evidence from Trend Followers,” models trend-following returns with option-like / lookback-straddle payoffs.
- Dao et al. (2016), “Tail Protection for Long Investors: Trend Convexity at Work,” links trend-following payoff convexity to variance structure and discusses an options representation.

These papers do not test CSI1000 R1_B and do not supply empirical evidence for this candidate.

## 6. Single mapping to be frozen before any option outcome is read

If instrument data later passes admission, the only candidate eligible for a separate pre-execution freeze is:

`R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT`

The intended deterministic mapping is:

1. **Event population:** the already-certified R1_B `S2-inside-S3` events; no event refit.
2. **Direction:** call for upward parent, put for downward parent.
3. **Underlying entry clock:** unchanged next observed 1m close after R1_B confirmation.
4. **Option entry clock:** first valid MO best-ask observation at or after that underlying entry timestamp; no interpolation across missing quotes.
5. **Strike:** listed strike with minimum absolute distance to CSI1000 spot at the option-entry timestamp. A deterministic tie rule must be frozen in the execution protocol before data outcomes are inspected.
6. **Expiry:** nearest listed expiry that remains alive beyond the inherited 1200-observed-1m-bar safety horizon under the exchange trading calendar. This avoids introducing an option-expiry exit into the already-frozen R1_B causal clock.
7. **Success exit:** the same first subsequent parent-aligned S2-wave causal confirmation used by `rmr_R1B_temporal_impulse_completion_v1`.
8. **Parent-failure exit:** the same original frozen S3 structural failure crossing.
9. **Safety censor:** the same inherited 1200 observed bars.
10. **Option exit price:** first valid best bid at or after the causal exit timestamp; no midpoint or last-price substitution in the primary result.
11. **Position:** one long option contract per hypothetical event. No delta targeting, volatility targeting, probability sizing, leverage optimization, or portfolio concurrency assumptions.
12. **Primary raw payoff:** realized RMB option P&L using entry ask and exit bid, minus historically applicable exchange/broker fees frozen before outcome inspection.
13. **Secondary descriptive outputs:** premium return, entry premium, intrinsic value, time to expiry, spot move, and exit class. No implied-volatility model is required for primary realized P&L.

## 7. Required instrument data contract

No empirical execution is allowed from the current repository state because it contains no MO intraday quote tape.

A valid source must provide, at minimum, for every admitted MO contract:

- contract code;
- call/put flag;
- strike;
- expiry date;
- quote timestamp with exchange timezone semantics;
- best bid price and size;
- best ask price and size;
- last price (diagnostic only);
- volume;
- open interest;
- trading-status / invalid-quote markers where available.

The source must also provide or be joinable to:

- CSI1000 spot/index timestamp;
- CFFEX trading calendar;
- historically applicable exchange fee schedule;
- brokerage fee assumption or actual schedule;
- contract-specification/version provenance.

Public daily OHLC/settlement data are insufficient for this intraday execution identity. Last price alone is insufficient because it suppresses the instrument spread that the payoff theory explicitly requires us to measure.

CFFEX documents historical-data product families including Level-1, Level-2, one-minute, and five-minute databases. For this primary execution study, best bid/ask provenance is required; a lower-information source may be used only for non-economic feasibility checks, not for the decisive result.

## 8. Data-role governance

MO began trading on 2022-07-22. The repository has already inspected substantial CSI1000 underlying-path outcomes through 2025 in prior RMR work. Therefore 2022-2025 must **not** be relabeled as a fresh mechanism BLACKBOX merely because option quotes were previously absent.

Before importing MO data, a separate data-admission receipt must freeze:

- exact source and checksum inventory;
- timestamp/session normalization;
- quote validity rules;
- fee schedule;
- historical reusable window;
- prospective validation boundary.

A scientifically clean default is to treat pre-freeze historical MO data as reusable instrument-development evidence and reserve post-freeze observations for prospective validation. No BLACKBOX allocation is created by this theory review.

## 9. Explicit prohibitions

This review does not authorize:

- selecting call/put delta after looking at R1_B option outcomes;
- strike search around ATM;
- expiry/DTE search;
- implied-volatility filters;
- probability thresholds or sizing;
- entry-delay search;
- alternative S2/S3 completion exits;
- 30/60/120/240-bar horizon selection;
- stop/target search;
- favorable year/regime/time-of-day filtering;
- replacing ask/bid execution by midpoint after seeing spread costs;
- IM futures as a lower-cost rescue of the closed linear identity;
- BLACKBOX query #4;
- production authority.

## 10. Decision

`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`

This is the first materially independent payoff-object theory surviving the post-diagnostic review. It is not yet an empirical candidate result.

Next authorized action: obtain/admit an MO intraday best-bid/best-ask dataset under a frozen provenance and fee contract. Until that exists, the correct scientific state is **theory accepted, instrument evidence unavailable**.

## External references

- CFFEX CSI1000 index options product page: https://www.cffex.com.cn/zz1000gzqq/
- CFFEX index-option trading rules: https://www.cffex.com.cn/cn/ssxz/20221214/43100.html
- CFFEX CSI1000 index futures rules: https://www.cffex.com.cn/cn/ssxz/20220718/43093.html
- CFFEX historical data service: https://www.cffex.com.cn/lssjfw/
- Fung & Hsieh trend-following option-like payoff paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=250542
- Dao et al. trend convexity paper: https://arxiv.org/abs/1607.02410

`BLACKBOX_query_count=3`.
`production_authority=false`.
