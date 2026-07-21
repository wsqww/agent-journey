# 第 5 阶段每日计划：Multi-Agent + 工具生态

> **周期：** 5 周（Phase 5 / Week 1-5，独立编号，非全局周号）
> **每日投入：** 工作日约 1-1.5 小时 / 周末 2-3 小时
> **目标：** 从单 Agent 升级到多 Agent 协作，掌握工业级工具集成，交付自动化研究团队
> **配套阶段文档：** [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md)

## 阶段核心认知（每天看一遍）

**Multi-Agent 不是银弹。**

- 90% 的场景单 Agent + 好的 Prompt 就够了
- Multi-Agent 引入 3 倍复杂度但只解决 10% 的问题
- **学会判断"什么时候该用、什么时候不该用"比学会"怎么用"更重要**
- **先单 Agent，再 Multi — 遇到瓶颈才升级**

## 进度追踪

- [ ] Week 1 - Multi-Agent 架构模式
- [ ] Week 2 - CrewAI / AutoGen 实战
- [ ] Week 3 - 工具生态集成
- [ ] Week 4 - Computer Use 与 MCP
## Week 5 - 自动化研究团队（作品集 #2）
- [ ] 阶段产出物已发布到 GitHub
- [ ] 单 Agent vs Multi-Agent 对比报告完成

---

## Week 1 - Multi-Agent 架构模式

**本周目标：** 先理解架构模式，再动手写代码。周末用 LangGraph 实现一个 Supervisor 模式。

### Day 1（周一）：Multi-Agent 基础 + 何时该用

**学习目标：** 建立 Multi-Agent 的心智模型，学会判断"该不该用"。

#### 核心概念

**为什么要 Multi-Agent**

- 分工：每个 Agent 专注一个职责
- 专业：每个 Agent 用不同的 Prompt / 模型
- 并行：多个 Agent 同时工作
- 对抗：Critic Agent 提出反对意见

**关键判断标准**

| 场景特征 | 推荐 |
|---------|------|
| 任务线性、简单 | 单 Agent |
| 团队不熟悉 Agent 调试 | 单 Agent |
| 没有评测体系 | 单 Agent（先建评测） |
| 任务可清晰拆分为角色 | Multi-Agent |
| 需要并行处理多个方向 | Multi-Agent |
| 单 Agent 上下文已经爆掉 | Multi-Agent |
| 需要对抗性思维 | Multi-Agent |

**重要原则：** 先把单 Agent 跑通、评测建好，再考虑 Multi-Agent。

#### 今日任务

- [ ] 阅读 [LangGraph Multi-Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/) 前半部分
- [ ] 回顾你 Phase 4 的研究助手，列出 3 个"它做不到 / 做不好"的点
- [ ] 判断这 3 个点是否真的需要 Multi-Agent（写下理由）

#### 自检

- [ ] 我能说出 Multi-Agent 的 4 个核心价值
- [ ] 我能列出 3 个"不该用 Multi-Agent"的场景
- [ ] 我对自己 Phase 4 项目的瓶颈有清晰认知

---

### Day 2（周二）：4 种架构模式对比

**学习目标：** 理解 Supervisor / Hierarchical / Network / Sequential 四种模式的差异。

#### 核心概念

**1. Supervisor 模式（最常用）**
```
       [Supervisor]
      /     |      \
[Worker1] [Worker2] [Worker3]
```
- 一个 Manager 调度多个 Worker
- Manager 决策，Worker 执行
- 最易调试，**新手首选**

**2. Hierarchical 模式**
```
         [CEO Agent]
         /         \
   [总监 Agent]  [总监 Agent]
    /     \         |
[员工] [员工]    [员工]
```
- 多层 Supervisor 嵌套
- 适合复杂组织结构（如大型研发团队模拟）

**3. Network 模式**
```
[Agent A] ↔ [Agent B]
   ↕           ↕
[Agent C] ↔ [Agent D]
```
- Agent 之间自由通信
- 最灵活、最难控制、最容易扯皮

**4. Sequential（顺序）模式**
```
[Agent A] → [Agent B] → [Agent C]
```
- Agent 依次执行
- 前一个的输出是后一个的输入
- 最简单、最可控，**生产线场景首选**

#### 选型决策树

```
任务能拆成清晰步骤？
├── 是 → Sequential
└── 否 → 需要中央决策？
         ├── 是 → Supervisor
         │       └── 需要多层管理？→ Hierarchical
         └── 否 → Agent 间需要自由协作？
                  ├── 是 → Network（慎重）
                  └── 否 → 重新评估是否真的需要 Multi
```

#### 今日任务

- [ ] 画出你 Phase 4 项目升级后的架构图
- [ ] 在笔记里写下：你选哪种模式？为什么？
- [ ] 找一个开源 Multi-Agent 项目，识别它用的什么模式

#### 自检

- [ ] 我能画出 4 种架构模式的示意图
- [ ] 我能解释为什么 Supervisor 是新手首选
- [ ] 我能说出 Network 模式的风险

---

### Day 3（周三）：LangGraph 基础回顾 + Supervisor 理论

**学习目标：** 复习 LangGraph 的 StateGraph，理解 Supervisor 的实现原理。

#### 核心概念回顾

**LangGraph 三要素**
- `State`：共享状态（TypedDict 或 Pydantic）
- `Node`：每个节点是一个函数或 Agent
- `Edge`：节点间的跳转逻辑（条件边）

**Supervisor 的本质**

Supervisor 本质上就是一个"路由 Node"：
1. 接收当前状态
2. 让 LLM 判断下一步该调用哪个 Worker
3. 跳转到对应 Worker
4. Worker 执行完返回 Supervisor
5. 循环直到任务完成

#### 代码示例：最小 Supervisor 骨架

```python
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END

# 1. 定义状态
class State(TypedDict):
    messages: list
    next: str

# 2. Supervisor 节点
def supervisor(state: State) -> dict:
    # 这里用 LLM 决策下一步
    # 简化版：直接返回固定路由
    last_msg = state["messages"][-1]
    if "研究" in last_msg:
        return {"next": "researcher"}
    elif "写作" in last_msg:
        return {"next": "writer"}
    else:
        return {"next": "FINISH"}

# 3. Worker 节点
def researcher(state: State) -> dict:
    return {"messages": ["研究结果..."], "next": "supervisor"}

def writer(state: State) -> dict:
    return {"messages": ["写作结果..."], "next": "supervisor"}

# 4. 路由函数
def route(state: State) -> Literal["researcher", "writer", "__end__"]:
    if state["next"] == "FINISH":
        return END
    return state["next"]

# 5. 构建图
builder = StateGraph(State)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route)
builder.add_edge("researcher", "supervisor")
builder.add_edge("writer", "supervisor")

graph = builder.compile()
```

#### 今日任务

