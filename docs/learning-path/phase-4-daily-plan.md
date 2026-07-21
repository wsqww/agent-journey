# 第 4 阶段每日计划：Agent 核心架构 + LangGraph

> **周期：** 5 周（Phase 4 / Week 1-5，独立编号，非全局周号）
> **目标：** 掌握 Agent 的核心抽象——状态机、循环决策、记忆系统，做出研究助手 Agent
> **每日投入：** 约 1-1.5 小时（工作日）/ 2-3 小时（周末）
> **关键产出物：** 研究助手 Agent（作品集项目 #2 雏形）

## 学习方法

1. **Agent = LLM 驱动的状态机** — 这是本阶段最核心的心智模型，刻进脑子
2. **用 React 思维学 LangGraph** — `useState` / `useReducer` 和 LangGraph State 是同构的
3. **先手写后用框架** — Week 1 不用框架纯手写，理解原理后再学 LangGraph
4. **每天必须敲代码** — 看懂 ≠ 会写，每个示例都要跑一遍
5. **有 trace 才有调试** — 从 Week 2 开始接入 LangSmith，养成可观测性习惯

## 进度追踪

- [ ] Week 1 - Agent 基础：手写 ReAct Agent
- [ ] Week 2 - LangChain Agent 生态
- [ ] Week 3 - LangGraph 核心（重点周）
- [ ] Week 4 - Agent 记忆系统
- [ ] Week 5 - 整合项目：研究助手 Agent
- [ ] 阶段产出物：研究助手 Agent 雏形可运行

---

## Week 1 - Agent 基础：手写 ReAct Agent

> **本周目标：** 不用任何框架，纯 Python 手写一个 100 行以内的 ReAct Agent
> **核心心智模型：** Agent 是一个"会自己决定下一步做什么"的 while 循环
> **产出物：** 可运行的 ReAct Agent，支持 3-5 个工具，有完整日志

### Day 1（周一）：Agent 的本质 = 状态机

**学习目标：** 建立"Agent 是状态机"的心智模型，把 React 状态管理经验迁移过来。

#### 核心概念

**关键认知转变：**
- Agent ≠ 更智能的聊天机器人
- Agent = **LLM 驱动的状态机**
- 前端的 React 组件就是"会自己决定下一步渲染什么的状态机"，Agent 完全是这个思路

**思维迁移对照表：**

| React 概念 | Agent 概念 | 说明 |
|-----------|-----------|------|
| `useState` | Agent State | 维护当前状态 |
| `useReducer` | Agent Loop | 根据当前状态决定下一步 |
| `dispatch(action)` | Tool Call | 触发状态变更 |
| `useEffect` 依赖 | Condition | 决定何时执行 |
| Render 函数 | LLM 决策 | 根据 state 产出输出 |

**Agent 的 5 个核心要素：**
- **感知（Perception）：** 接收用户输入、工具返回
- **思考（Reasoning）：** LLM 决定下一步
- **行动（Action）：** 调用工具或返回结果
- **观察（Observation）：** 收集行动结果
- **状态（State）：** 维护上下文

**ReAct 模式：** Reasoning + Acting，让 LLM 在"思考"和"行动"之间交替

#### 代码示例：状态机的最小骨架

```python
from dataclasses import dataclass, field
from typing import Any

# React 开发者眼里的 Agent State：就像一个 useReducer 的 state 对象
@dataclass
class AgentState:
    """Agent 的运行时状态，类比 React 的 state"""
    messages: list[dict] = field(default_factory=list)  # 对话历史
    current_step: int = 0                                # 当前步数
    max_steps: int = 10                                  # 最大步数
    task_complete: bool = False                          # 是否完成
    intermediate_results: list[str] = field(default_factory=list)  # 中间结果

# Agent Loop 的骨架，类比 React 的渲染循环
def agent_loop(state: AgentState, llm_decision_fn, execute_action_fn):
    """Agent 主循环：while not done, think and act"""
    while not state.task_complete and state.current_step < state.max_steps:
        # 1. 感知 + 思考：让 LLM 决定下一步
        thought, action = llm_decision_fn(state)

        # 2. 行动：执行工具
        observation = execute_action_fn(action)

        # 3. 更新状态（类似 setState）
        state.messages.append({"role": "assistant", "content": thought})
        state.intermediate_results.append(observation)
        state.current_step += 1

        # 4. 检查是否完成
        if action.get("type") == "finish":
            state.task_complete = True

    return state
```

#### 今日任务

- [ ] 阅读 [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)（必读）
- [ ] 在 `notes/week-1-notes.md` 写下你对"Agent = 状态机"的理解
- [ ] 把上面的 `AgentState` 和 `agent_loop` 骨架敲一遍跑通
- [ ] 列出你做 React 时用过的状态管理方案，思考它们和 Agent State 的对应关系

#### 自检

- [ ] 我能用一句话解释"为什么 Agent 是状态机"
- [ ] 我能说出 Agent 的 5 个核心要素
- [ ] 我理解 React 的 `useReducer` 和 Agent Loop 是同构的

---

### Day 2（周二）：LLM 调用 + 工具定义

**学习目标：** 掌握直接用 SDK 调用 LLM，定义可被 Agent 调用的工具。

#### 核心概念

**不用框架，纯 SDK：** 理解底层发生了什么，后面学框架才不会迷茫。

**工具的三要素：**
- **name：** 唯一标识（类似 API endpoint）
- **description：** 告诉 LLM 什么时候用这个工具（至关重要）
- **execute：** 实际执行函数

**前端类比：** 工具就像你暴露给后端的 RPC 接口，`description` 是接口文档，LLM 是调用方。

#### 代码示例

```python
import anthropic
import json
from typing import Callable, Any

client = anthropic.Anthropic()  # 自动读取 ANTHROPIC_API_KEY

# 定义工具（类比前端定义 API handler）
def search_web(query: str) -> str:
    """模拟网页搜索（真实项目用 Tavily / SerpAPI）"""
    return f"搜索结果：关于「{query}」的 3 条信息..."

def calculate(expression: str) -> str:
    """安全计算数学表达式（AST 解析，禁止 eval()）。"""
    import ast, operator as _op
    _OPS = {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul, ast.Div: _op.truediv, ast.USub: _op.neg}
    def _walk(n):
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.BinOp): return _OPS[type(n.op)](_walk(n.left), _walk(n.right))
        if isinstance(n, ast.UnaryOp): return _OPS[type(n.op)](_walk(n.operand))
        raise ValueError
    try:
        return str(_walk(ast.parse(expression.strip(), mode="eval").body))
    except Exception as e:
        return f"计算失败：{e}"

def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 工具注册表：name -> (function, description)
TOOLS: dict[str, tuple[Callable, str]] = {
    "search_web": (search_web, "搜索互联网获取信息。输入：搜索关键词"),
    "calculate": (calculate, "执行数学计算。输入：数学表达式，如 2+3*4"),
    "get_current_time": (get_current_time, "获取当前日期和时间。无需输入"),
}

# 把工具转成 Claude 能理解的 schema
def get_tool_schemas() -> list[dict]:
    return [
        {
            "name": "search_web",
            "description": "搜索互联网获取信息",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "calculate",
            "description": "执行数学计算",
            "input_schema": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
        {
            "name": "get_current_time",
            "description": "获取当前时间",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

# 调用 LLM
def call_llm(messages: list[dict]) -> anthropic.types.Message:
    return client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=get_tool_schemas(),
        messages=messages,
    )
```

#### 今日任务

- [ ] 确保 `ANTHROPIC_API_KEY` 已设置（或改用 OpenAI SDK）
- [ ] 定义 3 个工具，必须包含一个"真实联网搜索"（用 Tavily 或 DuckDuckGo）
- [ ] 跑通"单次工具调用"：让 LLM 决定调哪个工具、传什么参数
- [ ] 打印 LLM 的 raw response，观察 `tool_use` 结构

#### 自检

- [ ] 我能解释工具 `description` 为什么比函数名更重要
- [ ] 我理解 Claude 的 `tool_use` 和 `tool_result` 消息结构
- [ ] 我能定义带嵌套参数的工具 schema

---

### Day 3（周三）：ReAct Prompt 设计

**学习目标：** 设计高质量的 ReAct Prompt，让 LLM 稳定输出 Thought / Action / Observation 格式。

#### 核心概念

**两种 ReAct 实现路线：**
1. **Prompt-based：** 纯文本提示，LLM 输出 "Thought: ... Action: ..."（原版 ReAct 论文方式）
2. **Tool-use-based：** 用 LLM 原生的 tool calling 能力（推荐，更稳定）

**现代 ReAct 的最佳实践：** 用原生 tool calling，因为：
- LLM 训练时专门优化过 tool calling
- 不需要解析自然语言（避免解析错误）
- 结构化输出更可靠

**Prompt 的核心要素：**
- **角色定义：** 你是谁，能做什么
- **任务约束：** 一次只调一个工具 / 可以多步思考
- **输出格式：** 明确告诉 LLM 怎么表达"我完成了"
- **Few-shot 示例：** 给 1-2 个完整轨迹（trajectory）参考

#### 代码示例：高质量 System Prompt

```python
SYSTEM_PROMPT = """你是一个能调用工具的 AI 助手，通过 ReAct（Reasoning + Acting）模式解决用户问题。

## 工作流程
你可以多步骤地解决问题：
1. 思考：分析当前状态，决定下一步
2. 行动：调用工具获取信息
3. 观察：查看工具返回结果
4. 重复 1-3 直到能给出最终答案

## 重要约束
- 一次只调用一个工具
- 如果工具返回错误，分析原因后换一种方式重试
- 最多使用 10 步，避免无限循环
- 当你有足够信息回答时，直接输出最终答案（不要调用工具）

## 可用工具
{tools_description}

## 回答要求
- 最终答案要清晰、结构化
- 引用工具返回的关键信息
- 如果信息不足，明确说明哪些部分不确定
"""

def build_system_prompt() -> str:
    tools_desc = "\n".join(
        f"- {name}: {desc}" for name, (_, desc) in TOOLS.items()
    )
    return SYSTEM_PROMPT.format(tools_description=tools_desc)
```

**前端类比：** System Prompt 就像组件的 Props 类型 + 默认行为说明，决定了 LLM 的"接口契约"。

#### 今日任务

- [ ] 写一个完整的 System Prompt（不少于 200 字）
- [ ] 测试同一个问题，对比"有 Prompt" vs "无 Prompt" 的工具调用稳定性
- [ ] 故意问一个需要多步的问题（如"今年端午节的星期几？距离今天还有多少天？"）
- [ ] 把 Prompt 存到单独的 `prompts.py` 文件

#### 自检

- [ ] 我的 Prompt 明确了"什么时候调工具、什么时候直接回答"
- [ ] 我能用一个例子解释"Thought → Action → Observation"的完整轨迹
- [ ] 我理解为什么原生 tool calling 比纯文本解析更稳定

---

### Day 4（周四）：手写 Agent Loop 核心代码

