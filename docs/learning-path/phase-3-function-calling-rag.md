# 第 3 阶段：函数调用 + RAG 基础

> **周期：** 5 周（Phase 3 / Week 1-5，独立编号，非全局周号）
> **目标：** 掌握 Agent 的两大核心能力——调用外部工具、检索外部知识。
> **关键产出物：** 个人知识助手雏形（作品集项目 #1）

## 阶段目标

聊天机器人只能"用模型已有的知识回答"。真正的 Agent 需要：
1. **调用外部工具**（Function Calling）— 让 LLM 能"动手"
2. **检索外部知识**（RAG）— 让 LLM 能"查资料"

本阶段是 Agent 区别于聊天机器人的关键，也是你**第一个作品集项目**的起点。

## 进度追踪

> ⏱ **耗时参考（预估，第一轮内测后补真实数据）**
>
> | 学习者画像 | 实际/计划周数 | 卡点高发周 |
> |-----------|:----------:|----------|
> | 没用过向量库 / 数据库 | **1.3–1.4x**（6–7 周） | Week 2（Embedding 抽象）、Week 3（切分策略） |
> | 有后端/数据库经验 | **1.1x**（5–6 周） | Week 4（Hybrid Search 调参） |
> | RAG 已有雏形经验 | **1.0x**（5 周） | — |
>
> **关键提醒：** Week 4（RAG 优化）的"准确率从 60% 提升到 85%"是一个反复试错的过程，**调一次切分策略可能要重跑整个评测集**。预算 API 费用时，请给 Week 4 留出 2x 的调用量。

- [ ] Week 1 - Function Calling 深入
- [ ] Week 2 - RAG 基础：Embedding 与向量数据库
- [ ] Week 3 - RAG 流水线
- [ ] Week 4 - RAG 进阶：检索优化
- [ ] Week 5 - 阶段性整合项目
- [ ] 阶段产出物：个人知识助手雏形

> **降级提示：** 时间不够时——P2（可砍）：HyDE、Step-Back、向量索引算法深挖；P1（降为跑通 demo）：Hybrid Search、Reranking、RAGAS；**P0（不可砍）：Function Calling 协议 + 基础 RAG 流水线 + 知识助手雏形**。作品集 #1 雏形必须能跑。

---

## Week 1 - Function Calling 深入

**核心思路：** 第 1 阶段你接触过 Function Calling，这周深入理解它的工程化使用。