- [ ] 复习你 Phase 4 学过的 LangGraph 基础代码
- [ ] 把上面的 Supervisor 骨架敲一遍并跑通
- [ ] 用 [LangSmith](https://smith.langchain.com/) 看一次 trace

#### 自检

- [ ] 我能解释 State / Node / Edge 的关系
- [ ] 我能画出 Supervisor 模式的状态机
- [ ] 我理解 `add_conditional_edges` 的作用

---

### Day 4（周四）：LangGraph Supervisor 代码实战（上）

**学习目标：** 用 LangGraph + LangChain 实现一个真正能调 LLM 的 Supervisor。

#### 代码示例：带 LLM 的 Supervisor

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Literal
from pydantic import BaseModel

# Supervisor 决策模型
class Decision(BaseModel):
    next: Literal["researcher", "writer", "FINISH"]

llm = ChatOpenAI(model="gpt-5-latest", temperature=0)
supervisor_llm = llm.with_structured_output(Decision)

SUPERVISOR_PROMPT = """你是一个团队主管，负责调度以下成员：

- researcher：负责信息检索和研究
- writer：负责撰写内容

根据当前任务状态，决定下一步该让谁工作。
如果任务已完成，返回 FINISH。

当前消息历史：
{messages}
"""

def supervisor(state: State) -> dict:
    messages_str = "\n".join(state["messages"])
    decision: Decision = supervisor_llm.invoke(
        SUPERVISOR_PROMPT.format(messages=messages_str)
    )
    return {"next": decision.next}

def researcher(state: State) -> dict:
    response = llm.invoke([
        SystemMessage(content="你是一个专业研究员，输出简洁的研究结果。"),
        HumanMessage(content=state["messages"][-1])
    ])
    return {"messages": [response.content], "next": "supervisor"}

def writer(state: State) -> dict:
    response = llm.invoke([
        SystemMessage(content="你是一个专业写手，根据研究结果写一篇文章。"),
        HumanMessage(content=str(state["messages"]))
    ])
    return {"messages": [response.content], "next": "supervisor"}
```

#### 今日任务

- [ ] 新建项目目录 `phase-5/supervisor-demo/`
- [ ] 用 `uv init` 初始化，`uv add langchain langgraph langchain-openai`
- [ ] 把上面的代码补全并跑通
- [ ] 测试 3 种输入：研究类问题、写作类问题、完成信号

#### 自检

- [ ] Supervisor 能根据输入正确路由到 researcher / writer
- [ ] 任务完成时能正确返回 FINISH
- [ ] 我能在 LangSmith 看到完整 trace

---

### Day 5（周五）：Agent 间通信协议

**学习目标：** 理解 Agent 之间如何传递信息，三种通信模式的差异。

#### 核心概念

**1. 消息传递（Message Passing）**
```
[Agent A] --msg--> [Agent B]
```
- 每个 Agent 有独立状态
- 通过显式消息通信
- LangGraph 默认模式

**2. 共享状态（Shared State）**
```
[Agent A] → [Shared State] ← [Agent B]
```
- 所有 Agent 读写同一个 State
- LangGraph 的 `State` 就是这个模式
- 简单直接，但状态容易膨胀

**3. 黑板模式（Blackboard）**
```
       [Blackboard（黑板）]
      /     |      \
[Agent A] [Agent B] [Agent C]
```
- 一个中央"黑板"，所有 Agent 订阅感兴趣的内容
- 适合复杂协作（如 AutoGen 的 Group Chat）

#### 代码示例：状态扩展

```python
from typing import TypedDict, Annotated
from operator import add

class ResearchState(TypedDict):
    # 累加的消息列表
    messages: Annotated[list, add]
    # 研究结果（覆盖）
    research_data: str
    # 文章草稿（覆盖）
    draft: str
    # 当前阶段
    stage: Literal["planning", "researching", "writing", "reviewing", "done"]
    # 下一个节点
    next: str
```

#### 今日任务

- [ ] 为你的 Supervisor 项目设计一个完整的 State
- [ ] 改造代码，让 Worker 读写不同的字段
- [ ] 测试：研究员的结果能否被写手读到？

#### 自检

- [ ] 我能解释 3 种通信模式的差异
- [ ] 我理解 `Annotated[list, add]` 的作用（累加而非覆盖）
- [ ] 我知道何时该用共享状态，何时该用消息传递

---

### Day 6（周六）：实现完整 Supervisor 模式（项目日）

**学习目标：** 把前 5 天的内容整合，交付一个完整的 Supervisor Demo。

#### 项目：三人协作团队

**角色设计：**
- **Supervisor：** 调度决策
- **Researcher：** 信息检索（模拟，或接 Tavily）
- **Writer：** 内容撰写
- **Editor：** 审校润色

**目录结构：**
```
phase-5/
└── supervisor-demo/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── state.py         # State 定义
    │   ├── nodes.py         # Supervisor + Workers
    │   ├── graph.py         # 图的构建
    │   └── main.py          # 入口
    └── tests/
        └── test_graph.py
```

#### 今日任务

- [ ] 实现完整的 Supervisor + 3 个 Worker
- [ ] 支持 3 类任务：纯研究、纯写作、研究 + 写作 + 润色
- [ ] 加上 LangSmith trace
- [ ] 跑 5 个测试用例，观察 Supervisor 的路由决策
- [ ] 写 README，记录架构图和运行方式

#### 预期产出

- 一个能跑通的 Supervisor 项目
- 至少 5 个测试用例的 trace 截图
- 一份简短的架构说明文档

---

### Day 7（周日）：框架对比 + 复盘

**学习目标：** 建立框架选型的全局视角。

#### 学习内容

**四大框架对比**

| 框架 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| LangGraph | 完全可控、状态清晰 | 代码量大 | 生产级、复杂工作流 |
| CrewAI | 易用、角色化 | 抽象较重 | 快速原型、内容生产 |
| AutoGen | 对话式、灵活 | 调试困难 | 研究、对话场景 |
| OpenAI Swarm | 极简 | 功能少（实验性） | 学习、轻量场景 |

**选型建议（前端转 Agent 视角）**
- 先学 LangGraph：因为它最透明，能让你真正理解 Multi-Agent 的运作
- 再学 CrewAI：做快速原型时用它
- AutoGen 视情况：研究型项目可以考虑
- Swarm 跳过：实验性项目，不必投入

#### 今日任务

- [ ] 阅读 [CrewAI 文档](https://docs.crewai.com/) 和 [AutoGen 文档](https://microsoft.github.io/autogen/) 的 Quick Start
- [ ] 在 notes 里写一份《四大框架对比笔记》
- [ ] 在 [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md) 勾选 Week 1 完成项

#### 周末复盘问题

回答以下问题（写在 `notes/week-19-notes.md`）：

1. 用 Supervisor 模式后，你 Phase 4 的项目瓶颈是否真的解决了？
2. 调试 Multi-Agent 系统时，你最大的痛点是什么？
3. 如果让你重做 Phase 4 的项目，你会用单 Agent 还是 Multi-Agent？
4. 4 种架构模式中，你觉得哪种最难调试？为什么？

---

## Week 2 - CrewAI / AutoGen 实战

**本周目标：** 体验不同框架的设计哲学，学会选型，交付一个 CrewAI 内容团队。

### Day 1（周一）：CrewAI 环境搭建 + 核心概念

**学习目标：** 跑通 CrewAI Hello World，理解它的核心抽象。

#### 核心概念

**CrewAI 四要素**
- **Agent：** 角色定义（role / goal / backstory）
- **Task：** 具体任务（description / expected_output）
- **Crew：** Agent + Task 的组合 + 执行方式
- **Process：** sequential（顺序）/ hierarchical（层级）

**CrewAI vs LangGraph**
- CrewAI：声明式，配置驱动，上手快
- LangGraph：命令式，代码驱动，控制强

#### 代码示例：最小 CrewAI

```python
# uv add crewai crewai-tools

from crewai import Agent, Task, Crew, Process

# 1. 定义 Agent
researcher = Agent(
    role='研究员',
    goal='找到关于 {topic} 的最新信息',
    backstory='你是一位资深研究员，擅长从海量信息中提炼关键点。',
    verbose=True
)

writer = Agent(
    role='写手',
    goal='根据研究结果写一篇 500 字短文',
    backstory='你是一位前记者，擅长把复杂概念讲清楚。',
    verbose=True
)

# 2. 定义 Task
research_task = Task(
    description='研究主题：{topic}，列出 3 个关键点。',
    expected_output='一份包含 3 个关键点的研究简报',
    agent=researcher
)

writing_task = Task(
    description='基于研究结果，写一篇 500 字短文。',
    expected_output='一篇 500 字的 Markdown 文章',
    agent=writer,
    context=[research_task]  # 依赖前一个任务的输出
)

# 3. 组建 Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True
)

# 4. 执行
result = crew.kickoff(inputs={'topic': 'MCP 协议'})
print(result)
```

#### 今日任务

- [ ] 安装 CrewAI：`uv add crewai crewai-tools`
- [ ] 把上面的 Hello World 跑通
- [ ] 改一个你感兴趣的主题测试
- [ ] 用 LangSmith trace 看看 CrewAI 内部做了什么

#### 自检

- [ ] 我能解释 Agent / Task / Crew / Process 的关系
- [ ] 我能跑通 CrewAI Hello World
- [ ] 我看到 CrewAI 在 LangSmith 里的 trace 结构

---

### Day 2（周二）：CrewAI Agent 定义实战

**学习目标：** 写出高质量的 Agent 定义，理解 backstory 的作用。

#### 核心概念

**Agent 定义三要素**
- **role：** 一句话角色（研究员 / 写手 / 编辑）
- **goal：** 这个角色要达成什么目标（动词开头）
- **backstory：** 背景故事，影响 LLM 的"人格"

**为什么 backstory 重要**

backstory 不是装饰，它直接影响 LLM 的输出风格：
- "前调查记者" → 输出更严谨、有质疑精神
- "科技博客作者" → 输出更通俗、有故事感
- "学术研究员" → 输出更规范、有引用

#### 代码示例：工具集成

```python
from crewai_tools import SerperDevTool, WebsiteSearchTool