**学习目标：** 实现完整的 ReAct Agent Loop，这是本周的核心产出。

#### 核心概念

**Agent Loop 的核心步骤：**
```
1. 构造 messages（system + history + user）
2. 调用 LLM
3. 检查 LLM 返回：
   - 如果是 tool_use → 执行工具 → 把结果加回 messages → 回到第 1 步
   - 如果是最终回答 → 结束循环
4. 超过 max_steps → 强制结束
```

**关键细节：**
- 消息历史的拼接（`assistant` 消息和 `user` 的 `tool_result` 要成对）
- 异常处理（工具失败、LLM 超时）
- 每一步都要记录日志

#### 代码示例：100 行以内的 ReAct Agent

```python
import anthropic
import json
from typing import Callable

client = anthropic.Anthropic()

class SimpleReActAgent:
    """手写 ReAct Agent，目标：100 行以内核心逻辑"""

    def __init__(self, tools: dict, system_prompt: str, max_steps: int = 10):
        self.tools = tools  # name -> (fn, description)
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.history: list[dict] = []
        self.trace: list[dict] = []  # 每一步的日志

    def _get_tool_schemas(self) -> list[dict]:
        schemas = []
        for name, (fn, desc) in self.tools.items():
            schemas.append({
                "name": name,
                "description": desc,
                "input_schema": {"type": "object", "properties": {}},
            })
        return schemas

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """执行工具，带异常处理"""
        if tool_name not in self.tools:
            return f"错误：未知工具 {tool_name}"
        try:
            fn, _ = self.tools[tool_name]
            result = fn(**tool_input)
            return str(result)
        except Exception as e:
            return f"工具执行失败：{type(e).__name__}: {e}"

    def _log_step(self, step: int, thought: str, action: str, observation: str):
        """记录每一步（类比 React DevTools 的状态追踪）"""
        self.trace.append({
            "step": step,
            "thought": thought,
            "action": action,
            "observation": observation,
        })
        print(f"\n--- Step {step} ---")
        print(f"Thought: {thought[:100]}...")
        print(f"Action: {action}")
        print(f"Observation: {observation[:100]}...")

    def run(self, user_input: str) -> str:
        """Agent 主循环"""
        self.history.append({"role": "user", "content": user_input})

        for step in range(1, self.max_steps + 1):
            # 1. 调用 LLM
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=self.system_prompt,
                tools=self._get_tool_schemas(),
                messages=self.history,
            )

            # 2. 处理响应
            if response.stop_reason == "end_turn":
                # LLM 给出最终答案
                final_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                self.history.append({"role": "assistant", "content": response.content})
                self._log_step(step, final_text, "FINISH", "")
                return final_text

            if response.stop_reason == "tool_use":
                # LLM 要调工具
                self.history.append({"role": "assistant", "content": response.content})

                # 处理所有 tool_use（通常只有一个）
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        observation = self._execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": observation,
                        })
                        self._log_step(
                            step,
                            thought=response.content[0].text if response.content[0].type == "text" else "",
                            action=f"{block.name}({block.input})",
                            observation=observation,
                        )

                self.history.append({"role": "user", "content": tool_results})

        return f"⚠️ 已达到最大步数 {self.max_steps}，强制停止"


# 使用
if __name__ == "__main__":
    agent = SimpleReActAgent(tools=TOOLS, system_prompt=SYSTEM_PROMPT)
    result = agent.run("现在是几点？如果我在此刻下班，走 30 分钟到家，到家是几点？")
    print(f"\n最终答案：{result}")
    print(f"\n总步数：{len(agent.trace)}")
```

#### 今日任务

- [ ] 把上面的 Agent 代码敲一遍并跑通
- [ ] 测试 3 个不同复杂度的任务（1 步、3 步、5 步以上的）
- [ ] 观察并打印每一步的 `trace`，理解 Agent 的决策路径
- [ ] 故意触发一个错误（如让工具抛异常），看 Agent 怎么处理

#### 自检

- [ ] 我能解释 `stop_reason == "tool_use"` 和 `"end_turn"` 的区别
- [ ] 我理解为什么 `tool_result` 要放在 `user` 角色的消息里
- [ ] 我的 Agent 能处理"工具失败"的情况

---

### Day 5（周五）：工程化细节

**学习目标：** 给 Agent 加上生产级的工程化能力：超时、成本控制、重试、日志。

#### 核心概念

**必加的工程化能力：**
- **最大步数控制：** 防止死循环
- **超时机制：** 单次工具调用和整体执行都要有超时
- **Token 预算：** 累计 token 超限就停止
- **重试机制：** 工具临时失败要重试
- **结构化日志：** 每一步都记录，方便调试

**前端类比：**
- max_steps = 防抖动（debounce）的 max wait
- 超时 = fetch 的 AbortController
- Token 预算 = bundle size budget
- 重试 = axios-retry

#### 代码示例：增强版 Agent

```python
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class AgentConfig:
    max_steps: int = 10
    max_total_tokens: int = 50_000        # 总 token 预算
    tool_timeout_seconds: int = 30         # 单个工具超时
    max_retries: int = 2                   # 工具失败重试次数

@dataclass
class AgentMetrics:
    """Agent 执行指标，类比前端的性能埋点"""
    total_steps: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_time_seconds: float = 0
    tool_calls: dict[str, int] = None  # type: ignore

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = {}

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    def summary(self) -> str:
        return (
            f"Steps: {self.total_steps}, "
            f"Tokens: {self.total_tokens} (in:{self.total_input_tokens}/out:{self.total_output_tokens}), "
            f"Time: {self.total_time_seconds:.1f}s, "
            f"Tools: {self.tool_calls}"
        )


def execute_with_retry(fn, max_retries=2, timeout=30):
    """带重试和超时的工具执行。

    重要：真正的超时控制必须使用 asyncio.wait_for / concurrent.futures.Timeout，
    因为同步调用一旦卡住，事后检查 elapsed 无法中断已在执行的函数。
    这里以 Concurrent.futures 为例演示同步超时方案。
    """
    import concurrent.futures

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(fn)
                result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            return f"⚠️ 工具执行超时（>{timeout}s）"
        except Exception as e:
            last_error = e
            print(f"  工具失败（尝试 {attempt + 1}/{max_retries + 1}）：{e}")
            import time
            time.sleep(0.5 * (attempt + 1))
    return f"❌ 工具最终失败：{last_error}"
```

#### 今日任务

- [ ] 给 Day 4 的 Agent 加上 `AgentConfig` 和 `AgentMetrics`
- [ ] 实现 Token 预算检查（累计超限就停止）
- [ ] 用 `execute_with_retry` 包装工具执行
- [ ] 每次运行后打印 `metrics.summary()`

#### 自检

- [ ] 我的 Agent 有 4 道安全阀：max_steps / timeout / token budget / retry
- [ ] 我能从 `metrics` 看出一次运行的"成本"
- [ ] 我理解为什么"工具失败重试"和"LLM 重新决策"是两件事

---

### Day 6（周六）：实战日 — 完整 ReAct Agent

**学习目标：** 把 Day 1-5 的内容整合成一个完整、可演示的 Agent 项目。

#### 项目要求

**功能：**
- 支持 5 个工具：`search_web`、`calculate`、`get_current_time`、`read_file`、`write_file`
- 完整的 trace 日志（每一步都可见）
- 工程化配置（max_steps / timeout / token budget）
- 成本统计

**目录结构：**
```
phase-4/
└── react-agent/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── agent.py         # Agent 核心
    │   ├── tools.py         # 工具定义
    │   ├── prompts.py       # Prompt
    │   ├── config.py        # 配置和 metrics
    │   └── cli.py           # CLI 入口
    └── examples/
        └── run_examples.py  # 示例任务
```

**测试任务示例：**
1. 简单：「现在几点？」（1 步）
2. 计算：「(123 + 456) * 2 等于多少？」（1 步）
3. 多步：「今天是星期几？如果下周三有会议，还有几天？」（2-3 步）
4. 搜索 + 总结：「搜索 LangGraph 的最新版本，总结主要特性」（3-4 步）
5. 文件操作：「把刚才的总结写入到 summary.md」（2 步）

#### 今日任务

- [ ] 按目录结构初始化项目：`uv init react-agent`
- [ ] 添加依赖：`uv add anthropic`
- [ ] 实现完整 Agent（核心代码控制在 150 行以内）
- [ ] 跑通 5 个测试任务，记录每个任务的 trace 和 metrics
- [ ] 在 README 写清楚如何运行

---

### Day 7（周日）：测试 + 复盘

**学习目标：** 给 Agent 写测试，养成"Agent 也要测试"的习惯。

#### 学习内容

**Agent 测试的难点：**
- LLM 输出不确定 → 用 Mock LLM 测试 Agent Loop 逻辑
- 工具副作用 → 用 fake tool
- 端到端测试 → 需要真实 API key，跑得慢

**测试策略：**
- 单元测试：Mock LLM，测 Loop 逻辑、状态更新、异常处理
- 集成测试：用真实 LLM 跑简单任务
- 回归测试：固定 seed / temperature=0，对比输出

```python
# test_agent.py
import pytest
from unittest.mock import MagicMock, patch
from src.agent import SimpleReActAgent

def test_agent_calls_tool():
    """测试 Agent 在收到可解决问题时会调工具"""
    # Mock LLM 返回一个 tool_use
    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    mock_response.content = [MagicMock(
        type="tool_use",
        name="get_current_time",
        input={},
        id="test_id"
    )]

    with patch.object(SimpleReActAgent, "_call_llm", return_value=mock_response):
        agent = SimpleReActAgent(tools=TOOLS, system_prompt="test")
        # ... 断言 trace 中有 tool 调用
```

#### 今日任务

- [ ] 给 Agent 写至少 5 个单元测试（Mock LLM）
- [ ] 写 2 个集成测试（真实 LLM，简单任务）
- [ ] 跑 `uv run pytest -v` 全绿
- [ ] 写一篇 300 字的本周复盘到 `notes/week-1-notes.md`
- [ ] 在 [phase-4-agent-core-langgraph.md](./phase-4-agent-core-langgraph.md) 勾选 Week 1 完成项

#### 周末复盘问题

回答以下问题（写在 notes 里）：

1. 用一句话解释"Agent 是状态机"，并举一个 React 的类比
2. 手写 ReAct Agent 时，最让你"啊哈"的一个瞬间是什么？
3. LLM 的 tool calling 出错时，Agent 应该怎么处理？我的实现是怎样的？
4. 如果让你给这个 Agent 加一个"记忆"功能（记住之前的对话），你会怎么设计 State？
5. 对比 Week 1-3 学的"带工具的聊天机器人"，ReAct Agent 的核心差异是什么？

---

## Week 2 - LangChain Agent 生态

> **本周目标：** 理解工业级 Agent 框架的设计，知道它解决了什么问题、引入了什么问题
> **核心心智模型：** 框架是"封装好的最佳实践"，但封装的代价是失去灵活性
> **产出物：** 用 LangChain 重写 Week 1 的 Agent，并写下决策文档

