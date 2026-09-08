# 云端—本地协作记录

本地准备数据、框架、通用基础设施；论文ZIP由用户单独交付。云端可以在具备工具时直接执行本课题研究，但不得把GitHub Actions当默认研究算力。

缺输入时追加一条记录：任务ID、问题、当前commit、已完成内容、缺少的最小字段/时间/标的、可执行步骤、预期产物与验收、生产/权限边界。不要默认索取整个DataHub。

本地反馈需要含实际命令、退出码、数据/代码/结果hash和未验证事项；云端明确区分“收到本地反馈”和“已独立复核”。外部模型无执行/写权限时只能交付代码或patch，不冒称自动派发或push成功。

最终云端回传commit及变化清单，由本地验收保存。其他四个主题仓库不是本任务可写范围。

---

## SF-20260908-001 — 恢复非英国 Unsafe/Recovering 状态池并执行频段适配 v1

**状态：OPEN — protocol/core/inference/formal runner frozen; exact state-pool artifact still missing**

### 任务来源

另一个会话线程已经把研究切换到：

- 跳过英国数据预警验证；
- 使用已有**非英国状态池**；
- 研究 CSI1000 / STAR50 在 `Unsafe` / `Recovering` 下的策略与物理频段适配；
- 重点检验“高波动是否扩大短周期可承受摩擦预算”，而不是直接假定最短周期最赚钱。

当前接管分支：

`research/state-frequency-adaptation-v1`

父提交：

`5477340e66c124df7a4691328f796e83f1802255`

### 线程2已完成

1. 新建独立研究分支，不修改冻结的 v0.15 IM replay 线。
2. 新建 `CONTINUE_HERE.md`，恢复跨线程任务语义并标记旧探索结果为 consumed evidence。
3. results-blind 冻结：
   - `docs/research/STATE_FREQUENCY_ADAPTATION_V1_PROTOCOL.md`
4. 实现 fail-closed measurement core：
   - `src/regime_lab/state_frequency_adaptation.py`
5. 增加合成/完整性测试：
   - `tests/test_state_frequency_adaptation.py`
6. 独立 Python synthetic preflight 7/7 PASS：
   - future state availability -> expected fail-closed;
   - duplicate state timestamp -> expected fail-closed;
   - 2026 row -> expected fail-closed;
   - monotone path: trend positive / reversion negative and symmetric;
   - missing physical minute is not bridged by row position;
   - state change closes/reopens routed turnover;
   - break-even friction uses actual measured turnover.

线程2 GitHub handoff HEAD：

`c318710d244cb5f10b10caef5f8b5c339f98b639`

### 线程3继续完成

线程3明确从线程2 handoff 继续，不回到线程1，也不写其他仓库。

新增：

1. `src/regime_lab/state_frequency_inference.py`
   - year/month/AM-PM/15m 固定季节性 strata；
   - matched strata 内两状态按较小样本量等质量加权；
   - raw/matched `Unsafe - Recovering` break-even friction curve；
   - 固定 short=`1/2/3/5m`、long=`10/15/30m` cost-survival summary；
   - trading-day block bootstrap；
   - 同一 bootstrap day multiplicity 同时作用于七个 horizon，保留跨 horizon 日级依赖；
   - 七个 `Delta_B(h)` 使用 Holm family-wise correction。
2. `tests/test_state_frequency_inference.py`
   - one-state stratum 不进入 matched contrast；
   - matched state mass equalization；
   - `Unsafe - Recovering` contrast 方向；
   - frozen short/long horizon set；
   - bootstrap deterministic seed / Holm guardrail；
   - bootstrap replicate lower bound。
3. `scripts/run_state_frequency_adaptation_v1.py`
   - 必须显式提供 state-pool path、SHA256、source revision；
   - 只接受 CSV/Parquet；
   - PIT schema/timestamp/duplicate/2026 继续 fail closed；
   - 冻结两资产缺失时 fail closed；
   - state surface 若含 `future/forward/target/outcome/pnl/gross_edge/net_edge/...` 等未来或 tested-outcome 字段直接拒绝；
   - verified `load_market_data(..., '1m', ...)` 读取市场数据；
   - 固定两 family × 七 horizon，一次性 replay；
   - 生成协议要求的 `RESULT_CARD.md / summary.json / input_identity.json / state_pool_audit.json / frequency_curve.csv / seasonality_matched_curve.csv / cost_survival.csv / uncertainty.csv / execution_receipt.json`；
   - runner 不自行挑选有利 adjudication，结果完成后仍需按 frozen protocol 五选一。