# 搜索工具
search_tool = SerperDevTool()
web_tool = WebsiteSearchTool()

researcher = Agent(
    role='资深研究员',
    goal='为 {topic} 找到权威、最新的信息源',
    backstory='''你是一位有 10 年经验的研究员，
曾经在中科院工作，擅长跨学科研究。
你特别重视信息源的权威性，拒绝引用自媒体内容。''',
    tools=[search_tool, web_tool],
    verbose=True,
    llm='gpt-5-latest'  # 可指定模型
)

editor = Agent(
    role='严苛的编辑',
    goal='确保文章没有事实错误和逻辑漏洞',
    backstory='''你是前《南方周末》编辑，
眼里容不下任何事实错误。
你会逐字逐句校对，发现问题绝不放过。''',
    verbose=True
)
```

#### 今日任务

- [ ] 为你的内容团队定义 3 个角色（研究员 / 写手 / 编辑）
- [ ] 给每个角色写 50 字以上的 backstory
- [ ] 接入至少 1 个工具（SerperDev / Tavily）
- [ ] 对比：换了 backstory 后，输出风格是否有变化？

#### 自检

- [ ] 我能写出有"人格"的 Agent 定义
- [ ] 我会为 Agent 配置工具
- [ ] 我理解 backstory 对输出风格的影响

---

### Day 3（周三）：CrewAI Task 和 Process 模式

**学习目标：** 掌握 Task 的依赖关系和两种 Process 模式。

#### 核心概念

**Task 的关键字段**
- `description`：任务描述（清晰、可执行）
- `expected_output`：期望输出的格式（关键！）
- `agent`：执行该任务的 Agent
- `context`：依赖的其他 Task（列表）
- `output_file`：输出到文件

**两种 Process**
- `sequential`：按 Task 列表顺序执行
- `hierarchical`：有一个 Manager Agent 统筹调度

#### 代码示例：Hierarchical Process

```python
from crewai import Agent, Task, Crew, Process

# 不指定 agent，由 manager 决定
research_task = Task(
    description='研究 {topic} 的核心技术原理。',
    expected_output='一份 300 字的技术原理说明'
)

writing_task = Task(
    description='把研究结果改写为科普文章。',
    expected_output='一篇 800 字的科普文章（Markdown）'
)

review_task = Task(
    description='审校文章，修正事实错误和不通顺的表达。',
    expected_output='一份审校后的最终稿（Markdown）'
)

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, review_task],
    process=Process.hierarchical,  # 关键：启用 Manager
    verbose=True
)
```

#### 今日任务

- [ ] 用 sequential 模式跑一遍 3 个 Task
- [ ] 改成 hierarchical 模式再跑一遍
- [ ] 在 LangSmith 里对比两者的 trace 差异
- [ ] 笔记：两种模式各自的优缺点

#### 自检

- [ ] 我能解释 sequential vs hierarchical 的差异
- [ ] 我会设置 Task 的 context 依赖
- [ ] 我能在 trace 里看到 hierarchical 的 Manager 决策

---

### Day 4（周四）：AutoGen 核心概念

**学习目标：** 理解 AutoGen 的对话式 Agent 模型。

#### 核心概念

**AutoGen 三大角色**
- **ConversableAgent：** 可对话的 Agent（核心）
- **AssistantAgent：** ConversableAgent 的子类，默认 LLM 助手
- **UserProxyAgent：** 代理用户，可执行代码

**AutoGen 的设计哲学**
- 一切都是"对话"
- Agent 之间通过 conversable 接口互相调用
- 适合"讨论 / 协商"类任务

#### 代码示例：AutoGen Group Chat

```python
# uv add "autogen-agentchat" "autogen-ext[openai]"

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-5-latest")

researcher = AssistantAgent(
    name="researcher",
    model_client=model_client,
    system_message="你是一个研究员，输出简洁的研究结果。"
)

writer = AssistantAgent(
    name="writer",
    model_client=model_client,
    system_message="你是一个写手，根据研究结果写短文。输出后说 TERMINATE。"
)

team = RoundRobinGroupChat([researcher, writer], max_turns=6)

async def main():
    result = await team.run(task="写一篇 200 字的关于 MCP 协议的介绍。")
    print(result)

import asyncio
asyncio.run(main())
```

#### 今日任务

- [ ] 安装 AutoGen：`uv add autogen-agentchat autogen-ext[openai]`
- [ ] 把上面的 Group Chat 跑通
- [ ] 尝试加第三个 Agent（如 critic）
- [ ] 对比：AutoGen 和 CrewAI 的代码量

#### 自检

- [ ] 我能解释 AutoGen 的"对话式"设计哲学
- [ ] 我会定义 AssistantAgent 并配置 system_message
- [ ] 我能跑通 Group Chat

---

### Day 5（周五）：AutoGen 进阶 + 代码执行

**学习目标：** 用 UserProxyAgent 执行代码，理解 AutoGen 的代码执行能力。

#### 核心概念

**UserProxyAgent 的特殊能力**
- 可以执行 LLM 生成的代码
- 可以模拟用户输入
- 是 AutoGen 区别于其他框架的核心特性

**安全警告：** 代码执行默认在本地，不要跑不可信的 LLM 输出！用 Docker 或沙箱。

#### 代码示例：带代码执行的 Agent

```python
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat

import tempfile
work_dir = tempfile.mkdtemp()

# 本地代码执行器（仅在信任环境下使用！）
code_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

coder = AssistantAgent(
    name="coder",
    model_client=OpenAIChatCompletionClient(model="gpt-5-latest"),
    system_message="""你是一个 Python 工程师。
对于计算类问题，写 Python 代码求解，输出代码块。
不要解释，直接给代码。"""
)

executor = CodeExecutorAgent(
    name="executor",
    code_executor=code_executor
)

team = RoundRobinGroupChat([coder, executor], max_turns=4)

async def main():
    result = await team.run(task="计算斐波那契数列前 10 项之和。")
    print(result)

asyncio.run(main())
```

#### 今日任务

- [ ] 跑通带代码执行的 AutoGen 例子
- [ ] 测试 3 个数学题（让 Agent 写代码求解）
- [ ] 在笔记里写下：代码执行的风险点和防护措施

#### 自检

- [ ] 我能解释 UserProxyAgent / CodeExecutorAgent 的作用
- [ ] 我知道本地代码执行的风险
- [ ] 我能列出至少 2 种防护方案（Docker / E2B）

---

### Day 6（周六）：用 CrewAI 实现"内容团队"（项目日）

**学习目标：** 综合应用 CrewAI，交付一个可用的内容生产团队。

#### 项目：技术博客内容团队

**角色设计：**
- **Researcher：** 用搜索工具调研主题
- **Writer：** 撰写初稿
- **Editor：** 审校润色

**任务：** 输入一个技术主题，产出一篇 1000 字的 Markdown 技术博客。

**目录结构：**
```
phase-5/
└── content-crew/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── agents.py        # Agent 定义
    │   ├── tasks.py         # Task 定义
    │   ├── crew.py          # Crew 组装
    │   └── main.py          # 入口
    └── outputs/             # 生成的文章