### Day 1（周一）：LangChain 是什么、为什么、何时用

**学习目标：** 建立 LangChain 的整体认知，学会判断"何时用 / 何时不用"。

#### 核心概念

**LangChain 解决的问题：**
- 标准化 LLM 调用接口（一套代码切不同模型）
- 标准化工具、记忆、Prompt 组件
- 提供 Agent Executor 等高级抽象

**LangChain 引入的问题：**
- 抽象层多，调试困难（stack trace 很深）
- 版本迭代快，API 频繁 breaking change
- 隐藏了底层细节，出问题不知道怎么排查

**判断标准（重要，抄到笔记里）：**

| 场景 | 推荐方案 |
|------|---------|
| 单次工具调用 | 直接用 SDK |
| 简单 ReAct Agent | 手写（Week 1） |
| 需要 RAG + 多种文档源 | LangChain |
| 需要复杂状态、分支、人工介入 | **LangGraph**（Week 3） |
| 需要多 Agent 协作 | LangGraph |

#### 今日任务

- [ ] 安装：`uv add langchain langchain-anthropic langchain-community`
- [ ] 跑通官方 [Quickstart](https://python.langchain.com/docs/get_started/quickstart)
- [ ] 写一个最简的 `ChatAnthropic` 调用，对比手写 SDK 的差异
- [ ] 在 `notes/week-2-notes.md` 记录你的第一印象

#### 自检

- [ ] 我能说出 LangChain 解决了 3 个具体问题
- [ ] 我能说出 LangChain 的 2 个主要缺点
- [ ] 我知道遇到什么场景应该绕过 LangChain

---

### Day 2（周二）：Tool 抽象

**学习目标：** 理解 LangChain 的 `BaseTool` 和 `Toolkit` 设计。

#### 核心概念

**LangChain Tool 的三种定义方式：**
1. `@tool` 装饰器（推荐）
2. 继承 `BaseTool` 类
3. `StructuredTool.from_function`

**前端类比：** LangChain Tool 就像 React 的高阶组件，给普通函数"包装"出标准接口。

#### 代码示例

```python
from langchain_core.tools import tool
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# 方式 1：装饰器（推荐）
@tool
def search_web(query: str) -> str:
    """搜索互联网获取信息。输入：搜索关键词。"""
    # 注意：docstring 就是工具描述，会被 LLM 看到
    return f"搜索结果：关于「{query}」..."

@tool
def calculate(expression: str) -> str:
    """执行数学计算。输入：数学表达式，如 (1+2)*3。"""
    import ast, operator as _op
    _OPS = {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul, ast.Div: _op.truediv, ast.USub: _op.neg}
    def _walk(n):
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.BinOp): return _OPS[type(n.op)](_walk(n.left), _walk(n.right))
        if isinstance(n, ast.UnaryOp): return _OPS[type(n.op)](_walk(n.operand))
        raise ValueError
    try:
        return str(_walk(ast.parse(expression.strip(), mode="eval").body))
    except Exception as e:
        return f"计算失败：{e}"

# 方式 2：带复杂参数（用 Pydantic）
class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=5, description="最大返回结果数")

@tool(args_schema=SearchInput)
def search_advanced(query: str, max_results: int = 5) -> str:
    """高级搜索，支持结果数量控制"""
    return f"返回 {max_results} 条关于「{query}」的结果"

# 查看工具的 schema（重要，调试时用）
print(search_web.name)         # 工具名
print(search_web.description)  # 描述
print(search_web.args)         # 参数 schema
```

#### 今日任务

- [ ] 用 `@tool` 装饰器把 Week 1 的 3 个工具重写一遍
- [ ] 给每个工具加上详细的 docstring（这就是 description）
- [ ] 测试工具单独调用：`search_web.invoke({"query": "test"})`
- [ ] 对比手写工具 schema 和 LangChain `@tool` 的代码量

#### 自检

- [ ] 我知道工具的 `description` 来自哪里（docstring）
- [ ] 我能用 Pydantic 定义复杂参数的工具
- [ ] 我理解为什么 LangChain 工具比手写更"声明式"

---

### Day 3（周三）：Agent Executor 架构

**学习目标：** 理解 LangChain Agent Executor 的设计，知道它内部在做什么。

#### 核心概念

**Agent Executor 的两个核心组件：**
- **Agent：** 决策器，输入 messages，输出下一步动作（调工具 or 回答）
- **Executor：** 循环器，负责调用 Agent → 执行工具 → 回传结果 → 再调 Agent

**前端类比：**
- Agent = Render 函数（根据 state 决定输出什么）
- Executor = React 的 reconciler（管理循环、副作用）

**关键认知：** Agent Executor 就是 Week 1 手写的 `agent_loop`，只是封装好了。

#### 代码示例

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# 1. 初始化 LLM
llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)

# 2. 定义 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个能调用工具的助手。{agent_scratchpad}"),
    ("human", "{input}"),
])

# 3. 创建 Agent（决策器）
tools = [search_web, calculate]
agent = create_tool_calling_agent(llm, tools, prompt)

# 4. 创建 Executor（循环器）
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)

# 5. 运行
result = agent_executor.invoke({"input": "现在几点？"})
print(result["output"])
```

**重要观察：** `verbose=True` 会打印每一步的思考过程，这就是 Week 1 手写的 trace。

#### 今日任务

- [ ] 跑通上面的代码，用 Week 1 的 5 个测试任务对比
- [ ] 把 `verbose=True` 打开的输出，和 Week 1 手写的 trace 对比
- [ ] 查看 AgentExecutor 源码（在 IDE 里 cmd+click 进去看），找到主循环
- [ ] 记录你的观察：LangChain 帮你省了哪些代码？隐藏了哪些细节？

#### 自检

- [ ] 我能解释 Agent 和 AgentExecutor 的区别
- [ ] 我知道 `agent_scratchpad` 是干什么的（提示：中间步骤占位符）
- [ ] 我看过 AgentExecutor 的源码，找到了循环逻辑

---

### Day 4（周四）：用 LangChain 重写 Week 1 的 Agent

**学习目标：** 用 LangChain 完整重写 Week 1 的 ReAct Agent，做对比分析。

#### 今日任务

**重写要求：**
- [ ] 用 LangChain 实现 Week 1 的所有功能（5 个工具、max_steps、verbose）
- [ ] 加上 LangChain 的 `return_intermediate_steps=True`，拿到中间步骤
- [ ] 把 Week 1 的 5 个测试任务重跑一遍，记录结果
- [ ] **写对比表格**（这是本周核心产出）：

| 维度 | 手写 ReAct | LangChain |
|------|-----------|-----------|
| 核心代码行数 | ? 行 | ? 行 |
| 工具定义代码量 | ? 行 | ? 行 |
| 添加新工具成本 | ? | ? |
| 调试难度 | 容易/中/难 | 容易/中/难 |
| 自定义循环逻辑 | 完全可控 | 需 hack |
| 错误处理 | 自己写 | 内置但要懂 |
| Token 统计 | 自己算 | callback |
| 学习曲线 | 低 | 中 |

#### 自检

- [ ] 我能列出 3 个 LangChain 比手写更好的场景
- [ ] 我能列出 3 个手写比 LangChain 更好的场景
- [ ] 我的对比表格有数据支撑，不是主观感觉

---

### Day 5（周五）：LangSmith Trace 入门

**学习目标：** 学会用 LangSmith 做 Agent 的可观测性，这是后续所有项目的基础。

#### 核心概念

**为什么需要 Trace：**
- Agent 是黑盒，不 trace 就没法调试
- LangSmith 能看到每一步的 input / output / 耗时 / token
- 类比：React DevTools + Performance 火焰图

**Trace 的三个层级：**
- **Run：** 一次完整的 Agent 执行
- **Chain：** 中间每一步（LLM 调用、工具调用）
- **Step：** 最细粒度的操作

#### 今日任务

- [ ] 注册 [LangSmith](https://smith.langchain.com/) 账号
- [ ] 设置环境变量：
  ```bash
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_API_KEY=your_key
  export LANGCHAIN_PROJECT=phase-4-week-2
  ```
- [ ] 跑一次 Day 4 的 Agent，在 LangSmith 看板查看 trace
- [ ] 截图一个完整的 trace，分析每一步的耗时和 token
- [ ] 故意制造一个错误（如工具抛异常），看 trace 里长什么样

#### 自检

- [ ] 我的 LangSmith 看板能看到完整 trace
- [ ] 我能从 trace 里看出"哪一步最慢、哪一步最耗 token"
- [ ] 我理解为什么"没有 trace 就没有 Agent 工程"

---

### Day 6（周六）：LangChain 的局限 + 决策日

**学习目标：** 深入理解 LangChain 的局限，为 Week 3 学 LangGraph 做铺垫。

#### 核心概念

**LangChain Agent Executor 的核心局限：**

1. **状态管理不灵活：** 只能用 `intermediate_steps` 这种 list，没法维护结构化状态
2. **循环逻辑难以定制：** 想加"每 3 步反思一次"、"失败后切换策略"都很 hack
3. **难以实现复杂工作流：** 分支、并行、人工介入都很难
4. **调试不直观：** 错误堆栈很深，定位问题要翻好几层

**对比 React：**
- LangChain Agent Executor = 早期的 React Class Component（封装重、不灵活）
- LangGraph = Hooks 时代的 React（状态可控、组合灵活）

#### 今日任务

**尝试做这些事情，体会 LangChain 的局限：**

- [ ] 尝试让 Agent "每 3 步做一次自我检查"——你会发现很难实现
- [ ] 尝试加"条件分支：如果搜索失败就换一个工具"——需要 hack Executor
- [ ] 尝试"在关键节点暂停等用户确认"——基本做不到
- [ ] 写一篇决策文档 `notes/week-2-decision.md`，内容包括：
  - 什么场景我会用 LangChain
  - 什么场景我会绕过它
  - 我期待 LangGraph 解决什么问题

#### 自检

- [ ] 我亲身体验过 LangChain Agent 的至少 2 个局限
- [ ] 我的决策文档有具体场景，不是空话
- [ ] 我能解释为什么 LangGraph 是"状态优先"的设计

---

### Day 7（周日）：复盘 + 准备 LangGraph

**学习目标：** 巩固本周所学，为 Week 3 的 LangGraph 深度学习做准备。

#### 今日任务

- [ ] 给 Day 4 的 LangChain Agent 写 3 个测试
- [ ] 整理本周的 LangSmith trace，找出 3 个"印象最深"的执行案例
- [ ] 在 `notes/week-2-notes.md` 写一篇 400 字复盘
- [ ] 在 [phase-4-agent-core-langgraph.md](./phase-4-agent-core-langgraph.md) 勾选 Week 2 完成项
- [ ] **预习：** 浏览 [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/tutorials/) 的前两篇，不求看懂，先建立印象

#### 周末复盘问题

1. LangChain 帮我省了多少代码？代价是什么？
2. 如果我是新项目的 Tech Lead，在"手写 vs LangChain vs LangGraph"之间，我会怎么选？依据是什么？
3. LangSmith 的 trace 让我对 Agent 的认知有什么改变？
4. 我最期待 LangGraph 解决 Week 1-2 遇到的哪个问题？

---

## Week 3 - LangGraph 核心（重点周）

> **本周目标：** 深入掌握 LangGraph，这是目前工业级 Agent 的事实标准
> **核心心智模型：** LangGraph = "可编程的状态机" + React 的状态管理思维
> **产出物：** 用 LangGraph 实现一个完整的多步骤工作流（研究 → 起草 → 审校 → 定稿）
> **本周是重点周，周末建议投入 3 小时以上**

### Day 1（周一）：State 概念（核心中的核心）

**学习目标：** 理解 LangGraph 的 State，这是后面所有内容的基础。用 React 思维学，会非常顺。

#### 核心概念

**LangGraph 的核心抽象：**
- **State：** Agent 运行时的全部数据（类比 React 的 state）
- **Node：** 状态转换函数（类比 useReducer 的 reducer）
- **Edge：** 节点之间的连接（类比组件间的数据流）
- **Graph：** 节点和边的组合（类比组件树）

**思维迁移对照表（重点！）：**

| React 概念 | LangGraph 概念 | 说明 |
|-----------|---------------|------|
| `useState(s)` | `State(TypedDict)` | 定义状态结构 |
| `setState({key: val})` | Node 返回 dict 更新 State | 状态更新 |
| `useReducer(reducer, init)` | `StateGraph(State).add_node(fn)` | 状态转换 |
| `dispatch({type})` | Edge 触发下一个 Node | 触发流转 |
| `useEffect([deps])` | Conditional Edge | 条件触发 |
| `<Provider state>` | `graph.compile()` 后 invoke | 初始化并运行 |

**State 的两种定义方式：**
1. `TypedDict`（推荐，简洁）
2. `Pydantic BaseModel`（带校验）

#### 代码示例

```python
from typing import TypedDict, Annotated
from operator import add

