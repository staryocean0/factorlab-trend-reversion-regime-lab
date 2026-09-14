# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M6）

> **M5 COMPLETE，M6 PASS。** 正式表示已冻结为三桶方向状态 + 连续 strength。当前唯一下一步是 M7 stable consumer implementation。

## 1. 当前路径

```text
M2/M3 measurement + profiles
        +
M4 preregistered protocol
        +
M5 empirical evidence COMPLETE
        +
M6 representation: THREE BUCKET + CONTINUOUS STRENGTH
        ↓
M7 stable consumer
        ↓
M8 integration
        ↓
M9 release/governance
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G05 | caller/component 参数所有权 | M3 RESOLVED |
| G06/G07 | 三桶数学/completed-bar/T1 | M2 RESOLVED |
| G08 | 多周期 profile | M3 RESOLVED |
| G15 | interval cadence gap | M3 RESOLVED |
| G16 | 多周期总趋势歧义 | M3 RESOLVED：无 `global_state` |
| G18 | 五桶协议可事后改口 | M4 RESOLVED |
| G19/G20 | source admission / availability semantics | M5-1 RESOLVED |
| G21 | Validation 前 identity seal | M5-3 RESOLVED |
| G22 | primary T2=4 evidence | M5-4 RESOLVED：H1 CONTRADICTED |
| G23 | T2 sensitivity | M5-5 RESOLVED：8/8 sensitivity contrasts CONTRADICTED |
| G24 | cross-carrier replication | M5-6 RESOLVED：STAR50 clear qualitative replication |
| G09 | 五桶市场证据收口 | M5 RESOLVED |
| G25 | 最终 representation 未裁决 | **M6 RESOLVED：THREE_BUCKET_PLUS_CONTINUOUS_STRENGTH** |

## 3. M6 正式表示

Machine authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

V1 stable API 不包含 `STRONG_UP / STRONG_DOWN`、five-bucket state 或 caller-supplied T2。T2=3/4/5 只保留为 M4/M5 research artifacts。

选择连续 strength 的原因是 M5 在 T2=3/4/5 均得到同一 qualitative persistence evidence，支持连续 slope extremeness，但没有识别唯一 product cutoff；且 15m/60m 与 phase profiles 未获得同等级实证认证。

## 4. 仍未解决的核心 Gap

| ID | Gap | 当前证据/合同 | 目标 | 归属 |
|---|---|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | M6 representation 已冻结 | `query_regime/as_of` facade | M7 |
| G02 | `regime_state_consumer_v1` 未代码实现 | API contract 已冻结 | stable envelope | M7 |
| G03 | 无 snapshot lifecycle/store | measurement clocks 有 | immutable snapshot + expiry/no-fallback | M7 |
| G04 | unavailable/expiry 未代码化 | 文档合同 | runtime semantics | M7 |
| G10 | provider/source admission 不完整 | current empirical certification 仅 1m/5m；15m/60m/phase 未认证 | provider acceptance fail closed | M7/M9 |
| G11 | 无 trend snapshot identity/history | representation primitive 不是发布事件 | stable snapshot ID | M7 |
| G12 | 无 consumer conformance suite | 当前是底层/研究治理 tests | consumer compatibility tests | M7 |
| G13 | consumer 生命周期未登记 | representation 已有 version | owner/version/status/migration | M7/M9 |
| G14 | 多调用者集成未证明 | consumer 尚未实现 | integration validation | M8 |
| G17 | 完整交易日 completeness authority 不在 Layer-2 | session grid 可验 | Layer-1 calendar/provider receipt | M7/M9 |
| G26 | M6 representation 尚未进入正式 snapshot | M6 primitive + API contract 已冻结 | snapshot fields `state/directional_score/strength` | **M7** |

## 5. M7 唯一任务

M7 必须实现 immutable consumer/snapshot lifecycle，并继承 M6：

- stable state 仅三桶；
- `directional_score=slope_t`；
- `strength=abs(directional_score)`；
- 禁止 T2/STRONG_*/five-bucket stable fields；
- provider/profile fail closed；
- latest-expired no fallback；
- multi-interval 无 global state；
- `production_authority=false`。

M7 不得重开 M5 outcome 或改变 M6 representation。
