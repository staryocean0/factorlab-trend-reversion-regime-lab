# 三桶趋势状态基线（M2）

> 状态：**M2 基线冻结。**
>
> 本文冻结的是三桶趋势状态的测量定义与因果/缺失处理规则。它不是交易策略，不授予 production authority；M3 才处理多 K 线级别/profile 绑定，M4–M6 才研究五桶与极端斜率假设。

## 1. 为什么这是“新冻结基线”，不是“恢复旧公式”

M1 审计发现 measurement-plane capability 表保留了 `trend_continuity_diagnostic` 等历史能力记录，但其中引用的 `src/factor_lab/market_state/trend_continuity_regime.py` 在当前 checkout、pre-cleanup 保留源码和本仓提交历史中都没有可恢复实现。

因此不能把本轮实现描述成“恢复原来的三桶算法”。

本基线选择当前仓库确实存在、可审计的 signed OLS 测量原语作为 authority：`core_kline_attribute_pool.py` 的 `_signed_ols_t` 已经使用 log-close 上的 signed OLS/correlation identity。M2 把这一数学定义独立封装、补齐 `as_of` 和 fail-closed 规则，并冻结成：

- schema：`trend_regime_three_bucket_baseline@1.0`
- estimator：`log_close_ols_slope_t@1.0`

BDCI、DII、signed efficiency 等继续保留为辅助测量/诊断，不参与本版三桶主状态投票。

## 2. 输入坐标

M2 primitive 接收一组已经形成的 K 线行与 timezone-aware `as_of`。

每一行至少包含：

- `bar_end`
- `available_at`
- `close`

M2 **不绑定具体 `bar_interval`**。这不是遗漏：周期/profile 的产品化绑定属于 M3。M2 的任务是先回答“给定一串已经定义好的 K 线，三桶数学和因果规则是否唯一可重复”。

## 3. 冻结的数学定义

### 3.1 回看窗口

固定：

\[
N = 20
\]

即最近 20 根在 `as_of` 时刻已经完成且已经可用的 K 线。

`N=20` 是 M2 的工程参考锚点，不是通过本轮收益搜索挑出的最优窗口。修改它需要新版本，不允许在 `@1.0` 内静默漂移。

### 3.2 价格变换

对第 \(i\) 根 K 线收盘价：

\[
y_i = \ln(C_i)
\]

其中 \(C_i>0\)。

使用 log-close 的原因是：

1. 将绝对价格尺度移除；
2. 使同一百分比趋势在不同价格量级下具有相同几何含义；
3. 与当前 `core_kline_attribute_pool._signed_ols_t` 原语保持一致。

### 3.3 OLS slope

令：

\[
x_i=i,\quad i=0,\ldots,N-1
\]

在 \(y_i\) 对 \(x_i\) 的一元线性回归中，记录：

\[
\beta =
\frac{\sum_i (x_i-\bar{x})(y_i-\bar{y})}
{\sum_i (x_i-\bar{x})^2}
\]

`beta` 作为 `slope_per_bar` 输出，单位是 log-price / bar。

### 3.4 主状态 authority：signed slope t-score

计算 \(x\) 与 \(y\) 的相关系数 \(r\)，定义：

\[
s =
r\sqrt{
\frac{N-2}
{\max(1-r^2,10^{-12})}
}
\]

该 \(s\) 与现有 `_signed_ols_t` 使用同一 correlation identity，并作为 M2 三桶的唯一主状态 authority。

重要解释：由于金融时间序列存在序列相关和异方差，`slope_t` 在本组件中是**无量纲趋势几何强度分数**，不是独立同分布误差假设下可直接解释为显著性 p-value 的正式统计检验。

### 3.5 横盘阈值

固定：

\[
T_1=2.0
\]

`T1=2.0` 是 M2 在任何收益/五桶实验之前冻结的对称工程阈值；本轮没有通过搜索收益、持有期或特定指数结果选择它。

在 `@1.0` 内，调用者不能把 `T1` 改成自己的私有值。若后续研究证明应改变定义，必须新建 estimator/profile 版本并保留旧语义。

## 4. 三桶边界

状态定义严格为：

\[
DOWN: s < -2
\]

\[
SIDEWAYS: -2 \le s \le 2
\]

\[
UP: s > 2
\]

因此 `s=-2` 与 `s=+2` 都属于 `SIDEWAYS`。边界行为有回归测试，不允许实现间各自解释。

## 5. `as_of` 与 completed-bar 规则

某根 K 线只有同时满足以下条件，才对查询时点可见：

