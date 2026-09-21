> 本文件为外部事实核验调研，由 DeepSeek V4.1 Flash（opencode-go-deepseek）在 DeepSeek Harness 中执行网络检索完成（2026-09-21），主报告作者（Kimi K3）复核采用。
> 调研与实测分离：本文只含公开网页证据，不含任何本仓库的实测数据。

# Kimi 会员计费逆向报告 — 事实核验

检索日期 2026-09-21。所有结论均来自当日网络检索 + 官方页面直取。未核到的标 [未核实]。

---

## 1. Claude Pro / Max 额度机制

- Anthropic 官方 Max 帮助页明确定价两档：Max 5x 与 Max 20x，且 Max 5x = Pro 每会话额度的 5 倍、Max 20x = 20 倍（来源: https://support.claude.com/en/articles/11049741-what-is-the-max-plan）
- 5 小时窗口是官方口径："Your session-based usage limit will reset every five hours"，Pro 与 Max 皆适用（来源: https://support.claude.com/en/articles/11049741-what-is-the-max-plan）
- 周上限是官方口径：Max（及 Pro）在 5 小时窗口之外另有 "a weekly usage limit that applies across all models"，每周在账户固定时间重置，每周期发满额（来源: https://support.claude.com/en/articles/11049741-what-is-the-max-plan）
- Pro 档官方定价 $20/月，且 Pro 帮助页同样写明 5 小时会话重置 + 跨模型周上限（来源: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan）
- 官方**没有**公布固定消息条数：消息数随消息长度、附件长度、当前会话长度、所用模型/功能波动（来源: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan）
- Pro $20 / Max 5x $100 / Max 20x $200 三档价格在 Anthropic 帮助页与第三方汇总一致（来源: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan；https://support.claude.com/en/articles/11049741-what-is-the-max-plan）
- Anthropic 保留"其他限制方式"的裁量权：可另行施加周/月上限或模型与功能级限制（来源: https://support.claude.com/en/articles/11049741-what-is-the-max-plan）
- 团队档可作横向对照：Team Standard 席位 = Pro 每会话额度的 1.25 倍，另有跨模型周上限（来源: https://support.claude.com/en/articles/9266767-what-is-the-team-plan）
- **token 量级**：官方 help 页面不给 token 数值，[未核实]

---

## 2. Cursor Pro 2025-06 后的额度模式

- 2025-06-16 起 Pro 从"500 次模型请求/月"改为按 API 费率计价的用量额度池（来源: https://www.cometapi.com/cursor-ai-pricing-2025-complete-guide-analysis/）
- Cursor 官方定价页（当日直取）现在只写"每个方案都按模型推理用量计费"与 "Pro 含 $20 的 API 代理用量额度 + 额外赠送用量"，页面本身**不**再列请求次数（来源: https://cursor.com/pricing）
- Cursor 官方文档页给出月度包含额度数额：Pro $20 / Pro Plus $70 / Ultra $400 的 API 代理用量额度，并说明会尽量额外赠送（来源: https://docs.cursor.com/en/account/pricing）
- 官方文档给出"中位用户"量级换算：Pro ≈ 225 次 Sonnet 4 请求，或 ≈ 550 次 Gemini 请求，或 ≈ 500 次 GPT-5 请求（来源: https://docs.cursor.com/en/account/pricing）
- 超额后不降级：可选择按同样 API 费率追加 on-demand 用量，或升级套餐，"请求质量或速度绝不会被降级"（来源: https://docs.cursor.com/en/account/pricing）
- Cursor 现行档位为 Hobby 免费 / Pro $20 / Pro+ $60 / Ultra $200（来源: https://cursor.com/pricing）
- 注意口径冲突：官方定价页当前**未**单独列 Pro+ 的 $70 数额（只说 "3x Pro limits on Agent"），$70 只出现在官方文档页 —— 引用时建议以 docs 页为准（来源: https://cursor.com/pricing；https://docs.cursor.com/en/account/pricing）
- 第三方称 Ultra 含约 $400 用量、Pro+ 含约 $60–70，与官方 docs 的 $400/$70 基本吻合（来源: https://www.cloudzero.com/blog/cursor-ai-pricing/）

---

## 3. ChatGPT Plus 消息上限机制

