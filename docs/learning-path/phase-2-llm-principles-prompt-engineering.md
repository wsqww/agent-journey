# 第 2 阶段：LLM 原理 + Prompt 工程

> **周期：** 4 周（Phase 2 / Week 1-4，独立编号，非全局周号）
> **目标：** 理解 LLM 内部机制，掌握工业级 Prompt 设计方法论，学会用评测驱动迭代。
> **关键产出物：** Prompt 模式手册 + 评测脚本 + 经过评测优化的聊天机器人

## 阶段目标

第 1 阶段你已经能"调用 LLM"，但调用出来的结果质量不稳定。本阶段解决三个问题：
1. **为什么 LLM 会这样表现？**（理解原理，破除玄学）
2. **怎么让 LLM 稳定输出我要的结果？**（Prompt 工程方法论）
3. **怎么知道我的 Prompt 真的好？**（评测驱动，而非 vibe check）

## 进度追踪

- [ ] Week 1 - LLM 内部机制
- [ ] Week 2 - Prompt 工程核心模式
- [ ] Week 3 - 高级 Prompt 技术
- [ ] Week 4 - 评测驱动开发（分水岭）
- [ ] 补充专题 - 推理模型（Reasoning Models）
- [ ] 阶段产出物：Prompt 模式手册 + 评测基线

> **降级提示：** 时间不够时——P2（可砍）：ToT、Reflexion 深挖、DSPy 深入；P1（降为跑通 demo）：Self-Consistency、Meta-Prompting；**P0（不可砍）：ReAct 模式 + Week 4 评测体系**。评测是后续所有阶段的基石。

---

## Week 1 - LLM 内部机制

**核心思路：** 前端工程师不需要懂数学，但必须懂概念。否则永远是"黑盒调参"。

### 学习内容

**Token 化（BPE）**
- 为什么"token"不等于"词"
- 中文、英文、代码的 token 差异
- 用 `tiktoken` 实际观察 token 切分

**Transformer 直觉（不推导公式）**
- Attention 机制：每个 token 看其他所有 token
- Self-Attention vs Cross-Attention
- 为什么上下文窗口是硬限制（计算量 O(n²)）
- KV Cache 是什么（推理加速）

**训练流程三阶段**
- **预训练（Pretraining）：** 海量文本，学语言规律
- **SFT（Supervised Fine-Tuning）：** 人工标注的指令-回答对
- **RLHF / DPO：** 人类反馈强化学习，对齐价值观
- 为什么会产生幻觉（预训练数据的局限性）
- 为什么会"被越狱"（对齐不彻底）

**主流模型对比与选型**（2026-07 代际，具体型号请以各厂最新文档为准）
| 模型 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| GPT-5 系列（5.6 Sol/Terra/Luna） | 综合能力最强、推理模型成熟 | 贵、需要科学上网 | 复杂推理、生产环境 |
| Claude 4.5+ 系列（Sonnet/Opus） | 长文本、写作、代码、Agent 生态友好 | 同上 | 长文档、Agent |
| DeepSeek-R1 / V3 | 推理强、便宜、国内可用 | 生态较新 | 推理任务、国内项目 |
| Llama / Qwen 开源系列 | 开源、便宜、可本地部署 | 能力略弱 | 本地部署、微调 |

> ⚠️ **重要：** 各厂淘汰旧模型很快（如 Claude 3.5 / 4.0 / 4.1 系列已陆续退役）。写代码时**优先用 `-latest` 别名**（如 `gpt-5-latest`、`claude-sonnet-4-5-latest`），它会被厂商自动指向当前版本，避免几个月后调用失败。本文档代码示例统一采用此策略。

### 产出物

写一篇博客《前端工程师视角的 LLM 内部机制》（输出倒逼输入）。

### 推荐资源

- [3Blue1Brown 神经网络系列](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)
- [Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajv0)

---

## 补充专题：推理模型（Reasoning Models，2025+ 必读）

