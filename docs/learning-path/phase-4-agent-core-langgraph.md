# 第 4 阶段：Agent 核心架构 + LangGraph

> **周期：** 5 周（Phase 4 / Week 1-5，独立编号，非全局周号）
> **目标：** 掌握 Agent 的核心抽象——状态机、循环决策、记忆系统。
> **关键产出物：** 研究助手 Agent（作品集项目 #2 雏形）

## 阶段目标

前 3 个阶段你做的本质上还是"带工具的聊天机器人"。这一阶段开始才真正进入**Agent 工程**。

**核心思维转变：**
- Agent ≠ 更智能的聊天机器人
- Agent = **LLM 驱动的状态机**

前端的 React 状态管理经验在这里非常有用——把 Agent 想成"会自己决定下一步渲染什么的状态机"。

## 进度追踪

- [ ] Week 1 - Agent 基础：ReAct 落地
- [ ] Week 2 - LangChain Agent 生态
- [ ] Week 3 - LangGraph 核心（重点）
- [ ] Week 4 - Agent 记忆系统
- [ ] Week 5 - 阶段性整合项目
- [ ] 阶段产出物：研究助手 Agent 雏形

> **降级提示：** 时间不够时——P2（可砍）：LangChain 生态深挖、MemGPT 思路深挖；P1（降为跑通 demo）：长期/实体记忆、Subgraph；**P0（不可砍）：手写 ReAct Agent + LangGraph 核心（State/Node/Edge/条件分支）+ 研究助手雏形**。这是"Agent 工程师"身份的立足点。

---

## Week 1 - Agent 基础：ReAct 落地

**核心思路：** 不用任何框架，纯手写一个 Agent 循环。这是理解所有 Agent 框架的基础。

