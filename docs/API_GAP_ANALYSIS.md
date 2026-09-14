# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M7）

> **M7 PASS。** Stable consumer、snapshot identity/lifecycle、expiry/no-fallback、current provider admission 与 conformance suite 已实现。当前唯一下一步是 M8 上层调用集成验证。

## 1. 当前路径

```text
M2/M3 measurement + profiles
        +
M4/M5 evidence
        +
M6 three-bucket + continuous strength
        +
M7 stable consumer + snapshot lifecycle
        ↓
M8 caller integration
        ↓
M9 release/governance
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G01 | 无正式公开 trend consumer entrypoint | **M7 RESOLVED**：`TrendRegimeConsumer.query_regime` |
| G02 | `regime_state_consumer_v1` 未代码实现 | **M7 RESOLVED** |
| G03 | 无 snapshot lifecycle/store | **M7 RESOLVED**：immutable + append-only store |
| G04 | unavailable/expiry 未代码化 | **M7 RESOLVED**：expiry/no-fallback runtime semantics |
| G05 | caller/component 参数所有权 | M3/M7 RESOLVED |
| G06/G07 | 三桶数学/completed-bar/T1 | M2 RESOLVED |
| G08 | 多周期 profile | M3 RESOLVED |
| G09 | 五桶市场证据收口 | M5 RESOLVED |
| G11 | 无 trend snapshot identity/history | **M7 RESOLVED**：deterministic snapshot ID + append-only history |
| G12 | 无 consumer conformance suite | **M7 RESOLVED**：默认 CI 覆盖 causality/expiry/immutability/admission |
| G15/G16 | cadence / global trend 歧义 | M3 RESOLVED |
| G18–G24 | M4/M5 preregistration/evidence gaps | M4/M5 RESOLVED |
| G25 | representation 未裁决 | M6 RESOLVED：three-bucket + continuous strength |
| G26 | M6 representation 尚未进入 snapshot | **M7 RESOLVED** |

## 3. M7 当前 runtime contract

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

- consumer schema：`regime_state_consumer_v1`
- snapshot schema：`trend_regime_snapshot@1.0`
- formal state：`DOWN / SIDEWAYS / UP`
- `directional_score=slope_t`
- `strength=abs(directional_score)`
- latest expired/unavailable 不回退旧 snapshot
- current provider admission 仅两指数 1m official / 5m offset0
- 15m/60m 与 phase profiles 在当前 registry 下 `STATE_NOT_ADMITTED`
- T2 / STRONG_* / five-bucket / global_state / action fields 禁止进入 stable output
- `production_authority=false`

## 4. 仍未解决的核心 Gap

| ID | Gap | 当前状态 | 目标 | 归属 |
|---|---|---|---|---|
| G10 | provider/source admission 范围不完整 | V1 runtime 仅 1m/5m exact source；其他 profiles fail closed | 后续若扩张必须新 exact receipt/version | M9/未来版本 |
| G13 | release lifecycle / migration 尚未完整发布化 | M7 machine contract 已登记 owner/schema/status；release/migration 尚未做 | changelog/migration/release policy | M9 |
| G14 | 多调用者集成未证明 | stable consumer 已具备 | 至少两个上层 caller 的集成/conformance 验证 | **M8** |
| G17 | 完整交易日 completeness authority 不在 Layer 2 | consumer 不猜交易日 | Layer-1 calendar/provider authority | M9/上游 |
| G27 | 上层可能误把 state/strength 当交易动作 | M7 已明确无 trading authority，但尚未做实际 caller 约束验证 | integration boundary tests | **M8** |

## 5. 唯一下一步：M8

M8 只做策略层调用集成验证：证明不同 caller 能安全读取 M7 snapshot，并由上层自行处理多周期组合/风险组合/动作映射。

M8 不得：

- 修改 M6 representation；
- 修改 M7 provider admission、snapshot identity、expiry/no-fallback；
- 重跑 M5 或读取 Holdout；
- 把 `UP/DOWN/strength` 写成组件内部 BUY/SELL/仓位规则。