```

#### 今日任务

- [ ] 初始化项目 `uv init content-crew`
- [ ] 定义 3 个 Agent（带完整 backstory）
- [ ] 定义 3 个 Task（带 context 依赖）
- [ ] 跑 3 个不同主题（如 MCP / Browser Use / Computer Use）
- [ ] 把生成的文章保存到 `outputs/`
- [ ] 写 README，说明如何运行

#### 预期产出

- 一个可重复运行的 CrewAI 项目
- 3 篇生成的技术博客（Markdown）
- 一份运行说明文档

---

### Day 7（周日）：三大框架对比 + 复盘

**学习目标：** 形成自己的框架选型判断。

#### 今日任务

- [ ] 选一个相同任务（如"写一篇技术博客"），分别用 LangGraph / CrewAI / AutoGen 实现
- [ ] 记录以下数据：

| 维度 | LangGraph | CrewAI | AutoGen |
|------|-----------|--------|---------|
| 代码行数 | ? | ? | ? |
| 跑通时间 | ? | ? | ? |
| 输出质量（1-10） | ? | ? | ? |
| Token 消耗 | ? | ? | ? |
| 调试难度（1-10） | ? | ? | ? |
| 灵活性（1-10） | ? | ? | ? |

- [ ] 在 `notes/week-20-notes.md` 写下你的选型结论
- [ ] 在 [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md) 勾选 Week 2 完成项

#### 周末复盘问题

1. CrewAI 的"角色化抽象"和 LangGraph 的"状态机抽象"，你更喜欢哪个？为什么？
2. AutoGen 的对话式模式，适合哪类任务？
3. 这三个框架，哪个 trace 最清晰？哪个最难调试？
4. 你的"内容团队"项目，单 Agent 能做吗？如果可以，效果差异有多大？

---

## Week 3 - 工具生态集成

**本周目标：** 掌握工业级工具集成，发挥前端背景的优势。交付一个"工具箱 Agent"。

> **核心认知：** Agent 的能力上限取决于工具生态。前端工程师在浏览器自动化方向有天然优势。

### Day 1（周一）：工具设计原则 + Tavily 搜索

**学习目标：** 学会设计高质量工具，掌握 Tavily 搜索。

#### 核心概念

**工具设计四大原则**

1. **单一职责** — 一个工具只做一件事
2. **清晰的 description** — 给 LLM 看的，要无歧义
3. **友好的错误信息** — 也是给 LLM 看的，告诉它下一步该怎么做
4. **严格的 schema** — 用 Pydantic 定义输入输出

**为什么 Tavily 比谷歌搜索好（对 Agent 来说）**
- 专为 AI 设计，返回结构化结果
- 自带摘要，不需要再抓网页
- 有 `answer` 字段，直接给结论

#### 代码示例：Tavily 工具

```python
# uv add tavily-python

from tavily import TavilyClient
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    url: str
    content: str

tavily = TavilyClient(api_key="your-key")

def web_search(query: str, max_results: int = 5) -> list[SearchResult]:
    """搜索互联网，返回相关结果。

    Args:
        query: 搜索关键词
        max_results: 最多返回多少条结果（默认 5）

    Returns:
        搜索结果列表，每条包含 title / url / content
    """
    response = tavily.search(query=query, max_results=max_results)
    return [SearchResult(**r) for r in response["results"]]

# 包装成 LangChain Tool
from langchain.tools import Tool

search_tool = Tool.from_function(
    func=web_search,
    name="web_search",
    description="当你需要查找最新信息时使用。输入搜索关键词，返回网页结果。"
)
```

#### 今日任务

- [ ] 注册 [Tavily](https://tavily.com/) 账号（免费额度够用）
- [ ] 把上面的工具封装跑通
- [ ] 测试 5 个不同的查询，观察结果质量
- [ ] 用你 Phase 4 的研究助手接入这个工具

#### 自检

- [ ] 我能说出好工具的 4 个特征
- [ ] 我能写带 Pydantic schema 的工具
- [ ] 我会写"给 LLM 看的"description

---

### Day 2（周二）：Playwright 浏览器自动化

**学习目标：** 用 Playwright 做网页抓取，发挥前端优势。

#### 核心概念

**Playwright vs BeautifulSoup**
- BeautifulSoup：只能解析静态 HTML
- Playwright：能渲染 JS、模拟交互、截图

**何时用 Playwright**
- 网页需要 JS 渲染（SPA）
- 需要模拟点击 / 登录
- 需要截图给 Vision 模型

#### 代码示例：Playwright 抓取

```python
# uv add playwright
# playwright install chromium

from playwright.async_api import async_playwright

async def scrape_page(url: str) -> dict:
    """抓取网页的标题和正文。

    Args:
        url: 目标网页地址

    Returns:
        包含 title / content / links 的字典
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        title = await page.title()
        # 智能提取正文（前端经验派上用场）
        content = await page.evaluate("""
            () => {
                // 移除 nav / footer / script
                document.querySelectorAll('nav, footer, script, style').forEach(el => el.remove());
                return document.body.innerText;
            }
        """)
        links = await page.eval_on_selector_all(
            'a', 'els => els.map(e => e.href)'
        )

        await browser.close()
        return {"title": title, "content": content, "links": links[:20]}

# 测试
import asyncio
result = asyncio.run(scrape_page("https://example.com"))
print(result["title"])
```

#### 今日任务

- [ ] 安装 Playwright 并下载浏览器
- [ ] 跑通上面的抓取代码
- [ ] 尝试抓取一个 SPA 网站（如你的博客 / 某文档站）
- [ ] 把它包装成 LangChain Tool

#### 自检

- [ ] 我能用 Playwright 抓取动态网页
- [ ] 我能提取正文（去掉 nav / footer）
- [ ] 我会处理 `wait_until` 参数

---

### Day 3（周三）：Browser Use 实战

**学习目标：** 体验 AI 原生的浏览器控制，理解 Vision + Browser 的威力。

#### 核心概念

**Browser Use 是什么**
- 基于 Playwright 的 AI 浏览器控制库
- 让 Agent 像人一样看网页、点击、输入
- 用 Vision 模型理解页面

**Browser Use vs 纯 Playwright**
- Playwright：你写选择器，代码执行
- Browser Use：你描述目标，AI 自己找元素

#### 代码示例：Browser Use 基础

```python
# uv add browser-use
# playwright install chromium

import asyncio
from browser_use import Agent as BrowserAgent
from langchain_openai import ChatOpenAI

async def main():
    agent = BrowserAgent(
        task="打开 GitHub，搜索 'mcp server'，列出前 5 个 star 最多的项目",
        llm=ChatOpenAI(model="gpt-5-latest", temperature=0),  # 需要 Vision，用 gpt-5-latest
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

#### 今日任务

- [ ] 安装 browser-use 并跑通上面的例子
- [ ] 设计 3 个测试任务（如查天气、找文档、对比价格）
- [ ] 观察：Agent 失败的场景有哪些？
- [ ] 笔记：Browser Use 的适用场景和局限

#### 自检

- [ ] 我能用 Browser Use 完成一个多步操作任务
- [ ] 我能解释为什么需要 Vision 模型
- [ ] 我知道 Browser Use 的失败模式

---

### Day 4（周四）：代码执行沙箱

**学习目标：** 让 Agent 安全地执行代码，理解沙箱方案。

#### 核心概念

**三种代码执行方案**

| 方案 | 安全性 | 成本 | 适用场景 |
|------|--------|------|---------|
| `subprocess` + 超时 | 低 | 免费 | 本地信任环境 |
| Docker 容器 | 中 | 低 | 中等风险 |
| E2B / Daytona 云沙箱 | 高 | 按使用付费 | 生产环境 |

#### 代码示例：subprocess + 资源限制

```python
# uv add subprocess-dev (标准库即可)

import subprocess
import tempfile
from pathlib import Path

def run_python(code: str, timeout: int = 10) -> str:
    """在受限环境下执行 Python 代码。

    Args:
        code: 要执行的 Python 代码字符串
        timeout: 超时时间（秒），默认 10

    Returns:
        stdout + stderr 输出
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["python3", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            # 注意：Windows 不支持这些参数
            # 在生产环境请用 Docker
        )
        output = result.stdout + result.stderr
        return output[:2000]  # 截断防止爆 token
    except subprocess.TimeoutExpired:
        return f"ERROR: 代码执行超时（{timeout}s）"
    finally:
        tmp_path.unlink(missing_ok=True)

# 测试
print(run_python("print(1 + 1)"))
print(run_python("import time; time.sleep(100)", timeout=2))
```

#### 代码示例：E2B 云沙箱（推荐用于生产）

```python
# uv add e2b-code-interpreter

import os
from e2b_code_interpreter import Sandbox

async def run_with_e2b(code: str) -> str:
    """用 E2B 云沙箱执行代码（安全）。"""
    sbx = Sandbox(api_key=os.getenv("E2B_API_KEY"))
    execution = sbx.run_code(code)
    return execution.text or execution.error or "(no output)"

