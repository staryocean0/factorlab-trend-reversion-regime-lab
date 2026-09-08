# 云端—本地协作记录

本地/DataHub 为核心存储权威；云端可在具备工具时执行研究，但不得把 GitHub Actions 当默认研究算力。缺输入时只请求完成当前任务所需的最小输入。反馈必须区分“收到执行结果”和“已独立复核”，并记录命令、退出码、代码/数据/结果 hash 与未验证事项。

其他主题仓库不是本任务可写范围。2026、生产/live trading 和 UK 预警验证均不在当前研究范围。

---

## SF-20260908-001 — State-frequency adaptation v1

**状态：PAUSED / PRESERVED**

分支：`research/state-frequency-adaptation-v1`

已完成 protocol、fail-closed measurement core、inference、tests、formal runner 和 handoff。该研究仍缺 prior-thread exact `Unsafe/Recovering` state-pool immutable artifact/hash/source revision，因此不得重新制造标签，也未产生正式 state-frequency empirical adjudication。

该分支保持不变；当前用户已明确把下一优先级切换到“图形识别能力”。

---

## KSR-20260908-001 — K线图形/状态识别 v1

**状态：OPEN — recognition exam implemented; real historical score pending data-capable execution**

### 用户目标

```text
K线图形 -> 特征 -> 市场状态 -> 状态切换识别 -> 验证识别正确率
```

当前分支：

`research/kline-state-recognition-v1`

基线：

`research/state-frequency-adaptation-v1`

### 冻结协议

`docs/research/KLINE_STATE_RECOGNITION_V1_PROTOCOL.md`

协议在第一次真实历史 recognition score 前冻结。preflight 阶段把最初 24 根主窗口改为 12 x 5m（60交易分钟），并增加 `recognition_eligible` gate；修改发生在没有看到真实 recognition score 的情况下，用于消除物理 warm-up 不可识别行对覆盖率的结构性惩罚。

Frozen design：

```text
clock = 5m
short = 6 bars / 30m
primary = 12 bars / 60m
centered offline judge = +/- 6 bars
strict-prior reference = 480 finite observations
states = UpTrend / DownTrend / Range / Shock / Uncertain
transition confirm = 2 consecutive eligible bars
transition tolerance = +/-3 eligible bars / 15m
```

### 已完成代码

1. `src/regime_lab/kline_state_recognition.py`
   - verified/quality-filtered K线输入；
   - missing physical 5m bar breaks run；
   - strict lunch bridge；
   - causal signed efficiency / BDCI / DII / RV / bar geometry；
   - strict-prior shock ranks；
   - online state classifier；
   - centered offline visual-reference judge；
   - recognition eligibility；
   - two-bar transition confirmation；
   - one-to-one destination-specific transition matching。

2. `src/regime_lab/kline_state_evaluation.py`
   - strict separated evaluator；
   - concrete-state confusion/per-state metrics；
   - eligible abstention counts as miss；
   - supported class completely missed => F1 exactly 0；
   - 4-state balanced accuracy / macro F1；
   - yearly metrics；
   - transition precision/recall/F1 / delay / false transitions per day。

3. `tests/test_kline_state_recognition.py`
   - four concrete state rule；
   - missing context abstention；
   - prefix-causality guard；
   - lunch-gap guard；
   - 2026 fail closed；
   - transition confirmation/matching；
   - zero-match F1；
   - empty-event safety；
   - abstention penalty；
   - ineligible warm-up exclusion；
   - fully missed class retained as F1=0 in macro score。

4. `scripts/run_kline_state_recognition_v1.py`
   - verified repository `5m` data only；
   - CSI1000 2015-01-05..2025-12-31；
   - STAR50 2020-07-23..2025-12-31；
   - canonical scorer = `regime_lab.kline_state_evaluation.score_recognition_strict`；
   - emits required experiment bundle and Level 2/3/4 adjudication。

### Capability gates

Level 3（两资产都满足）：

```text
balanced_accuracy >= 0.55
transition_F1 >= 0.40
concrete coverage >= 0.60
each concrete-state support >= 100
```

Level 4（两资产都满足）：

```text
balanced_accuracy >= 0.70
transition_F1 >= 0.60
concrete coverage >= 0.75
>= 3 eligible yearly slices
yearly median balanced_accuracy >= 0.60
no eligible year balanced_accuracy < 0.50
```

Level 5 不允许由本 consumed-history v1 给出；需要 fresh held-out 或独立人工/外部图形标注。

### 已做 synthetic/preflight

独立 Python synthetic reconstruction 在修正“整类漏识别 F1 必须为0”后达到：

`ALL_CHECKS_PASS`

覆盖：state rule、prefix causality、missing-bar/lunch guard、transition matching、zero F1、empty events、abstention penalty、eligibility gate、missed-class macro-F1 inclusion。

### 当前执行限制

尝试 real clone：

```text
git clone --depth 1 --branch research/kline-state-recognition-v1 \
  https://github.com/staryocean0/factorlab-trend-reversion-regime-lab.git \
  /mnt/data/regime-lab-kline
```

结果：

```text
exit = 128
Could not resolve host: github.com
```

因此当前记录**不声称**：

- full repository `python -m pytest -q` 已在真实 clone 通过；
- full CSI1000/STAR50 historical recognition replay 已执行；
- empirical Level 2/3/4 已确定。

没有使用 GitHub Actions 代替该执行。

### 下一位有数据执行者只需执行

```text
git checkout research/kline-state-recognition-v1
python scripts/validate_seed.py
python -m pytest -q
python scripts/run_kline_state_recognition_v1.py
```

结果必须写到：

`experiments/kline_state_recognition_v1/`

核心产物：

```text
RESULT_CARD.md
summary.json
input_identity.json
feature_contract.json
state_timeseries.csv
transition_events.csv
confusion_matrix.csv
per_state_metrics.csv
yearly_metrics.csv
execution_receipt.json
```

反馈至少包含：commit、三条实际命令与 exit code、input/output hashes、两个资产的 balanced accuracy / macro F1 / coverage / transition F1，以及最终 Level。

### 禁止项

- 不用未来收益/P&L定义 online state；
- centered oracle 只能用于评分，不能进入 online feature；
- 不因 v1 分数低就修改阈值、状态名、窗口或切换 1m；
- v1 弱则保留失败结果并另开 preregistered v2；
- 不打开 2026；
- 不改其他仓库；
- 不做 production/live；
- 不把收益率当成图形识别正确率。