- Plus 官方定价 $20/月（来源: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus）
- 官方对 Plus 上限的表述是"可能包含消息上限等用量限制，且可能随系统状况变化"——即**不承诺固定数值**（来源: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus）
- 官方 GPT-5.5 help 页曾公布具体数字：GPT-5.5 Plus 与 Go 为每 3 小时最多 160 条消息（来源: https://www.anygen.io/showcase/chatgpt-plus-message-limit/index.html，转述 OpenAI 2026-05 help 文章）
- 官方 GPT-5.6 help 页（当日直取）**不再**给 Plus 的通用条数，只写限制取决于套餐、模型与工作区设置（来源: https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt）
- 官方 GPT-5.6 help 页公布的当前具体配额只覆盖 Pro 档 Pro 模型：Pro $200 = GPT-6 Pro 200 条/周 + GPT-5.6 Sol Pro 单独 170 条/天（两者合计另限 200 条/天）；Pro $100 = 两模型共享 50 条/周（来源: https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt）
- 官方确认 Free 与 Go 的 Instant 日常文本对话为无限（受防滥用约束），文件上传、图像生成、语音、数据分析仍另有限额（来源: https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt）
- 历史机制参考（非当前）：Plus 曾为 GPT-5 Thinking 每周 3000 条、GPT-4o 约每 3 小时 150 条（来源: https://www.bentoml.com/blog/chatgpt-usage-limits-explained-and-how-to-remove-them；https://tech.yahoo.com/ai/articles/gpt-5-just-got-first-102853223.html）
- 官方 2026-09-10 起暂停 ChatGPT Pro $200 新订阅与升级（来源: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus）

---

## 4. GitHub Copilot Pro premium request 配额

- **重要变化**：Copilot 个人档计费已从 premium request 转为 GitHub AI Credits，官方 plans 页当前列 Copilot Pro $10/月 = 1,000 base credits + 500 flex = **1,500 AI credits/月**；Pro+ $39 = 7,000；Copilot Max $100 = 20,000（来源: https://docs.github.com/en/copilot/get-started/plans）
- premium request 制现仅适用于 **2026-06-01 后仍留在旧制上的 Copilot Pro/Pro+ 年度套餐用户**，官方文章已明确标注为 legacy（来源: https://docs.github.com/en/copilot/managing-copilot/monitoring-usage-and-entitlements/about-premium-requests）
- legacy 制下的历史配额：Copilot Pro **300 premium requests/月**，Pro+ 1,500/月，超出可加购 $0.04/次（来源: https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/copilot-requests）
- 官方社区回答独立复述同一数字：Pro 上限 300 premium requests/月，追加 $0.04/次（来源: https://github.com/orgs/community/discussions/170856）
- legacy 规则细节：agentic 功能只有用户发出的 prompt 计费，Copilot 自主执行的工具调用不计；未用完的 requests 不结转，每月 1 日 00:00:00 UTC 重置（来源: https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/copilot-requests）
- legacy 模型乘数会放大扣减：2026-06-01 起 Copilot code review 乘数为 13，即每次 review 扣 13 次配额（来源: https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/copilot-requests）
- 代码补全不计 credits：所有付费档的 completions 与 next edit suggestions 不计 AI credits，保持无限（来源: https://docs.github.com/en/copilot/get-started/plans）

---

## 5. Kimi 会员档位体系

