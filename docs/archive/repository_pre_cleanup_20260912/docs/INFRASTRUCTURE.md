# 项目级择时基础设施裁剪

参考已有two-wave/overnight/STAR仓库的“固定数据＋来源清单＋环境＋测试＋提示词”模式，直接从本地FactorLab精选通用模块，未fork任何旧仓库历史。完整来源SHA见`infrastructure_manifest.json`。

| 能力 | 入口 | 使用限制 |
|---|---|---|
| Layer 1时钟与成交窗配对 | `factor_lab.data.session_offset_defaults` | 菜单不等于已交付数据；不本地重采样墙钟OHLC |
| 通用回测适配 | `factor_lab.data.services.standard_backtest_service` | 输入收益序列的诊断性回放；不构成真实撮合/T+1/限价/容量执行引擎 |
| 成本与相对表现 | `filtering.costs`、`portfolio.relative_performance` | 参数须由新协议冻结；云脊常量只为兼容，不带其数据 |
| Layer 2测量坐标/列边界 | `market_state.timing_layer2_measurement_plane` | 因果feature、后验target、兼容定义分开 |
| 基本K线测量与归一化 | `market_state.core_kline_attribute_pool`、`normalization`、`indicators.*` | 年度reducer仅作描述，不能贴回每根bar成为在线特征 |
| 多重检验与时序证据 | `governance.multiple_testing`、`temporal_integrity`、`evidence_resolver` | 辅助函数不替代新研究完整审计 |
| 冻结来源解析 | `governance.sealed_source` | 本新仓没有旧FactorLab Git历史；旧hash不可恢复就失败，不伪造 |
| 公共异常依赖 | `core.errors`、`observability.exceptions`、`shared.observability` | 仅导入闭包，不带完整运行时/服务 |

源模块原字节保留；`__init__.py`使用轻量命名空间壳，避免完整项目的eager imports把旧策略/衍生品模块拉进来。本包不是完整FactorLab，不保证未列API存在。

未上传：旧策略、参数winner、模型、回测结果、其他主题输入、策略注册表和生产指针；也未把two-wave的300多个依赖模块整个搬来。更深的Layer 2旧模块若直接依赖旧策略实现，此次不强行引入。需要新的逐时点测量时，由研究AI按本课题数据与因果合同开发并测试。

这是一份可复用基础设施快照，而非策略级实现；策略的白皮书/代码/测试/工作流待接手AI建立。