# 方式 1：TypedDict（推荐入门用）
class ResearchState(TypedDict):
    """研究 Agent 的状态，类比 React 的 state 对象"""
    question: str               # 用户问题
    plan: list[str]             # 研究计划
    search_results: list[str]   # 搜索结果
    draft: str                  # 草稿
    review_feedback: str        # 审校反馈
    final_report: str           # 最终报告
    iteration: int              # 当前迭代次数

# 方式 2：带 reducer 的 State（重要！）
# reducer 决定状态如何被更新（类比 useReducer 的 reducer）
class AgentState(TypedDict):
    messages: Annotated[list, add]  # 用 add reducer：新消息追加而不是覆盖
    current_step: str               # 默认行为：直接覆盖

# 对比 React：
# const [messages, setMessages] = useState([])
# setMessages([...messages, newMsg])  // 这就是 add reducer
# const [step, setStep] = useState("")
# setStep("new_step")                 // 这就是默认 reducer（覆盖）
```

**关键认知：** `Annotated[list, add]` 的意思是"这个字段用追加方式更新"，这和 React 里 `setArr([...arr, item])` 是一回事。

#### 今日任务

- [ ] 安装：`uv add langgraph`
- [ ] 定义 3 个不同的 State（对应不同场景：聊天、研究、代码生成）
- [ ] 在 `notes/week-3-notes.md` 画一张思维导图：React 状态 ↔ LangGraph State
- [ ] 用 `Annotated[list, add]` 写一个"消息追加"的 State 示例

#### 自检

- [ ] 我能用 TypedDict 定义 State
- [ ] 我理解 `Annotated[list, add]` 的含义和作用
- [ ] 我能解释 LangGraph State 和 React useState 的对应关系

---

### Day 2（周二）：Node 和 Edge

**学习目标：** 掌握 Node（状态转换函数）和 Edge（节点连接）。

#### 核心概念

**Node = 状态转换函数：**
- 接收当前 State
- 执行某些操作（调 LLM、调工具、计算）
- 返回 State 的部分更新（不是完整 State）

**前端类比：** Node 就像 `useReducer` 里的 reducer 函数，根据当前 state 和 action 返回新的 state。

**Edge 的类型：**
- **普通 Edge：** A 完了一定去 B
- **Conditional Edge：** 根据 State 动态决定下一个节点
- **Entry / End：** 起点和终点

#### 代码示例：最小 LangGraph

```python
from langgraph.graph import StateGraph, START, END

# 1. 定义 State
class SimpleState(TypedDict):
    messages: Annotated[list, add]
    current_task: str

# 2. 定义 Nodes（每个 Node 是一个函数：State -> State 更新）
def greet_node(state: SimpleState) -> dict:
    """打招呼节点"""
    return {
        "messages": [{"role": "ai", "content": f"你好！我来帮你处理：{state['current_task']}"}],
        "current_task": state["current_task"],
    }

def process_node(state: SimpleState) -> dict:
    """处理节点"""
    result = f"已处理：{state['current_task']}"
    return {"messages": [{"role": "ai", "content": result}]}

# 3. 构建 Graph
graph = StateGraph(SimpleState)
graph.add_node("greet", greet_node)
graph.add_node("process", process_node)

# 4. 添加 Edges
graph.add_edge(START, "greet")        # 入口 → greet
graph.add_edge("greet", "process")    # greet → process
graph.add_edge("process", END)        # process → 结束

# 5. 编译并运行
app = graph.compile()
result = app.invoke({"messages": [], "current_task": "学习 LangGraph"})
print(result["messages"])
```

**前端类比：** 这就像定义一个组件树，`add_node` 是定义组件，`add_edge` 是定义组件间的数据流。

#### 今日任务

- [ ] 把上面的最小示例敲一遍跑通
- [ ] 在 LangSmith 看这个 Graph 的 trace（会有可视化流程图）
- [ ] 扩展到 4 个 Node：`greet → ask → process → summarize`
- [ ] 尝试让每个 Node 打印收到的 State，观察 State 如何流转

#### 自检

- [ ] 我能解释 Node 函数的返回值是"State 的部分更新"
- [ ] 我理解 START 和 END 的作用
- [ ] 我能在 LangSmith 看到流程图

---

### Day 3（周三）：Conditional Edge（条件分支）

**学习目标：** 掌握 Conditional Edge，这是 LangGraph 强大的根源。

#### 核心概念

**Conditional Edge：** 根据 State 动态决定下一个节点，让 Graph 能"做决策"。

**前端类比：**
- Conditional Edge = `if (condition) renderA() else renderB()`
- 这就是 React 里的条件渲染，只不过这里条件的是"下一个 Node"

**典型应用：**
- ReAct 循环：`tool_use → 回到 agent` / `end_turn → 结束`
- 审校循环：`review_pass → END` / `review_fail → 回到 draft`
- 路由：根据问题类型路由到不同处理节点

#### 代码示例：带条件分支的 Graph

```python
from langgraph.graph import StateGraph, START, END

class WorkflowState(TypedDict):
    task: str
    draft: str
    review_passed: bool
    iteration: int

def draft_node(state: WorkflowState) -> dict:
    """起草节点"""
    draft = f"这是关于「{state['task']}」的第 {state['iteration'] + 1} 版草稿"
    return {"draft": draft, "iteration": state["iteration"] + 1}

def review_node(state: WorkflowState) -> dict:
    """审校节点：这里用简单逻辑模拟，真实场景调 LLM"""
    # 模拟：第 3 版才通过
    passed = state["iteration"] >= 3
    return {"review_passed": passed}

def should_revise(state: WorkflowState) -> str:
    """条件函数：决定下一步去哪"""
    if state["review_passed"]:
        return "end"
    if state["iteration"] >= 5:  # 防止无限循环
        return "end"
    return "revise"

# 构建带条件分支的 Graph
graph = StateGraph(WorkflowState)
graph.add_node("draft", draft_node)
graph.add_node("review", review_node)

graph.add_edge(START, "draft")
graph.add_edge("draft", "review")

# 关键：Conditional Edge
graph.add_conditional_edges(
    "review",              # 从哪个节点出发
    should_revise,         # 条件函数
    {                      # 条件结果的映射
        "revise": "draft", # 返回 "revise" 就去 draft 节点（形成循环）
        "end": END,        # 返回 "end" 就结束
    }
)

app = graph.compile()

# 运行
result = app.invoke({"task": "LangGraph 教程", "draft": "", "review_passed": False, "iteration": 0})
print(f"最终版本：迭代 {result['iteration']} 次")
```

**关键认知：** Conditional Edge 让你能在 LangGraph 里实现"循环"——这就是 ReAct Agent 的循环本质。

#### 今日任务

- [ ] 把上面的审校循环代码敲一遍跑通
- [ ] 在 LangSmith 看 trace，观察条件分支如何工作
- [ ] 修改条件，让审校更严格（如 5 次才通过），观察行为
- [ ] **关键练习：** 用 Conditional Edge 实现"计数器累加到 10 就停"

#### 自检

- [ ] 我能解释 Conditional Edge 的三个要素（源节点、条件函数、结果映射）
- [ ] 我理解为什么 Conditional Edge 能实现循环
- [ ] 我知道如何防止无限循环（max_iteration + 条件判断）

---

### Day 4（周四）：完整 ReAct Agent（用 LangGraph 重写）

**学习目标：** 用 LangGraph 完整重写 Week 1 的 ReAct Agent，理解框架的价值。

#### 核心概念

**ReAct 在 LangGraph 里的形态：**
- 2 个 Node：`agent`（调 LLM 决策）+ `tools`（执行工具）
- 1 个 Conditional Edge：`agent` 之后根据是否调工具决定去 `tools` 还是 `END`
- 1 个普通 Edge：`tools` 之后回到 `agent`

**对比 Week 1 手写：**
- 手写：while 循环 + 状态字典
- LangGraph：StateGraph + Conditional Edge
- 核心逻辑完全一样，但 LangGraph 的抽象让代码更清晰、可扩展

#### 代码示例：LangGraph 版 ReAct

```python
from typing import TypedDict, Annotated
from typing_extensions import override
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

# 1. State
class AgentState(TypedDict):
    messages: Annotated[list, add]  # 消息列表用追加方式更新

# 2. Tools（复用 Week 2 的定义）
@tool
def search_web(query: str) -> str:
    """搜索互联网获取信息"""
    return f"搜索结果：{query}..."

@tool
def calculate(expression: str) -> str:
    """执行数学计算"""
    import ast, operator as _op
    _OPS = {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul, ast.Div: _op.truediv, ast.USub: _op.neg}
    def _walk(n):
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.BinOp): return _OPS[type(n.op)](_walk(n.left), _walk(n.right))
        if isinstance(n, ast.UnaryOp): return _OPS[type(n.op)](_walk(n.operand))
        raise ValueError
    try:
        return str(_walk(ast.parse(expression.strip(), mode="eval").body))
    except Exception:
        return "计算失败"

