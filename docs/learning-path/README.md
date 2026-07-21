# Agent 工程师学习路线

> 为前端工程师定制的 6-9 个月兼职转型路线，目标：**全职 Agent 工程师**。

> **⚠️ 时效说明：** 本路线文档生成于 2026-07。AI 领域迭代极快，文中出现的**模型名、价格、工具版本**会随时间过时——使用时请以各厂官方最新文档为准，不要照抄。**核心方法论**（评测驱动、渐进复杂度、状态机思维、前端优势迁移）不会过时；**具体技术选型**（用哪个模型、哪个框架版本）建议每季度自行校准一次。
>
> **📝 代码示例占位约定：** 文中代码统一用各厂的 `-latest` 别名（如 `gpt-5-latest`、`claude-sonnet-4-5-latest`）作为模型名占位——厂商会自动把 `-latest` 指向当前版本，避免几个月后调用失败。实际运行时请替换为**你 API Key 实际可访问的模型**（登录各厂控制台查看可用列表）。

## 起点

- **技术背景：** 前端工程师，写过少量 Node.js / Python 脚本
- **学习时间：** 每周 **10-15 小时**（工作日每天 1-1.5 小时 + 周末 3-4 小时）
- **学习周期：** **32-36 周（8-9 个月）**，含 20-30% 缓冲。原计划的 28 周偏理想化，兼职学习大概率超时，预留缓冲更利于坚持
- **学习风格：** 理论 + 实践交替

> 📊 **各阶段实际耗时参考：** 每个阶段文档顶部都有一张「耗时参考表」，按学习者画像给出 1.0x–1.6x 计划周数的实际预估。**当你觉得"我又超时了"时，先去对照那张表**——多数情况下你的进度在正常区间。这些预估值会随内测数据更新。

## 技术栈策略

**Python 为主（70%）+ TypeScript 辅助（30%）**

| 用途 | 语言 | 原因 |
|------|------|------|
| Agent 核心开发 | Python | 业界主流生态（LangChain、LangGraph、AutoGen、CrewAI） |
| LLM API 调用 | Python | SDK 最全、示例最多 |
| 前端界面 / Demo | TypeScript | 发挥前端优势，做"看得见"的作品集 |
| 全栈整合 | Python 后端 + Next.js 前端 | FastAPI + Vercel AI SDK |

**为什么不是纯 TS：** 业界 80%+ 的 Agent 职位、论文复现、开源项目都是 Python 优先，坚持纯 TS 会与主流生态隔离。
**为什么需要 TS：** 前端背景是核心竞争力，TS 让你在"AI + 前端"场景（聊天 UI、Agent 可视化调试、Copilot 界面）快速产出 Demo。

## 学习路线总览

| 阶段 | 周数 | 主题 | 关键产出物 | 阶段文档 | 每日计划 |
|------|------|------|----------|---------|---------|
| 第 1 阶段 | **6 周** | Python 基础 + LLM API 入门 | CLI 聊天机器人 | [phase-1](./phase-1-python-llm-basics.md) | [daily-plan](./phase-1-daily-plan.md) |
| 第 2 阶段 | 4-5 周 | LLM 原理 + Prompt 工程 | Prompt 模式手册 + 评测脚本 | [phase-2](./phase-2-llm-principles-prompt-engineering.md) | [daily-plan](./phase-2-daily-plan.md) |
| 第 3 阶段 | 5 周 | 函数调用 + RAG 基础 | 文档问答机器人 | [phase-3](./phase-3-function-calling-rag.md) | [daily-plan](./phase-3-daily-plan.md) |
| 第 4 阶段 | 5 周 | Agent 核心架构 + LangGraph | 多步任务执行 Agent | [phase-4](./phase-4-agent-core-langgraph.md) | [daily-plan](./phase-4-daily-plan.md) |
| 第 5 阶段 | 5 周 | Multi-Agent + 工具生态 | 自动化研究 Agent | [phase-5](./phase-5-multi-agent-tool-ecosystem.md) | [daily-plan](./phase-5-daily-plan.md) |
| 第 6 阶段 | 5-6 周 | 评测 + 部署 + 作品集 | 上线产品 + 求职作品集 | [phase-6](./phase-6-eval-deploy-portfolio.md) | [daily-plan](./phase-6-daily-plan.md) |

## 核心原则