**本周学什么（一句话概览）：** Agent 五要素（感知/思考/行动/观察/状态）、Agent Loop 核心骨架、100 行代码手写 ReAct Agent、工程化细节（max_steps/超时/异常/成本控制）。详细代码见 [每日计划](./phase-4-daily-plan.md#week-14---agent-基础手写-react-agent)。

### 产出物

纯 Python 实现的 ReAct Agent：
- 能完成"查资料 → 总结 → 输出"任务
- 支持 3-5 个工具
- 有完整日志（每一步的 Thought / Action / Observation）
- 100 行核心代码，注释清晰

### 推荐资源

- [ReAct 论文精读](https://arxiv.org/abs/2210.03629)
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)（Anthropic 必读）

---

## Week 2 - LangChain Agent 生态

**核心思路：** 理解工业级框架的设计，知道它解决了什么问题、引入了什么问题。

**本周学什么（一句话概览）：** AgentExecutor 架构、Tool 抽象（BaseTool/Toolkit）、LangChain Hub、LangChain 的局限（状态管理不灵活→这正是 LangGraph 要解决的）、何时用/不用的判断标准。详细代码见 [每日计划](./phase-4-daily-plan.md#week-15---langchain-agent-生态)。

### 产出物

用 LangChain 重写 Week 1 的 Agent，对比纯手写 vs LangChain 的代码量和可调试性。

### 推荐资源

- [LangChain Python 文档](https://python.langchain.com/)
- [DeepLearning.AI LangChain 课程](https://www.deeplearning.ai/short-courses/)

---

## Week 3 - LangGraph 核心（重点）

**核心思路：** LangGraph 是目前工业级 Agent 的事实标准，必须深入掌握。

### 为什么是 LangGraph

- LangChain Agent 是"封装好的循环"，难以定制
- LangGraph 把 Agent 看成**状态机**，所有细节可控
- 支持复杂工作流：分支、循环、人工介入、持久化
- **前端 React 开发者学 LangGraph 非常顺**——和组件状态管理是同构的

**本周学什么（一句话概览）：** State/Node/Edge/Conditional Edge/Graph 核心概念、用 LangGraph 实现 ReAct、Plan-and-Execute/Reflection 经典模式、Human-in-the-Loop/Checkpointing/Streaming 进阶特性。详细代码见 [每日计划](./phase-4-daily-plan.md#week-16---langgraph-核心重点周)。

### 产出物

用 LangGraph 实现一个多步骤工作流：
- 场景："研究 → 起草 → 审校 → 定稿"
- 包含条件分支（审校不通过则回起草）
- 包含人工介入（关键节点暂停确认）
- 有完整 trace（用 LangSmith）

### 推荐资源

- [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph 示例库](https://github.com/langchain-ai/langgraph/tree/main/examples)

---

## Week 4 - Agent 记忆系统

**核心思路：** 没有记忆的 Agent 只是"一次性工具"。真正的助手需要记住你。

**本周学什么（一句话概览）：** 三种记忆类型（短期/长期/工作记忆）、对话历史管理（滑动窗口/Token 预算/摘要压缩）、长期记忆方案（向量库/结构化/知识图谱）、MemGPT 分层记忆思路、实体记忆（用户偏好/项目背景/历史决策）。详细代码见 [每日计划](./phase-4-daily-plan.md#week-17---agent-记忆系统)。

### 产出物

给 Week 3 的 Agent 加上记忆系统：
- 短期：会话内上下文管理
- 长期：跨会话记住用户偏好
- 实体：记住你的项目背景
- 测试：关掉程序重开，Agent 还"认识你"

### 推荐资源

- [MemGPT 论文](https://arxiv.org/abs/2310.08560)
- [LangGraph Memory 文档](https://langchain-ai.github.io/langgraph/concepts/persistence/)

---

## Week 5 - 阶段性整合项目

**核心思路：** 综合应用 LangGraph + 工具调用 + RAG + 记忆，做出一个有真实价值的研究助手。

### 项目：研究助手 Agent

**功能需求：**
- 接收研究问题（如"对比 React Server Components 和传统 SSR 的优劣"）
- 自动规划研究步骤
- 并行 / 串行搜索多个来源
- 阅读和对比信息
- 综合输出结构化研究报告

**技术架构：**
```
用户问题
    ↓
[Planner Node] ← LangGraph
    ↓
[Researcher Node] ← Web Search + RAG
    ↓
[Synthesizer Node] ← LLM
    ↓
[Reviewer Node] ← Critic
    ↓
   通过？
    ↓ 是
[Output Node]
    ↓ 否
回到 Researcher
```

**工程要求：**
- LangGraph 实现，节点清晰
- 完整 trace（LangSmith）
- 评测集（至少 10 个研究问题）
- 成本监控（每次研究的 token 消耗）
- 失败回退（某个来源失败不影响整体）

### 产出物

**作品集项目 #2 雏形：**
- GitHub 仓库
- 完整 README（架构图、使用说明、示例输出）
- 至少 3 个真实研究报告示例
- 评测报告（人工评分 + LLM-as-Judge）
- 成本分析报告

这个项目会在第 5 阶段升级为 Multi-Agent 版本。

---

## 阶段总结与自检

### 完成标准

- [ ] 能纯手写 ReAct Agent（不用框架）
- [ ] 理解 LangChain Agent 的优劣
- [ ] 能用 LangGraph 实现复杂状态机
- [ ] 能实现条件分支、循环、人工介入
- [ ] 理解短期 / 长期 / 实体记忆
- [ ] 能实现跨会话记忆
- [ ] 研究助手 Agent 雏形可运行、有评测
- [ ] 接入了 LangSmith trace

### 核心认知

**Agent 设计的三大原则：**

1. **状态优先** — 先设计 State schema，再设计 Node
2. **可观测性** — 没有 trace 就没有调试
3. **渐进复杂度** — 先用单 Agent，遇到瓶颈才上 Multi-Agent

### 常见卡点

| 卡点 | 解决方案 |
|------|---------|
| LangGraph 学习曲线陡 | 先跑官方示例，再改造 |
| Agent 进入死循环 | 加 max_steps 和超时 |
| 记忆系统效果差 | 检查 Embedding 质量，加摘要 |
| Trace 看不懂 | 先看 Input / Output，再看中间步骤 |

### 下一步

进入第 5 阶段：[Multi-Agent + 工具生态](./phase-5-multi-agent-tool-ecosystem.md)