tools = [search_web, calculate]

# 3. LLM（绑定工具）
llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 4. Nodes
def agent_node(state: AgentState) -> dict:
    """Agent 决策节点：调 LLM 决定下一步"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ToolNode 是预置的 Node，自动执行所有 tool_use
tool_node = ToolNode(tools)

# 5. Conditional Edge 的条件函数
def should_use_tools(state: AgentState) -> str:
    """检查最后一条消息是否有 tool_calls"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# 6. 构建 Graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_use_tools,
    {"tools": "tools", "end": END}
)
graph.add_edge("tools", "agent")  # 工具执行完回到 agent

# 7. 编译
app = graph.compile()

# 8. 运行
result = app.invoke({
    "messages": [{"role": "user", "content": "现在是几点？2 小时后是几点？"}]
})
print(result["messages"][-1].content)
```

**关键对比：**
- Week 1 手写：约 100 行核心代码，while 循环 + 手动消息管理
- LangGraph 版：约 40 行核心代码，结构清晰，易于扩展

#### 今日任务

- [ ] 把上面的 LangGraph 版 ReAct 敲一遍跑通
- [ ] 用 Week 1 的 5 个测试任务对比两个版本
- [ ] 在 LangSmith 看 trace，对比两者的可视化流程
- [ ] **思考题：** 如果要加"每 3 步反思一次"，手写版和 LangGraph 版分别要怎么改？

#### 自检

- [ ] 我的 LangGraph 版 ReAct 能处理 Week 1 的所有任务
- [ ] 我能解释 `ToolNode` 的作用（预置的工具执行节点）
- [ ] 我理解 Conditional Edge 在 ReAct 里扮演的角色

---

### Day 5（周五）：Checkpointing（状态持久化）

**学习目标：** 掌握 LangGraph 的 Checkpointing，实现状态持久化和恢复。

#### 核心概念

**Checkpointing 是什么：**
- 每次状态变更后自动保存快照
- 支持中断后恢复
- 支持回放历史
- 支持时间旅行（回到某个历史节点）

**前端类比：**
- Checkpoint = Redux DevTools 的 time-travel debugging
- 可以回到任意一个历史状态，重新执行

**核心用途：**
- 长任务断点续传
- 调试（回到出错前的状态）
- Human-in-the-Loop（暂停等用户确认）

#### 代码示例

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

# 构建你的 Graph（用 Day 4 的 ReAct）
graph = StateGraph(AgentState)
# ... add_node / add_edge ...

# 编译时传入 checkpointer
checkpointer = MemorySaver()  # 内存版，生产用 PostgreSQL / SQLite
app = graph.compile(checkpointer=checkpointer)

# 运行时指定 thread_id（用于隔离不同会话）
config = {"configurable": {"thread_id": "user-123-session-1"}}

result = app.invoke(
    {"messages": [{"role": "user", "content": "我叫 wsq"}]},
    config=config
)

# 新会话：同一个 thread_id 能记住之前的状态
result2 = app.invoke(
    {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
    config=config
)
print(result2["messages"][-1].content)  # 应该能答出 "wsq"

# 查看历史快照
for snapshot in app.get_state_history(config):
    print(f"Step {snapshot.metadata.get('step', '?')}: {snapshot.values.get('messages', [])[-1]}")
```

#### 今日任务

- [ ] 给 Day 4 的 ReAct Agent 加上 MemorySaver
- [ ] 测试"跨 invoke 记忆"：第一次告诉它信息，第二次问它
- [ ] 用 `get_state_history` 查看所有历史快照
- [ ] 尝试从某个历史快照恢复执行（`app.invoke(None, config, ...)`）

#### 自检

- [ ] 我理解 `thread_id` 的作用（会话隔离）
- [ ] 我能从历史快照里看到每一步的 State
- [ ] 我知道生产环境应该用持久化的 Checkpointer

---

### Day 6（周六）：Human-in-the-Loop（重点）

**学习目标：** 实现 Human-in-the-Loop，这是 LangGraph 最强大的特性之一。

#### 核心概念

**Human-in-the-Loop 的典型场景：**
- 工具调用前让用户确认（如"是否发送邮件？"）
- 关键决策让用户选择（如"用 A 方案还是 B 方案？"）
- 工具失败后让用户介入

**实现机制：**
- 在关键节点前"中断"
- 等待用户输入
- 把用户输入加入 State，继续执行

**前端类比：**
- Human-in-the-Loop = `window.confirm()` 的异步版
- 或者像 `useSWR` 的 mutate，等待用户触发再继续

#### 代码示例

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class EmailState(TypedDict):
    recipient: str
    subject: str
    body: str
    approved: bool
    sent: bool

def draft_email_node(state: EmailState) -> dict:
    """起草邮件"""
    return {
        "recipient": "boss@example.com",
        "subject": "请假申请",
        "body": "您好，我想请假 3 天..."
    }

def review_node(state: EmailState) -> dict:
    """人工审核节点：在这里中断，等用户确认"""
    user_decision = interrupt({
        "type": "approval_request",
        "email": {
            "recipient": state["recipient"],
            "subject": state["subject"],
            "body": state["body"],
        },
        "message": "是否批准发送这封邮件？"
    })
    return {"approved": user_decision == "yes"}

def send_email_node(state: EmailState) -> dict:
    """发送邮件"""
    if state["approved"]:
        print(f"✉️ 已发送给 {state['recipient']}")
        return {"sent": True}
    else:
        print("❌ 用户拒绝了发送")
        return {"sent": False}

# 构建 Graph
graph = StateGraph(EmailState)
graph.add_node("draft", draft_email_node)
graph.add_node("review", review_node)
graph.add_node("send", send_email_node)

graph.add_edge(START, "draft")
graph.add_edge("draft", "review")
graph.add_conditional_edges(
    "review",
    lambda s: "send" if s["approved"] else END,
    {"send": "send", END: END}
)
graph.add_edge("send", END)

# 编译（必须有 checkpointer 才能用 interrupt）
app = graph.compile(checkpointer=MemorySaver())

# 运行：第一次调用会在 review 节点中断
config = {"configurable": {"thread_id": "email-1"}}
result = app.invoke({"recipient": "", "subject": "", "body": "", "approved": False, "sent": False}, config)

# 检查是否在中断点
state = app.get_state(config)
if state.next == ("review",):
    print("⏸️  Agent 在等待人工确认...")
    print(f"邮件内容：{state.values}")

    # 用户确认后，恢复执行
    user_input = input("批准发送吗？(yes/no): ")
    result = app.invoke(Command(resume=user_input), config)
    print(f"最终结果：{result}")
```

#### 今日任务

- [ ] 把上面的 Human-in-the-Loop 示例敲一遍跑通
- [ ] 在 LangSmith 看 trace，理解中断是如何发生的
- [ ] **实战：** 给 Day 4 的 ReAct Agent 加上"工具调用前确认"功能
- [ ] 尝试实现"工具失败后问用户怎么办"（重试 / 跳过 / 换工具）

#### 自检

- [ ] 我能解释 `interrupt()` 函数的作用
- [ ] 我知道恢复执行需要用 `Command(resume=...)`
- [ ] 我理解为什么 Human-in-the-Loop 必须用 Checkpointer

---

### Day 7（周日）：完整多步骤工作流（本周收官）

**学习目标：** 整合 Week 3 所有内容，做一个完整的"研究 → 起草 → 审校 → 定稿"工作流。

#### 项目要求

**场景：** 自动写一篇技术博客
1. **Planner：** 规划文章大纲
2. **Researcher：** 搜索每个大纲点的资料
3. **Drafter：** 根据资料起草文章
4. **Reviewer：** 审校草稿，给出修改意见
5. **条件分支：** 审校通过 → 定稿；不通过 → 回到 Drafter

**State 设计：**
```python
class BlogWorkflowState(TypedDict):
    topic: str
    outline: list[str]
    research_data: dict[str, str]  # outline point -> search results
    draft: str
    review_feedback: str
    review_passed: bool
    iteration: int
    final_article: str
```

**要求：**
- [ ] 包含条件分支（审校循环）
- [ ] 包含 Human-in-the-Loop（Reviewer 前让用户确认）
- [ ] 使用 Checkpointing（支持中断恢复）
- [ ] 接入 LangSmith trace
- [ ] 控制最大迭代次数（如 3 次）

#### 今日任务

- [ ] 设计完整 State 和 Node 划分（先画图再写代码）
- [ ] 实现 5 个 Node（Planner / Researcher / Drafter / Reviewer / Finalizer）
- [ ] 连接 Graph，包含条件分支和 Human-in-the-Loop
- [ ] 跑 2 个测试主题（如"React Server Components 入门"、"LangGraph 是什么"）
- [ ] 写一篇 500 字复盘，重点对比 LangGraph vs 手写 vs LangChain
- [ ] 在 [phase-4-agent-core-langgraph.md](./phase-4-agent-core-langgraph.md) 勾选 Week 3 完成项

#### 周末复盘问题

1. 用 LangGraph 实现 ReAct Agent 后，我对"Agent 是状态机"的理解有什么深化？
2. LangGraph 的 Conditional Edge 解决了 LangChain Agent 的什么问题？
3. Human-in-the-Loop 能用来做什么？列举 3 个真实应用场景
4. 如果我要给本周的工作流加"并行搜索多个大纲点"，应该怎么改？（思考即可，不必实现）
5. 我对"状态优先"的设计哲学有什么体会？

---

## Week 4 - Agent 记忆系统

> **本周目标：** 给 Agent 加上完整的记忆系统，让它"真正记住你"
> **核心心智模型：** 记忆不是"存对话历史"，而是"存有用的结构化信息"
> **产出物：** 给 Week 3 的 Agent 加上短期 / 长期 / 实体记忆

### Day 1（周一）：记忆类型概览

**学习目标：** 建立记忆系统的整体认知，区分不同类型的记忆。

#### 核心概念

**三种记忆类型：**

| 记忆类型 | 类比 | 持续时间 | 实现方式 |
|---------|------|---------|---------|
| 短期记忆 | 工作记忆（脑子里的当前任务）| 单次会话 | messages 列表 |
| 长期记忆 | 笔记本 / 日记 | 跨会话 | 向量库 / 数据库 |
| 实体记忆 | 对某个人的印象 | 永久 | 结构化存储 |

**前端类比：**
- 短期记忆 = 组件 state（页面刷新就没）
- 长期记忆 = localStorage / IndexedDB
- 实体记忆 = 用户画像（User Profile）

**记忆的核心挑战：**
- **容量有限：** Context window 有限，不能全塞进去
- **相关性：** 当前任务需要哪部分记忆？
- **时效性：** 旧记忆可能过时，要更新或遗忘

#### 今日任务

- [ ] 阅读 [MemGPT 论文](https://arxiv.org/abs/2310.08560) 的前 3 节（不看公式）
- [ ] 在 `notes/week-4-notes.md` 画一张记忆系统架构图
- [ ] 回顾你用过的 AI 产品，分析它们的记忆能力（如 ChatGPT、Claude、Cursor）
- [ ] 列出你希望自己的 Agent 记住什么（至少 5 项）

#### 自检

- [ ] 我能解释短期 / 长期 / 实体记忆的区别
- [ ] 我理解"记忆的核心挑战是相关性，不是存储"
- [ ] 我能说出 MemGPT 的核心思路（分层 + 溢出归档）

---

### Day 2（周二）：短期记忆 + Token 管理

**学习目标：** 实现高效的短期记忆管理，解决"对话太长爆 Context"的问题。

#### 核心概念

**短期记忆的三种策略：**

1. **滑动窗口：** 只保留最近 N 条消息（简单粗暴）
2. **Token 预算：** 累计 token 超过阈值就裁剪（精细）
3. **摘要压缩：** 把旧消息压缩成摘要（智能）

**前端类比：**
- 滑动窗口 = 固定长度的环形缓冲区
- Token 预算 = bundle size 限制
- 摘要压缩 = 数据序列化时的"有损压缩"

#### 代码示例：多策略短期记忆

```python
from typing import Annotated
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