> **为什么单独拎出来：** 自 OpenAI o1（2024 末）以来，"推理模型"成为 LLM 最大的范式变化。OpenAI o 系列、Anthropic Claude（extended thinking）、DeepSeek-R1、Gemini 2.x Thinking 等已陆续成熟。**它们改变了 Prompt 工程和 Agent 设计的基本假设**，前端转 Agent 必须建立这个认知，否则会用旧方法套新模型，事倍功半。

### 什么是推理模型

- **传统 LLM（GPT-4o、Claude 3.5 等）：** 直接输出答案，CoT 需要 Prompt 引导（"let's think step by step"）
- **推理模型（o1/o3、R1、Claude thinking）：** 模型内部自带"长思考"，先在隐藏的思维链里推理，再输出最终答案
- **训练方式：** 在 SFT/RLHF 之外，增加大规模 RL（强化学习）训练推理能力，让模型学会"自己跟自己辩论"

### 对 Prompt 工程的影响（关键认知转变）

| 维度 | 传统模型 | 推理模型 |
|------|---------|---------|
| CoT Prompt | **必需**，"let's think step by step" | **有害**，模型自带思考，额外 CoT 反而干扰 |
| Few-shot | 有效 | 效果减弱，甚至降低表现（模型有自己的推理路径） |
| 角色扮演 / 情绪 Prompt | 有效 | 基本无效（模型不会"被鼓励"就推理更好） |
| Prompt 长度 | 越详细越好 | **越简洁越好**，把思考交给模型 |
| 延迟 | 秒级 | 几十秒到几分钟（要等思考结束） |
| 成本 | 输出 token 计费 | **思考 token 也计费**，成本可能 10x |
| 适合任务 | 通用 | 复杂推理（数学、代码、多步规划、研究） |

**口诀：** 对推理模型，**少写 Prompt、多给问题、把思考还给它**。

### 对 Agent 设计的影响（为 Phase 4 铺垫）

- **Planner 节点适合用推理模型**（规划质量高），**Executor 节点用传统模型**（快、便宜）
- **ReAct 模式需要重新审视**：推理模型可能把"何时调用工具"也内化了，tool use 协议有变化（注意看各厂最新文档）
- **成本控制是重点**：推理模型跑 Agent 循环很容易单次任务烧几美元，必须加 max_thinking_tokens、提前终止条件
- **延迟治理**：思考时间长，前端必须用流式 + 进度提示，否则用户体验崩塌

### 落地建议

1. **先体验：** 申请一家推理模型 API，问同一个复杂问题，对比传统模型 vs 推理模型的输出质量和耗时
2. **建立选型直觉：**
   - 简单 QA / 分类 / 格式化 → 传统小模型（便宜快）
   - 复杂推理 / 多步规划 / 代码生成 → 推理模型
   - 不要无脑全用推理模型，成本和延迟会失控
3. **评测对比：** 用 Week 4 的评测集，分别跑传统模型和推理模型，看准确率提升是否值成本

### 推荐资源

