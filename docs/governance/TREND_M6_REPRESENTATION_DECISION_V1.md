# M6 Representation Decision

状态：**PASS / FROZEN — THREE BUCKET + CONTINUOUS STRENGTH**。

机器 authority：`TREND_M6_REPRESENTATION_DECISION_V1.json`。

## 1. 正式产品表示

M6 决定：Layer 2 趋势状态组件的 V1 正式表示为：

- categorical `state`: `DOWN / SIDEWAYS / UP`；
- signed `directional_score`: 精确等于 M2 已冻结的 `slope_t`；
- non-negative `strength`: `abs(directional_score)`。

正式 representation schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。

`DOWN/SIDEWAYS/UP` 的边界继续完全继承 M2：`T1=2.0`。M6 不修改 M2 数学，也不引入新的 estimator/window/normalization。

## 2. 为什么不把五桶升级成正式产品状态

M5 对“extreme slope 是否更容易耗竭”的原 H1 给出了强烈反证，但这个反证在 `T2=3 / 4 / 5` 上都成立。因此 M5 真正支持的是：**absolute slope extremeness 本身携带 persistence/strength 信息**，而不是“4.0 是一个被独特识别出的产品分界线”。

此外：

1. 15m/60m anchors 与 phase profiles 在 M5 仍 `NOT_ADMITTED_NOT_EXECUTED`；
2. 5-bar direction-adjusted return 没有像 persistence/reversal 那样形成稳定一致证据；
3. 固定五桶会把连续信息离散化，并把研究阈值误升级成产品语义；
4. M2 三桶方向合同已经稳定，而 continuous strength 可以在不破坏该合同的前提下保留 M5 发现的信息。

所以 `STRONG_UP / STRONG_DOWN` **不进入 V1 正式 state enum**。

## 3. 五桶研究资产如何处理

M4/M5 的五桶 protocol、T2=3/4/5 结果和 replication 证据全部保留，继续作为可审计的 research artifacts。

但它们：

- 不能由 M7 stable consumer 返回为正式 state；
- 不能成为 caller 参数；
- 不能以 `strong_state`、`five_bucket_state` 等字段进入 V1 stable snapshot；
- 不能产生 BUY/SELL/position/order 语义。

以后如果要把五桶升级为产品能力，必须新建 representation schema/version，并重新进行结果前冻结与证据验证；不能静默修改 M6 V1。

## 4. 连续 strength 的精确定义

M6 不创造新 score。

```text
directional_score = M2 slope_t
strength = abs(directional_score)
```

其中 `directional_score` 保留方向；`strength` 只表达绝对趋势几何强度。二者都不是 iid t-test 显著性，也不是收益预测概率。

对于 V1：

- `DOWN` 必须与 `directional_score < -2` 一致；
- `SIDEWAYS` 必须与 `-2 <= directional_score <= 2` 一致；
- `UP` 必须与 `directional_score > 2` 一致。

任何 state/score 不一致都应 fail closed，而不是强行修正。

## 5. 证据范围

M5 对 strength/persistence 语义的实证支持目前只覆盖：

- intervals：1m、5m；
- carriers：CSI1000 `000852.SH`、STAR50 `000688.SH`；
- historical Validation：2023-01-03–2024-12-31；
- `fresh_oos=false`。

15m/60m 和 phase profiles 仍没有 M5 实证认证。M6 的 representation 在结构上可以包装同一个 M2 score，但文档/consumer 不得声称这些未验证 interval 已获得同等级 persistence certification。

## 6. M7 必须继承的边界

M7 stable snapshot 至少要包含：

- `state`；
- `directional_score`；
- `strength`；
- `representation_schema_id`；
- `state_scheme_id`；
- `strength_definition_id`。

并且：

- `state` 只能是三桶；
- `directional_score` 必须等于 frozen `slope_t`；
- `strength` 必须等于其绝对值；
- caller 不能传 T2；
- stable API 不得返回 strong-state 字段；
- multi-interval 仍不得产生 `global_state`；
- `production_authority=false`。

M7 只实现 consumer/snapshot lifecycle，不重新讨论表示层。

## 7. 不变的产品边界

组件仍然只是 Layer 2 市场状态测量组件，不是交易策略。M6 只决定“怎样表示趋势方向和强度”，不决定“应该做什么交易”。