# 策略 1：滑动窗口
def sliding_window_messages(messages: list, keep_last_n: int = 10) -> list:
    """保留最近 N 条消息（但永远保留 system 消息）"""
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    non_system = [m for m in messages if not isinstance(m, SystemMessage)]

    # 永远保留 system，非 system 只留最近 keep_last_n 条
    return system_msgs + non_system[-keep_last_n:]

# 策略 2（变体）：基于 token 预算的滑动窗口
# from tiktoken import encoding_for_model
# def sliding_window_by_tokens(messages: list, model: str, max_tokens: int = 4000) -> list:
#     """从后往前累加，直到达到 token 预算。需要预先建好 enc。"""
#     enc = encoding_for_model(model)
#     system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
#     non_system = [m for m in messages if not isinstance(m, SystemMessage)]
#     kept, total = [], 0
#     for msg in reversed(non_system):
#         msg_tokens = len(enc.encode(str(msg.content)))
#         if total + msg_tokens > max_tokens:
#             break
#         kept.insert(0, msg)
#         total += msg_tokens
#     return system_msgs + kept

# 策略 3：摘要压缩（旧消息压成摘要）
async def summarize_old_messages(messages: list, llm) -> list:
    """把旧消息压成一条摘要消息"""
    if len(messages) <= 6:
        return messages

    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    recent = [m for m in messages if not isinstance(m, SystemMessage)][-4:]
    old = [m for m in messages if not isinstance(m, SystemMessage)][:-4]

    summary_prompt = f"请把以下对话压缩成 200 字以内的摘要：\n\n{old}"
    summary = await llm.ainvoke(summary_prompt)

    return system_msgs + [HumanMessage(content=f"[历史摘要] {summary.content}")] + recent
```

#### 今日任务

- [ ] 实现以上 3 种短期记忆策略
- [ ] 用一个长对话（20+ 条消息）测试三种策略的效果
- [ ] 对比三种策略的 token 消耗和信息保留度
- [ ] 给 Week 3 的 Agent 加上"Token 预算"短期记忆

#### 自检

- [ ] 我能实现滑动窗口、Token 预算、摘要压缩三种策略
- [ ] 我理解每种策略的适用场景
- [ ] 我能解释为什么摘要压缩比滑动窗口"更聪明"

---

### Day 3（周三）：长期记忆 — 向量库方案

**学习目标：** 用向量库实现跨会话的长期记忆。

#### 核心概念

**向量库记忆的核心思路：**
1. 把每条重要信息 embedding 成向量
2. 存入向量库（Chroma / Qdrant / Pinecone）
3. 新对话时，根据当前问题检索相关记忆
4. 把检索到的记忆塞进 prompt

**前端类比：**
- 向量库 = IndexedDB（持久化存储）
- Embedding = 给每条信息打"标签"
- 检索 = 用相似度搜索（不是精确匹配）

**关键问题：什么时候存？存什么？**
- 不要存所有对话（噪音太多）
- 存"用户告诉你的事实"（如"我喜欢简洁的代码风格"）
- 存"关键决策和原因"
- 用 LLM 帮你判断"这条信息值得存吗"

#### 代码示例

```python
import chromadb
from chromadb.utils import embedding_functions

# 1. 初始化向量库
client = chromadb.PersistentClient(path="./memory_store")
embed_fn = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection("long_term_memory")

# 2. 存记忆
def save_memory(text: str, metadata: dict = None):
    """把一条信息存入长期记忆"""
    import uuid
    mem_id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[metadata or {}],
        ids=[mem_id]
    )
    print(f"💾 已存储记忆：{text[:50]}...")

# 3. 检索记忆
def retrieve_memory(query: str, n_results: int = 3) -> list[str]:
    """根据当前问题检索相关记忆"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0]

# 4. 用 LLM 判断"是否值得存"
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)

async def maybe_save_memory(message: str):
    """让 LLM 判断这条消息是否值得记住"""
    prompt = f"""判断以下用户消息是否包含值得长期记住的信息（如偏好、事实、决策）。

用户消息：{message}

只回答 JSON：{{"should_save": true/false, "reason": "...", "summary": "如果保存，摘要是什么"}}
"""
    response = await llm.ainvoke(prompt)
    import json
    result = json.loads(response.content)
    if result["should_save"]:
        save_memory(result["summary"], {"type": "user_fact"})
        return True
    return False

# 5. 构建带记忆的 prompt
def build_prompt_with_memory(user_input: str) -> str:
    memories = retrieve_memory(user_input)
    memory_text = "\n".join(f"- {m}" for m in memories) if memories else "（无）"
    return f"""以下是关于用户的已知信息：
{memory_text}

用户当前问题：{user_input}
"""
```

#### 今日任务

- [ ] 安装：`uv add chromadb`
- [ ] 实现上面的向量库记忆（存 / 查 / 判断）
- [ ] 测试场景：告诉 Agent "我前端主要用 React"，新对话问"我常用什么框架"
- [ ] 对比"有记忆" vs "无记忆"的对话体验

#### 自检

- [ ] 我的 Agent 能跨会话记住用户信息
- [ ] 我理解为什么不能把所有对话都存进向量库
- [ ] 我能用 LLM 自动判断"哪些信息值得存"

---

### Day 4（周四）：实体记忆 — 结构化用户画像

**学习目标：** 实现实体记忆，让 Agent 拥有"用户画像"。

#### 核心概念

**实体记忆 vs 向量库记忆：**
- 向量库记忆：非结构化文本，靠相似度检索
- 实体记忆：结构化字段（如 `name`、`role`、`preferences`），精确查询

**前端类比：**
- 向量库 = 全文搜索
- 实体记忆 = 用户 Profile 对象（`user.name`、`user.preferences`）

**实体记忆的典型字段：**
- 基础信息：姓名、职业、技术栈
- 偏好：回答风格、详细程度、语言
- 项目背景：在做什么项目、用什么技术
- 历史决策：为什么这么选

#### 代码示例

```python
from pydantic import BaseModel, Field
from typing import Optional
import json
from pathlib import Path

class UserProfile(BaseModel):
    """用户画像（实体记忆）"""
    name: Optional[str] = None
    role: Optional[str] = None                      # 前端工程师 / 后端工程师
    tech_stack: list[str] = Field(default_factory=list)  # ["React", "TypeScript"]
    preferences: dict[str, str] = Field(default_factory=dict)  # {"style": "concise"}
    projects: list[dict] = Field(default_factory=list)  # [{"name": "...", "stack": [...]}]

    def to_prompt_context(self) -> str:
        """转成 prompt 上下文"""
        lines = []
        if self.name: lines.append(f"姓名：{self.name}")
        if self.role: lines.append(f"职业：{self.role}")
        if self.tech_stack: lines.append(f"技术栈：{', '.join(self.tech_stack)}")
        if self.preferences:
            prefs = ", ".join(f"{k}={v}" for k, v in self.preferences.items())
            lines.append(f"偏好：{prefs}")
        return "\n".join(lines) if lines else "（暂无用户信息）"

class EntityMemory:
    """实体记忆管理器"""

    def __init__(self, storage_path: str = "user_profile.json"):
        self.storage_path = Path(storage_path)
        self.profile = self._load()

    def _load(self) -> UserProfile:
        if self.storage_path.exists():
            data = json.loads(self.storage_path.read_text())
            return UserProfile(**data)
        return UserProfile()

    def save(self):
        self.storage_path.write_text(self.profile.model_dump_json(indent=2))

    async def update_from_message(self, message: str, llm):
        """用 LLM 从用户消息中提取实体信息"""
        prompt = f"""从用户消息中提取可更新的用户画像字段。

当前画像：{self.profile.model_dump_json()}

用户消息：{message}

