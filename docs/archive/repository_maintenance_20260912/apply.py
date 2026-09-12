"""One-time, bounded repository housekeeping. No market data or study execution."""
from pathlib import Path
import hashlib, json, os, re, subprocess
ROOT = Path.cwd()
BASE = 'b4d023b100c49c7dbaa44e81417d7a0386a5b004'
ARCHIVE = 'docs/archive/repository_pre_cleanup_20260912'
STATE = 'docs/REPOSITORY_STATE.json'

def write(path, text):
    p=ROOT/path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip()+'\n', encoding='utf-8')

def read(path): return (ROOT/path).read_text(encoding='utf-8')
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def link(path, target, title=None):
    return '['+(title or target)+']('+os.path.relpath(target, str(Path(path).parent))+')'

MODULES = {
'etf_day_reconciliation': ('READ_ONLY_SOURCE_CONSUMER', 'ETF_DAY_RECONCILIATION_REVIEW_20260912.md', 'etf-day-reconciliation.yml'),
'etf_one_day_review': ('COMPLETED_SOURCE_AUDIT_REPLAY_ONLY', 'ETF_ONE_DAY_CLOUD_REVIEW_20260912.md', 'etf-one-day-observation.yml'),
'etf_upstream_review': ('COMPLETED_SOURCE_AUDIT_REPLAY_ONLY', 'ETF_UPSTREAM_CLOUD_REVIEW_20260912.md', 'etf-upstream-delivery.yml'),
'etf_source_repair': ('COMPLETED_KNOWN_ACTION_REPAIR_REPLAY_ONLY', 'ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md', 'etf-source-repair.yml'),
'etf_index_measurability': ('COMPLETED_MEASUREMENT_REPLAY_ONLY', 'ETF_INDEX_MEASURABILITY_REVIEW_20260912.md', 'etf-index-measurability.yml'),
'r1a_evidence_closeout': ('RESERVE_DISPOSITION_READ_ONLY_AUDIT', 'R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md', 'r1a-evidence-closeout.yml'),
'r1a_walkforward_prediction': ('RESERVED_HISTORICAL_REPLAY_ONLY', 'R1A_WALKFORWARD_PREDICTION_REVIEW_20260912.md', 'r1a-walkforward-prediction.yml'),
'r1a_control_design': ('CLOSED_DESIGN_NO_SELECTED_OUTCOMES', 'R1A_CAUSAL_CONTROL_DESIGN_REVIEW_20260912.md', 'r1a-control-design.yml'),
'r1a_development_noise': ('COMPLETED_DEVELOPMENT_REPLAY_ONLY', 'R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md', 'r1a-development-noise-regression.yml'),
'r1a_confirmation_feasibility': ('COMPLETED_PLANNING_NO_NEW_PROBES', 'R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md', 'legacy-price-statistics-replay.yml'),
'r1a_method_calibration': ('COMPLETED_SYNTHETIC_REPLAY_ONLY', 'R1A_METHOD_CALIBRATION_REVIEW_20260912.md', 'legacy-price-statistics-replay.yml'),
'r1a_endpoint_robustness': ('COMPLETED_RETROSPECTIVE_REPLAY_ONLY', 'R1A_ENDPOINT_ROBUSTNESS_REVIEW_20260912.md', 'legacy-price-statistics-replay.yml'),
'r1a_carrier_transport': ('RESERVED_LEGACY_PRICE_REPLAY_ONLY', 'R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md', 'legacy-price-statistics-replay.yml'),
'index_price_validity': ('COMPLETED_HISTORICAL_REPLAY_ONLY', 'INDEX_PRICE_VALIDITY_STUDY_20260911.md', 'legacy-price-statistics-replay.yml'),
'r1_incremental_alpha_attribution': ('COMPLETED_HISTORICAL_REPLAY_ONLY', 'R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md', 'legacy-price-statistics-replay.yml'),
'r1b_mo_data_admission': ('RETIRED_ACQUISITION_RETAINED_FOR_DEPENDENCIES', 'R1B_MO_OUTCOME_STUDY_20260911.md', 'legacy-price-statistics-replay.yml'),
'r1b_mo_pre_execution': ('CLOSED_OPTION_IDENTITY_REPLAY_ONLY', 'R1B_MO_PRE_EXECUTION_FREEZE_20260911.md', 'legacy-price-statistics-replay.yml'),
'r1b_mo_outcome': ('CLOSED_OPTION_IDENTITY_REPLAY_ONLY', 'R1B_MO_OUTCOME_STUDY_20260911.md', 'legacy-price-statistics-replay.yml'),
'r1b_mo_backspread': ('CLOSED_OPTION_IDENTITY_REPLAY_ONLY', 'R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md', 'legacy-price-statistics-replay.yml'),
}

