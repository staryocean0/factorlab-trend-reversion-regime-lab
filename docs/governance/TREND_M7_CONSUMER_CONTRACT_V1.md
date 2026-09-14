# M7 Stable Consumer Contract

状态：**PASS — Stable Consumer V1**。机器 authority 为 `TREND_M7_CONSUMER_CONTRACT_V1.json`。

正式只读入口：

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

查询方只选择 symbol、timezone-aware as_of、bar interval，以及 interval 存在歧义时的 profile。查询方不能传 estimator/window/T1/T2/provider admission/有效期策略，更不能传买卖、仓位或路由参数。

正式 snapshot schema 为 `trend_regime_snapshot@1.0`，产品表示继续严格继承 M6：state 仅 `DOWN / SIDEWAYS / UP`，`directional_score` 为冻结 M2 `slope_t`，`strength=abs(directional_score)`。Stable API 不允许 `STRONG_UP/STRONG_DOWN`、five-bucket state、T2 或 `global_state`。

生命周期为 append-only + immutable：相同 snapshot ID 的完全相同 payload 可幂等重复；冲突改写拒绝；不得在 published_at 前接收；source snapshot 和 consumer receipt 都不能倒序。As-of 只能看到当时已经被 consumer 收到的 snapshot。

若 as_of 前最新 snapshot 已过期，返回 `UNAVAILABLE / LATEST_SNAPSHOT_EXPIRED`，禁止回退旧 snapshot；若最新 snapshot 本身显式 unavailable，也禁止回退。Unavailable 查询不泄露 state/score/strength。

当前 V1 provider registry 冻结为 DataHub `factorlab_unified_index_kline_v3_20260824`，仅接纳两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`。M3 其余工程 profiles 并未因此消失，但在当前 provider admission 下必须 fail closed 为 `STATE_NOT_ADMITTED`。调用者和构造器都不能自行扩张这个 V1 registry。

`valid_until` 是 component/provider publication layer 的因果坐标，不是 query caller knob；consumer 负责强制 expiry/no-fallback，而不自行猜测交易日或源端有效期。

M7 不授予 production authority，也没有交易动作语义。M5 outcome 不重开，2025 Holdout 仍未读取。下一里程碑只能是 M8 的上层调用集成验证，不能改变 M7 consumer 语义。