只返回 JSON，格式：{{"field_name": "new_value"}}，只包含需要更新的字段。
可更新字段：name, role, tech_stack (list), preferences (dict), projects (list)
"""
        response = await llm.ainvoke(prompt)
        try:
            updates = json.loads(response.content)
            current = self.profile.model_dump()
            # 智能合并：list 追加，dict 合并，其他覆盖
            for k, v in updates.items():
                if k in current:
                    if isinstance(current[k], list) and isinstance(v, list):
                        current[k] = list(set(current[k] + v))  # 去重合并
                    elif isinstance(current[k], dict) and isinstance(v, dict):
                        current[k].update(v)
                    else:
                        current[k] = v
            self.profile = UserProfile(**current)
            self.save()
            return updates
        except json.JSONDecodeError:
            return {}
```

#### 今日任务

- [ ] 实现 `UserProfile` 和 `EntityMemory`
- [ ] 测试：和 Agent 聊几句（"我叫 wsq，前端工程师，主要写 React"），看 profile 是否更新
- [ ] 重启程序，确认 profile 是持久化的
- [ ] 让 Agent 回答问题时使用 profile（"基于我的技术栈，解释 X"）

#### 自检

- [ ] 我的 Agent 有结构化的用户画像
- [ ] 画像能跨会话持久化
- [ ] LLM 能自动从对话中提取实体信息

---

### Day 5（周五）：MemGPT 思路 — 分层记忆

**学习目标：** 理解 MemGPT 的分层记忆思路，实现"记忆溢出归档"机制。

#### 核心概念

**MemGPT 的核心思想：**
- 记忆分两层：**核心记忆**（Context 内）+ **归档记忆**（Context 外）
- 当核心记忆满了，自动把旧的归档
- 需要时通过检索把归档记忆"召回"到核心

**前端类比：**
- 核心记忆 = 内存（RAM），快但容量小
- 归档记忆 = 硬盘（SSD），慢但容量大
- 召回 = 把数据从硬盘加载到内存

**关键机制：**
- **Page Out：** 核心记忆满时，把最旧的归档
- **Page In：** 当前任务需要某条归档记忆时，召回

#### 代码示例：简化版 MemGPT

```python
from dataclasses import dataclass, field
from collections import deque

@dataclass
class MemGPTState:
    """简化版 MemGPT 状态"""
    core_memory: deque = field(default_factory=lambda: deque(maxlen=10))  # 核心记忆（容量 10）
    archive_memory: list = field(default_factory=list)                    # 归档记忆
    max_core_size: int = 10

    def add(self, item: str):
        """添加记忆，满了自动 page out"""
        if len(self.core_memory) >= self.max_core_size:
            # Page Out：把最旧的归档
            oldest = self.core_memory[0]  # deque 自动会丢弃，但我们要先归档
            self.archive_memory.append(oldest)
        self.core_memory.append(item)

    def recall(self, query: str, llm=None) -> list[str]:
        """从归档记忆召回相关的到核心"""
        if not self.archive_memory:
            return []
        # 简化版：用关键词匹配。真实场景用 embedding 检索
        relevant = [m for m in self.archive_memory if query.lower() in m.lower()]
        for item in relevant:
            if item not in self.core_memory:
                self.add(item)  # 会触发 page out
        return relevant

    def get_context(self) -> str:
        """获取当前核心记忆作为 Context"""
        return "\n".join(f"- {m}" for m in self.core_memory)

# 使用示例
memory = MemGPTState(max_core_size=5)
for i in range(8):
    memory.add(f"事件 {i}：用户说了某某")

print("核心记忆：")
print(memory.get_context())
print(f"\n归档记忆：{memory.archive_memory}")
print(f"\n召回事件 0：{memory.recall('事件 0')}")
```

#### 今日任务

- [ ] 实现简化版 MemGPT（上面的代码）
- [ ] 把它集成到 Week 3 的 Agent 里
- [ ] 测试：连续聊 20+ 条，观察哪些被归档、哪些被召回
- [ ] 对比"有 MemGPT 机制" vs "只有滑动窗口"的对话连贯性

#### 自检

- [ ] 我理解核心记忆和归档记忆的区别
- [ ] 我能实现"自动 Page Out"
- [ ] 我能实现"按需 Page In（召回）"

---

### Day 6（周六）：整合 — 给 Week 3 Agent 加完整记忆

**学习目标：** 把三种记忆（短期 / 长期 / 实体）整合到 LangGraph Agent 中。

#### 项目要求

**改造 Week 3 的 Blog Workflow：**
- **短期记忆：** 用 Token 预算管理对话历史
- **长期记忆：** 用向量库记住用户的历史问题和偏好
- **实体记忆：** 用 UserProfile 记住用户画像

**State 扩展：**
```python
class MemoirizedAgentState(TypedDict):
    messages: Annotated[list, add]
    user_id: str                          # 用于区分不同用户
    short_term_context: str               # 滑动窗口后的近期上下文
    retrieved_long_term: list[str]        # 检索到的长期记忆
    user_profile_snapshot: dict           # 用户画像快照
    current_task: str
    response: str
```

**新增 Node：**
- `memory_retrieval_node`：开始时检索相关记忆
- `memory_update_node`：结束时更新记忆

#### 今日任务

- [ ] 设计带记忆的 State 和 Graph 结构
- [ ] 实现 `memory_retrieval_node`（开始时检索）
- [ ] 实现 `memory_update_node`（结束时更新）
- [ ] 跑通"跨会话测试"：第一次告诉信息，第二次问，第三次回忆
- [ ] 在 LangSmith 看 trace，观察记忆如何被使用

---

### Day 7（周日）：复盘 + 记忆策略决策

**学习目标：** 总结记忆系统，形成自己的"记忆策略决策框架"。

#### 今日任务

- [ ] 给 Day 6 的 Agent 写 3 个集成测试（跨会话记忆测试）
- [ ] 在 `notes/week-4-notes.md` 写一篇 500 字复盘
- [ ] **画一张记忆系统决策图：**
  - 什么场景用短期记忆？
  - 什么场景用长期记忆？
  - 什么场景用实体记忆？
  - 什么场景用 MemGPT 思路？
- [ ] 在 [phase-4-agent-core-langgraph.md](./phase-4-agent-core-langgraph.md) 勾选 Week 4 完成项

#### 周末复盘问题

1. 没有"记忆"的 Agent 和有"记忆"的 Agent，用户体验差异有多大？
2. 我做记忆系统时，最大的挑战是什么？（容量？相关性？时效性？）
3. MemGPT 的"分层 + 溢出"思路，能用在前端应用的什么地方？
4. 如果要做多用户系统，我的记忆架构要怎么扩展？
5. 向量库记忆的"检索质量"受什么因素影响？我会怎么优化？

---

## Week 5 - 整合项目：研究助手 Agent

> **本周目标：** 综合应用 LangGraph + 工具调用 + RAG + 记忆，做出作品集项目 #2 雏形
> **核心心智模型：** 真实的 Agent 项目 = 80% 工程化 + 20% 算法
> **产出物：** 可演示、有评测、有 README 的研究助手 Agent

### Day 1（周一）：项目规划 + State 设计

**学习目标：** 学会"先设计后实现"的 Agent 项目方法论。

#### 项目定义

**研究助手 Agent 功能：**
- 接收研究问题（如"对比 React Server Components 和传统 SSR 的优劣"）
- 自动规划研究步骤
- 并行 / 串行搜索多个来源
- 阅读和对比信息
- 综合输出结构化研究报告

**架构设计：**
```
用户问题
    ↓
[Planner Node]  ← 规划研究步骤
    ↓
[Researcher Node]  ← Web Search + RAG（并行多个）
    ↓
[Synthesizer Node]  ← 综合信息起草报告
    ↓
[Reviewer Node]  ← Critic，检查质量
    ↓
   通过？
    ↓ 是 → [Output Node] → 输出报告
    ↓ 否 → 回到 Researcher（带反馈）
```

#### 今日任务

- [ ] 写 `project-brief.md`：明确项目目标、用户故事、验收标准
- [ ] 设计完整 State schema（参考下面）
- [ ] 画 Graph 流程图（用 Mermaid 或纸笔）
- [ ] 列出所有需要的工具（搜索、抓网页、RAG、打分）

**State 设计参考：**
```python
class ResearchAgentState(TypedDict):
    # 输入
    question: str
    user_id: str

    # 规划阶段
    research_plan: list[str]          # 子问题列表
    current_sub_question_idx: int

    # 研究阶段
    search_results: list[dict]        # [{sub_q, source, content}]
    failed_sources: list[str]

    # 综合阶段
    draft_report: str
    report_outline: list[str]

    # 审校阶段
    review_score: int                 # 0-100
    review_feedback: str
    review_passed: bool

    # 控制
    iteration: int
    max_iterations: int
    cost_tracker: dict                # {tokens, api_calls, dollars}

    # 输出
    final_report: str
    references: list[dict]
```

#### 自检

- [ ] 我有完整的项目 brief
- [ ] 我的 State schema 覆盖了所有阶段
- [ ] 我画出了 Graph 流程图

---

### Day 2（周二）：核心 Node 实现

**学习目标：** 实现 Planner、Researcher、Synthesizer 三个核心 Node。

#### 代码示例：Planner Node

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)

def planner_node(state: ResearchAgentState) -> dict:
    """规划研究步骤：把大问题拆成子问题"""
    prompt = ChatPromptTemplate.from_template("""
你是一个研究规划专家。把以下研究问题拆成 3-5 个可独立搜索的子问题。

研究问题：{question}

要求：
- 子问题应该覆盖问题的不同方面
- 每个子问题应该能通过 1-2 次搜索回答
- 返回 JSON 数组，如 ["子问题1", "子问题2", ...]
""")
    chain = prompt | llm
    response = chain.invoke({"question": state["question"]})

    import json
    try:
        sub_questions = json.loads(response.content)
    except json.JSONDecodeError:
        sub_questions = [state["question"]]  # fallback

    return {
        "research_plan": sub_questions,
        "current_sub_question_idx": 0,
        "search_results": [],
        "iteration": state.get("iteration", 0) + 1,
    }

def researcher_node(state: ResearchAgentState) -> dict:
    """研究单个子问题（每次处理一个）"""
    idx = state["current_sub_question_idx"]
    if idx >= len(state["research_plan"]):
        return {}

    sub_q = state["research_plan"][idx]
    # 这里用真实搜索工具（Tavily / SerpAPI）
    search_result = search_web(sub_q)

    return {
        "search_results": state["search_results"] + [{
            "sub_question": sub_q,
            "source": "web_search",
            "content": search_result,
        }],
        "current_sub_question_idx": idx + 1,
    }
```

#### 今日任务

- [ ] 实现 `planner_node`：能用 LLM 把问题拆成子问题
- [ ] 实现 `researcher_node`：能调用真实搜索工具
- [ ] 实现 `synthesizer_node`：能把多个搜索结果综合成草稿
- [ ] 单元测试每个 Node（Mock LLM 和搜索）

#### 自检

- [ ] 三个核心 Node 都能独立运行
- [ ] 每个 Node 都有单元测试
- [ ] Planner 能合理拆解 3-5 个测试问题

---

### Day 3（周三）：Graph 组装 + 条件分支

**学习目标：** 把所有 Node 连成完整的 Graph，实现审校循环。

#### 代码示例

```python
from langgraph.graph import StateGraph, START, END

# 构建完整 Graph
graph = StateGraph(ResearchAgentState)

# 添加所有 Node
graph.add_node("planner", planner_node)
graph.add_node("researcher", researcher_node)
graph.add_node("synthesizer", synthesizer_node)
graph.add_node("reviewer", reviewer_node)
graph.add_node("finalizer", finalizer_node)

# 入口
graph.add_edge(START, "planner")

# Planner → Researcher
graph.add_edge("planner", "researcher")

# Researcher 循环：还有子问题就继续，没有就去综合
def should_continue_research(state: ResearchAgentState) -> str:
    if state["current_sub_question_idx"] < len(state["research_plan"]):
        return "continue"
    return "synthesize"

graph.add_conditional_edges(
    "researcher",
    should_continue_research,
    {"continue": "researcher", "synthesize": "synthesizer"}
)

# Synthesizer → Reviewer
graph.add_edge("synthesizer", "reviewer")

# Reviewer 循环：通过就定稿，不通过就重新研究（带反馈）
def should_revise(state: ResearchAgentState) -> str:
    if state["review_passed"]:
        return "finalize"
    if state["iteration"] >= state["max_iterations"]:
        return "finalize"  # 超过最大次数，强制结束
    return "revise"

graph.add_conditional_edges(
    "reviewer",
    should_revise,
    {"finalize": "finalizer", "revise": "researcher"}
)

# Finalizer → END
graph.add_edge("finalizer", END)

# 编译
from langgraph.checkpoint.memory import MemorySaver
app = graph.compile(checkpointer=MemorySaver())
```

#### 今日任务

- [ ] 组装完整 Graph
- [ ] 实现两个 Conditional Edge（研究循环 + 审校循环）
- [ ] 加上 `max_iterations` 防止无限循环
- [ ] 跑通一个完整测试：「对比 React Server Components 和 SSR」

#### 自检

- [ ] Graph 能从 START 跑到 END
- [ ] 条件分支工作正常（审校不通过会回到 Researcher）
- [ ] 有最大迭代保护

---

### Day 4（周四）：Reviewer + 质量评测

**学习目标：** 实现 Reviewer 节点，学会用 LLM-as-Judge 做质量评测。

#### 核心概念

**Reviewer 的核心任务：**
- 检查报告是否回答了原问题
- 检查信息是否准确（对比 sources）
- 检查结构是否清晰
- 检查是否有遗漏

**LLM-as-Judge 的关键：**
- 给明确的评分维度（不要模糊的"好不好"）
- 给参考答案或 rubric
- 让 LLM 先输出推理，再输出分数
- 多次采样取平均（减少随机性）

#### 代码示例

```python
def reviewer_node(state: ResearchAgentState) -> dict:
    """审校节点：给报告打分"""
    prompt = f"""你是一个严格的研究报告审校员。请评估以下报告。