def run():
    if os.environ.get('GITHUB_REF_NAME') != 'maintenance/repository-consistency-20260912':
        raise SystemExit('One-time migration allowed only on the named maintenance branch.')
    raw=subprocess.check_output(['git','ls-tree','-rz',BASE])
    entries={}
    for line in raw.split(b'\0'):
        if line:
            meta,path=line.split(b'\t',1); mode,kind,sha=meta.decode().split()
            if kind=='blob': entries[path.decode()]={'mode':mode,'git_blob':sha}
    if (ROOT/'docs/maintenance/BASELINE_COMPONENTS.json').exists():
        raise SystemExit('Migration already sealed; use the consistency checker instead.')
    roots=['README.md','CONTINUE_HERE.md','AGENTS.md','PROMPT.md','ai-readme.md']
    overview=['docs/DATA.md','docs/INFRASTRUCTURE.md','docs/RESEARCH_GOVERNANCE.md','docs/cloud_local_communication.md']
    handoffs=['docs/ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md','docs/ops/ETF_ONE_DAY_SOURCE_DELIVERY_20251201.md']
    snapshots=roots+overview+handoffs+['docs/seed_manifest.json','docs/infrastructure_manifest.json','.codex/cloud_setup.sh','pyproject.toml','src/regime_lab/__init__.py','docs/archive/README.md']
    snapshots += sorted(p for p in entries if p.startswith('.github/workflows/'))
    snapshots += sorted(p for p in entries if p.startswith('research/') and p.endswith('/README.md'))
    for p in snapshots:
        b=(ROOT/p).read_bytes(); assert blob(b)==entries[p]['git_blob'], p
        dest=ROOT/ARCHIVE/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
    (ROOT/'docs/seed_manifest.json').unlink()
    for p in sorted(ROOT.glob('.github/workflows/*.yml')):
        if str(p.relative_to(ROOT)) not in entries: continue
        text=p.read_text(); name=p.name
        text=re.sub(r'(?ms)^on:\n.*?(?=^permissions:)', 'on:\n  workflow_dispatch:\n  workflow_call:\n\n', text)
        if 'persist-credentials:' not in text:
            text=text.replace('        with:\n          ref:', '        with:\n          persist-credentials: false\n          ref:')
            if 'persist-credentials:' not in text:
                text=text.replace('        with:\n          sparse-checkout:', '        with:\n          persist-credentials: false\n          sparse-checkout:')
        if name=='r1b-mo-data-admission-gate.yml':
            name='legacy-price-statistics-replay.yml'
            text=text.replace('name: research-regression-gate','name: legacy-price-statistics-replay')
            text=text.replace('            docs/governance\n','            docs\n')
            p.unlink()
        write('.github/workflows/'+name,text)
    write('src/regime_lab/__init__.py','"""Research data access and publication guards; no production trading authority."""')
    project=read('pyproject.toml').replace('FactorLab reversal/mean-reversion research and MO data-admission lab','Reproducible trend/reversion research, source audits and retained historical evidence')
    project=project.replace('[tool.hatch.build.targets.wheel]', '[project.optional-dependencies]\nmaintenance = ["PyYAML>=6,<7"]\n\n[tool.hatch.build.targets.wheel]')
    write('pyproject.toml',project)
    write('.codex/cloud_setup.sh', '''#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
.venv/bin/python -m pip install -e '.[maintenance]'
.venv/bin/python scripts/repository_consistency.py --check
.venv/bin/python -m pytest -q tests/test_repository_consistency.py
# Full retained-data regression is explicit; setup never starts a historical fit.
if [[ "${RUN_FULL_REGRESSION:-0}" == 1 ]]; then
  .venv/bin/python -m pytest -q
fi''')
    state={'schema_id':'factorlab_repository_state@1.0','baseline_commit':BASE,'scientific_status':'FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION','r1a_status':'R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED','active_empirical_candidate':None,'new_local_transfer_required':False,'production_authority':False,'fresh_oos':False,'BLACKBOX_query_count':3,'latest_review':'docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md','latest_receipt':'docs/ops/evidence/etf_day_reconciliation_20260912/receipt.json','r1a_disposition':'docs/governance/R1A_PRICE_RESEARCH_DISPOSITION_20260912.json','consumer_contract':'docs/governance/ETF_SOURCE_LABEL_CONSUMER_V1_20260912.json','maintenance_does_not_change_scientific_status':True,'modules':{},'generated_documents':{},'manual_workflows':[]}
    for name,(status,report,wf) in MODULES.items():
        assert (ROOT/'research'/name).is_dir(),name
        assert (ROOT/'docs/research'/report).exists(),report
        state['modules'][name]={'status':status,'report':'docs/research/'+report,'workflow':'.github/workflows/'+wf}
    state['manual_workflows']=sorted('.github/workflows/'+p.name for p in ROOT.glob('.github/workflows/*.yml') if p.name not in {'repository-maintenance.yml','repository-consistency.yml'})
    bodies={
'README.md':'''# FactorLab 趋势反转与均值回归研究

## 入口

[当前状态与下一步边界](CONTINUE_HERE.md) · [当前研究与工程白皮书](docs/WHITEPAPER.md) · [组件索引](docs/COMPONENTS.md) · [测试与工作流](docs/TESTING.md) · [数据用途说明](docs/DATA.md)

当前没有已确认策略或自动续开的实验。已完成的研究、数据修正和审计可复现，但复现通过不增加市场证据。请勿将归档快照或旧manifest中的complete=true作为新的研究准入。

## 本地环境

```bash
bash .codex/cloud_setup.sh
```

默认只安装依赖并检查组件一致性，不自动回放历史拟合。完整回归需要已检出测试依赖数据，见测试说明。源码包版本0.1.0是包装版本，不是策略成熟度。
''',
'CONTINUE_HERE.md':'''# 从这里接管

最近完成的是2025-12-01字段对账和受限读取层，不是新收益实验。本次整理仅修复组件同步与运行入口。

先读 [当前白皮书](docs/WHITEPAPER.md)、[最新来源对账](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)、[组件生命周期](docs/COMPONENTS.md)。

现有五年分钟包、上游说明和六个单日Parquet已经交付，不再索取相同材料。已知份额合并遗漏已修正且旧样本/均值不受影响，不重复该任务。不同产品的同步、单位和原生分钟生成语义仍有限制；不得拟合时移或补造字段让数据通过。

没有正在等待执行的金融实验。下一项实证须由用户另行授权，先明确问题和数据假设。本仓维护、合成测试、保留证据核对不构成重开R1_A或旧期权身份。

修改当前状态时只编辑 [状态源](docs/REPOSITORY_STATE.json)，再运行 `python scripts/repository_consistency.py --render` 和 `--check`。不要分别手改多个入口。历史研究报告、冻结文件和原始数据保持原路径与原字节。
''',
'AGENTS.md':'''# 接管与修改约束

读取 [CONTINUE_HERE](CONTINUE_HERE.md)、[组件索引](docs/COMPONENTS.md)、[数据边界](docs/DATA.md)。

当前状态只由docs/REPOSITORY_STATE.json及它引用的裁决和回执定义。历史报告、迁移白皮书、旧任务和source副本不是新授权。不得从R1机制记录推导生产资格。

维护时保留原数据、冻结定义和决定性回执；不改科学公式、阈值、配对、已关闭样本或研究数据角色。全仓保留清单由一致性检查验证。历史代码因导入和复现依赖保留，不代表可以直接新采集、新拟合或新回测。

RestrictedSourceView只是离线来源标签消费者；禁止坏区间、跨阶段延续、未来checkpoint回填、无效最新状态后退用旧值。源DataHub生产器未修复；不能把本地防误用措施称为实时PIT、净值或同步认证。

默认CI只做组件一致性和合成检查；历史工作流为手动/受控复用。全部测试和保留证据复现使用测试说明中的显式入口，不覆盖旧输出。不要强推或清理其他仓库。
''',
'PROMPT.md':'''# 本地模型交接

目标仓库：staryocean0/factorlab-trend-reversion-regime-lab。先保护未提交修改，安全fetch/fast-forward main，再读 [CONTINUE_HERE](CONTINUE_HERE.md)。

当前没有新的数据搬运或研究执行任务。五年ETF分钟CSV、上游说明、2025-12-01六个文件均已交付并经云端检查。不要再次运行已完成交付指令，不需要重试完整clone来证明现有文件存在。

本地默认任务仅为同步或维护；需要新增材料时，必须有新任务写明确切字段/日期/权限。不能采购、猜单位、平移时钟、重开R1_A或改旧结果。非公开文件和凭据不进公共Git。

启动：`bash .codex/cloud_setup.sh`。完整测试见 [测试说明](docs/TESTING.md)，默认环境安装不再调用已退役的validate_seed.py。
''',
'ai-readme.md':'''# AI入口

唯一接管入口：[CONTINUE_HERE.md](CONTINUE_HERE.md)。当前规范：[WHITEPAPER](docs/WHITEPAPER.md)。组件和测试：[COMPONENTS](docs/COMPONENTS.md)、[TESTING](docs/TESTING.md)。

本文件由状态源生成，不单独维护下一任务或数据缺口。
''',
'docs/WHITEPAPER.md':'''# 当前研究与工程白皮书

## 目的与证据边界

本仓研究中证1000与科创50的趋势反转、均值回归及相关价格观测问题。指数价格反应、相对匹配对照的增量、模型预测评分、来源审计和交易执行是不同问题，不能混写为一个PASS。

R1_A历史价格线索与后续统计/预测局限均保留；当前版本已阶段性收口并储备。新ETF—指数方向完成可测量性和单日字段对账，尚不能把跨产品标签差异解释为可交易修复。当前没有批准的新实证候选。

## 当前代码承担什么

`src/regime_lab/market_data.py`是固定指数包读取器；`src/factor_lab`和`shared`是裁剪后的支持模块，不是完整FactorLab。`research/etf_day_reconciliation/audit.py`保留单日对账和RestrictedSourceView。其他研究模块均按[组件索引](COMPONENTS.md)保留用于已固定历史复现或来源追溯，旧数据采集工具已退役为参考代码。

读取视图拒绝倒置/空/未知结束区间、未来初始化、跨会话延续及无效最新状态后退用旧值；只在消费视图裁剪阶段终点，不改变原始价格。它使用离线valid_until，不证明实时可知或完整快照。

## 数据和可作结论

旧分钟、逐笔、报价、指数3秒的量纲和时间含义按各自来源合同解释。旧Z墙钟例外不泛化为所有字段。日终总量一致不能证明日内同步；四种分桶不能完整复原旧OHLC也不能以优化平移补齐证据。IOPV为零不能计算真实净值折溢价。详见[数据说明](DATA.md)。

## 维护规范

[状态源](REPOSITORY_STATE.json)同步生成入口与本白皮书状态块；[测试说明](TESTING.md)定义执行层级。业务状态变更必须同步裁决、模块和测试，不通过改历史报告假装过去已知当前结论。

历史白皮书和报告作为冻结研究快照保留原字节：[历史资料索引](research/README.md)、[归档索引](archive/README.md)。源数据附带白皮书是上游文档，不是本项目当前策略白皮书。

新研究须明确研究对象、数据角色、缺失处理、停止条件和授权；本维护不新增模型、参数、研究收益或2026行情读取。
''',
'docs/DATA.md':'''# 当前数据用途与来源边界

现有数据均用于历史研究或来源检查；数据可读、hash一致与金融语义完整是不同验收层。旧manifest按原字节保留，里面的complete=true或shares只代表当时声明，不自动准入新研究。

| 数据组 | 路径 | 当前用途 |
|---|---|---|
| 固定指数历史包 | `data/market/`、`data/manifest.json` | 按原合同读取与历史复现；补齐及available_at含义须分来源 |
| 已关闭MO研究包 | `data/r1b_research/` | 保留旧结果/依赖核验，不重开期权 |
| ETF历史分钟包 | `data/r1a_carrier_prices/cloud_pack_v1/` | 旧价格层研究复现；原生分桶、部分数量单位、完整行动表不视为已认证 |
| 已知行动修正版 | `data/etf_source_actions_v2/` | 已核实行动overlay，不是全历史完整性证明 |
| 上游文档/代码/固定样例 | `data/etf_upstream_evidence_v1/` | 固定来源解释，副本不是独立供应商认证 |
| 单日高频研究产品 | `data/etf_microstructure_sample_20251201_v1/` | 2025-12-01来源标签层核对，非实时/PIT或净值认证 |

指数amount/volume不得超出已核实源定义解释为统一交易量；指数观察分钟available_at为生产者日终赋值，填行是标签值，ETF归档是后来入库时刻，不能混作同一实时过滤字段。旧指数读取时间映射保持不变，不把上游知识时刻改成市场时刻。

512100已知2022-09-02合并及停牌、09-05复牌已登记，新/旧份额0.36555；2022-08-03取消提案不执行。该遗漏对旧已发表样本/均值无影响的审计已完成。588000空行动表不等于完整无事件证明。

单日报价末行两条倒置区间仍在原文件，只由受限消费者拒绝；全日数量相等不推出日内统一时钟。历史材料、元数据中的2026时间不等于已打开新确认行情；不得自动扩大日期。

数据原始文件、旧清单和供应商说明不由本次整理改写。完整性以当前用途说明和裁决为准，不以文件名或单个布尔值为准。
''',
'docs/INFRASTRUCTURE.md':'''# 当前代码与运行环境

Python支持范围以[pyproject.toml](../pyproject.toml)为准。包装版本不是策略成熟度。[当前支持模块清单](infrastructure_manifest.json)仅列实际存在的文件；旧导入时清单已经归档，不再宣称不存在的standard_backtest_service可导入。

`src/regime_lab`提供市场包读取与发布检查；`src/factor_lab`、`shared`为裁剪后的支持库；`research/`按[生命周期索引](COMPONENTS.md)保留。历史算法模块与归档源码仍被固定研究导入，不能为了目录好看破坏导入闭包。

[云端初始化](../.codex/cloud_setup.sh)安装依赖并运行结构门禁，不调用已移走的seed验证器，不自动重新训练历史预测器。[统一一致性检查](../scripts/repository_consistency.py)检查状态块、文件角色、路径、导入、测试和工作流。

完整研究回归和冻结复现见[TESTING](TESTING.md)。工程验收不授予数据源真实性、实时撮合或策略生产资格。
''',
'docs/RESEARCH_GOVERNANCE.md':'''# 当前研究与维护权限

最高优先级是用户授权；当前科研状态见[状态源](REPOSITORY_STATE.json)及引用裁决。冻结协议只定义某一次历史实验，不是永久继续试验的许可。历史PASS/FAIL均保留，不能用较早结论覆盖后来的储备或用途限制。

维护只同步文档/代码边界/测试/工作流，不改变信号、配对、阈值、样本、原始数据和旧证据。已有历史不是新独立样本；复现、合成测试和真实市场证据必须分别报告。

R1_A当前价格版本储备，R1_B/旧期权及已关闭身份不重开。没有新确认时钟、没有生产权限，也没有新的本地数据交付任务。

未来立项需先写明目标、数据及可用时点、缺失语义、统计方案、预算和停止条件。不得根据结果改时移、单位、分桶或筛选困难事件，不能用模型补造来源事实。

[归档](archive/README.md)是历史引用，不是运行入口。原资料中的外部路径、旧commit和当时状态按原貌保留；当前入口和工具链则由一致性门禁要求可用。
''',
'docs/cloud_local_communication.md':'''# 当前云端与本地协作

云端可直接读取本仓既有指数、ETF分钟及单日高频文件并运行授权的核验。不是“研究启动包”，也不再禁止使用已配置GitHub Actions进行有范围的复现。

本地负责仅本地可得且已获准交付的原材料；云端负责独立核验和研究判断。完整clone失败不是已交付文件失效，固定提交窄检出和实际hash可作为文件交付核验。

当前没有新增本地搬运任务。已完成的两份任务保留为[来源交付历史](ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md)和[单日交付历史](ops/ETF_ONE_DAY_SOURCE_DELIVERY_20251201.md)，不可再次派发。

确需新材料时另写精确日期、字段、来源权限及验收标准；不要要求整个DataHub，不上传凭据或未经准许公开的原包，不把本地报告当独立核验。
''',
'docs/TESTING.md':'''# 测试与工作流

## 默认快速门禁

```bash
python -m pip install -e '.[maintenance]'
python scripts/repository_consistency.py --check
python -m pytest -q tests/test_repository_consistency.py
```

`repository-consistency.yml`在main推送和PR时运行，检查整个Git文件树、所有当前Python源码语法/本地导入路径、生成文档、组件注册、冻结输入保护以及工作流结构。它不读取行情来计算新策略收益，也不声称替代全套测试。

## 全套测试

```bash
python -m pytest -q
```

需要当前全部`tests/`、相关保留证据和数据目录（特别是MO包存在性测试及ETF历史数据测试）。`repository-regression.yml`以窄检出提供这些依赖，收集全部非归档测试并逐项运行；不通过忽略失败或隐式跳过缺数据测试来报绿。完整回归较重，手动选择repository-consistency的full_regression，或维护提交显式带`[full-regression]`。

## 冻结研究复现

其余工作流保留既有计算步骤和严格证据对比，取消旧开发分支的push自动触发，改为手动或受控workflow_call。默认改文档不会自动重跑历史拟合/统计模拟。完整维护验收会调用单日观察、字段对账、上游说明及无拟合收口的既有复现。

名称`legacy-price-statistics-replay.yml`取代误导性的r1b-mo-data-admission-gate.yml；它是旧价格/统计流水线的复现，不是当前MO准入任务。全套测试由独立统一工作流承担，不再依赖旧文件名通配符覆盖所有新增测试。

工作流只读仓库，checkout不保留凭据；新输出只放临时目录或artifact，不写回冻结证据。保留的可执行文件不构成自动新实验授权。所有工作流必须通过语法/调用及维护约束检查。
''',
'data/README.md':'''# 数据入口

当前用途和未验证事项以[数据说明](../docs/DATA.md)与[状态源](../docs/REPOSITORY_STATE.json)为准。

子目录README、manifest和上游白皮书可能是交付时的不可变快照。保留它们用于hash和复现，不把旧pending、shares或complete=true单独当成现在的状态。新数据准入必须另行授权，当前不要求任何重复上传。
''',
'docs/archive/README.md':'''# 历史归档入口

归档和迁移材料不是当前授权。[当前入口](../../CONTINUE_HERE.md)与[组件索引](../COMPONENTS.md)决定运行用途。

`repository_pre_cleanup_20260912/`逐字节保存这次清理前的入口、启动配置、旧清单和工作流；旧seed清单已移出当前docs层。迁移的旧白皮书、脚本与报告继续保持原字节。归档内部路径是当时工程的路径，不应误当成当前可运行命令。

既有历史组：legacy_seed、rmr_migrated_from_star50_20260909、broad_rmr_migrated_from_two_wave_20260909、rmr_discovery_migrated_from_star50_20260910、scope_repair_20260909、r5_b1_closed_20260910、ciis_public_sample_recovery_20260910、rmr_parent_state_legacy_20260911。

历史报告、冻结协议和若干算法源码被后续研究按路径与hash引用，故采用“原位归档”：原文件不搬不改，当前报告索引标明历史身份。不能为物理移动而破坏复现，也不能因仍在原路径就重启策略。
'''
    }
    for path in handoffs:
        bodies[path]='# 已完成并退役的交付任务\n\n此任务已完成，不再派发。原指令逐字节保存在 '+link(path,ARCHIVE+'/'+path)+'。\n\n当前没有本地重复交付需求；后续任务必须重新获得授权，详见 '+link(path,'CONTINUE_HERE.md')+'。\n'
    for name, info in state['modules'].items():
        path='research/'+name+'/README.md'; old=ARCHIVE+'/'+path
        text='# '+name+'\n\n生命周期：`'+info['status']+'`。\n\n解释报告：'+link(path,info['report'])+'。冻结复现入口：'+link(path,info['workflow'])+'（手动/受控调用，不自动新实验）。\n\n'
        text+='实现、源文件、冻结输入和已保存结果保持原样。复现只能使用原范围、新输出目录，并与保留证据比较；不能覆盖旧回执。\n\n'
        if path in entries:text+='旧使用说明作为历史参考保留：'+link(path,old)+'。其中的下载/继续/准入措辞不是当前任务。\n\n'
        text+='当前用途和统一测试：'+link(path,'docs/COMPONENTS.md')+'、'+link(path,'docs/TESTING.md')+'。\n'
        bodies[path]=text
    for section in ('research','governance'):
        path=f'docs/{section}/README.md'
        body='# '+('历史研究报告索引' if section=='research' else '冻结与当前裁决索引')+'\n\n以下原文件按历史快照保留，不自动代表当前许可。最新解释与相互关系见 '+link(path,STATE)+'。\n\n'
        for p in sorted((ROOT/'docs'/section).iterdir()):
            if p.is_file() and p.name!='README.md':body+='- '+link(path,str(p.relative_to(ROOT)))+' — 保留原路径/原字节；按对应实验和后续裁决解释。\n'
        bodies[path]=body
    comp='# 文件组件与生命周期\n\n当前维护工具和生成文档受统一门禁保护；历史源码保留导入闭包，历史研究不自动执行。\n\n| 模块 | 状态 | 解释 | 复现工作流 |\n|---|---|---|---|\n'
    for name,info in state['modules'].items():
        comp+='| '+link('docs/COMPONENTS.md','research/'+name+'/README.md',name)+' | `'+info['status']+'` | '+link('docs/COMPONENTS.md',info['report'],'报告')+' | '+link('docs/COMPONENTS.md',info['workflow'],'手动复现')+' |\n'
    comp+='\n所有原始data、决定性evidence、历史报告与冻结文件按[基线清单](maintenance/BASELINE_COMPONENTS.json)受保护。归档副本保存清理前字节。新增文件也必须属于已注册组件；新research目录不会自动取得权限。\n\n上游白皮书位于data交付包；迁移策略白皮书位于docs/archive，均为来源/历史快照。本仓当前规范白皮书为[WHITEPAPER](WHITEPAPER.md)。\n'
    bodies['docs/COMPONENTS.md']=comp
    state['generated_documents']=bodies
    write(STATE,json.dumps(state,ensure_ascii=False,indent=2))
    current_infra=[]
    for p in sorted(list(ROOT.glob('src/**/*.py'))+list(ROOT.glob('shared/**/*.py'))):
        current_infra.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    write('docs/infrastructure_manifest.json',json.dumps({'schema_id':'factorlab_current_infrastructure@2.0','scope':'existing installable support files, not the original import snapshot','historical_manifest':ARCHIVE+'/docs/infrastructure_manifest.json','production_authority':False,'files':current_infra},ensure_ascii=False,indent=2))
    baseline={'baseline_commit':BASE,'baseline_file_count':len(entries),'modified_baseline_paths':snapshots,'removed_active_paths':['docs/seed_manifest.json','.github/workflows/r1b-mo-data-admission-gate.yml'],'archive_prefix':ARCHIVE,'entries':entries}
    write('docs/maintenance/BASELINE_COMPONENTS.json',json.dumps(baseline,ensure_ascii=False,indent=2))
    write(ARCHIVE+'/README.md','# 清理前快照\n\n基线：`'+BASE+'`。子文件保持原字节，仅用于历史追溯；不运行归档配置或再次派发旧任务。原位历史报告与冻结证据没有移动。\n')
    write('docs/maintenance/README.md','# 维护记录\n\n这轮统一状态源、文档/白皮书、模块生命周期、启动脚本和工作流。基线清单保护原始数据和科学证据；清理不提升研究结论。\n\n原文件变化在BASELINE_COMPONENTS.json列明。机器验收包含源码语法、导入、生成文档、路径及工作流；完整pytest和受限复现结果以实际Actions记录为准，不能提前写为通过。\n')
    print(json.dumps({'baseline_files':len(entries),'archived_original_files':len(snapshots),'modules':len(MODULES),'generated_docs':len(bodies)},ensure_ascii=False))

if __name__=='__main__':run()
