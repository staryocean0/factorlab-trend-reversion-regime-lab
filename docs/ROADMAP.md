# 趋势状态识别组件路线图

> 本路线图定义执行顺序。组件是 Layer 2 市场状态基础设施，不是交易策略。
>
> 执行纪律：一次会话只推进当前里程碑；通过 Gate 后也不自动进入下一里程碑。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：versioned interval/profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：五桶研究协议在 outcome 前冻结。
- **M5 — PASS**：CSI1000 primary、T2 sensitivity、STAR50 replication 收口；原 extreme-slope exhaustion H1 被稳健反驳。
- **M6 — PASS**：正式表示为三桶 + 连续 strength。
- **M7 — PASS**：stable `regime_state_consumer_v1`、immutable snapshot、append-only lifecycle、expiry/no-fallback 与 provider admission 已实现并进入默认 CI。
- **唯一下一步：M8 — 策略层调用集成验证。**

## M6 正式表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。V1 stable API 不包含 T2、`STRONG_UP/STRONG_DOWN`、five-bucket state 或 `global_state`。

## M7 Stable Consumer（PASS）

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

正式调用面：

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

已实现：

- immutable `trend_regime_snapshot@1.0` + deterministic snapshot ID；
- append-only ingest；相同 duplicate 幂等、冲突 duplicate 拒绝；
- `received_at >= published_at`，receipt/source snapshot 禁止倒序；
- as-of 只读取当时 consumer 已收到的 snapshot；
- latest expired => `LATEST_SNAPSHOT_EXPIRED`，禁止 fallback；
- latest explicit unavailable 同样禁止 fallback；
- unavailable 不泄露 state/score/strength；
- 当前 V1 provider registry 固定为 DataHub exact source，两指数仅 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；其余 M3 engineering profiles 返回 `STATE_NOT_ADMITTED`；
- provider registry 不能由 caller/constructor 自行扩张；
- `source_receipt_id` 必须为非空字符串；
- `production_authority=false`、无交易动作 authority。

M7 不读取市场 outcome，不重开 M5，不打开 2025 Holdout。

## M8 — 策略层调用集成验证（唯一下一步）

M8 只验证上层 caller 如何安全消费 M7 snapshot。趋势组件继续只描述状态/强度；多周期综合、与风险状态组合、策略选择和交易动作全部属于上层。

M8 不得修改 M6 representation、M7 snapshot lifecycle/provider admission，也不得把 state/strength 直接写成 BUY/SELL/仓位规则。

## M9 — 发布、版本与治理

负责稳定版本、migration/changelog、证据追踪和发布治理。

## 全程不变原则

1. 组件不是交易策略。
2. 状态绑定 symbol / as_of / interval / profile / version。
3. V1 是三桶方向 + 连续强度。
4. 当前 runtime source admission 只有两指数 1m official / 5m offset0。
5. 研究阈值不得静默升级为产品语义。
6. `production_authority=false`，直到未来独立治理明确改变。