- 国内在售档位名称与月费：Andante ¥49 / Moderato ¥99 / Allegretto ¥199 / Allegro ¥699，另有免费档 Adagio（来源: https://www.kimi.com/help/membership/membership-pricing；https://www.kimi.com/help/membership/membership-overview）
- 官方定位词：Andante 日常使用 / Moderato 效率升级 / Allegretto 专业优选 / Allegro 全能尊享（来源: https://www.kimi.com/help/membership/membership-overview）
- **"4 倍"官方出处**：官方权益对比表在 "Agent 额度" 一行给出 —— Andante「更多 Agent 额度」、Moderato「2 倍 Agent 额度」、**Allegretto「4 倍 Agent 额度」**、Allegro「10 倍 Agent 额度」（来源: https://www.kimi.com/help/membership/membership-overview）
- 官方 pricing 页「Kimi Code」行另有一组乘数，取值为 1 倍 / 4 倍 / 20 倍 / 60 倍；抓取到的正文未包含该表表头与该行的列对齐，**具体哪一档对应哪个乘数未经正文核实** [未核实（列对齐）]（来源: https://www.kimi.com/help/membership/membership-pricing）
- **不要混淆两套倍率**：官方 overview 页的「Agent 额度」行是 2×/4×/10×（Moderato/Allegretto/Allegro）；pricing 页的「Kimi Code」行是 1×/4×/20×/60×。"Allegretto 是 Agent 档额度的 4 倍"这一说法只在**「Agent 额度」这一行**成立，把它当成 Kimi Code 或总池的倍数属口径错误（来源: https://www.kimi.com/help/membership/membership-overview；https://www.kimi.com/help/membership/membership-pricing）
- 官方公布具体数值型的估算量：Agent 用量约 30 / 60 / 150 / 360 个（Andante → Allegro），并注明"基于常见任务 token 消耗估算，将月额度用于同一功能时的参考值"（来源: https://www.kimi.com/help/membership/membership-pricing）
- 国际版另有海外档位 Vivace，官方英文 pricing 页列 Moderato $19 / Allegretto $39 / Allegro $99 / Vivace $199 每月，Agent 额度 60 / 150 / 360 / 720（来源: https://www.kimi.ai/zh-hans/help/membership/membership-pricing；https://www.kimi.ai/help/agent/quota-and-billing）
- 档位音乐术语对应：Adagio 柔板 / Andante 行板 / Moderato 中板 / Allegretto 小快板 / Allegro 快板（来源: https://www.c114.net.cn/industry/122419.html）
- 计费口径：所有会员功能（Agent、深度研究、PPT、Kimi Code、Kimi Work、Kimi Claw 等）共享一个额度池，按实际 token 消耗扣除；免费/赠送额度优先扣，加油包最后扣（来源: https://www.kimi.com/help/membership/membership-update-rules；https://www.kimi.com/help/kimi-code/benefits）
- Kimi Code 另有 5 小时 + 周双窗口限额，仅作用于 Kimi Code，不影响其他会员功能（来源: https://www.kimi.com/help/membership/membership-pricing）
- 新套餐体系变动中：官方 Kimi Code 文档称新会员**取消每周额度限制**、仅保留 5 小时滚动窗口，Go 档无 coding 额度、Plus 及以上可用 Kimi Code（来源: https://www.kimi.com/code/docs/kimi-code/membership.html）
- **是否公布 tokens/额度数值**：官方页面公布的是倍率与"N 个 Agent 用量"估算值，**未公布**额度池的绝对 token 数或人民币折算值 —— 官方明确写"以上 Agent 用量数值基于常见任务 token 消耗估算…仅供参考"（来源: https://www.kimi.com/help/membership/membership-pricing）
- 官方关联页面同样只给比例口径：简单 PPT ≈ 1–2% 月度额度、一次深度研究 ≈ 5–10%、编写一段代码 ≈ 0.5–2%，均为百分比而非绝对值（来源: https://www.kimi.com/help/membership/membership-overview）
- 官方确认存在固定后台扣费项：Kimi Claw 云主机每天约扣会员额度 0.6%（每天 16:00 结算，闲置亦扣）；发布网站在线期间约扣 0.08%（来源: https://www.kimi.com/help/membership/membership-pricing）
- 官方公布加油包计费示例量级：一次简单请求约 ¥0.03，一次复杂多步任务约 ¥1.6（来源: https://www.kimi.ai/zh-hans/help/kimi-code/benefits）
- 档位改名历史的第三方记录：老版 Andante/Moderato/Allegretto/Allegro 曾对应新版 Go/Plus/Pro/Max，价格未变（来源: https://www.chooseai.net/news/6988）—— 与官方 Kimi Code 文档中出现的 "Go / Plus" 命名方向一致（来源: https://www.kimi.com/code/docs/kimi-code/membership.html）

---

## 6. Prior art：公开的逆向分析 / 吐槽

- **LINUX DO「kimi新的套餐有佬订阅了吗，code 的量怎么样」** —— 帖内用户自称推出最精准的额度换算公式，明确说"Kimi 消耗额度不是按 API 价格算的"，并按 199 套餐逐项给出"未命中输入（全新上下文）每 1M Token 扣除…"的扣减规则，是本次检索到的最接近接口级逆向的一手帖（来源: https://linux.do/t/topic/2897188?tl=zh_CN；检索日期 2026-09-21）
- **知乎专栏「Kimi 深度体验，额度为何跑得飞快?」** —— 199 档实测称额度约为 API 定价的"一折"月度总额度；按 98% 缓存命中、平均请求 56K 的场景折算出月度请求数与总 token 量级；同页给出 99 套餐 ≈ 一周 80M、49 套餐 ≈ 1x 的对照（来源: https://zhuanlan.zhihu.com/p/2047340329087526384；检索日期 2026-09-21）
  - 注意：该文正文当日抓取返回 HTTP 403，只核到搜索引擎摘要与标题，具体数字建议引用前二次确认 [未核实（正文不可直取）]