**本周学什么（一句话概览）：** OpenAI vs Anthropic 两套协议对比、JSON Schema 工具定义、多工具编排与并行调用、工具执行的工程化（错误处理/超时/重试/权限）。详细代码见 [每日计划](./phase-3-daily-plan.md#week-9---function-calling-深入)。

### 产出物

扩展第 2 阶段的聊天机器人，支持 3+ 工具：
- 查天气（调用免费天气 API）
- 算数学（用 Python `eval` 沙箱）
- 查时间（时区转换）
- 查汇率（调用汇率 API）

每个工具都要有完整的错误处理。

> 🔐 **安全提示（从第一个工具开始养成习惯）：**
> - **参数校验：** 所有工具入参用 Pydantic 做 schema 强校验，拒绝越界参数
> - **最小权限：** 危险操作（写文件、发邮件、调外部付费 API）必须加白名单或人工确认
> - **审计日志：** 记录每次工具调用的参数、结果、耗时，出问题时能回溯
> - 这些习惯在 Phase 4-6 做多工具 Agent 时会被放大——一个不安全的小工具被 LLM 循环调用 10 次，后果不堪设想

### 推荐资源

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

---

## Week 2 - RAG 基础：Embedding 与向量数据库

**核心思路：** RAG 的第一步是"把文本变成向量，能按语义搜索"。

**本周学什么（一句话概览）：** Embedding 原理（文本→高维向量→语义空间）、主流 Embedding 模型选型（OpenAI/BGE/Cohere）、向量数据库入门（Chroma/Qdrant/Pgvector）、相似度搜索（Cosine/L2）。Embedding 模型对比表和向量库选型见下方参考。详细代码见 [每日计划](./phase-3-daily-plan.md#week-10---rag-基础embedding-与向量数据库)。

**Embedding 模型参考：**

| 模型 | 维度 | 优势 | 适用场景 |
|------|------|------|---------|
| OpenAI text-embedding-3-small | 1536 | 便宜、效果好 | 通用 |
| OpenAI text-embedding-3-large | 3072 | 效果最好 | 高精度 |
| BGE-M3 | 1024 | 开源、中文好 | 本地部署、中文 |
| Cohere embed-v3 | 1024 | 多语言 | 多语言场景 |

### 产出物

建立一个 100 条文档的小知识库：
- 用你自己的笔记 / Notion / Obsidian 内容
- 实现"语义搜索"：输入 query，返回最相似的 5 条文档
- 对比不同 Embedding 模型的搜索效果

### 推荐资源

- [Chroma 官方教程](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## Week 3 - RAG 流水线

**核心思路：** 把 Embedding + 向量库 + LLM 串成完整的"文档问答"系统。

**本周学什么（一句话概览）：** 文档加载（PDF/Markdown/网页）、切分策略（固定/递归/语义/父子文档）、完整 RAG 流程（加载→切分→入库→检索→生成）、引用溯源、RAG 专用 Prompt 设计。详细代码见 [每日计划](./phase-3-daily-plan.md#week-11---rag-流水线)。

### 产出物

**文档问答机器人 v1：**
- 上传 PDF / Markdown 文件
- 自动切分、Embedding、入库
- 提问 → 检索 → 生成回答
- 回答附带引用来源

### 推荐资源

- [LangChain RAG 教程](https://python.langchain.com/docs/use_cases/question_answering/)
- [LlamaIndex 教程](https://docs.llamaindex.ai/)

---

## Week 4 - RAG 进阶：检索优化

**核心思路：** 基础 RAG 效果通常一般（60-70% 准确率），进阶优化能提升到 85%+。

**本周学什么（一句话概览）：** Hybrid Search（BM25+向量+RRF 融合）、Reranking（Cohere/BGE 重排序）、Query 改写（HyDE/Multi-Query/Step-Back）、上下文压缩、RAGAS 评测框架。详细代码见 [每日计划](./phase-3-daily-plan.md#week-12---rag-进阶检索优化)。

### 产出物

用评测集对比不同 RAG 策略：
- Baseline：纯向量检索
- V2：Hybrid Search
- V3：Hybrid + Reranking
- V4：V3 + HyDE
- 输出对比报告（准确率、延迟、成本）

### 推荐资源

- [RAGAS 文档](https://docs.ragas.io/)
- [Cohere Rerank](https://docs.cohere.com/docs/reranking)
- [Advanced RAG 论文合集](https://arxiv.org/abs/2312.10997)

---

## Week 5 - 阶段性整合项目

**核心思路：** 把 Function Calling + RAG 结合，做出第一个作品集项目的雏形。

### 项目：个人知识助手

**功能需求：**
- 知识库管理：上传、删除、更新文档
- 智能问答：基于知识库回答问题（RAG）
- 工具调用：
  - 查本地知识库
  - 调用外部 API（如查天气、查时间）
  - 记录笔记（写入文件 / Notion）
- 跨会话记忆：记住用户偏好

**技术架构：**
```
用户输入 → Agent 决策
            ↓
      ┌─────┴─────┐
      ↓           ↓
   RAG 检索    其他工具
      ↓           ↓
      └─────┬─────┘
            ↓
         LLM 综合
            ↓
         输出回答
```

**工程要求：**
- 完整的日志（每次调用记录）
- 错误处理和重试
- 评测集（至少 30 条）
- LangSmith trace 接入

### 产出物

**作品集项目 #1 雏形：**
- 代码托管在 GitHub
- 完整 README（架构图、使用说明）
- 至少 3 个核心功能的演示
- 评测报告（基线分数）

这个项目会在第 6 阶段打磨上线，加入 Web UI 和用户系统。

---

## 阶段总结与自检

### 完成标准

- [ ] 能定义复杂的 Function Calling schema
- [ ] 能实现多工具编排和错误处理
- [ ] 理解 Embedding 原理，能选合适的模型
- [ ] 能用 Chroma / Qdrant 建立向量库
- [ ] 能实现完整的 RAG 流水线
- [ ] 能用 Hybrid Search + Reranking 优化 RAG
- [ ] 能用 RAGAS 或类似工具评测 RAG
- [ ] 个人知识助手雏形可运行、有评测

### 常见卡点

| 卡点 | 解决方案 |
|------|---------|
| RAG 效果差 | 先检查切分策略，再试 Hybrid + Rerank |
| 工具调用不稳定 | 检查工具描述是否清晰，加 Few-shot |
| 向量库选型纠结 | 先用 Chroma，生产再换 Qdrant |
| 长文档 Lost in Middle | 用 Rerank 或 Map-Reduce |

### 下一步

进入第 4 阶段：[Agent 核心架构 + LangGraph](./phase-4-agent-core-langgraph.md)