1. **理论 : 实践 = 3 : 7** — 每周以动手为主
2. **每个阶段都有可展示的产出物** — 拒绝"看完就忘"
3. **评测驱动** — 从 Week 8 开始，所有项目都要有评测集
4. **作品集导向** — 第 3、5、6 阶段产出 3 个作品集项目
5. **发挥前端优势** — 第 6 阶段重点把后端能力包装成完整产品
6. **允许延期，不允许放弃** — 兼职学习 90% 会超时。每个阶段文档都标注了 P0/P1/P2 优先级，时间不够时**砍 P2 保 P0**，不要因为"做不完"而中断

## 时间不够怎么办（降级路径）

每个阶段都可能出现"本周没空"。统一降级原则：

| 优先级 | 含义 | 何时可砍 |
|--------|------|---------|
| **P0 必做** | 阶段核心产出物、评测体系 | **不可砍**，砍了等于没学这阶段 |
| **P1 选做** | 进阶优化（如 Reranking、Multi-Agent 对比报告） | 时间紧可降为"读一遍+跑通 demo" |
| **P2 加分** | 博客、对比实验、额外工具集成 | 可直接跳过，作品集阶段再补 |

**底线：** 宁可每个 P0 都做到 70 分，也不要某一项追到 100 分而整体停摆。

## 作品集项目规划

| # | 项目名 | 类型 | 出现阶段 | 技术栈 |
|---|--------|------|---------|--------|
| 1 | 个人知识助手 | RAG + Function Calling | 第 3 阶段雏形，第 6 阶段打磨 | Python + FastAPI + Next.js |
| 2 | 自动化研究团队 | Multi-Agent | 第 5 阶段雏形，第 6 阶段扩展 | Python + LangGraph + CrewAI |
| 3 | 自选创新项目 | MCP / Browser Agent / AI Coding | 第 6 阶段 | 按选题定 |

## 关键认知

### 思维转变
- **Agent ≠ 更智能的聊天机器人**，Agent = LLM 驱动的状态机
- **Prompt 工程 ≠ 玄学**，是工程化的、可评测的
- **Multi-Agent ≠ 银弹**，90% 场景单 Agent 就够，复杂度要慎重

### 前端工程师的独特优势
- React 状态管理思维 → LangGraph 状态机设计
- 组件化思维 → Agent 模块化设计
- 用户视角 → Agent 产品体验设计
- TS 类型系统 → Pydantic 结构化输出

### 求职市场判断
- 对"前端 + Agent"复合人才需求极大
- 团队缺的是"能把 Agent 做成好产品的人"，不是"懂 LLM 的人"
- 前端背景不是劣势，是**稀缺优势**

## 学习成本估算（API 费用）

完成整条路线大约需要多少 API 费用？以下按各阶段主要调用量估算（2026-07 量级参考，以经济模型为主、旗舰模型为辅的混合策略）：

| 阶段 | 主要消耗 | 预估费用 (USD) | 备注 |
|------|---------|:-----------:|------|
| 第 1 阶段 | 少量 API 调用，熟悉 SDK | $2 - 5 | 用便宜模型学习即可 |
| 第 2 阶段 | 评测集反复调用 + Prompt 迭代 | $10 - 20 | Week 8 评测体系调用量较大 |
| 第 3 阶段 | RAG + Embedding + 重排序 | $15 - 30 | Embedding 量大、Reranker 调用 |
| 第 4 阶段 | Agent 循环多轮调用 + LangSmith | $20 - 40 | Agent 每一步都是 API 调用 |
| 第 5 阶段 | Multi-Agent 并行调用 | $30 - 60 | 多个 Agent 同时跑，成本翻倍 |
| 第 6 阶段 | 部署 + 评测 + Demo | $10 - 20 | 主要是部署平台费用 |
| **合计** | | **$87 - 175** | 约 600 - 1200 元人民币 |

> **省钱技巧：**
> - 开发调试阶段用便宜模型（DeepSeek、Claude Haiku），评测 / 上线前再用旗舰模型验证
> - 设置 API 用量上限（各厂控制台都有 budget cap），防止误操作烧钱
> - Embedding 建议用 text-embedding-3-small（$0.02/1M tokens），不要无脑用 large
> - 价格随时在变，以上为 2026-07 量级参考，以各厂官方定价页为准

## 如何获得反馈与保持动力

全职自学最大的敌人不是难度，而是**孤立无援**。建议：

### 获取技术反馈
- **Twitter(X) / 即刻：** 把每个阶段的产出物（评测报告、Prompt 模式手册、项目 Demo）发出来，标注 #AgentEngineer #BuildInPublic
- **LangChain Discord / Anthropic Developer Community：** 问具体技术问题，响应很快
- **掘金 / 知乎：** 发技术博客，写在 Phase 2 Week 5 的《前端工程师视角的 LLM 内部机制》就是第一篇

### 找学习搭子
- 找一个同样在转型的人，每周互相 review 代码和评测集。评审别人的代码是最高效的学习方式之一
- 在即刻 / Twitter 搜索"Agent 学习"或"前端转 AI"关键词，找到同期学习者
- 如果没有搭子，**让 LLM 当你的代码评审员**——把代码和思路发给 Claude/GPT，让它从架构、错误处理、可维护性角度评审

### 对抗动力低谷
- 兼职学习 90% 会超时，**允许延期，不允许放弃**
- 每个阶段文档顶部的进度勾选框，勾下去有正反馈
- Week 3 第一次看到 LLM 流式输出的时候，记住那种兴奋感——那是你转型的起点

## 学习资源汇总

### 必读文档

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- 🚫 [反模式库（本项目）](../anti-patterns.md) — 18 个真实工程坑，按阶段分类
- 🔧 [工具速查表（本项目）](../toolkit.md) — 一页汇总所有工具，含选型决策树

### 必读论文（速读）
- ReAct: Reasoning + Acting
- Reflexion
- Toolformer
- RAG（Retrieval-Augmented Generation）

### 必用工具
- **评测：** Promptfoo、LangSmith、Braintrust
- **框架：** LangChain、LangGraph、CrewAI、AutoGen
- **部署：** Fly.io、Railway、Vercel
- **Trace 调试：** LangSmith（必备）

### 模型版本策略

> 本仓库代码示例统一使用 `-latest` 别名（如 `gpt-5-latest`）作为模型名占位，方便你拿到代码就能跑。但在真实工程中，不同场景需要不同的版本策略：

| 场景 | 策略 | 原因 |
|------|------|------|
| **学习 / 快速试验** | `-latest` 别名 | 不用管版本，始终指向当前最新，不会因旧模型下线而报错 |
| **回归评测** | 固定 snapshot（如 `gpt-5-2026-01-15`） | 确保同一份评测集每次跑的结果可对比；`-latest` 指向变了，指标就不可比 |
| **生产环境** | 模型路由 + 固定版本 + 回滚基线 | 简单任务路由到经济模型、复杂任务到旗舰模型；每个模型锁定版本；保留上一版本基线用于快速回滚 |
| **Prompt 版本管理** | Git + 评测集版本号 | Prompt 内容和评测集一起打 tag（如 `v2.1-evalset-2026Q2`），确保"当时跑出这个分数的是什么 Prompt"完全可追溯 |

> **经验法则：** 开发阶段用别名（快）；评测和上线前切固定版本（稳）；生产永远保留回滚能力（安全）。

## 目录结构建议

```
agent-journey/
├── docs/
│   └── learning-path/         # 本学习路线文档
├── phase-1/                   # 第 1 阶段代码练习
├── phase-2/
├── phase-3/
│   └── knowledge-assistant/   # 作品集 #1 雏形
├── phase-4/
├── phase-5/
│   └── research-team/         # 作品集 #2 雏形
├── phase-6/
│   ├── knowledge-assistant/   # 作品集 #1 完整版
│   ├── research-team/         # 作品集 #2 完整版
│   └── innovation-project/    # 作品集 #3
└── notes/                     # 学习笔记
```

## 文档分工约定（SSOT，避免维护时两边不同步）

每个阶段有两份文档，**职责严格分离**，修改时只改对应那份：

| 文档 | 职责 | 改动触发 |
|------|------|---------|
| **阶段文档** `phase-N-xxx.md` | **Why / 认知 / 标准**：为什么学、心智模型、核心原则、完成标准、降级路径、推荐资源 | 认知更新、标准调整 |
| **每日计划** `phase-N-daily-plan.md` | **How / 代码 / 每天任务**：每天的代码示例、任务清单、自检题、复盘问题 | 教学内容调整 |

**原则：** 阶段文档里的"本周学什么"只写**一句话概览**，详细内容一律指向 daily plan。反之，daily plan 不重复讲阶段文档的认知/原则。若同一信息两边都需要，以阶段文档为准，daily plan 用链接引用。

## 进度追踪

每个阶段文档顶部都有进度勾选框，完成一项就勾选一项。建议每周日做一次复盘：
- 本周学了什么？
- 产出物是什么？
- 遇到什么卡点？
- 下周计划是什么？

---

**开始日期：** _______
**目标完成日期：** _______（开始日期 + 32-36 周，预留缓冲）
