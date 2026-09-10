# R1_B MO — CIIS official CFFEX Level-2 acquisition route — 2026-09-10

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Scope: **instrument-data acquisition/admission only**. This document does not authorize an R1_B event join, option return/PnL, parameter search, BLACKBOX query #4, or production use.

`BLACKBOX_query_count=3`  
`production_authority=false`

## 1. Why this route is admissible to pursue

China Investment Information Services Limited (CIIS) currently states on its Historical Data service that historical products from SSE, CSI and CFFEX are official products **directly provided by the respective exchanges/index provider**, and specifically lists:

`China Financial Futures Exchange (CFFEX) Level-2 Intra-Day Snapshot Historical Data`

CIIS therefore fits the already-frozen protocol's conditionally admissible class:

> licensed vendor/distributor feed with field-level provenance traceable to CFFEX.

This document does **not** change `R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`; it records a concrete acquisition route already permitted by that frozen source hierarchy.

Official CIIS pages:

- historical-data introduction: https://www.ciis.com.hk/hongkong/en/historicaldata1/his_introduction/index.shtml
- sample-data page: https://www.ciis.com.hk/hongkong/en/historicaldata1/sampledata/index.shtml
- document downloads: https://www.ciis.com.hk/hongkong/en/productsandservices/documentdownloads/index.shtml

Contact published by CIIS for historical data: `hd@ciis.com.hk`.

## 2. Coverage and current commercial terms

CIIS currently lists the CFFEX Level-2 historical snapshot product with first issue date **2010-04-16**, so the required MO period beginning 2022-07-22 is within the product's stated historical coverage window.

Current published unit price:

- recent three calendar years to present: USD 1,200 per three months;
- periods earlier than the recent three calendar years: USD 960 per three months.

Current listed delivery modes include cloud download for recent ongoing-subscription data, external storage media for larger deliveries, and SFTP for smaller packages. Exact billing for a partial first/last quarter must not be inferred from the web price table; obtain an actual CIIS quote/order confirmation before treating a purchase amount as fixed.

Current CIIS document index lists:

- `Historical Data Fee Schedule (v20260720)`;
- `Historical Data Product Manual (v20260819)`;
- `Historical Data Order Form (Form HD) (v20260820)`.

## 3. Public sample exists, but sample bytes are not yet admitted

The CIIS sample-data page explicitly lists under **CFFEX Level-2**:

- `20221206_Sample_CFF_Day.xlsx`;
- `20221206_Sample_CFF_Minute.xlsx`;
- `20221206_Sample_CFF_Snapshot.xlsx`.

The Snapshot sample is the only one relevant to the primary executable-quote admission check.

In the current research session the website/search index exposed the sample filename, but the actual XLSX bytes were not successfully retrieved. Therefore there is **no sample checksum, row count or byte-level schema receipt yet** and no claim that the sample itself has passed admission.

State:

`CIIS_CFFEX_LEVEL2_PUBLIC_SAMPLE_IDENTIFIED_BYTES_NOT_YET_ACQUIRED`

## 4. Historical product-manual schema evidence

The CIIS historical-data product manual available for 2022 describes CFFEX Snapshot as:

`cff\yyyymmdd\Snapshot.csv`

and documents, among other fields:

- `SecurityID`;
- `DateTime`;
- `LastPrice`;
- `Volume`;
- `OpenInterest`;
- `BidPrice[5]`;
- `BidVolume[5]`;
- `AskPrice[5]`;
- `AskVolume[5]`.

This directly supports the frozen canonical requirements for:

- contract identifier source field;
- quote timestamp source field;
- top-of-book bid and ask;
- top-of-book sizes;
- last price;
- volume;
- open interest.

The current 2026 product manual search index still describes the CFFEX Snapshot hierarchy as:

`CFF/Snapshot/<Date>/Snapshot.csv`

and states for the CFFEX section that `DateTime` uses local China market time and may include milliseconds as shown in the example.

This is documentation-level evidence only. It does not replace inspection of the delivered file version.

## 5. Canonical mapping that can already be frozen at the documentation layer

Subject to byte-level confirmation on the actual sample/delivery:

| Frozen canonical field | CIIS/CFFEX source candidate | Status before file receipt |
|---|---|---|
| `contract_code` | `SecurityID` | documented candidate |
| `timestamp` | `DateTime` | documented candidate; China local-time semantics documented in current manual |
| `bid1` | first element of `BidPrice[5]` | documented candidate |
| `bid1_size` | first element of `BidVolume[5]` | documented candidate |
| `ask1` | first element of `AskPrice[5]` | documented candidate |
| `ask1_size` | first element of `AskVolume[5]` | documented candidate |
| `last_price` | `LastPrice` | documented candidate |
| `volume` | `Volume` | documented candidate; delivered-version accumulation semantics still must be recorded |
| `open_interest` | `OpenInterest` | documented candidate |
| `option_type` | deterministic parse from MO contract identity / contract master | must be proved on delivered SecurityID convention |
| `strike` | deterministic parse from MO contract identity / contract master | must be proved on delivered SecurityID convention |
| `expiry` | official contract master / deterministic CFFEX contract convention | source/master still required |
| `trading_status` | delivered status field or fail-closed deterministic validity mapping | **not yet established** |

No mapping is allowed to be revised based on R1_B option outcomes.

## 6. Remaining admission blockers after this source review

The source-discovery problem is no longer generic. The remaining blockers are concrete:

1. acquire the actual `20221206_Sample_CFF_Snapshot.xlsx` bytes or an equivalent non-event-conditioned CFFEX Level-2 sample;
2. record SHA-256, byte size, workbook/sheet structure and row count;
3. verify that actual delivered CFFEX option `SecurityID` values include/reconstruct MO call/put, strike and expiry without outcome-conditioned logic;
4. verify exact array/column representation of five-level bid/ask and sizes in delivered files;
5. obtain authoritative zero/missing-quote semantics;
6. obtain/define trading-status and invalid-quote semantics sufficient for ask-entry/bid-exit execution;
7. obtain the current delivery's data dictionary/version and correction/republication policy;
8. acquire the full historical MO quote package for 2022-07-22 through 2026-09-10 without event-selected contracts;
9. freeze the complete exchange fee effective-period chain;
10. obtain and freeze the actual broker/customer historical commission schedule.

Until all required manifest and fee conditions pass, the state remains:

`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`

## 7. Exact acquisition request through CIIS

Request the following without supplying or conditioning on any R1_B event timestamps:

> CFFEX Level-2 Intra-Day Snapshot Historical Data for all listed CSI1000 index option (`MO`) contracts from 2022-07-22 through 2026-09-10, plus the current CFFEX Snapshot field dictionary / product manual / contract-master semantics. The delivery must preserve SecurityID, exchange-local DateTime, five-level bid/ask prices and quantities, LastPrice, Volume, OpenInterest, and any trading-status / quote-validity / zero-value semantics. Please also provide the public CFFEX Snapshot sample (`20221206_Sample_CFF_Snapshot.xlsx`) or a current equivalent sample before purchase if available.

Prospective observations from 2026-09-11 onward must remain a separately inventoried validation segment under the existing data-role freeze.

## 8. Decision

`CIIS_OFFICIAL_CFFEX_LEVEL2_ROUTE_ACCEPTED_FOR_ACQUISITION_NOT_YET_ADMITTED`

This is a source-provenance and schema-capability advance, not an empirical strategy result.