# 测试（async 函数必须用 asyncio.run 触发，直接 print 会得到 coroutine 对象）
import asyncio
print(asyncio.run(run_with_e2b("import sys; print(sys.version)")))
```

#### 今日任务

- [ ] 跑通 subprocess 版本，测试正常 + 超时场景
- [ ] 注册 [E2B](https://e2b.dev/)，跑通云沙箱版本
- [ ] 包装成 LangChain Tool
- [ ] 笔记：三种方案的取舍

#### 自检

- [ ] 我能解释为什么不能直接 `eval()` 用户输入
- [ ] 我会用 subprocess + timeout
- [ ] 我能跑通 E2B 云沙箱

---

### Day 5（周五）：文件系统 + 数据库 + API 工具

**学习目标：** 掌握三大类常用工具，让 Agent 能"动手"操作数据。

#### 代码示例：文件系统工具

```python
from pathlib import Path
from pydantic import BaseModel

class FileInfo(BaseModel):
    path: str
    size: int
    is_dir: bool

def list_files(dir_path: str, pattern: str = "*") -> list[FileInfo]:
    """列出目录下的文件。

    Args:
        dir_path: 目录路径
        pattern: glob 模式，默认所有文件
    """
    root = Path(dir_path)
    return [
        FileInfo(
            path=str(p.relative_to(root)),
            size=p.stat().st_size,
            is_dir=p.is_dir()
        )
        for p in root.glob(pattern)
    ]

def read_file(file_path: str, max_chars: int = 10000) -> str:
    """读取文本文件内容。"""
    content = Path(file_path).read_text(encoding="utf-8")
    return content[:max_chars]  # 截断

def write_file(file_path: str, content: str) -> str:
    """写入文本文件。"""
    Path(file_path).write_text(content, encoding="utf-8")
    return f"已写入 {len(content)} 字符到 {file_path}"
```

#### 代码示例：SQL 查询工具（只读）

```python
import sqlite3
from typing import Literal

def query_sqlite(
    db_path: str,
    sql: str,
    limit: int = 100
) -> list[dict]:
    """查询 SQLite 数据库（只读）。

    Args:
        db_path: 数据库文件路径
        sql: SELECT 查询语句（只允许 SELECT）
        limit: 最多返回多少行
    """
    # 安全检查：只允许 SELECT
    if not sql.strip().lower().startswith("select"):
        raise ValueError("只允许 SELECT 查询")

    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql)
        rows = cursor.fetchmany(limit)
        return [dict(r) for r in rows]
```

#### 代码示例：REST API 工具

```python
import httpx