4. 更新 `CONTINUE_HERE.md`，把 active continuation 推进到 executable-harness gate。

线程3 GitHub 写入序列：

```text
6854af21ecb28da82ccb9dbe2595c06748fa23a6  add frozen state-frequency inference helpers
a7266861be109fd2792055ca30208959b3bae139  add inference guardrail tests
1b448c13b3390e6a2fb2390fa579f8b0c4aec1ac  add fail-closed formal state-frequency replay runner
eaa097b9e560526cccb46ced68b7daae9ed26d3d  advance thread-3 continuation to executable state-frequency gate
```

### 状态池恢复搜索

线程3再次检查：

- 当前 branch recursive tree；
- 本仓库 Issue；
- 本仓库 commit search；
- 可恢复的跨线程上下文。

仍未得到 exact prior-thread state-pool 的：

```text
artifact path / immutable git identity
SHA256
state-generation source revision
```

因此不得从价格、未来收益或本次频率结果重建 `Unsafe/Recovering`。

### 当前 cloud shell 执行限制（真实记录）

线程2已记录一次 clone DNS 失败。线程3在新增 runner 后再次尝试：

```text
git clone --depth 1 --branch research/state-frequency-adaptation-v1 \
  https://github.com/staryocean0/factorlab-trend-reversion-regime-lab.git \
  /tmp/regime-lab-thread3

exit = 128
fatal: unable to access 'https://github.com/staryocean0/factorlab-trend-reversion-regime-lab.git/':
Could not resolve host: github.com
```

因此当前记录仍然**不声称**整仓 `python -m pytest -q` 已在 cloud shell 通过，也没有启动 GitHub Actions。

线程3对新增 inference helper 做了独立 Python synthetic compile/exercise，覆盖 matched summary、contrast、cost survival、day-block bootstrap 与 deterministic seed；这不是整仓 pytest 的替代品。

### 当前缺少的最小输入

不是 DataHub 全库，也不是 UK 数据。只需要把另一个线程实际使用的状态池以不可变 artifact/文件形式放回本项目可读面，至少包含：

```text
symbol                 # 000852.SH / 000688.SH
market_time_shanghai
state                  # Unsafe / Recovering；其他原始标签可保留但不得重映射
state_available_at
source_revision        # 或 artifact identity
```

并给出文件 SHA256 / immutable Git identity。若状态池本身有 generation/config hash，也一并保留。

### 本地/有数据执行者下一动作

1. 拉取本分支最新提交；
2. 运行 `python scripts/validate_seed.py` 与 `python -m pytest -q`，保存真实退出码；
3. 恢复 exact state-pool artifact，不做重算/改标签；
4. 运行示例（实际 path/hash/revision 以原 artifact 为准）：

```text
python scripts/run_state_frequency_adaptation_v1.py \
  --state-pool <EXACT_STATE_POOL.csv_or_parquet> \
  --state-pool-sha256 <EXACT_SHA256> \
  --source-revision <EXACT_SOURCE_REVISION>
```

5. **不要修改 frozen protocol**；
6. 结果写入 `experiments/state_frequency_adaptation_v1/`，包含协议要求的全部输出；
7. 根据固定输出选择恰好一个 frozen adjudication；
8. 反馈 commit、命令/exit code、input/output hashes、正式 adjudication，并明确“云端独立复核尚未发生”。

### 禁止项

- 不从未来波动/收益重建 Unsafe/Recovering；
- 不因结果好看添加频段；
- 不用 best-of trend/reversion 作为主结论；
- 不打开 2026；
- 不做 UK 预警验证；
- 不改其他仓库；
- 不做 production/live trading；
- 不用 GitHub Actions 代替缺失 state-pool 或代替默认研究算力。