\[
bar\_end \le as\_of
\]

且

\[
available\_at \le as\_of
\]

这意味着：

- 尚未结束的 bar 不可用；
- 已经结束但尚未发布/到达的 bar 不可用；
- 向输入中追加未来 bar，不得改变较早 `as_of` 的结果；
- `as_of`、`bar_end`、`available_at` 必须是 timezone-aware；
- `available_at < bar_end` 被视为非法时间语义并直接拒绝。

`observation_time` 对应被选窗口最后一根 bar 的 `bar_end`；结果中的 `available_at` 是所选 20 根 bar 中最晚的可用时间。

## 6. 缺失与异常：fail closed

M2 不允许为了“凑满 20 根”而静默改变数据：

- 少于 20 根 eligible bars：`UNAVAILABLE / INSUFFICIENT_COMPLETED_BARS`
- 最近 20 根中存在缺失、非有限或非正 `close`：`UNAVAILABLE / INVALID_CLOSE_IN_WINDOW`
- 不跳过坏 bar 后拿更老的一根补位；
- 不 forward-fill；
- 不插值；
- 重复 `bar_end`：输入合同错误，直接拒绝；
- 输入顺序不构成语义，内部按时间排序后计算。

一个仍明确留给 M3 的边界是**时间网格缺口**：M2 尚未绑定 `bar_interval`，因此不能在不知道预期 cadence 的情况下判断“09:40 后直接到 09:50”究竟是缺了一根 5m bar，还是本来就在用别的周期。M3 绑定 interval/profile 时必须补上 cadence-gap admission；M2 不用猜测频率来填洞。

## 7. 为什么 BDCI / DII 不参与主状态裁决

当前仓库还有：

- BDCI：回答 close-to-close 方向是否经常切换，偏“趋势友好 vs 震荡友好”，但本身没有上涨/下跌方向 authority；
- DII：描述 directional thrust，默认已经有 `strong_up / strong_down / balanced` 语义；
- signed efficiency / BCI / WBI：描述路径效率或方向不平衡。

这些量对后续研究很有价值，但如果 M2 直接把多个指标投票合成状态，就会同时引入权重、冲突处理和阈值选择，导致“三桶基线”无法成为简单、可复现的参考系。

因此 `@1.0` 只用 signed OLS slope t-score 决定 `DOWN/SIDEWAYS/UP`；其他量可以作为诊断字段或未来研究变量，但不能在不升版本的情况下改变主状态。

## 8. 回归测试冻结

`tests/test_trend_regime_baseline.py` 覆盖：

1. `-2/+2` 边界都属于 SIDEWAYS；
2. 合成上行、平坦、下行序列分别稳定得到 UP、SIDEWAYS、DOWN；
3. log-close 定义对整体价格乘法缩放保持状态/强度不变；
4. 未来或尚未发布的 bar 不影响较早 `as_of`；
5. 第 20 根 bar 尚未可见时返回 unavailable；
6. 最近 20 根中坏 close fail closed，不跳过补位；
7. 输入行逆序不改变结果；
8. naive datetime 被拒绝；
9. 重复 `bar_end` 被拒绝；
10. `lookback=20` 与 `T1=2.0` 不能在同一基线版本中静默改动。

这些测试验证的是**定义与因果一致性**，不是收益或预测有效性。

## 9. 当前输出与 authority

实现位于：

`src/factor_lab/market_state/trend_regime_baseline.py`

当前结果至少包含：

- `state`
- `slope_t`
- `slope_per_bar`
- `r_squared`
- `completed_bar_count`
- `as_of`
- `observation_time`
- `available_at`
- estimator/schema identity
- `measurement_authority=true`
- `production_authority=false`

这仍是 M2 measurement primitive，不是 M7 的 `regime_state_consumer_v1`。它不拥有 snapshot ingest/store、`valid_until`、consumer expiry/no-fallback facade，也不直接供生产策略绕过 M7 使用。

## 10. M2 Gate

M2 Gate 判定条件：

- 同一输入、同一冻结版本、同一 `as_of` 结果唯一；
- 未来/未发布 bar 不可影响当前结果；
- 缺失/坏值不被静默填补；
- 三桶边界固定；
- 低层参数不会在同一版本中静默漂移；
- 不包含交易动作语义。

满足以上条件后，下一唯一里程碑才是 **M3 — 多 K 线级别参数化**。

M3 要解决的是 interval/profile 绑定、各周期 cadence 完整性与跨周期阈值解释；不得把 M3 自动扩展成 M4/M5 的五桶实证。
