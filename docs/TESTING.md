# 测试与工作流

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

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
