# 趋势状态识别组件路线图

> 本路线图定义未来工作的执行顺序。它不是收益研究结论，也不把市场状态直接写成策略规则。
>
> 执行纪律：**一次会话只推进当前里程碑；完成当前 Gate 后也不自动进入下一里程碑。**

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：冻结 20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：冻结 `1m/5m/15m/60m` versioned profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：结果前冻结五桶实验协议。
- **M5 — PASS**：CSI1000 primary、T2 sensitivity、STAR50 replication 完整收口；原 extreme-slope exhaustion H1 被稳健反驳。
- **M6 — PASS**：正式产品表示冻结为 **三桶 + 连续 strength**；正式 state 仅 `DOWN/SIDEWAYS/UP`，`directional_score=slope_t`，`strength=abs(slope_t)`；五桶保留为 research artifacts，不进入 V1 stable API。
- **唯一下一步：M7 — Stable Consumer API + Snapshot Lifecycle。**

---

## M0–M3 — 基础工程（PASS）

组件始终是 Layer 2 趋势状态识别组件，不是交易策略。M2 冻结三桶数学，M3 绑定 DataHub Layer-1 V3 wall-clock views；不同周期独立并存，不产生 `global_state`，不本地 resample，不输出交易动作。

## M4 — 五桶实验协议（PASS）

预注册 H1：同 interval/方向下，extreme absolute slope state 可能比 moderate trend state 更难持续、更容易衰减/反转。

冻结 `T1=2.0`、primary `T2=4.0`、sensitivity `T2=3/5`、Development/Validation/Holdout split、episode/horizon/sample floor、ISO-week bootstrap、Holm family 与 negative-result rules。

## M5 — 极端斜率持续性实证（PASS）

机器 closeout：`docs/governance/TREND_M5_CLOSEOUT_V1.json`。

当前 active exact source 对两 carrier 只实证准入 1m official / 5m offset0；15m/60m anchors 与 phase profiles 均 `NOT_ADMITTED_NOT_EXECUTED`。

### CSI1000 primary `T2=4`

四个 executable survival Strong−Moderate contrasts 为 `+0.3673` 至 `+0.3853`，所有 CI > 0；reversal10 为 `-0.2360` 至 `-0.2507`，所有 CI < 0。Headline：`H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS`。

### T2=3/5 sensitivity

8/8 executable sensitivity contrasts 继续 H1_CONTRADICTED，0/8 朝 H1 方向。因此结果不是 T2=4 单点阈值偶然。

### STAR50 replication

四个 executable replication survival contrasts 为 `+0.3394` 至 `+0.3735`，所有 CI > 0；reversal10 同样全部 < 0。Replication：`CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION`。

M5 最终解释：对 admitted 1m/5m exact views，absolute slope extremeness 是有实证支持的 **persistence/strength descriptor 候选**，但 5-bar direction-adjusted return 没有形成同等级稳定证据，因此不能翻译成收益/交易规则。2025 Holdout 从未打开；M5 one-shot outcome jobs 均 consumed。

---

## M6 — Representation Decision（PASS）

机器 authority：`docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json`。

### 选择

正式 V1 representation：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

### 为什么不正式五桶

- M5 在 `T2=3/4/5` 都给出同一 qualitative persistence 结果，支持连续 extremeness，而没有识别一个独特、必须固定的产品 cutoff；
- 15m/60m 和 phase profiles 未获得 M5 实证认证；
- return evidence 没有 persistence/reversal 那样稳定；
- 连续 strength 能保留信息，同时不破坏已经稳定的三桶方向合同。

因此 `STRONG_UP / STRONG_DOWN` 不属于 V1 formal state enum；T2 不属于 stable caller parameter；M4/M5 五桶资产只保留为 research audit artifacts。

### M6 强度定义

`directional_score` 精确等于 frozen `log_close_ols_slope_t@1.0` 的 `slope_t`；`strength=abs(directional_score)`。不做 unit-interval normalization，不做 quantile normalization，不重新拟合。

M5 的 persistence/strength evidence certification 当前只覆盖 1m/5m 与两个 carrier，`fresh_oos=false`。这不妨碍同一数学 representation 包装其他 profile，但不得宣称 15m/60m 已获得同等级实证认证。

---

## M7 — Stable Consumer API + Snapshot Lifecycle（唯一下一步）

M7 必须实现并测试：

- `query_regime(symbol, as_of, bar_interval, profile_id)`；
- immutable snapshot + stable snapshot ID；
- `published_at <= as_of < valid_until`；
- latest-expired no fallback；
- provider/profile fail-closed admission；
- M6 fields：`state / directional_score / strength / representation_schema_id / state_scheme_id / strength_definition_id`；
- stable API 禁止 T2 / STRONG_* / five-bucket state；
- multi-interval 仍无 `global_state`；
- `production_authority=false`。

M7 不得重开 M5 outcome、打开 Holdout 或重新裁决 M6 representation。

## M8 — 策略匹配与集成验证

趋势组件只描述状态/强度；上层策略决定如何与风险状态组合并映射交易动作。

## M9 — 发布、版本与治理

形成稳定 schema、API 示例、profile 清单、证据追踪、changelog/migration 与 CI 治理。

---

## 全程不变原则

1. **组件不是策略。**
2. **状态必须绑定时间尺度/profile/version。**
3. **方向三桶 + 连续强度是 V1 正式表示。**
4. **研究阈值不得静默升级成产品语义。**
5. **负结果允许；禁止调参救结论。**
