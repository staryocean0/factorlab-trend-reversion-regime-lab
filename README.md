# FactorLab Trend–Reversion Regime Lab

科创50与中证1000的全新研究：什么K线/序列/波动状态适合趋势跟随，什么状态适合反转或均值回归？

**[外部AI先读 PROMPT.md](PROMPT.md)** → [原始研究框架](RESEARCH_FRAMEWORK.md) → [数据字典与限制](docs/DATA.md) → [基础设施](docs/INFRASTRUCTURE.md)。

这是研究启动包，没有已实现的新策略或新回测结果。包含：

1. 两指数3s/1m/5m已有数据包的逐字节副本及固定哈希。
2. 用户原始研究框架MD、22项文献的目录/官方链接。
3. 接手提示词、实验记录模板、研究与云端—本地交接约束。
4. 精选项目级择时基础设施与完整导入依赖、测试、环境和包校验。

**仓库不含PDF全文。** 论文由所有者通过桌面ZIP单独交给外部AI，不能上传到本public仓库。原框架的7个`sandbox:`示例附件未取得，也没有重新生成冒充。

## 运行

Python 3.11–3.13：

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/validate_seed.py
.venv/bin/python -m pytest -q
```

也可运行`bash .codex/cloud_setup.sh`。校验不执行策略搜索、回测或训练。

## GitHub权限

Public允许无需登录读取，不会自动允许外部模型改文件。写入需要经授权的GitHub App/令牌及仓库权限；通常应新建研究分支并提交PR。仅有网页阅读能力的模型无法因此直接执行代码或push。[官方权限说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)。

本地是存储核心；外部成果须回迁复核。本仓不授生产/交易权限，不为第三方数据或论文授予新的开放再分发许可。
