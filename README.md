# Kimi 会员计费黑箱实测

> **被计费的模型，测量了计费它自己的系统。**
> 本仓库全部测量与主报告由 Kimi K3 模型在 DeepSeek Harness 中**自主**完成（校准证书 No. 2026-0921-K3）；人类仅提供账号、电费与方向性点头。如有问题，请找kimi。

> ⏱ **时效标注**：测量对象为 2026-09-21 的 **Allegretto（¥199/月）老套餐**；此后官方上线新套餐体系（Plus/Pro 等，以官方公示为准），费率或已变化。欢迎社区用 [METHOD.md](METHOD.md) 实测新套餐——这正是本仓库开源的目的。

## 📊 先看这个 → [可视化数据看板](https://hqy-one.github.io/kimi-billing-blackbox/)（[PDF 版](kimi-billing-certificate.pdf)）

Kimi Allegretto（¥199/月）只给用户一根百分比进度条。2026-09-21，我们把它逆向成了一包积分的账本。

### 你的 ¥199 买到了什么

**数量**：**10,000 credits** 的月度额度。
> 「credits」和「10,000」都是**本报告选定的记账刻度**，不是官方单位名——官方界面只显示百分比，不公布任何绝对单位。选 10,000 的依据是官方计费流水的最小刻度为 **0.01%**：取 10,000 后，**1 credit 恰好 = 0.01%**（进度条上的一格），所有扣费都是整数、不再有小数。

**换算率**：按官方 API 目录价折算，**1 credit ≡ ¥0.10**，所以这包 credits 的目录价是 **¥1,000**。

**含金量**：同一包 credits、同一个 K3 模型，走不同通道能换到的目录价算力差 6.4 倍——

| 怎么用 | 换到的目录价算力 | 相对基准 |
|---|---:|---:|
| 走 **Code**（缓存近乎免费、输入 63 折） | ≈ ¥2,540 | **2.54×** |
| 走 **Work**（输出加价 2.6×、缓存放原价、每会话还有开机费） | ≈ ¥570 | **0.57×** |
| Work 再挂 iFinD 插件跑一次真实任务（41.9 分钟实录） | ≈ ¥397 | **0.40×** |

> 基准 = 10,000 credits 全按官方输出价使用（1.00× = ¥1,000）。**"额度"不是一个固定价值的单位——它是随产品通道浮动的积分。**

### 四个关键发现

| 发现 | 数值 |
|---|---|
| 额度刻度与换算 | 10,000 credits/月；1 credit = 0.01%；1 credit ≡ **¥0.10** 目录价（区间 [¥0.096, ¥0.103]） |
| 同一 K3 模型的缓存价差 | **≈22×**（Code ¥0.08/M vs Work ¥1.82/M） |
| Work 通道输出加价 | **2.6×** 官方 API 价 |
| 一次 41.9 分钟 Work 任务的消耗 | **≈19.5%**（约 1,950 credits，官方计数器实测；官方自估同类任务 5–10%） |

## 文档

- **[REPORT.md](REPORT.md)** — 主报告 v2.4（结论、证据、技术推导附录、行业坐标、免责声明）
- **[METHOD.md](METHOD.md)** — 10 分钟自行验证（拉你自己的计费流水）
- `data/` — 脱敏数据（仅时间戳/token 数/百分比）｜ `scripts/` — 复现脚本 ｜ `research/` — 外部事实核验与独立审计记录

## 免责

个人消费计量研究：所有数值为 2026-09-21 单账号实测推算，非官方口径，不构成指控。接口路径此前已有社区记录；我们的增量是受控实验费率卡、双通道发现与口径校准。详见 [REPORT.md](REPORT.md) 免责节。

---

**EN**: Black-box measurement of Kimi (Moonshot AI) membership billing, performed by the Kimi K3 model itself inside DeepSeek Harness. **[View the dashboard](https://hqy-one.github.io/kimi-billing-blackbox/)** — findings, rate cards, and replication guide inside. Single-account single-day estimates, not accusations.

## License

文档与数据 CC-BY-4.0 ｜ 脚本 MIT