- 各厂官方推理模型文档（OpenAI o 系列、Anthropic Extended Thinking、DeepSeek-R1 技术报告）
- [DeepSeek-R1 论文](https://arxiv.org/abs/2501.12948)（RL 训练推理能力的代表作，速读）

---

---

## Week 2 - Prompt 工程核心模式

**核心思路：** Prompt 工程是工程，不是玄学。有方法论，有模式，可评测。

**本周学什么（一句话概览）：** Zero-shot / Few-shot / CoT / Role-Playing 四大基础模式，System Message 设计，XML/Markdown/JSON 结构化模板，防御性 Prompt（注入攻击 + 多层防御），Prompt 调试技巧。详细代码和每日任务见 [每日计划](./phase-2-daily-plan.md#week-6---prompt-工程核心模式)。

### 产出物

**Prompt 模式手册：**
建立 5-10 个常用 Prompt 模式库，每个包含：
- 适用场景
- Prompt 模板
- 输入示例
- 输出示例
- 失败案例与修复

---

## Week 3 - 高级 Prompt 技术

**核心思路：** 这一阶段为 Agent 做铺垫，ReAct 是 Agent 的核心模式。

**本周学什么（一句话概览）：** Self-Consistency（多次采样投票）、**ReAct 模式**（Thought→Action→Observation 循环，Agent 的基石）、Chain Prompting（多步串联）、ToT / Reflexion（树形搜索 + 反思重试）、DSPy 入门（程序化 Prompt 优化）。详细代码和每日任务见 [每日计划](./phase-2-daily-plan.md#week-7---高级-prompt-技术)。

### 产出物

用 ReAct 模式重写第 1 阶段的聊天机器人：
- 让它能"思考"（输出 Thought）
- 让它能"行动"（调用简单工具，如计算器）
- 对比 ReAct 前后的效果差异

### 推荐资源

- [ReAct 论文](https://arxiv.org/abs/2210.03629)（速读）
- [Reflexion 论文](https://arxiv.org/abs/2303.11366)（速读）
- [DSPy 文档](https://dspy.ai/)

---

## Week 4 - 评测驱动开发（分水岭）

**核心思路：** 这是整个学习路线**最关键的一周**。能否成为工程师而非"调参侠"，分水岭就在这里。

### 为什么评测如此重要

- **没有评测，就没有迭代方向** — 你不知道改 Prompt 是变好还是变坏
- **没有评测，就无法协作** — 团队成员无法判断你的改动
- **没有评测，就无法上线** — 生产环境需要质量保证
- **很多前端转 AI 的人直接跳到 LangChain 写代码，结果做出来的东西质量不可控，原因就是没学评测**

**本周学什么（一句话概览）：** 评测集构建（golden set/rubric、20+ 条起步）、三种评测方法（规则匹配 / LLM-as-Judge / 人工标注）、Promptfoo / LangSmith 工具实操、A/B 回归测试、至少 3 轮 Prompt 迭代并记录数据。详细代码和每日任务见 [每日计划](./phase-2-daily-plan.md#week-8---评测驱动开发分水岭)。

### 产出物

给 ReAct 版聊天机器人建立评测体系：
1. **构建评测集：** 20+ 条用例，覆盖不同任务类型
2. **建立基线：** 跑出当前 Prompt 的准确率、忠实度分数
3. **迭代优化：** 至少 3 轮 Prompt 修改，每轮都跑评测
4. **产出报告：** 记录每轮改动的指标变化

### 推荐资源

- [Promptfoo 文档](https://www.promptfoo.dev/)
- [LangSmith 评测教程](https://docs.smith.langchain.com/evaluation)
- [Anthropic 的 Evaluation 指南](https://docs.anthropic.com/en/docs/build-with-claude/evals)

---

## 阶段总结与自检

### 完成标准

- [ ] 能解释 LLM 的基本工作原理（token、attention、训练三阶段）
- [ ] 能针对不同场景选合适的模型
- [ ] 能区分传统模型与推理模型，知道何时该用哪种、Prompt 写法有何不同
- [ ] 掌握 5+ 种 Prompt 模式，知道何时用哪种
- [ ] 能识别和防御 Prompt 注入攻击
- [ ] 能手写 ReAct Prompt
- [ ] 能用 Promptfoo 或 LangSmith 跑评测
- [ ] 有一个 20+ 条的评测集
- [ ] 至少做过 3 轮 Prompt 优化，并有数据记录

### 关键认知

**这一阶段最大的认知转变：**

| 错误认知 | 正确认知 |
|---------|---------|
| Prompt 是玄学 | Prompt 是工程 |
| "我觉得效果好" | "评测集显示效果好" |
| 越长越复杂越好 | 越简单越好，除非评测证明复杂更好 |
| 模型越贵越好 | 便宜模型 + 好 Prompt 经常胜过贵模型 |

### 下一步

进入第 3 阶段：[函数调用 + RAG 基础](./phase-3-function-calling-rag.md)

**重要：** Week 4 的评测体系会在后续每个阶段都用到，**它是后续所有项目的基石**。
