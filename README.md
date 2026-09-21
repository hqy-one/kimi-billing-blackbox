# Kimi 会员计费黑箱实测

> **被计费的模型，测量了计费它自己的系统。**
> 本仓库全部测量与主报告由 Kimi K3 模型在 DeepSeek Harness 中**自主**完成（校准证书 No. 2026-0921-K3）；人类仅提供账号、电费与方向性点头。如对内容有异议，请直接约谈 K3——约谈它也走贵司额度。

> ⏱ **时效标注**：测量对象为 2026-09-21 的 **Allegretto（¥199/月）老套餐**；此后官方上线新套餐体系（Plus/Pro 等，以官方公示为准），费率或已变化。欢迎社区用 [METHOD.md](METHOD.md) 实测新套餐——这正是本仓库开源的目的。

## 📊 先看这个 → [可视化数据看板](https://hqy-one.github.io/kimi-billing-blackbox/)（[PDF 版](kimi-billing-certificate.pdf)）

Kimi Allegretto（¥199/月）只给用户一根百分比进度条。2026-09-21，我们把它逆向成了一包积分的账本：

> 你的 ¥199 买的是 **10,000 credits**（1 credit = 0.01%，恰是最小计费刻度）。按官方目录价，它锚定 **¥1,000**；走 **Code** 通道，它实际值 **¥2,540**（缓存近免费 + 输入 63 折，积分升值）；走 **Work** 通道，只值 **¥570**（输出加价 2.6× + 缓存照价收 + 开机费，积分贬值）；再挂上 iFinD 插件跑一次真实任务，只剩 **¥397**。

| 发现 | 数值 |
|---|---|
| 实测汇率 | 1 credit ≡ **¥0.10** 官方 API 标价，区间 [¥0.096, ¥0.103] |
| 同一 K3 模型的双通道缓存价差 | **≈22×**（Code ¥0.08/M vs Work ¥1.82/M） |
| Work 通道输出加价 | **2.6×** 官方 API 价 |
| 一次 41.9 分钟 Work 任务的消耗 | **2,089 credits**（流水口径）≈ **19.5%**（计数器口径；官方自估同类任务 5–10%） |

## 文档

- **[REPORT.md](REPORT.md)** — 主报告 v2.3（结论、证据、行业坐标、免责声明）
- **[TECHNICAL.md](TECHNICAL.md)** — 技术附录（拟合方法与推导，数值以 REPORT 为准）
- **[METHOD.md](METHOD.md)** — 10 分钟自行验证（拉你自己的计费流水）
- `data/` — 脱敏数据（仅时间戳/token 数/百分比）｜ `scripts/` — 复现脚本 ｜ `research/` — 外部事实核验与两轮独立审计记录（DeepSeek V4.1 Flash）

## 免责

个人消费计量研究：所有数值为 2026-09-21 单账号实测推算，非官方口径，不构成指控。接口路径此前已有社区记录；我们的增量是受控实验费率卡、双通道发现与口径校准。详见 [REPORT.md](REPORT.md) 免责节。

---

**EN**: Black-box measurement of Kimi (Moonshot AI) membership billing, performed by the Kimi K3 model itself inside DeepSeek Harness. **[View the dashboard](https://hqy-one.github.io/kimi-billing-blackbox/)** — findings, rate cards, and replication guide inside. Single-account single-day estimates, not accusations.

## License

文档与数据 CC-BY-4.0 ｜ 脚本 MIT
