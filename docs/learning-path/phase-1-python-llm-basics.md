# 第 1 阶段：Python 基础 + LLM API 入门

> **周期：** **6 周**（含 1 周缓冲。Week 1 拆分为语法速通 + 类型/异步两周，避免内容过密导致的流失）
> **目标：** 从前端工程师平滑过渡到 Python 开发，跑通第一个 LLM 调用。
> **关键产出物：** CLI 聊天机器人 v2（支持流式输出 + 结构化指令）

## 阶段目标

前端工程师转 Agent 工程师的第一道门槛不是 AI，而是 Python。本阶段用 5-6 周时间：
1. 把 JS/TS 思维迁移到 Python（**给足缓冲，不要赶**）
2. 建立 Python 工程化习惯
3. 跑通第一个 LLM API 调用
4. 理解结构化输出和错误处理

## 进度追踪

> ⏱ **耗时参考（预估，第一轮内测后补真实数据）**
>
> | 学习者画像 | 实际/计划周数 | 卡点高发周 |
> |-----------|:----------:|----------|
> | 纯前端，从未写过 Python | **1.4–1.6x**（8–10 周） | Week 2（异步）、Week 3（CI） |
> | 有 Node.js/脚本经验 | **1.1–1.2x**（7 周） | Week 3（mypy 严格模式） |
> | 时间充裕（每周 > 15h） | **1.0x**（6 周） | — |
>
> **如何使用这张表：** 进度落后于计划时，对照同档位画像判断是否在正常区间。若你"纯前端档"已经花了 10 周还在 Week 3，那不是你慢，是路线本身就要这么久——砍 P2 保 P0，别放弃。
>
> **回填约定：** 学习本阶段时，每周用[复盘模板](../../notes/retro-template.md)记录实际耗时；本阶段完成后，把实测周数回填到上表，并将标题中的"预估"改为"实测"。

- [ ] Week 1 - Python 语法基础（数据结构 + 函数 + 模块）
- [ ] Week 2 - Python 进阶（OOP + 类型 + Pydantic + 异步）
- [ ] Week 3 - Python 工程化（uv + Ruff + mypy + pytest + CI）
- [ ] Week 4 - LLM API 调用 + Prompt 基础
- [ ] Week 5 - 结构化输出 + 错误处理
- [ ] Week 6（缓冲周）- 补作业 / 复盘 / 赶进度
- [ ] 阶段产出物：CLI 聊天机器人 v2 完成

> **降级提示：** 时间不够时，Week 6 缓冲周可砍；Week 3 的 CI 部分可降为"能看懂 YAML"。**不可砍**的是 Week 4-5 的 LLM 调用与结构化输出——这是后续所有阶段的地基。

---

## Week 1 - Python 语法速通（对比 JS 学）

**核心思路：** 不要从零学 Python，用 JS/TS 作为锚点对比学习，效率最高。每天约 1-1.5 小时。

**本周学什么（一句话概览）：** list/dict/set/tuple 数据结构、函数/模块/class、装饰器入门。详细内容见 [每日计划](./phase-1-daily-plan.md#week-1python-语法速通)。

### 产出物

用 Python 重写一个你写过的 JS 小工具（推荐：CLI 工具，比如 Markdown 转换器、文件重命名工具）。

### 推荐资源

- [Real Python](https://realpython.com/) — 按需检索
- [Learn X in Y minutes (Python)](https://learnxinyminutes.com/docs/python/) — 速览语法
- [Pydantic 官方文档](https://docs.pydantic.dev/)

---

## Week 2 - Python 进阶（类型 + 异步）

**核心思路：** OOP、Pydantic、异步编程——Python 对前端开发者最友好的三个能力。

**本周学什么（一句话概览）：** class/继承/dataclass、Type Hints + Pydantic（TS→Python 最顺的迁移点）、asyncio/httpx 异步编程。详细内容见 [每日计划](./phase-1-daily-plan.md#week-2python-进阶类型--pydantic--异步--pytest)。

### 产出物

把 Week 1 的小工具升级为 OOP 结构，加入 Pydantic 类型定义。

---

## Week 3 - Python 工程化（uv + Ruff + pytest + CI）

**核心思路：** 像前端有 ESLint/Prettier/TypeScript 一样，建立 Python 工程化肌肉记忆。

**本周学什么（一句话概览）：** uv 依赖管理、Ruff + mypy 代码检查、pytest 测试、GitHub Actions CI。详细内容见 [每日计划](./phase-1-daily-plan.md#week-3python-工程化uv--ruff--pytest--ci)。

### 产出物

把项目升级为工程化标准：uv 管理依赖、Ruff+mypy 通过、10+ 个 pytest、GitHub Actions CI。

---

## Week 4 - LLM API 调用 + Prompt 基础

**核心思路：** 第一次真正接触 LLM，重点是理解 API 协议，不急着学 Prompt 技巧。

**本周学什么（一句话概览）：** API Key 准备、OpenAI/Anthropic SDK 调用、messages 结构、temperature 参数、token 与计费、流式输出。详细内容见 [每日计划](./phase-1-daily-plan.md#week-4llm-api-调用--prompt-基础)。

### 产出物

**CLI 聊天机器人 v1：** 命令行交互、多轮对话、流式输出、切换模型。

---

## Week 5 - 结构化输出 + 错误处理

**核心思路：** 真正的 Agent 应用 99% 都需要结构化输出，这是从"玩具"到"工程"的关键一步。

**本周学什么（一句话概览）：** Function Calling/Tool Use、JSON Mode/Structured Outputs、Pydantic 输出校验、tenacity 重试、自修复 Prompt。详细内容见 [每日计划](./phase-1-daily-plan.md#week-5结构化输出--错误处理)。

### 产出物

**CLI 聊天机器人 v2：** 结构化指令（翻译、摘要、情感分析），Pydantic 校验，自动重试。

### 推荐资源

- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

---

## Week 6（缓冲周）- 补作业 / 复盘 / 赶进度

这一周不安排新内容。用于查漏补缺、补充测试、写阶段总结。**多数兼职学习的人会用到这里。**

---

## 阶段总结与自检

### 完成标准

- [ ] 能熟练用 `uv` 创建项目、管理依赖
- [ ] 能用 pytest 写基础测试
- [ ] 能用 OpenAI / Anthropic SDK 发起请求
- [ ] 能处理流式输出
- [ ] 能用 Pydantic 定义输出 schema
- [ ] 能实现 Function Calling 基础逻辑
- [ ] 能写带重试和错误处理的 API 调用
- [ ] CLI 聊天机器人 v2 可运行、有测试

### 常见卡点

| 卡点 | 解决方案 |
|------|---------|
| Python 异步不熟 | 先用同步 SDK，Week 5+ 再用异步 |
| 装饰器看不懂 | 先理解"函数作为参数"，用 1-2 个实际例子即可 |
| Pydantic 报错 | 看报错信息，配 VS Code 类型提示 |
| API Key 不稳定 | 多备几家，写个 provider 切换函数 |

### 下一步

进入第 2 阶段：[LLM 原理 + Prompt 工程](./phase-2-llm-principles-prompt-engineering.md)