原始问题：{state['question']}

报告内容：
{state['draft_report']}

参考信息：
{[r['content'][:200] for r in state['search_results']]}

请按以下维度评分（0-100）：
1. 相关性：是否回答了原问题？
2. 准确性：信息是否和参考一致？
3. 完整性：是否覆盖了主要方面？
4. 结构性：组织是否清晰？

返回 JSON：
{{
  "scores": {{"relevance": 0-100, "accuracy": 0-100, "completeness": 0-100, "structure": 0-100}},
  "average_score": 0-100,
  "feedback": "具体的改进建议",
  "passed": true/false  // 平均分 >= 75 才通过
}}
"""
    response = llm.invoke(prompt)
    import json
    try:
        result = json.loads(response.content)
        score = result.get("average_score", 0)
        return {
            "review_score": score,
            "review_feedback": result.get("feedback", ""),
            "review_passed": result.get("passed", False) or score >= 75,
        }
    except json.JSONDecodeError:
        return {"review_score": 0, "review_feedback": "解析失败", "review_passed": False}
```

#### 今日任务

- [ ] 实现 `reviewer_node`
- [ ] 实现 `finalizer_node`（格式化输出 + 生成 references）
- [ ] 跑 3 个测试问题，观察审校反馈质量
- [ ] 调优评分阈值（75 是否合理？）

#### 自检

- [ ] Reviewer 能给出结构化反馈
- [ ] 报告不达标时能回到 Researcher 带反馈修改
- [ ] 最终报告格式清晰、有引用

---

### Day 5（周五）：评测集 + 成本监控

**学习目标：** 给 Agent 建立评测集和成本监控，这是"工程化"的核心。

#### 今日任务

**评测集（至少 10 个问题）：**
- [ ] 准备 10 个不同类型的研究问题
- [ ] 每个问题写"理想答案要点"（3-5 个关键点）
- [ ] 跑 Agent，对比输出是否覆盖要点
- [ ] 用 LLM-as-Judge 自动打分
- [ ] 生成评测报告（表格 + 平均分）

**成本监控：**
```python
@dataclass
class CostTracker:
    """成本追踪器"""
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    usd_spent: float = 0.0

    # Claude Sonnet 4.5 的价格（示例，以实际为准）
    PRICE_INPUT_PER_1M = 3.0
    PRICE_OUTPUT_PER_1M = 15.0

    def add_call(self, input_tokens: int, output_tokens: int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.api_calls += 1
        self.usd_spent += (
            input_tokens / 1_000_000 * self.PRICE_INPUT_PER_1M
            + output_tokens / 1_000_000 * self.PRICE_OUTPUT_PER_1M
        )

    def summary(self) -> str:
        return (
            f"API 调用：{self.api_calls} 次 | "
            f"Tokens：{self.input_tokens + self.output_tokens:,} "
            f"(in:{self.input_tokens:,}/out:{self.output_tokens:,}) | "
            f"花费：${self.usd_spent:.4f}"
        )
```

- [ ] 给每个 Node 加上成本追踪
- [ ] 每次运行后打印 `cost_tracker.summary()`
- [ ] 统计 10 个问题的平均成本

#### 自检

- [ ] 评测集有 10+ 个问题
- [ ] 每个 Agent 运行都有成本统计
- [ ] 我知道"一份研究报告平均花多少钱"

---

### Day 6（周六）：项目打磨 + README

**学习目标：** 把项目打磨成"作品集级别"，重点写好 README。

#### 今日任务

**项目打磨：**
- [ ] 清理代码，确保 100% 类型注解
- [ ] 加上完整的错误处理（搜索失败、LLM 失败、解析失败）
- [ ] 支持流式输出（让用户看到研究过程）
- [ ] 加上 CLI 入口（`python -m research_agent "你的问题"`）
- [ ] 准备 3 个高质量的示例输出（保存到 `examples/`）

**README 必须包含：**
- [ ] 项目介绍（一句话说明是什么、解决什么问题）
- [ ] 架构图（Mermaid 画的 Graph 流程）
- [ ] Quick Start（5 分钟内能跑起来）
- [ ] 3 个示例输出
- [ ] 评测结果（平均分 + 成本）
- [ ] 局限性和未来改进方向
- [ ] 技术栈说明

**目录结构：**
```
phase-4/
└── research-agent/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── agent.py          # Graph 定义
    │   ├── nodes/            # 各个 Node
    │   ├── tools/            # 工具集
    │   ├── state.py          # State 定义
    │   ├── prompts/          # Prompt 模板
    │   ├── memory.py         # 记忆系统
    │   └── cli.py            # CLI 入口
    ├── examples/
    │   ├── example-1.md
    │   ├── example-2.md
    │   └── example-3.md
    ├── eval/
    │   ├── dataset.json      # 评测集
    │   └── results.md        # 评测结果
    └── tests/
```

---

### Day 7（周日）：阶段总结 + 下一步规划

**学习目标：** 总结整个第 4 阶段，为第 5 阶段做准备。

#### 今日任务

- [ ] 跑一次完整的 10 题评测，记录分数和成本
- [ ] 在 `notes/phase-4-summary.md` 写一篇 1000 字的阶段总结
- [ ] 把项目推到 GitHub（公开仓库，作为作品集）
- [ ] 录一个 3-5 分钟的 Demo 视频（展示 Agent 处理一个研究问题）
- [ ] 在 [phase-4-agent-core-langgraph.md](./phase-4-agent-core-langgraph.md) 勾选所有完成项

#### 阶段总结复盘问题

回答以下问题（写在 notes 里）：

1. **关于 Agent 本质：** 经过这 5 周，我对"Agent 是状态机"的理解有多深？能向别人讲清楚吗？

2. **关于框架选择：** 手写 / LangChain / LangGraph，我各自的判断标准是什么？

3. **关于记忆系统：** 我做的记忆系统最让你骄傲的部分是什么？最大的遗憾是什么？

4. **关于工程化：** 评测、监控、错误处理这些"无聊但重要"的事，我的体会是什么？

5. **关于 React 思维迁移：** 前端经验在哪些地方最有用？哪些地方反而是障碍？

6. **关于下一步：** 第 5 阶段要学 Multi-Agent，我最想解决本阶段项目的什么问题？

---

## 常见卡点速查表

| 卡点 | 现象 | 解决方案 |
|------|------|---------|
| Agent 死循环 | 不断调同一个工具 | 加 `max_steps` + `max_iterations`，记录已调用工具 |
| LLM 不调工具 | 直接回答应该查资料的问题 | 检查工具 `description`，加 Few-shot 示例 |
| LangGraph 状态不更新 | Node 返回值没生效 | 检查是否用 `Annotated[list, add]`，返回 dict 的 key 是否匹配 |
| Conditional Edge 报错 | "Could not find node" | 检查 `add_conditional_edges` 的第三个参数映射是否完整 |
| Tool Use 消息结构错误 | "tool_use_id mismatch" | 确认 `tool_result` 和 `tool_use` 的 id 一一对应 |
| Human-in-the-Loop 不工作 | interrupt 没触发 | 确认编译时传了 `checkpointer` |
| 记忆检索质量差 | 召回的不相关 | 检查 Embedding 质量，尝试换模型；检查 query 是否合适 |
| LangSmith 看不到 trace | Project 为空 | 检查环境变量 `LANGCHAIN_TRACING_V2=true` 和 API Key |
| Checkpoint 恢复失败 | "Thread not found" | 确认 `thread_id` 一致，确认用了同一个 checkpointer 实例 |
| 成本超预期 | Token 消耗爆炸 | 加 Token 预算检查，用摘要压缩，换更便宜的模型做简单任务 |
| LangChain 版本不兼容 | Import 报错 | 锁定版本，用 `uv pip install langchain==0.3.x` |
| Async / Sync 混用 | "coroutine never awaited" | 统一用 async 或 sync，LangGraph 推荐 async |

## 推荐速查资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph 示例库](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [MemGPT 论文](https://arxiv.org/abs/2310.08560)
- [LangSmith 文档](https://docs.smith.langchain.com/)
- [LangChain Hub](https://smith.langchain.com/hub)

## 完成标准

第 4 阶段结束时，你应该能：

### 技能掌握

- [ ] 能纯手写 ReAct Agent（不用框架，100 行以内）
- [ ] 能解释 LangChain Agent Executor 的内部工作原理
- [ ] 能用 LangGraph 实现复杂状态机（条件分支、循环、Human-in-the-Loop）
- [ ] 能实现短期 / 长期 / 实体三种记忆
- [ ] 能用 LangSmith 做 Agent 的可观测性
- [ ] 能用 LLM-as-Judge 做质量评测

### 项目产出

- [ ] 手写 ReAct Agent 项目（Week 1）
- [ ] LangChain 版 Agent + 决策文档（Week 2）
- [ ] LangGraph 多步骤工作流项目（Week 3）
- [ ] 带完整记忆系统的 Agent（Week 4）
- [ ] **研究助手 Agent（作品集项目 #2 雏形）**（Week 5）
  - [ ] GitHub 公开仓库
  - [ ] 完整 README + 架构图
  - [ ] 3+ 个示例输出
  - [ ] 10+ 题评测集 + 评测报告
  - [ ] 成本分析

### 核心认知

- [ ] 我深刻理解"Agent = LLM 驱动的状态机"
- [ ] 我有"状态优先"的设计直觉（先设计 State，再设计 Node）
- [ ] 我有"可观测性优先"的工程习惯（先接 trace，再写逻辑）
- [ ] 我有"渐进复杂度"的判断力（先单 Agent，遇到瓶颈再 Multi-Agent）

**准备好了就进入第 5 阶段：[Multi-Agent + 工具生态](./phase-5-multi-agent-tool-ecosystem.md)**