- **MoonshotAI/kimi-code Issue #3781** —— Allegretto 年费 + K3 用户报告扩展 0.7.5 更新后额度消耗异常放大：两个问题未答完 5 小时窗口已耗约 30%，按此速度一个窗口仅够 6–7 个问题，7 天额度已 100% 耗尽；请求官方提供逐次请求消耗明细与预估（来源: https://github.com/MoonshotAI/kimi-code/issues/3781）
- **GitHub Javis603/token-monitor Issue #181** —— 从 Kimi 前端代码确认会员月度额度走 Connect RPC：`/apiv2/kimi.gateway.membership.v2.MembershipService/GetSubscriptionStats`，并列出 `subscription_balance.amount_used_ratio`、`kimi_code_used_ratio`、`ratelimit_5h`、`ratelimit_7d` 等字段；指出官方 Kimi Code API 只暴露 5h/7d，看不到会员月度总用量（来源: https://github.com/Javis603/token-monitor/issues/181）
- **GitHub chendefine/dsh-plugins-plan-usage / dsh.fish 文档** —— 实现层面复述同一条逆向路径：官方接口 `GET https://api.kimi.com/coding/v1/usages` 返回 7 天周限 + 5 小时频限 + 会员等级；**月度会员额度**需网页会话 `kimi-auth` Cookie（JWT）调用 `MembershipService/GetSubscriptionStats`，并明确标注"该接口是逆向的、非官方，可能随时变更"（来源: https://github.com/chendefine/dsh-plugins-plan-usage；https://dsh.fish/zh-CN/a/dsh-plan-usage）
- **LINUX DO「kimi的用量消耗的巨快啊」** —— 订阅"一百多的那档位"用户称两三天耗尽一周额度、5 小时限额从未触发而周额度先触发（来源: https://linux.do/t/topic/2693209?tl=zh_CN）
- **80aj.com 转载 Linux.do 反馈** —— 99 元会员两轮常规提问消耗约 14% 额度，用户申请退款（来源: https://www.80aj.com/2026/07/30/kimi-membership-cost-usage/）
- **Linux.do 短帖（经 Telegram 镜像收录）** —— 用户吐槽"kimi 这个 agent 额度消耗优先级也太坑了吧"：下午刚开会员做 PPT，发现先扣会员额度再扣免费额度（来源: https://t.me/s/linuxdoit?before=217135）
- **知乎「如何看待 Kimi 7 月 19 号发布的新版会员体系？」** —— 回答称 199 套餐 Coding 额度总共 2000 API 额度，5 小时/周窗口为 200/1000，并称 HighSpeed 上线前为 80/400（来源: https://www.zhihu.com/question/2062320288046625064）
- **英文检索结论**：以 "Kimi membership quota billing" / "reverse engineered" 为主的英文检索**未命中**英文学术或工程向的独立逆向分析，命中的多为中文社区帖、工具仓库与聚合站转述（来源: 本次 web_search 多轮检索 0 命中，检索日期 2026-09-21）

---

## 核验边界（验了什么／没验什么）

**验了**：上述所有 URL 均由当日实际检索返回；Claude Max/Pro help 页、Cursor pricing + docs 页、ChatGPT Plus + GPT-5.6 help 页、GitHub Copilot plans 页与 legacy requests 页、Kimi help 全部相关页（membership-overview / membership-pricing / membership-update-rules / kimi-code benefits / code docs membership）均为**直接抓取正文**后引述，非搜索摘要转述。

**没验**：
- `https://www.kimi.com/membership/pricing`（产品订阅页）当日抓取只返回 JS 壳，表内数字来自搜索索引摘要，**未**在正文中直取确认
- 知乎两篇文章正文均 403 或不可达，仅核对到标题与搜索摘要
- 未做接口抓包或复现，本文不含任何自测数据
- Kimi "Allegretto 4 倍" 只对「Agent 额度」成立；若你的报告原文把它当作 Kimi Code 或总额度的 4 倍，那是**口径错误**，官方对 Kimi Code 给的是 Allegretto 20 倍