async def call_api(
    method: Literal["GET", "POST", "PUT", "DELETE"],
    url: str,
    headers: dict | None = None,
    body: dict | None = None
) -> dict:
    """调用 REST API。

    Args:
        method: HTTP 方法
        url: 完整 URL
        headers: 请求头（可选）
        body: 请求体（可选）
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.request(
            method, url, headers=headers or {}, json=body
        )
        r.raise_for_status()
        return {"status": r.status_code, "data": r.json()}
```

#### 今日任务

- [ ] 实现文件系统工具（list / read / write）
- [ ] 实现只读 SQL 工具（用一个测试数据库）
- [ ] 实现 REST API 工具
- [ ] 给每个工具写 Pydantic schema 和清晰的 description

#### 自检

- [ ] 我会写"只读"的 SQL 工具（防止 LLM 写入）
- [ ] 我能处理 API 工具的超时和错误
- [ ] 我的文件工具有路径长度限制（防爆 token）

---

### Day 6（周六）：构建"工具箱 Agent"（项目日）

**学习目标：** 把本周学的所有工具集成到一个 Agent 里。

#### 项目：万能工具箱 Agent

**功能：**
- 集成 5+ 类工具：搜索 / 浏览器 / 代码 / 文件 / SQL / API
- Agent 根据任务自动选择工具
- 工具失败有降级策略
- 完整的工具调用日志

**目录结构：**
```
phase-5/
└── toolbox-agent/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── tools/
    │   │   ├── __init__.py
    │   │   ├── search.py      # Tavily
    │   │   ├── browser.py     # Playwright / Browser Use
    │   │   ├── code.py        # 代码执行
    │   │   ├── files.py       # 文件系统
    │   │   └── api.py         # REST API
    │   ├── agent.py           # Agent 主逻辑
    │   └── main.py
    └── tests/
```

#### 今日任务

- [ ] 搭建项目骨架
- [ ] 集成本周学过的 5+ 工具
- [ ] 用 LangGraph 组装 Agent（让 LLM 在工具中选择）
- [ ] 测试 5 个复合任务（如"查天气并写文件"、"抓网页并分析"）
- [ ] 加上 LangSmith trace，观察工具选择行为
- [ ] 写 README

#### 预期产出

- 一个能调用 5+ 工具的 Agent 项目
- 5 个测试用例的 trace 截图
- 一份工具选择行为的观察笔记

---

### Day 7（周日）：工具生态复盘

**学习目标：** 沉淀工具设计的经验。

#### 今日任务

- [ ] 在 `notes/week-21-notes.md` 写一份《工具设计笔记》
- [ ] 包含：每种工具的适用场景、踩过的坑、最佳实践
- [ ] 在 [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md) 勾选 Week 3 完成项

#### 周末复盘问题

1. 工具数量越多越好吗？为什么？（提示：工具过多会怎样？）
2. Tavily / Playwright / Browser Use 三者，什么时候用哪个？
3. 你写的工具里，哪个 description 最难写？为什么？
4. 如果让你的 Agent 评估"工具调用得好不好"，你会怎么设计评测？

---

## Week 4 - Computer Use 与 MCP

**本周目标：** 理解前沿 Agent 形态，写一个完整的 MCP Server。

> **核心认知：** MCP 是 Anthropic 推出的工具协议标准，正在成为 Agent 生态的"USB-C 接口"。掌握 MCP = 抢占未来 1-2 年的生态红利。

### Day 1（周一）：Computer Use 概念

**学习目标：** 理解 Computer Use 范式，知道它和 Tool Use 的区别。

#### 核心概念

**Computer Use 是什么**
- Anthropic 在 Claude 3.5 Sonnet 推出的能力
- Agent 通过截图 + 鼠标键盘控制电脑
- 让 Agent 像人一样操作 GUI

**Computer Use vs Tool Use**

| 维度 | Tool Use | Computer Use |
|------|---------|--------------|
| 交互方式 | 调用 API | 截图 + 点击 |
| 适用场景 | 有 API 的服务 | 只有 GUI 的老应用 |
| 速度 | 快 | 慢（每步要截图） |
| 成本 | 低 | 高（Vision 调用） |
| 可靠性 | 高 | 中（UI 变化会失败） |

**当前生态**
- Anthropic Computer Use：原生支持
- OpenAI Operator：GPT-4 + Vision 模式
- 各种 RPA 厂商在跟进

#### 今日任务

- [ ] 阅读 [Anthropic Computer Use 文档](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)
- [ ] 看一个 Computer Use 的 demo 视频
- [ ] 笔记：Computer Use 适合哪 3 类场景？

#### 自检

- [ ] 我能解释 Computer Use 和 Tool Use 的区别
- [ ] 我知道 Computer Use 的成本和速度代价
- [ ] 我能列出 3 个适合 Computer Use 的场景

---

### Day 2（周二）：代码 Agent 架构剖析

**学习目标：** 理解主流代码 Agent 的架构，这是前端最容易共情的方向。

#### 核心概念

**主流代码 Agent 产品**

| 产品 | 特点 | 架构亮点 |
|------|------|---------|
| Claude Code | Anthropic 官方 CLI | 工具调用 + 文件系统 |
| Cursor | AI 编辑器 | Inline 补全 + Agent 模式 |
| Cline | 开源 VS Code 插件 | 工具协议 + 可扩展 |
| Continue | 开源 AI 编程插件 | RAG + Agent |
| OpenDevin / SWE-Agent | 开源自主编程 | 沙箱 + 长任务 |

**代码 Agent 的核心循环**
```
1. 读取用户指令
2. 读取当前代码上下文
3. 决策：编辑 / 搜索 / 运行 / 问用户
4. 执行工具
5. 观察结果
6. 循环 2-5 直到任务完成
```

#### 今日任务

- [ ] 阅读一篇代码 Agent 架构分析文章（推荐 [Cline 源码](https://github.com/cline/cline)）
- [ ] 在笔记里画出 Cline 的工具调用流程图
- [ ] 思考：如果你要做一个"前端代码 Agent"，它需要哪些工具？

#### 自检

- [ ] 我能解释代码 Agent 的核心循环
- [ ] 我能列出代码 Agent 至少 5 个必备工具
- [ ] 我理解为什么代码 Agent 多用沙箱执行

---

### Day 3（周三）：MCP 协议入门

**学习目标：** 理解 MCP 是什么、为什么重要、它的架构。

#### 核心概念

**MCP 是什么**

Model Context Protocol（模型上下文协议）—— Anthropic 提出的开放标准，解决"每个 Agent 框架工具不互通"的问题。

**类比：USB-C 接口**
- 以前：每个手机厂商用自己的充电口（每个 Agent 框架有自己的工具）
- 现在：统一用 USB-C（所有框架共用 MCP 工具）

**MCP 的核心价值**
- 工具复用：写一次，所有 MCP Client 都能用
- 生态共享：Anthropic / OpenAI / LangChain 都在接入
- 标准化：工具定义有统一规范

**MCP 架构**
```
Agent（MCP Client，如 Claude Desktop）
    ↓
MCP Protocol（JSON-RPC）
    ↓
MCP Server（你写的，暴露工具）
    ↓
实际服务（Notion / GitHub / DB / 任何 API）
```

**MCP 三类能力**
- **Tools：** 可被 Agent 调用的函数（最常用）
- **Resources：** 可被 Agent 读取的数据（如文件内容）
- **Prompts：** 预定义的 Prompt 模板

#### 今日任务

- [ ] 阅读 [MCP 官方文档](https://modelcontextprotocol.io/) 的 Introduction 和 Architecture
- [ ] 看 [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers) 里有哪些现成 Server
- [ ] 笔记：MCP 解决了什么问题？为什么是"协议"而不是"库"？

#### 自检

- [ ] 我能解释 MCP 是什么，用什么类比介绍
- [ ] 我能画出 MCP 的架构图
- [ ] 我知道 MCP 的三类能力（Tools / Resources / Prompts）

---

### Day 4（周四）：MCP Server Python SDK 实操

**学习目标：** 跑通第一个 MCP Server，理解它的代码结构。

#### 核心概念

**MCP Python SDK 核心组件**
- `Server`：MCP Server 实例
- `@server.tool()` 装饰器：定义工具
- `@server.resource()` 装饰器：定义资源
- Stdio / SSE 传输：Server 和 Client 之间的通信方式

#### 代码示例：最小 MCP Server

```python
# uv add "mcp[cli]"

from mcp.server.fastmcp import FastMCP

# 1. 创建 Server
mcp = FastMCP("my-first-server")

# 2. 定义工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """两个整数相加。

    Args:
        a: 第一个数
        b: 第二个数
    """
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """生成问候语。

    Args:
        name: 要问候的人的名字
    """
    return f"你好，{name}！"

# 3. 定义资源（可选）
@mcp.resource("config://app")
def get_config() -> str:
    """返回应用配置。"""
    import json
    return json.dumps({"version": "1.0", "name": "demo"})

# 4. 启动
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

#### 如何在 Claude Desktop 测试

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）：

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/your/project",
        "run",
        "server.py"
      ]
    }
  }
}
```

重启 Claude Desktop，应该能看到工具图标亮起。

#### 今日任务

- [ ] 安装 MCP Python SDK：`uv add "mcp[cli]"`
- [ ] 跑通上面的 Hello World Server
- [ ] 接入 Claude Desktop 测试
- [ ] 让 Claude 调用你的 `add` 和 `greet` 工具

#### 自检

- [ ] 我能跑通最小 MCP Server
- [ ] 我能把它接入 Claude Desktop
- [ ] 我能解释 stdio 传输的工作方式

---

### Day 5（周五）：写一个实用 MCP Server（设计 + 第一个工具）

**学习目标：** 选一个你常用的服务，开始写实用 MCP Server。

#### 选型建议（选一个你熟悉的）

- **Notion：** 查询 / 创建页面（推荐，文档场景多）
- **GitHub：** 查 issue / PR / 仓库
- **Linear / Jira：** 查任务
- **数据库：** 查业务数据
- **本地文件：** 搜索 / 读取（简单易实现）

#### 项目：GitHub MCP Server（示例）

```python
# uv add "mcp[cli]" httpx

from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("github-server")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

async def github_request(url: str) -> dict:
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def list_my_repos(limit: int = 10) -> list[dict]:
    """列出我自己的 GitHub 仓库。

    Args:
        limit: 最多返回多少个，默认 10
    """
    data = await github_request(
        f"https://api.github.com/user/repos?per_page={limit}&sort=updated"
    )
    return [
        {"name": r["name"], "stars": r["stargazers_count"], "url": r["html_url"]}
        for r in data
    ]

@mcp.tool()
async def get_repo_issues(owner: str, repo: str, state: str = "open") -> list[dict]:
    """获取某个仓库的 issue 列表。

    Args:
        owner: 仓库所有者，如 'langchain-ai'
        repo: 仓库名，如 'langgraph'
        state: 'open' / 'closed' / 'all'，默认 'open'
    """
    data = await github_request(
        f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=20"
    )
    return [
        {"number": i["number"], "title": i["title"], "url": i["html_url"]}
        for i in data
    ]
```

#### 今日任务

- [ ] 选一个服务（推荐 GitHub 或 Notion）
- [ ] 拿到对应 API Token
- [ ] 实现第 1 个工具（列表查询类最简单）
- [ ] 在 Claude Desktop 测试

#### 自检

- [ ] 我的 MCP Server 能跑通
- [ ] 第一个工具能被 Claude Desktop 正确调用
- [ ] 错误信息对 LLM 友好（如 401 时告诉它"Token 失效"）

---

### Day 6（周六）：完善 MCP Server（项目日）

**学习目标：** 把 MCP Server 做到"可发布"水平。

#### 今日任务

- [ ] 补齐 3+ 工具（列表 / 查询 / 创建）
- [ ] 加上完善的错误处理（API 失败、Token 失效、限流）
- [ ] 写 Pydantic schema 严格控制输入输出
- [ ] 写 README，说明如何配置
- [ ] 在 Claude Desktop 实际使用 5 次，记录体验

**目录结构示例：**
```
phase-5/
└── my-mcp-server/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── server.py         # 入口
    │   ├── tools/
    │   │   ├── repos.py
    │   │   ├── issues.py
    │   │   └── pulls.py
    │   └── github_client.py  # API 封装
    └── .env.example
```

#### 加分项（可选）

- [ ] 发布到 [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers)
- [ ] 写一篇介绍文章
- [ ] 让朋友 / 同事试用并收集反馈

#### 预期产出

- 一个完整可用的 MCP Server
- 至少 3 个工具
- 一份清晰的 README
- 在 Claude Desktop 中的实际使用截图

---

### Day 7（周日）：MCP 生态复盘

**学习目标：** 沉淀 MCP 的设计与使用经验。

#### 今日任务

- [ ] 在 `notes/week-22-notes.md` 写一份《MCP 实践笔记》
- [ ] 包含：MCP 是什么 / 怎么写 Server / 怎么接入 Client / 踩过的坑
- [ ] 在 [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md) 勾选 Week 4 完成项

#### 周末复盘问题

1. MCP 相比直接写 LangChain Tool，最大的优势是什么？
2. 你写的 MCP Server，能用在哪些 Client（Claude Desktop / Cursor / Cline）？
3. 如果让你给团队推广 MCP，你会怎么介绍它的价值？
4. MCP 目前的局限是什么？（提示：调试、部署、版本管理等）

---

## Week 5 - 整合项目：自动化研究团队

**本周目标：** 综合应用 Multi-Agent + 工具生态，交付作品集 #2 完整版。

> **核心认知：** 这是你第 5 阶段的"期末考试"。所有学过的东西（LangGraph / Multi-Agent / 工具生态 / MCP / 评测）都要用上。

### Day 1（周一）：项目设计 + 架构图

**学习目标：** 做好充分的设计，避免后期返工。

#### 项目：自动化研究团队

**角色设计（6 个 Agent）**
- **Planner Agent：** 拆解研究问题，制定计划
- **Researcher Agent × N：** 并行搜索多个来源
- **Writer Agent：** 综合信息，起草报告
- **Reviewer Agent：** 审校内容，提出修改意见
- **Critic Agent：** 故意挑刺，防止信息茧房
- **Editor Agent：** 最终润色定稿

**技术架构**
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

#### 今日任务

- [ ] 写一份 `DESIGN.md`，包含：
  - 角色定义（每个 Agent 的 role / goal / backstory）
  - 状态机设计（State 字段）
  - 工具清单（每个 Agent 用哪些工具）
  - 评测方案
- [ ] 用 Excalidraw 画出完整架构图
- [ ] 列出技术风险点和应对方案

#### 自检

- [ ] 我能说清楚每个 Agent 的职责边界（不重叠）
- [ ] 我画出了完整的状态机
- [ ] 我有明确的评测方案

---

### Day 2（周二）：Planner + Researcher 实现

**学习目标：** 实现核心的研究流水线。

#### 代码示例：并行 Researcher

```python
import asyncio
from typing import Annotated
from langgraph.graph import StateGraph, START, END

class ResearchState(TypedDict):
    question: str
    plan: list[str]              # Planner 输出的子问题列表
    research_results: Annotated[list, add]  # 各 Researcher 的结果（累加）
    draft: str
    review_comments: list[str]
    final_report: str
    next: str

def planner(state: ResearchState) -> dict:
    """把大问题拆成 3-5 个子问题。"""
    prompt = f"""你是一个研究规划师。
    把以下研究问题拆成 3-5 个独立的子问题，便于并行研究。
    只输出子问题列表，用 JSON 数组。

    研究问题：{state["question"]}
    """
    # 用 structured output 拿到 list[str]
    plan = planner_llm.invoke(prompt)
    return {"plan": plan}

async def researcher(state: ResearchState, sub_question: str) -> dict:
    """单个 Researcher，处理一个子问题。"""
    # 用 Tavily / Playwright 等工具
    result = await search_and_summarize(sub_question)
    return {"research_results": [result]}

async def parallel_research(state: ResearchState) -> dict:
    """并行调用多个 Researcher。"""
    tasks = [researcher(state, q) for q in state["plan"]]
    results = await asyncio.gather(*tasks)
    # 合并所有结果
    merged = {"research_results": []}
    for r in results:
        merged["research_results"].extend(r["research_results"])
    return merged
```

#### 今日任务

- [ ] 初始化项目：`uv init research-team`
- [ ] 实现 Planner（带 structured output）
- [ ] 实现并行 Researcher（用 asyncio.gather）
- [ ] 接入 Tavily 搜索工具
- [ ] 测试：输入一个问题，观察子问题拆解和并行研究

#### 自检

- [ ] Planner 能输出结构化的子问题列表
- [ ] 多个 Researcher 能并行执行
- [ ] 研究结果能正确累加到 state

---

### Day 3（周三）：Writer + Reviewer + Critic 实现

**学习目标：** 实现核心的"起草 → 审校 → 对抗"循环。

#### 代码示例：对抗循环

```python
def writer(state: ResearchState) -> dict:
    """根据研究结果起草报告。"""
    prompt = f"""你是一个专业写手。
    基于以下研究结果，写一份结构清晰的研究报告（Markdown）。

    研究问题：{state["question"]}
    研究结果：{state["research_results"]}

    输出格式：
    # 报告标题
    ## 摘要
    ## 主要发现（3-5 点）
    ## 详细分析
    ## 结论
    ## 参考资料
    """
    draft = writer_llm.invoke(prompt)
    return {"draft": draft}

def reviewer(state: ResearchState) -> dict:
    """审校报告，找出事实错误和逻辑漏洞。"""
    prompt = f"""你是一个严苛的审稿人。
    检查以下报告的事实准确性、逻辑严密性、结构完整性。

    报告：{state["draft"]}

    输出 JSON：
    {{
      "pass": true/false,
      "issues": ["问题1", "问题2"],
      "suggestions": ["建议1", "建议2"]
    }}
    """
    review = reviewer_llm.invoke(prompt)
    return {"review_comments": [review]}

def critic(state: ResearchState) -> dict:
    """故意挑刺，提出反对意见。"""
    prompt = f"""你是一个魔鬼辩护人（Devil's Advocate）。
    站在对立面，尽可能找出以下报告的问题、偏见、缺失。

    报告：{state["draft"]}

    列出至少 3 个反对观点。
    """
    critique = critic_llm.invoke(prompt)
    return {"review_comments": [critique]}

def should_revise(state: ResearchState) -> str:
    """决策：是否需要修改？"""
    # 如果 reviewer 不通过或 critic 有强反对意见，回到 writer
    if any("pass: false" in c.lower() for c in state["review_comments"]):
        return "writer"
    return "editor"
```

#### 今日任务

- [ ] 实现 Writer（带清晰的输出格式）
- [ ] 实现 Reviewer（带 pass/fail 判断）
- [ ] 实现 Critic（强制提反对意见）
- [ ] 用条件边实现"起草 → 审校 → 修改"循环
- [ ] 测试：观察对抗循环如何提升质量

#### 自检

- [ ] Writer 能输出结构化报告
- [ ] Reviewer 能给出明确的 pass/fail
- [ ] Critic 能提出有价值的反对意见
- [ ] 循环不超过 3 轮（防止无限修改）

---

### Day 4（周四）：Editor + 完整图组装

**学习目标：** 把所有 Agent 组装成完整的图，跑通端到端流程。

#### 代码示例：完整图

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(ResearchState)

# 添加节点
builder.add_node("planner", planner)
builder.add_node("researcher", parallel_research)
builder.add_node("writer", writer)
builder.add_node("reviewer", reviewer)
builder.add_node("critic", critic)
builder.add_node("editor", editor)

# 固定边
builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")

# Reviewer 和 Critic 并行
builder.add_edge("writer", "reviewer")
builder.add_edge("writer", "critic")

# 条件边：审校后决定下一步
def after_review(state: ResearchState) -> str:
    if revision_count(state) >= 3:
        return "editor"  # 防止无限循环
    return should_revise(state)

builder.add_conditional_edges("reviewer", after_review)
builder.add_edge("critic", "reviewer")  # critic 的意见汇总到 reviewer
builder.add_edge("editor", END)

graph = builder.compile()

# 运行
result = graph.invoke({"question": "MCP 协议会如何改变 Agent 生态？"})
print(result["final_report"])
```

#### 今日任务

- [ ] 实现最终 Editor（润色 + 统一格式）
- [ ] 组装完整图
- [ ] 加上 `revision_count` 防止无限循环
- [ ] 端到端跑通 3 个测试问题
- [ ] 用 LangSmith 看完整 trace

#### 自检

- [ ] 完整流程能跑通
- [ ] 每个节点的输入输出都能在 trace 里看到
- [ ] 循环有终止保护（max_turns / revision_count）

---

### Day 5（周五）：评测集 + 成本监控

**学习目标：** 给项目建立评测体系，这是 Multi-Agent 的命脉。

#### 代码示例：评测集

```python
# eval_dataset.py
EVAL_QUESTIONS = [
    {
        "id": "q1",
        "question": "MCP 协议是什么，它的核心价值是什么？",
        "expected_points": [
            "Anthropic 提出",
            "工具协议标准",
            "解决工具不互通问题",
        ],
    },
    {
        "id": "q2",
        "question": "LangGraph 和 CrewAI 各自的优劣是什么？",
        "expected_points": [
            "LangGraph 控制力强但代码量大",
            "CrewAI 易用但抽象重",
            "适用场景不同",
        ],
    },
    # ... 至少 20 个
]

# LLM-as-Judge 评测
from langchain_openai import ChatOpenAI

judge_llm = ChatOpenAI(model="gpt-5-latest", temperature=0)

JUDGE_PROMPT = """你是一个研究报告评测专家。

