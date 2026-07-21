# 第 5 阶段：Multi-Agent + 工具生态

> **周期：** 5 周（Phase 5 / Week 1-5，独立编号，非全局周号）
> **目标：** 从单 Agent 升级到多 Agent 协作，掌握工业级工具集成，理解 Agent 系统的复杂度治理。
> **关键产出物：** 自动化研究团队（作品集项目 #2 完整版）

## 阶段目标

第 4 阶段你做了一个单 Agent 的研究助手。本阶段：
1. 把它升级为 Multi-Agent 系统（专业分工）
2. 接入更丰富的工具生态（浏览器、代码执行、MCP）
3. 学会治理 Agent 系统的复杂度

## 关键认知（必读）

**Multi-Agent 不是银弹。**

- 90% 的场景单 Agent + 好的 Prompt 就够了
- Multi-Agent 引入 3 倍复杂度但只解决 10% 的问题
- **学会判断"什么时候该用、什么时候不该用"比学会"怎么用"更重要**

### 什么时候用 Multi-Agent

- 任务可以清晰拆分为不同角色（研究员 + 写手 + 编辑）
- 需要并行处理（同时调研多个方向）
- 需要对抗性思维（Critic 反驳 Planner）
- 单 Agent 的上下文已经爆掉

### 什么时候不用

- 任务线性、简单
- 团队（你）不熟悉 Agent 调试
- 没有评测体系（Multi-Agent 没有评测就是灾难）

## 进度追踪

> ⏱ **耗时参考（预估，第一轮内测后补真实数据）**
>
> | 学习者画像 | 实际/计划周数 | 卡点高发周 |
> |-----------|:----------:|----------|
> | 第一次接触 Multi-Agent | **1.3–1.5x**（6–7 周） | Week 1（Supervisor 模式）、Week 4（MCP） |
> | 已熟悉单 Agent + 分布式系统 | **1.1x**（5–6 周） | Week 4（MCP Server 开发） |
> | 已用过 CrewAI / AutoGen | **1.0x**（5 周） | — |
>
> **关键提醒：** Week 4（MCP）是 2026 新生态，**官方文档还在频繁变动**，照着教程抄可能因为 SDK 版本更新而跑不通。预算时给 Week 4 留出"读官方最新文档"的时间，不要只看二手博客。

- [ ] Week 1 - Multi-Agent 架构模式
- [ ] Week 2 - CrewAI / AutoGen 实战
- [ ] Week 3 - 工具生态集成
- [ ] Week 4 - Computer Use 与 MCP
- [ ] Week 5 - 阶段性整合项目
- [ ] 阶段产出物：自动化研究团队（完整版）

> **降级提示：** 时间不够时——P2（可砍）：CrewAI/AutoGen 三框架横评、Hierarchical/Network 架构深挖；P1（降为跑通 demo）：Computer Use、代码 Agent 架构剖析；**P0（不可砍）：Supervisor 模式 + 工具生态集成 + MCP Server 实操**。MCP 是 2026 生态核心，不能跳。

---

## Week 1 - Multi-Agent 架构模式

**核心思路：** 先理解架构模式，再动手写代码。

**本周学什么（一句话概览）：** Multi-Agent 四大价值（分工/专业/并行/对抗）、四种架构模式（Supervisor/Hierarchical/Network/Sequential）、框架对比选型（LangGraph/CrewAI/AutoGen/Swarm）、Agent 间通信协议。详细代码见 [每日计划](./phase-5-daily-plan.md#week-19---multi-agent-架构模式)。

**框架对比参考：**

| 框架 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| LangGraph | 完全可控、状态清晰 | 代码量大 | 生产级、复杂工作流 |
| CrewAI | 易用、角色化 | 抽象较重 | 快速原型、内容生产 |
| AutoGen | 对话式、灵活 | 调试困难 | 研究、对话场景 |
| OpenAI Swarm | 极简 | 功能少（实验性） | 学习、轻量场景 |

### 产出物

用 LangGraph 实现 Supervisor 模式：
- 1 个 Manager Agent
- 3 个 Worker Agent（如：研究员、写手、编辑）
- Manager 决定调用哪个 Worker
- 完整 trace 可观察

### 推荐资源

- [LangGraph Multi-Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)
- [AutoGen 论文](https://arxiv.org/abs/2308.08155)

---

## Week 2 - CrewAI / AutoGen 实战

**核心思路：** 体验不同框架的设计哲学，学会选型。

**本周学什么（一句话概览）：** CrewAI 核心概念（Agent/Task/Crew/Process）、AutoGen 核心概念（ConversableAgent/Group Chat/UserProxyAgent）、同一任务三框架对比（代码量/可调试性/效果/成本）、框架陷阱（过度抽象/调试困难/性能开销）。详细代码见 [每日计划](./phase-5-daily-plan.md#week-20---crewai--autogen-实战)。

### 产出物

用 CrewAI 实现"内容团队"：
- Researcher Agent：调研主题
- Writer Agent：撰写初稿
- Editor Agent：审校润色
- 协作产出一篇完整文章（如技术博客）

### 推荐资源

- [CrewAI 文档](https://docs.crewai.com/)
- [AutoGen 文档](https://microsoft.github.io/autogen/)

---

## Week 3 - 工具生态集成

**核心思路：** Agent 的能力上限取决于工具生态。前端背景在这里是巨大优势。

**本周学什么（一句话概览）：** Web 搜索工具（Tavily/Brave/DuckDuckGo）、浏览器自动化（Playwright/Browser Use/Computer Use）、代码执行（E2B/Daytona/沙箱）、文件与数据（SQL/CSV/图像）、API 集成（Notion/GitHub/Slack/Gmail/OAuth）、工具设计原则。详细代码见 [每日计划](./phase-5-daily-plan.md#week-21---工具生态集成)。

### 产出物

构建一个"工具箱 Agent"：
- 集成 5+ 类工具（搜索、浏览器、代码、文件、API）
- 根据任务自动选择工具
- 工具失败有降级策略
- 完整的工具调用日志

### 推荐资源

- [Tavily](https://tavily.com/)
- [Browser Use](https://github.com/browser-use/browser-use)
- [E2B](https://e2b.dev/)

---

## Week 4 - Computer Use 与 MCP（重点，2026 生态核心）

**核心思路：** 理解当前最前沿的 Agent 形态，MCP 是 Agent 工程师必须掌握的能力。

**本周学什么（一句话概览）：** Computer Use 概念（截图+键鼠控制）、代码 Agent 架构剖析（Claude Code/Cursor/Cline）、**MCP 协议**（Server 开发/资源-工具-Prompt 三类原语/传输层/与 Agent 框架集成）。MCP 是 2026 Agent 工具生态的事实标准——一次实现，所有 MCP Client 通用。详细代码见 [每日计划](./phase-5-daily-plan.md#week-22---computer-use-与-mcp)。

**MCP 架构参考：**
```
Agent (MCP Client)
    ↓
MCP Protocol
    ↓
MCP Server (暴露工具)
    ↓
实际服务（Notion / GitHub / DB）
```

### 产出物

写一个 MCP Server：
- 选择你常用的服务（Notion / GitHub / Linear / Jira）
- 实现 3+ 工具
- 接入 Claude Desktop 实际使用
- 发布到 MCP Server 仓库（加分项）

> 🔐 **MCP 安全提示——远程 MCP 不是"本地函数调用"：**
> - MCP 涉及 OAuth 授权时，必须校验 PKCE、redirect_uri、最小 scope 和 token audience
> - Server 端应验证 Client 身份，不要信任任意连接；传输层使用加密（HTTPS / TLS）
> - 参考 [MCP Authorization 规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) 和 [安全最佳实践](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)

### 推荐资源

- [Anthropic Computer Use](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Cline 源码](https://github.com/cline/cline)（学习 AI 编程 Agent 架构）

---

## Week 5 - 阶段性整合项目

**核心思路：** 综合应用 Multi-Agent + 工具生态，升级 Phase 4 的研究助手为完整的"研究团队"。

### 项目：自动化研究团队

**角色设计：**
- **Planner Agent：** 拆解研究问题，制定计划
- **Researcher Agent × N：** 并行搜索多个来源
- **Writer Agent：** 综合信息，起草报告
- **Reviewer Agent：** 审校内容，提出修改意见
- **Critic Agent：** 故意挑刺，防止信息茧房
- **Editor Agent：** 最终润色定稿

**技术架构：**
```
用户问题
    ↓
[Planner] ← LangGraph Supervisor
    ↓
并行调用多个 [Researcher]
    ↓
[Writer] 起草
    ↓
[Reviewer] 审校 ←→ [Critic] 对抗
    ↓
通过？
    ↓ 是
[Editor] 定稿
    ↓ 否
回到 [Researcher] / [Writer]
```

**工程要求：**
- LangGraph 实现（不要用 CrewAI 的黑盒）
- 完整 trace（每个 Agent 的输入输出）
- 成本监控（每个 Agent 的 token 消耗）
- 评测集（至少 20 个研究问题）
- 对比报告：单 Agent（Phase 4）vs Multi-Agent

### 产出物

**作品集项目 #2 完整版：**
- 替换 Phase 4 的雏形
- GitHub 仓库（架构图、README、示例）
- 5+ 真实研究报告示例
- 评测报告（人工 + LLM-as-Judge）
- 成本分析（每次研究的成本）
- 对比报告：单 Agent vs Multi-Agent 的效果差异

---

## 阶段总结与自检

### 完成标准

- [ ] 理解 4 种 Multi-Agent 架构模式
- [ ] 能用 LangGraph 实现 Supervisor 模式
- [ ] 能用 CrewAI / AutoGen 实现 Multi-Agent
- [ ] 能集成 5+ 类工具
- [ ] 理解 Computer Use 和 MCP
- [ ] 写过至少 1 个 MCP Server
- [ ] 自动化研究团队可运行、有评测
- [ ] 有单 Agent vs Multi-Agent 的对比数据

### 核心认知

**Multi-Agent 设计的三大陷阱：**

1. **过度工程** — 简单任务上 Multi-Agent，徒增复杂度
2. **角色边界不清** — Agent 之间职责重叠，互相干扰
3. **没有评测** — Multi-Agent 没有评测就是黑盒中的黑盒

**Multi-Agent 设计的三大原则：**

1. **先单 Agent，再 Multi** — 遇到瓶颈才升级
2. **角色清晰** — 每个 Agent 职责明确，不重叠
3. **可观测性** — 每个 Agent 的输入输出都可追溯

### 常见卡点

| 卡点 | 解决方案 |
|------|---------|
| Agent 互相扯皮 | 明确角色边界，加 Planner 统筹 |
| 成本爆炸 | 加 max_turns，用便宜模型跑辅助 Agent |
| 调试困难 | 必须接 LangSmith trace |
| 效果不如单 Agent | 可能就不该用 Multi-Agent，回归单 Agent |

### 下一步

进入第 6 阶段：[评测 + 部署 + 作品集](./phase-6-eval-deploy-portfolio.md)