请根据以下标准给报告打分（1-10）：
- 准确性（事实是否正确）
- 完整性（是否覆盖关键点）
- 结构性（逻辑是否清晰）
- 可读性（语言是否流畅）

研究问题：{question}
报告内容：{report}
期望覆盖的关键点：{expected_points}

输出 JSON：
{{
  "scores": {{"accuracy": 8, "completeness": 7, "structure": 9, "readability": 8}},
  "overall": 8.0,
  "issues": ["问题1", "问题2"]
}}
"""

async def evaluate(report: str, question: dict) -> dict:
    result = await judge_llm.ainvoke(
        JUDGE_PROMPT.format(
            question=question["question"],
            report=report,
            expected_points=question["expected_points"],
        )
    )
    return parse_json(result.content)
```

#### 代码示例：成本监控

```python
import tiktoken
from langchain.callbacks import get_openai_callback

def run_with_cost(question: str) -> dict:
    """运行研究团队并统计成本。"""
    with get_openai_callback() as cb:
        result = graph.invoke({"question": question})
        cost_info = {
            "total_tokens": cb.total_tokens,
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_cost_usd": cb.total_cost,
        }
    return {"report": result["final_report"], "cost": cost_info}

# 跑完记录到日志
import json
from pathlib import Path

def log_eval(question_id: str, result: dict, eval_result: dict):
    log = {
        "question_id": question_id,
        "cost": result["cost"],
        "scores": eval_result["scores"],
        "overall": eval_result["overall"],
    }
    Path(f"logs/{question_id}.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2)
    )
```

#### 今日任务

- [ ] 设计 20+ 个评测问题（含期望覆盖的关键点）
- [ ] 实现 LLM-as-Judge 评测
- [ ] 加上成本监控（每个 Agent / 每次研究的 token 消耗）
- [ ] 把评测结果保存到 `logs/`

#### 自检

- [ ] 我有至少 20 个评测问题
- [ ] LLM-as-Judge 能给出结构化的评分
- [ ] 我能知道每次研究的成本（美元 + token）

---

### Day 6（周六）：对比报告 + README（项目日）

**学习目标：** 完成单 Agent vs Multi-Agent 的对比报告，把项目打磨到作品集水平。

#### 对比实验

用你 Phase 4 的单 Agent 研究助手，跑相同的 20 个评测问题；再用本周的 Multi-Agent 团队跑同样的问题。对比：

| 维度 | 单 Agent | Multi-Agent | 差异 |
|------|---------|-------------|------|
| 平均评分 | ? | ? | ? |
| 平均成本 | ? | ? | ? |
| 平均耗时 | ? | ? | ? |
| 报告字数 | ? | ? | ? |
| 信息覆盖度 | ? | ? | ? |

#### 今日任务

- [ ] 跑完 20 个评测问题（单 Agent + Multi-Agent）
- [ ] 生成对比表格
- [ ] 写一份 `COMPARISON.md`，分析数据背后的结论
- [ ] 写项目 `README.md`：
  - 项目介绍（一句话）
  - 架构图
  - 如何运行
  - 评测结果摘要
  - 示例报告链接
- [ ] 挑出 5 份最佳报告放到 `examples/`

#### 自检

- [ ] 对比报告有数据支撑（不是凭感觉）
- [ ] README 能让陌生人在 5 分钟内跑起来项目
- [ ] 有 5 份以上真实研究报告示例

---

### Day 7（周日）：发布 + 阶段复盘

**学习目标：** 把项目发布到 GitHub，完成第 5 阶段的总复盘。

#### 今日任务

- [ ] 把项目发布到 GitHub（公开仓库）
- [ ] 在你的社交平台 / 群里分享（获取反馈）
- [ ] 写一份阶段复盘 `notes/phase-5-summary.md`：
  - 学到的最重要的 3 件事
  - 遇到的最大困难
  - 下一步（第 6 阶段）的学习重点
- [ ] 在 [phase-5-multi-agent-tool-ecosystem.md](./phase-5-multi-agent-tool-ecosystem.md) 勾选所有完成项

#### 周末复盘问题

1. Multi-Agent 系统相比单 Agent，带来的收益是否值得 3 倍复杂度？
2. 你的"研究团队"里，哪个 Agent 价值最大？哪个可有可无？
3. Critic（魔鬼辩护人）真的能提升质量吗？还是有副作用？
4. 如果让你重做这个项目，你会怎么简化？
5. 第 5 阶段最大的认知冲击是什么？

---

## 常见卡点速查表

| 卡点 | 解决方案 |
|------|---------|
| Agent 互相扯皮，谁都不干活 | 明确角色边界，加 Planner 统筹，减少 Agent 数量 |
| 成本爆炸（一次研究几美元） | 加 `max_turns`，辅助 Agent 用便宜模型（gpt-5-latest） |
| 调试困难，不知道哪一步出错 | 必须接 LangSmith trace，每个节点的输入输出可观测 |
| LangGraph 条件边不生效 | 检查 `add_conditional_edges` 的返回值是否和节点名匹配 |
| State 字段被覆盖而不是累加 | 用 `Annotated[list, add]` 让 LangGraph 自动累加 |
| CrewAI Agent 不调工具 | 检查 `tools=[...]` 是否正确传入，工具 description 是否清晰 |
| AutoGen 代码执行危险 | 用 Docker 或 E2B 沙箱，不要在本地直接跑 |
| Playwright 抓不到动态内容 | 用 `wait_until="networkidle"` 或显式 `await page.wait_for_selector(...)` |
| Browser Use 找不到元素 | 提供更清晰的任务描述，或换用支持 Vision 的模型（如 GPT-5、Claude Sonnet 4.5） |
| MCP Server 在 Claude Desktop 不显示 | 检查 `claude_desktop_config.json` 的绝对路径，重启 Claude Desktop |
| MCP 工具调用超时 | 检查 stdio 通信是否被阻塞，避免在工具里写死循环 |
| Multi-Agent 效果不如单 Agent | 可能就不该用 Multi-Agent，回归单 Agent 是合理的决策 |
| Reviewer / Critic 无限循环 | 加 `revision_count` 上限（如 3 轮），超了直接进 Editor |
| LLM 输出 JSON 格式错误 | 用 `with_structured_output()` 或 Pydantic + 重试机制 |

## 推荐速查资源

- [LangGraph Multi-Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)
- [CrewAI 官方文档](https://docs.crewai.com/)
- [AutoGen 官方文档](https://microsoft.github.io/autogen/)
- [LangSmith trace 文档](https://docs.smith.langchain.com/)
- [Tavily 官网](https://tavily.com/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [E2B 官网](https://e2b.dev/)
- [Anthropic Computer Use](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers)

## 第 5 阶段完成标准

第 5 阶段结束时，你应该能：

- [ ] 理解 4 种 Multi-Agent 架构模式（Supervisor / Hierarchical / Network / Sequential）
- [ ] 能用 LangGraph 实现 Supervisor 模式
- [ ] 能用 CrewAI 实现 Multi-Agent 协作
- [ ] 能用 AutoGen 实现 Group Chat
- [ ] 能集成 5+ 类工具（搜索 / 浏览器 / 代码 / 文件 / API）
- [ ] 理解 Computer Use 和代码 Agent 架构
- [ ] 理解 MCP 协议的价值和架构
- [ ] 写过至少 1 个完整的 MCP Server（3+ 工具）
- [ ] 自动化研究团队可运行、有评测（20+ 问题）
- [ ] 有单 Agent vs Multi-Agent 的数据对比报告
- [ ] 作品集 #2 完整版已发布到 GitHub
- [ ] 能清晰回答："什么时候该用 Multi-Agent，什么时候不该用"

### 核心认知（带走这 6 句话）

**Multi-Agent 设计的三大陷阱：**

1. **过度工程** — 简单任务上 Multi-Agent，徒增复杂度
2. **角色边界不清** — Agent 之间职责重叠，互相干扰
3. **没有评测** — Multi-Agent 没有评测就是黑盒中的黑盒

**Multi-Agent 设计的三大原则：**

1. **先单 Agent，再 Multi** — 遇到瓶颈才升级
2. **角色清晰** — 每个 Agent 职责明确，不重叠
3. **可观测性** — 每个 Agent 的输入输出都可追溯

---

**准备好了就进入第 6 阶段：** [评测 + 部署 + 作品集](./phase-6-eval-deploy-portfolio.md)�
