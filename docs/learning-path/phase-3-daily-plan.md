# 第 3 阶段每日计划：函数调用 + RAG 基础

> **周期：** 5 周（Phase 3 / Week 1-5，独立编号，非全局周号）
> **每日投入：** 约 1-1.5 小时（工作日）/ 2-3 小时（周末）
> **产出物：** 多工具聊天机器人 + 文档问答系统 + 个人知识助手雏形（作品集 #1）
> **配套文档：** [phase-3-function-calling-rag.md](./phase-3-function-calling-rag.md)

## 进度追踪

- [ ] Week 1 - Function Calling 深入
  - [ ] Day 1 OpenAI Function Calling 基础
  - [ ] Day 2 Anthropic Tool Use 协议对比
  - [ ] Day 3 工具定义最佳实践
  - [ ] Day 4 多工具编排与并行调用
  - [ ] Day 5 工具执行的工程化
  - [ ] Day 6 项目实战：多工具聊天机器人
  - [ ] Day 7 测试 + 周复盘
- [ ] Week 2 - RAG 基础：Embedding 与向量数据库
  - [ ] Day 1 Embedding 原理
  - [ ] Day 2 OpenAI Embedding API 实操
  - [ ] Day 3 Chroma 向量数据库入门
  - [ ] Day 4 Qdrant 对比与选型
  - [ ] Day 5 相似度搜索算法
  - [ ] Day 6 项目实战：语义搜索引擎
  - [ ] Day 7 效果对比 + 周复盘
- [ ] Week 3 - RAG 流水线
  - [ ] Day 1 文档加载（LangChain Loaders）
  - [ ] Day 2 固定长度与递归切分
  - [ ] Day 3 语义切分 + 父子文档
  - [ ] Day 4 完整 RAG 流水线
  - [ ] Day 5 引用溯源
  - [ ] Day 6 项目实战：文档问答机器人 v1
  - [ ] Day 7 测试 + 周复盘
- [ ] Week 4 - RAG 进阶：检索优化
  - [ ] Day 1 Hybrid Search（BM25 + 向量）
  - [ ] Day 2 Reranking 重排序
  - [ ] Day 3 Query 改写技术
  - [ ] Day 4 HyDE 与 Multi-Query
  - [ ] Day 5 RAGAS 评测框架
  - [ ] Day 6 项目实战：RAG 策略对比
  - [ ] Day 7 对比报告 + 周复盘
- [ ] Week 5 - 阶段性整合项目
  - [ ] Day 1 项目规划与架构设计
  - [ ] Day 2 知识库管理模块
  - [ ] Day 3 RAG + Function Calling 整合
  - [ ] Day 4 跨会话记忆
  - [ ] Day 5 日志、错误处理、LangSmith trace
  - [ ] Day 6 完整项目开发 + 评测集
  - [ ] Day 7 README + 作品集整理 + 阶段总复盘

## 学习方法

1. **理论 + 实践交替** — 每天先理解概念，再敲代码验证
2. **工具当 API 设计** — 工具定义就是接口设计，参数描述就是文档
3. **切分决定 RAG 上限** — 别一上来就调模型，先看切分对不对
4. **评测驱动迭代** — 沿用 Phase 2 的评测方法，所有改动都要跑评测
5. **作品集思维** — Week 5 的项目要能展示，不是"跑通就行"

## 环境准备（Day 0，提前一晚）

```bash
# 1. 进入第 3 阶段目录
cd phase-3/

# 2. 初始化主项目
uv init agent-toolkit
cd agent-toolkit
uv add openai anthropic pydantic httpx tenacity python-dotenv

# 3. RAG 相关依赖（后续按周添加）
uv add chromadb qdrant-client langchain langchain-community
uv add sentence-transformers rank-bm25 cohere
uv add ragas  # RAG 评测

# 4. LangSmith（可选，但强烈推荐）
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=lsv2_xxx
export LANGCHAIN_PROJECT=phase-3-agent

# 5. 配置 API Key（沿用第 2 阶段）
export OPENAI_API_KEY=sk-xxx
export ANTHROPIC_API_KEY=sk-ant-xxx

# 6. VS Code 推荐扩展
# - SQLite Viewer（查看 Chroma 底层存储）
# - Thunder Client（测试 API）
```

**完成标志：** 能跑通一次 OpenAI Function Calling 调用，能往 Chroma 插入 1 条向量。

---

# Week 1 - Function Calling 深入

> **本周目标：** 把"让 LLM 调用工具"这件事从"会用"升级到"工程化"。

## Day 1（周一）：OpenAI Function Calling 基础

**学习目标：** 掌握 OpenAI Function Calling 的完整调用流程。

### 核心概念

| 概念 | 说明 |
|------|------|
| `tools` | 工具列表，每个工具是一个 JSON Schema |
| `tool_choice` | 控制模型是否调用工具（auto / none / 强制指定）|
| `tool_calls` | 模型返回的 tool 调用请求 |
| `tool` role | 把工具执行结果回传给模型的对话角色 |

**完整流程：**
```
用户消息 → 模型决定调用工具 → 返回 tool_calls
                                    ↓
                        你执行工具，得到结果
                                    ↓
                  把结果以 role=tool 回传 → 模型生成最终回答
```

### 学习内容

**1. 最简 Function Calling 示例**
```python
from openai import OpenAI
import json

client = OpenAI()

# 定义工具（JSON Schema）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，如 '北京'、'上海'",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位，默认摄氏度",
                    },
                },
                "required": ["city"],
            },
        },
    }
]

# 工具实现
def get_weather(city: str, unit: str = "celsius") -> str:
    """实际项目里这里调用真实天气 API"""
    mock = {"北京": "25°C 晴", "上海": "28°C 多云", "广州": "30°C 雨"}
    return mock.get(city, "未知城市")

# 完整调用流程
def chat_with_tools(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]

    # 第 1 步：模型决定是否调用工具
    response = client.chat.completions.create(
        model="gpt-5-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto / none / required
    )
    msg = response.choices[0].message

    # 第 2 步：如果模型决定调用工具
    if msg.tool_calls:
        messages.append(msg)  # 把 assistant 的 tool_calls 加入历史
        for tool_call in msg.tool_calls:
            args = json.loads(tool_call.function.arguments)
            print(f"[调用工具] {tool_call.function.name}({args})")

            # 执行工具
            result = get_weather(**args)

            # 把结果回传给模型
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # 第 3 步：模型根据工具结果生成最终回答
        final = client.chat.completions.create(
            model="gpt-5-latest",
            messages=messages,
        )
        return final.choices[0].message.content

    return msg.content

# 测试
print(chat_with_tools("北京今天天气怎么样？"))
print(chat_with_tools("你好，你是谁？"))  # 不会调用工具
```

**2. tool_choice 的三种模式**
```python
# auto（默认）：模型自己决定
client.chat.completions.create(..., tool_choice="auto")

# none：禁止调用工具
client.chat.completions.create(..., tool_choice="none")

# required：强制调用至少一个工具
client.chat.completions.create(..., tool_choice="required")

# 指定具体工具：强制调用某个工具
client.chat.completions.create(
    ...,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)
```

### 今日任务

- [ ] 跑通上面的完整 Function Calling 代码
- [ ] 自己加一个工具（如 `get_time`），让模型能查时间
- [ ] 测试 `tool_choice` 的三种模式，观察模型行为差异
- [ ] 思考题：为什么工具描述（description）这么重要？

### 自检

- [ ] 我能解释 Function Calling 的完整流程（3 步）
- [ ] 我知道 `tool_choice` 的三种模式各有什么用
- [ ] 我理解 `role=tool` 的消息必须带 `tool_call_id`

---

## Day 2（周二）：Anthropic Tool Use 协议对比

**学习目标：** 理解 Anthropic 的 Tool Use 协议，能对比两套方案的差异。

### 核心对比

| 维度 | OpenAI | Anthropic |
|------|--------|-----------|
| 工具定义位置 | `tools` 参数 | `tools` 参数（结构类似）|
| 调用返回 | `message.tool_calls` 数组 | `content` 中的 `tool_use` block |
| 结果回传 | `role=tool` 消息 | `role=user` + `tool_result` block |
| 多轮工具调用 | 自动（靠消息历史）| 自动（靠消息历史）|
| 设计哲学 | 函数调用语义 | content block 组合（更通用）|

**关键差异：**
- Anthropic 把 tool_use 当作"内容块"的一种（和文本块并列）
- 这种设计在后续多模态、思考链等场景更灵活
- 但对前端工程师来说，OpenAI 的 API 更直观

### 学习内容

**1. Anthropic Tool Use 完整示例**
```python
from anthropic import Anthropic
import json

client = Anthropic()

# 工具定义（和 OpenAI 几乎一样）
tools = [
    {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名",
                },
            },
            "required": ["city"],
        },
    }
]

def get_weather(city: str) -> str:
    mock = {"北京": "25°C 晴", "上海": "28°C 多云"}
    return mock.get(city, "未知")

def chat_with_anthropic(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]

    response = client.messages.create(
        model="claude-sonnet-4-5-latest",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    # Anthropic 的返回是 content blocks 列表
    # 可能包含：[TextBlock, ToolUseBlock, TextBlock, ...]
    if response.stop_reason == "tool_use":
        # 找到 tool_use block
        toolUses = [b for b in response.content if b.type == "tool_use"]

        # 把 assistant 的完整 content 加入历史
        messages.append({"role": "assistant", "content": response.content})

        for tu in toolUses:
            print(f"[调用工具] {tu.name}({tu.input})")
            result = get_weather(**tu.input)

            # 用 tool_result block 回传
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": result,
                    }
                ],
            })

        # 第 2 轮调用：模型根据结果生成最终回答
        final = client.messages.create(
            model="claude-sonnet-4-5-latest",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )
        return final.content[0].text

    # 没调用工具，直接返回文本
    return response.content[0].text

print(chat_with_anthropic("北京天气如何？"))
```

**2. 写一个统一抽象层**
```python
from typing import Callable, Any

class UnifiedToolCaller:
    """统一封装 OpenAI 和 Anthropic 的工具调用"""

    def __init__(self, provider: str = "openai"):
        self.provider = provider
        if provider == "openai":
            from openai import OpenAI
            self.client = OpenAI()
        else:
            from anthropic import Anthropic
            self.client = Anthropic()

    def convert_tool_schema(self, tool: dict) -> dict:
        """把统一的 schema 转成各家格式"""
        if self.provider == "openai":
            return {"type": "function", "function": tool}
        else:
            return {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"],
            }
```

### 今日任务

- [ ] 跑通 Anthropic 的 Tool Use 代码
- [ ] 对比同一个问题，两家模型的工具调用行为差异
- [ ] 实现 `UnifiedToolCaller` 的完整版（至少能跑通一轮）
- [ ] 思考题：为什么 Anthropic 把 tool_use 设计成 content block？

### 自检

- [ ] 我能解释 OpenAI 和 Anthropic 工具调用协议的核心差异
- [ ] 我知道 `stop_reason == "tool_use"` 在 Anthropic 里的含义
- [ ] 我能写出兼容两家的工具定义格式

---

## Day 3（周三）：工具定义最佳实践

**学习目标：** 学会写高质量的工具定义，这是模型准确调用的关键。

### 核心原则

**工具定义 = API 设计**
- 模型就像一个"看文档编程"的初级工程师
- 你的描述越清晰，模型调用越准确
- **描述写得烂，模型就乱调**

### 学习内容

**1. 用 Pydantic 自动生成 JSON Schema**
```python
from pydantic import BaseModel, Field
from typing import Literal
import json

class WeatherQuery(BaseModel):
    """天气查询参数"""
    city: str = Field(
        ...,
        description="城市名，支持中英文，如 '北京'、'Shanghai'"
    )
    unit: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="温度单位：celsius 摄氏度，fahrenheit 华氏度"
    )
    date: str | None = Field(
        default=None,
        description="日期，格式 YYYY-MM-DD，默认今天。支持 '明天'、'后天'"
    )

# 自动转 JSON Schema
schema = WeatherQuery.model_json_schema()
print(json.dumps(schema, indent=2, ensure_ascii=False))

# 拼成 OpenAI 工具格式
tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市指定日期的天气。支持未来 7 天预报。",
        "parameters": WeatherQuery.model_json_schema(),
    }
}
```

**2. 工具命名与描述的规范**

```python
# ❌ 差的工具定义
bad_tool = {
    "name": "search",  # 太泛
    "description": "搜索",  # 没说明搜什么
    "parameters": {
        "type": "object",
        "properties": {
            "q": {"type": "string"},  # 参数名不清晰
        },
    },
}

# ✅ 好的工具定义
good_tool = {
    "name": "search_web",  # 动词 + 名词
    "description": (
        "搜索互联网获取最新信息。"
        "适用场景：查新闻、查实时数据（股价、天气、比分）、"
        "查模型训练数据截止后的事件。"
        "不适用：数学计算（用 calculator）、查本地知识库（用 search_kb）。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词，用自然语言描述要查的内容，如 '2024 年诺贝尔和平奖得主'"
            },
            "max_results": {
                "type": "integer",
                "description": "返回结果数量，默认 5，最大 20",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}
```

**3. 帮助模型区分相似工具（关键技巧）**
```python
# 当有多个相似工具时，description 里要明确"什么时候用我，什么时候不用"
tools = [
    {
        "name": "calculator",
        "description": (
            "精确的数学计算。支持加减乘除、幂运算、三角函数。"
            "用这个而不是自己算，避免计算错误。"
            "示例：calculator(expression='25 * 17 + 3')"
        ),
        ...
    },
    {
        "name": "search_kb",
        "description": (
            "搜索用户的个人知识库（笔记、文档）。"
            "当用户问'我的笔记里有没有...'、'我之前写过...'时用这个。"
            "不要用这个搜索互联网。"
        ),
        ...
    },
    {
        "name": "search_web",
        "description": (
            "搜索互联网。当用户问时事、最新数据、模型不知道的事时用。"
        ),
        ...
    },
]
```

### 今日任务

- [ ] 用 Pydantic 为 3 个工具定义参数模型
- [ ] 自动生成 JSON Schema 并拼成 OpenAI 工具格式
- [ ] 对比"好描述"和"烂描述"对模型调用准确率的影响（至少测 5 个问题）
- [ ] 思考题：为什么"什么时候不用"比"什么时候用"更重要？

### 自检

- [ ] 我会用 Pydantic 自动生成 JSON Schema
- [ ] 我的工具命名遵循"动词_名词"规范
- [ ] 我的工具 description 包含"适用"和"不适用"场景

---

## Day 4（周四）：多工具编排与并行调用

**学习目标：** 掌握多工具场景下的编排，包括并行调用和依赖处理。

### 核心概念

**并行调用（Parallel Function Calling）：**
- GPT-4 / GPT-4o 支持一次返回多个 tool_calls
- 适合：无依赖的工具（如同时查北京和上海的天气）
- 你可以并行执行，再一起回传

**工具依赖：**
- 如"先查用户 ID，再用 ID 查订单"
- 模型会自动分多轮调用
- 你要做的是：每轮正确回传结果

### 学习内容

**1. 多工具并行调用**
```python
from openai import OpenAI
import json
import asyncio

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "查询汇率，从 from 货币到 to 货币",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "源货币代码，如 USD"},
                    "to_currency": {"type": "string", "description": "目标货币代码，如 CNY"},
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
            },
        },
    },
]

def get_weather(city: str) -> str:
    return {"北京": "25°C", "上海": "28°C"}.get(city, "未知")

def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    rates = {("USD", "CNY"): "7.2", ("EUR", "CNY"): "7.8"}
    return rates.get((from_currency, to_currency), "未查到")

def calculator(expression: str) -> str:
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
        return f"错误：{e}"

TOOL_MAP = {
    "get_weather": get_weather,
    "get_exchange_rate": get_exchange_rate,
    "calculator": calculator,
}

async def execute_tools_parallel(tool_calls) -> list[dict]:
    """并行执行多个无依赖的工具"""
    async def run_one(tc):
        args = json.loads(tc.function.arguments)
        result = TOOL_MAP[tc.function.name](**args)
        return {
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result),
        }
    return await asyncio.gather(*[run_one(tc) for tc in tool_calls])

def multi_tool_chat(user_input: str, max_rounds: int = 5) -> str:
    messages = [{"role": "user", "content": user_input}]

    for _ in range(max_rounds):
        resp = client.chat.completions.create(
            model="gpt-5-latest",
            messages=messages,
            tools=tools,
        )
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        # 并行执行所有工具
        tool_results = asyncio.run(execute_tools_parallel(msg.tool_calls))
        messages.extend(tool_results)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"[并行调用] {tc.function.name}({args})")

    return "（达到最大轮数）"

# 测试：模型可能一次性调用多个工具
print(multi_tool_chat("北京和上海哪个温度高？同时告诉我 100 美元等于多少人民币？"))
```

**2. 工具依赖链**
```python
# 模型会自动分多轮处理依赖
# 例："帮我查用户 wsq 的订单，算一下总价"
# Round 1: get_user_id(username="wsq") → 12345
# Round 2: get_orders(user_id=12345) → [订单列表]
# Round 3: calculator(sum of order prices) → 总价
# Final: 综合回答
```

### 今日任务

- [ ] 跑通多工具并行调用代码
- [ ] 设计一个需要"依赖链"的问题（如"查某用户最近 3 笔订单的总价"）
- [ ] 观察：模型如何分多轮处理依赖
- [ ] 思考题：为什么不能把所有工具结果一次性塞给模型？

### 自检

- [ ] 我能实现并行工具调用
- [ ] 我理解工具依赖是怎么自动处理的
- [ ] 我知道什么时候用 `asyncio.gather` 加速

---

## Day 5（周五）：工具执行的工程化

**学习目标：** 把"能跑"的工具变成"能上线"的工具。

### 核心概念

**工程化要考虑的事：**
| 问题 | 方案 |
|------|------|
| 工具执行失败 | try/except + 错误回传给模型 |
| 工具超时 | timeout + 降级 |
| 偶发性失败 | 自动重试（tenacity）|
| 权限控制 | 工具白名单 |
| 调用审计 | 完整日志 |
| 资源限制 | rate limit、并发限制 |

### 学习内容

**1. 用 tenacity 做重试**
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

class TransientError(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(TransientError),
)
def call_external_api(url: str) -> dict:
    """带重试的 HTTP 调用"""
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(url)
            if r.status_code >= 500:
                raise TransientError(f"服务器错误: {r.status_code}")
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException as e:
        raise TransientError(f"超时: {e}") from e
```

**2. 完整的工程化工具执行框架**
```python
import logging
import time
import json
from typing import Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger("tool_executor")

@dataclass
class ToolCallRecord:
    """单次工具调用的完整记录"""
    tool_name: str
    arguments: dict
    result: Any = None
    error: str | None = None
    elapsed_sec: float = 0
    attempts: int = 1

class ToolExecutor:
    """工程化的工具执行器"""

    def __init__(self, tools: dict[str, Callable], timeout: int = 30):
        self.tools = tools
        self.timeout = timeout
        self.history: list[ToolCallRecord] = []

    def execute(self, tool_name: str, arguments: dict) -> str:
        """执行单个工具，带完整错误处理"""
        record = ToolCallRecord(tool_name=tool_name, arguments=arguments)
        start = time.time()

        # 1. 检查工具是否存在
        if tool_name not in self.tools:
            record.error = f"未知工具: {tool_name}"
            record.elapsed_sec = time.time() - start
            self.history.append(record)
            return f"错误：未知工具 {tool_name}"

        # 2. 执行
        try:
            result = self.tools[tool_name](**arguments)
            record.result = result
            logger.info(f"工具 {tool_name} 执行成功")
            return str(result)
        except TypeError as e:
            record.error = f"参数错误: {e}"
            return f"错误：参数不匹配 - {e}"
        except Exception as e:
            record.error = str(e)
            logger.exception(f"工具 {tool_name} 执行失败")
            # 把错误信息回传给模型，让它自己处理
            return f"工具执行出错: {type(e).__name__}: {e}"
        finally:
            record.elapsed_sec = time.time() - start
            self.history.append(record)

    def execute_tool_calls(self, tool_calls) -> list[dict]:
        """批量执行 OpenAI 格式的 tool_calls"""
        results = []
        for tc in tool_calls:
            args = json.loads(tc.function.arguments)
            output = self.execute(tc.function.name, args)
            results.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": output,
            })
        return results

    def summary(self) -> dict:
        """调用统计"""
        n = len(self.history)
        success = sum(1 for r in self.history if r.error is None)
        return {
            "total_calls": n,
            "success_rate": f"{success/n*100:.1f}%" if n else "N/A",
            "total_time_sec": round(sum(r.elapsed_sec for r in self.history), 2),
        }
```

**3. 错误信息的回传策略**
```python
# 关键：错误信息要回传给模型，让它"知道"并调整
# 不要直接抛异常中断对话

# 错误示例：直接抛
def bad_handler(tool_call):
    result = risky_operation()  # 可能抛异常
    return result  # 异常直接冒泡，对话崩溃

# 正确示例：捕获并回传
def good_handler(tool_call):
    try:
        result = risky_operation()
        return {"content": str(result)}
    except Exception as e:
        # 模型看到这个错误，可能会：重试 / 换工具 / 告诉用户
        return {"content": f"工具执行失败: {e}. 请尝试其他方法或告知用户。"}
```

### 今日任务

- [ ] 实现 `ToolExecutor` 类，集成到你的多工具代码中
- [ ] 故意制造 3 种错误（参数错、超时、工具不存在），看模型如何反应
- [ ] 用 `logging` 配置日志，把工具调用记录到文件
- [ ] 思考题：为什么把错误信息回传给模型，比直接抛异常更好？

### 自检

- [ ] 我会用 tenacity 做自动重试
- [ ] 我的 `ToolExecutor` 能处理 5+ 种错误场景
- [ ] 我理解"错误回传给模型"的工程价值

---

## Day 6（周六）：项目实战日 —— 多工具聊天机器人

**学习目标：** 把本周学的整合成一个完整的多工具聊天机器人。

### 项目：Toolkit Chatbot

**功能要求：**
- 支持多轮对话
- 至少 4 个工具：
  - `get_weather`：天气查询（调用免费 API 或 mock）
  - `calculator`：数学计算（沙箱 eval）
  - `get_time`：时间查询（支持时区）
  - `get_exchange_rate`：汇率查询
- 工程化：
  - 用 `ToolExecutor` 统一执行
  - 错误处理 + 重试
  - 完整日志
- 兼容 OpenAI 和 Anthropic 两套协议（用 `UnifiedToolCaller`）

**目录结构：**
```
phase-3/
└── toolkit-chatbot/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── tools/
    │   │   ├── __init__.py
    │   │   ├── base.py           # Tool 基类
    │   │   ├── weather.py
    │   │   ├── calculator.py
    │   │   ├── time_tool.py
    │   │   └── exchange.py
    │   ├── executor.py           # ToolExecutor
    │   ├── agent.py              # 主 Agent
    │   ├── providers.py          # OpenAI / Anthropic 抽象
    │   └── cli.py                # CLI 入口
    ├── tests/
    │   ├── test_tools.py
    │   └── test_executor.py
    └── logs/
```

**核心代码：Tool 基类**
```python
# src/tools/base.py
from pydantic import BaseModel
from typing import Callable, Any

class Tool:
    """工具基类：把函数 + schema 打包"""
    def __init__(self, func: Callable, name: str, description: str, args_model: type[BaseModel]):
        self.func = func
        self.name = name
        self.description = description
        self.args_model = args_model

    def __call__(self, **kwargs) -> Any:
        # 用 Pydantic 校验参数
        validated = self.args_model(**kwargs)
        return self.func(**validated.model_dump())

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            }
        }

    def to_anthropic_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.args_model.model_json_schema(),
        }
```

**核心代码：Agent 主循环**
```python
# src/agent.py
from openai import OpenAI
from .executor import ToolExecutor

class ToolkitAgent:
    def __init__(self, tools: list, system_prompt: str, model: str = "gpt-5-latest"):
        self.client = OpenAI()
        self.model = model
        self.tools = {t.name: t for t in tools}
        self.tool_schemas = [t.to_openai_schema() for t in tools]
        self.system_prompt = system_prompt
        self.executor = ToolExecutor(self.tools)
        self.history: list[dict] = []

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        for round_idx in range(5):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas,
            )
            msg = resp.choices[0].message
            messages.append(msg)
            self.history.append({"role": "assistant", "content": msg.content or ""})

            if not msg.tool_calls:
                return msg.content or ""

            tool_results = self.executor.execute_tool_calls(msg.tool_calls)
            messages.extend(tool_results)
            # tool 消息不入 self.history，避免污染对话

        return "（达到最大轮数）"
```

### 今日任务

- [ ] 初始化项目：`uv init toolkit-chatbot`
- [ ] 实现 `Tool` 基类和 4 个具体工具
- [ ] 实现 `ToolExecutor` 和 `ToolkitAgent`
- [ ] CLI 支持多轮对话
- [ ] 跑通 5+ 轮对话，包含工具调用、错误处理、并行调用

---

## Day 7（周日）：测试 + 周复盘

**学习目标：** 给工具和 Agent 写测试，建立工程化习惯。

### 学习内容

**1. 测试工具**
```python
# tests/test_tools.py
import pytest
from src.tools.calculator import calculator, CalculatorArgs

def test_calculator_basic():
    assert calculator(expression="2 + 3") == "5"

def test_calculator_division():
    assert calculator(expression="10 / 4") == "2.5"

def test_calculator_invalid():
    result = calculator(expression="import os")
    assert "非法" in result or "错误" in result

def test_calculator_div_zero():
    result = calculator(expression="1 / 0")
    assert "错误" in result
```

**2. 测试 Agent（用 mock）**
```python
# tests/test_agent.py
import pytest
from unittest.mock import MagicMock, patch
from src.agent import ToolkitAgent

@pytest.fixture
def agent():
    return ToolkitAgent(tools=[...], system_prompt="test")

def test_agent_no_tool(agent):
    """不触发工具的对话"""
    with patch.object(agent.client.chat.completions, "create") as mock:
        mock.return_value.choices = [MagicMock(
            message=MagicMock(content="你好", tool_calls=None)
        )]
        result = agent.chat("你好")
        assert result == "你好"

def test_agent_with_tool(agent):
    """触发工具的对话"""
    # mock 第 1 轮：返回 tool_call
    # mock 第 2 轮：返回最终回答
    ...
```

### 今日任务

- [ ] 给 4 个工具各写 3+ 个测试
- [ ] 给 `ToolExecutor` 写测试（包括错误场景）
- [ ] 跑通 `pytest -v`，覆盖率 > 70%
- [ ] 写周复盘到 `notes/week-9-summary.md`
- [ ] 在 phase-3 文档勾选 Week 1 完成项

### 周末复盘问题

1. OpenAI 和 Anthropic 的工具调用协议，你更喜欢哪个设计？为什么？
2. 工具定义里，最容易踩的坑是什么？
3. 多工具场景下，模型选错工具的情况怎么减少？
4. 工具执行的错误处理，你的策略是什么？
5. 这一周的代码相比 Phase 2 的 ReAct，工程化程度提升了哪些？

---

# Week 2 - RAG 基础：Embedding 与向量数据库

> **本周目标：** 理解 Embedding 原理，能用 Chroma 建立第一个向量知识库。

## Day 1（周一）：Embedding 原理

**学习目标：** 理解什么是 Embedding，为什么"语义相近 = 向量相近"。

### 核心概念

| 概念 | 说明 |
|------|------|
| Embedding | 把文本映射成高维向量（如 1536 维浮点数）|
| 语义空间 | 语义相近的文本，向量距离也近 |
| 维度 | 向量的长度，常见 768 / 1024 / 1536 / 3072 |
| 归一化 | 把向量长度变成 1，便于算相似度 |

**前端类比：**
- Embedding 就像把每个句子投影到一个"语义坐标系"
- 相似的句子在这个坐标系里"靠得近"
- 不需要懂训练过程，会**用**就行

**为什么有用？**
- 传统搜索：关键词匹配（"猫粮"搜不到"宠物食品"）
- 语义搜索：向量相近（"猫粮"能搜到"宠物食品"）

### 学习内容

**1. 直观感受 Embedding**
```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def embed(text: str) -> np.ndarray:
    """获取文本的 embedding"""
    r = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return np.array(r.data[0].embedding)

# 相似语义
v1 = embed("我喜欢吃苹果")
v2 = embed("我爱吃水果")
v3 = embed("今天天气不错")
v4 = embed("股市大跌")

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"苹果 vs 水果: {cosine(v1, v2):.3f}")  # 高
print(f"苹果 vs 天气: {cosine(v1, v3):.3f}")  # 低
print(f"天气 vs 股市: {cosine(v3, v4):.3f}")  # 中等
```

**2. 可视化降维（直觉建立）**
```python
# 把 1536 维降到 2 维，画散点图
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

texts = [
    "猫", "狗", "宠物",           # 动物类
    "苹果", "香蕉", "水果",       # 水果类
    "北京", "上海", "中国",       # 地理类
    "编程", "代码", "开发",       # 技术类
]

vectors = [embed(t) for t in texts]
pca = PCA(n_components=2)
reduced = pca.fit_transform(vectors)

plt.figure(figsize=(8, 6))
for i, text in enumerate(texts):
    plt.scatter(reduced[i, 0], reduced[i, 1])
    plt.annotate(text, (reduced[i, 0], reduced[i, 1]))
plt.savefig("embedding-visualization.png")
# 你会看到同类词聚在一起
```

### 今日任务

- [ ] 跑通上面的代码，观察相似度差异
- [ ] 自己设计 10 个词（分 3 类），可视化降维看聚类
- [ ] 思考题：为什么"国王 - 男人 + 女人 ≈ 女王"这种向量运算能成立？
- [ ] 把可视化图保存到 `notes/week-10-embedding.png`

### 自检

- [ ] 我能用一句话解释 Embedding 是什么
- [ ] 我知道为什么语义搜索比关键词搜索强
- [ ] 我会算两个向量的余弦相似度

---

## Day 2（周二）：OpenAI Embedding API 实操

**学习目标：** 掌握 OpenAI Embedding API 的工程化使用。

### 核心对比

| 模型 | 维度 | 价格（/1M tokens）| 优势 |
|------|------|------------------|------|
| text-embedding-3-small | 1536 | $0.02 | 性价比之王 |
| text-embedding-3-large | 3072 | $0.13 | 效果最好 |
| text-embedding-ada-002 | 1536 | $0.10 | 老版本，不推荐 |
| BGE-M3（开源）| 1024 | 免费 | 可本地部署，中文好 |

### 学习内容

**1. 批量 Embedding**
```python
from openai import OpenAI
import time

client = OpenAI()

def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """批量 embedding，OpenAI 单次最多 2048 条"""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        r = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )
        # 注意：返回顺序和输入一致
        all_embeddings.extend([d.embedding for d in r.data])
        time.sleep(0.1)  # 避免 rate limit
    return all_embeddings

# 批量处理文档
docs = [f"这是第 {i} 条文档" for i in range(500)]
embeddings = embed_batch(docs)
print(f"Got {len(embeddings)} embeddings, dim={len(embeddings[0])}")
```

**2. 用 Pydantic 建模**
```python
from pydantic import BaseModel
from typing import Any

class Document(BaseModel):
    """带向量的文档"""
    id: str
    content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = {}  # 来源、页码、时间等

class EmbeddingConfig(BaseModel):
    model: str = "text-embedding-3-small"
    dimensions: int = 1536  # 3-small 支持降维
    batch_size: int = 100

# OpenAI 的 3-small / 3-large 支持降维（减少存储）
r = client.embeddings.create(
    model="text-embedding-3-small",
    input="hello",
    dimensions=256,  # 从 1536 降到 256，效果损失很小
)
```

**3. 成本估算**
```python
import tiktoken

def estimate_embedding_cost(texts: list[str], model: str = "text-embedding-3-small"):
    """估算 embedding 成本"""
    enc = tiktoken.get_encoding("cl100k_base")  # 近似计数，新模型 tiktoken 可能未收录
    total_tokens = sum(len(enc.encode(t)) for t in texts)

    pricing = {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
    }
    cost = total_tokens / 1_000_000 * pricing.get(model, 0.02)
    return {
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(cost, 4),
        "n_texts": len(texts),
    }
```

### 今日任务

- [ ] 跑通批量 embedding 代码
- [ ] 准备 50 条你自己的笔记 / 文档，做 embedding
- [ ] 估算成本：你的 100 条笔记 embedding 一次要多少钱？
- [ ] 测试 `dimensions=256` 降维后，相似度排序变化大不大

### 自检

- [ ] 我会批量调用 Embedding API
- [ ] 我知道怎么估算 embedding 成本
- [ ] 我理解降维的 trade-off（存储 vs 效果）

---

## Day 3（周三）：Chroma 向量数据库入门

**学习目标：** 掌握 Chroma 的基本用法，建立第一个向量知识库。

### 核心概念

**为什么需要向量数据库？**
- 100 条文档可以暴力搜索（算所有相似度）
- 10 万条以上必须用索引（HNSW 等算法）
- 向量数据库封装了存储、索引、检索

**Chroma 特点：**
- 纯 Python，零配置
- 底层用 SQLite + DuckDB
- 适合开发和小规模生产（百万级）

### 学习内容

**1. Chroma 基础**
```python
import chromadb

# 创建客户端（持久化到磁盘）
client = chromadb.PersistentClient(path="./vector_db")

# 创建 collection（类似数据库的表）
collection = client.get_or_create_collection(
    name="my_notes",
    metadata={"description": "我的个人笔记"}
)

# 添加文档
collection.add(
    documents=["今天学了 Python", "RAG 是检索增强生成", "向量数据库很重要"],
    metadatas=[
        {"source": "diary", "date": "2024-01-01"},
        {"source": "study", "topic": "rag"},
        {"source": "study", "topic": "vector-db"},
    ],
    ids=["1", "2", "3"]
    # 不传 embeddings，Chroma 会用默认模型自动 embedding
)
```

**2. 用 OpenAI Embedding 的 Chroma**
```python
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# 用 OpenAI 的 embedding 模型
ef = OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="my_notes_openai",
    embedding_function=ef,
)

# 添加（这次不用传 embeddings，Chroma 自动调 OpenAI）
collection.add(
    documents=["我喜欢吃苹果", "我爱吃水果", "今天天气不错"],
    ids=["1", "2", "3"],
)

# 查询
results = collection.query(
    query_texts=["水果"],
    n_results=2,
)
print(results)
# 输出：最相似的 2 条文档 + 距离 + metadata
```

**3. 增删改查**
```python
# 查
results = collection.query(
    query_texts=["学习"],
    n_results=5,
    where={"source": "study"},  # 元数据过滤
)

# 改
collection.update(
    ids=["1"],
    documents=["今天学了 Python 和 Rust"],
)

# 删
collection.delete(ids=["3"])

# 统计
print(f"共 {collection.count()} 条文档")
```

**4. 元数据过滤（很常用）**
```python
# 相似度 + 条件过滤
results = collection.query(
    query_texts=["Agent"],
    n_results=10,
    where={
        "$and": [
            {"source": "study"},
            {"date": {"$gte": "2024-01-01"}}
        ]
    },
)
```

### 今日任务

- [ ] 安装 Chroma：`uv add chromadb`
- [ ] 建一个 `my_notes` collection，插入 20+ 条文档
- [ ] 测试 5+ 种查询（相似度、过滤、组合）
- [ ] 思考题：为什么 metadata 过滤在 RAG 里很重要？

### 自检

- [ ] 我能用 Chroma 建立持久化的向量库
- [ ] 我会做相似度查询 + 元数据过滤
- [ ] 我知道 Chroma 默认用什么 embedding 模型

---

## Day 4（周四）：Qdrant 对比与选型

**学习目标：** 了解 Qdrant，知道何时选 Chroma vs Qdrant。

### 核心对比

| 维度 | Chroma | Qdrant | Pgvector |
|------|--------|--------|----------|
| 部署 | 纯 Python，零配置 | Docker / 云服务 | PostgreSQL 扩展 |
| 性能 | 中（百万级够用）| 高（Rust 实现）| 中 |
| 元数据过滤 | 一般 | 强大 | SQL 全功能 |
| 适合场景 | 原型、小项目 | 生产、大规模 | 已有 PG 的项目 |
| 学习成本 | 极低 | 低 | 中 |

### 学习内容

**1. Qdrant 快速上手**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

# 内存模式（开发用）
client = QdrantClient(":memory:")

# 或者 Docker 部署
# client = QdrantClient(host="localhost", port=6333)

# 创建 collection
client.create_collection(
    collection_name="my_notes",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# 插入
client.upsert(
    collection_name="my_notes",
    points=[
        PointStruct(
            id=1,
            vector=[0.1] * 1536,  # 实际用 embed() 替换
            payload={"text": "今天学了 Python", "source": "diary"}
        ),
        PointStruct(
            id=2,
            vector=[0.2] * 1536,
            payload={"text": "RAG 是检索增强生成", "source": "study"}
        ),
    ]
)

# 查询
results = client.search(
    collection_name="my_notes",
    query_vector=[0.15] * 1536,
    limit=5,
    query_filter=Filter(
        must=[{"key": "source", "match": {"value": "study"}}]
    ),
)
```

**2. 同一份文档跑两套数据库**
```python
import chromadb
from qdrant_client import QdrantClient

def benchmark_same_data(docs: list[str]):
    """同一份数据分别在 Chroma 和 Qdrant 跑"""
    # ... 略，作为练习
    pass

# 对比维度：
# - 写入速度（1000 条文档耗时）
# - 查询延迟（p50, p95）
# - 内存占用
# - API 易用性
```

### 今日任务

- [ ] 用 Docker 跑一个 Qdrant（或用内存模式）
- [ ] 把 Day 3 的 Chroma 数据在 Qdrant 也跑一遍
- [ ] 对比写入速度、查询延迟、API 易用性
- [ ] 写一份简单的选型笔记到 `notes/vector-db-comparison.md`

### 自检

- [ ] 我能解释 Chroma 和 Qdrant 的核心差异
- [ ] 我知道什么场景该选哪个
- [ ] 我会用 Qdrant 的 payload filter

---

## Day 5（周五）：相似度搜索算法

**学习目标：** 理解相似度搜索背后的数学（不用深，够用就行）。

### 核心概念

| 算法 | 公式直觉 | 特点 |
|------|---------|------|
| Cosine Similarity | 向量夹角的余弦 | 最常用，关注方向 |
| Dot Product | 向量内积 | 归一化后等价于 cosine |
| L2 Distance | 欧氏距离 | 关注绝对距离 |

**关键：**
- OpenAI Embedding 已归一化，cosine = dot product
- 大部分场景用 cosine 就对了

### 学习内容

**1. 手写相似度算法**
```python
import numpy as np

def cosine_similarity(a, b):
    """余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def dot_product(a, b):
    """内积（归一化后等价 cosine）"""
    return np.dot(a, b)

def l2_distance(a, b):
    """L2 距离"""
    return np.linalg.norm(np.array(a) - np.array(b))

# 对比
v1 = np.array([1, 0, 0])
v2 = np.array([1, 0, 0])
v3 = np.array([0, 1, 0])

print(f"cos(v1,v2) = {cosine_similarity(v1, v2)}")  # 1.0
print(f"cos(v1,v3) = {cosine_similarity(v1, v3)}")  # 0.0
print(f"l2(v1,v2) = {l2_distance(v1, v2)}")         # 0.0
print(f"l2(v1,v3) = {l2_distance(v1, v3)}")         # 1.414
```

**2. 暴力搜索 vs 索引搜索**
```python
import time
import numpy as np

# 造 10 万条 1536 维向量
np.random.seed(42)
db = np.random.randn(100_000, 1536).astype(np.float32)
db = db / np.linalg.norm(db, axis=1, keepdims=True)  # 归一化
query = np.random.randn(1536).astype(np.float32)
query = query / np.linalg.norm(query)

# 暴力搜索：算所有相似度，排序
start = time.time()
scores = db @ query  # 矩阵乘法，比 for 快
top_k_idx = np.argpartition(-scores, 5)[:5]
elapsed = time.time() - start
print(f"暴力搜索 10 万条耗时: {elapsed*1000:.1f}ms")
```

**3. 了解 HNSW（主流索引算法）**
```python
# HNSW = Hierarchical Navigable Small World
# 直觉：构建一张"导航图"，查询时快速跳到附近
# 优点：查询快（亚线性）
# 缺点：内存占用大，构建慢
# Chroma / Qdrant 默认都用 HNSW

# 不需要自己实现，知道概念即可
```

### 今日任务

- [ ] 跑通 3 种相似度算法的代码
- [ ] 跑暴力搜索 benchmark，感受 10 万条的查询延迟
- [ ] 思考题：为什么归一化后 cosine = dot product？
- [ ] 思考题：什么场景下 HNSW 比 暴力搜索 更值得？

### 自检

- [ ] 我能解释 cosine similarity 和 L2 distance 的区别
- [ ] 我知道为什么生产环境必须用索引（不能暴力搜索）
- [ ] 我了解 HNSW 的存在和价值

---

## Day 6（周六）：项目实战日 —— 语义搜索引擎

**学习目标：** 建立一个 100 条文档的小知识库，实现语义搜索。

### 项目：Personal Semantic Search

**功能要求：**
- 数据源：你自己的笔记 / Notion / Obsidian 导出的 Markdown
- 数据量：至少 100 条
- 功能：
  - 全文入库（自动 chunk + embed）
  - 语义搜索（Top-K）
  - 元数据过滤（按标签、按时间）
  - 搜索结果高亮关键词
- 工程化：
  - 增量更新（已入库的不重复 embed）
  - 成本统计

**目录结构：**
```
phase-3/
└── semantic-search/
    ├── pyproject.toml
    ├── README.md
    ├── data/
    │   └── notes/                # 你的笔记 .md 文件
    ├── src/
    │   ├── __init__.py
    │   ├── indexer.py            # 入库逻辑
    │   ├── searcher.py           # 搜索逻辑
    │   ├── embedder.py           # Embedding 封装
    │   └── cli.py
    └── vector_db/                # Chroma 持久化目录
```

**核心代码：indexer**
```python
# src/indexer.py
import hashlib
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from tqdm import tqdm

class NotesIndexer:
    def __init__(self, db_path: str, notes_dir: str):
        self.client = chromadb.PersistentClient(path=db_path)
        self.ef = OpenAIEmbeddingFunction(model_name="text-embedding-3-small")
        self.collection = self.client.get_or_create_collection(
            "notes", embedding_function=self.ef
        )
        self.notes_dir = Path(notes_dir)

    def _doc_id(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def index_all(self):
        """增量索引所有笔记"""
        md_files = list(self.notes_dir.glob("**/*.md"))
        existing_ids = set(self.collection.get()["ids"])

        new_docs, new_ids, new_metas = [], [], []
        for f in tqdm(md_files, desc="Indexing"):
            content = f.read_text()
            doc_id = self._doc_id(content)
            if doc_id in existing_ids:
                continue  # 已存在，跳过
            new_docs.append(content)
            new_ids.append(doc_id)
            new_metas.append({
                "source": str(f),
                "modified": f.stat().st_mtime,
            })

        if new_docs:
            self.collection.add(
                documents=new_docs,
                ids=new_ids,
                metadatas=new_metas,
            )
            print(f"新增 {len(new_docs)} 条，总计 {self.collection.count()} 条")
        else:
            print("无新增")
```

**核心代码：searcher**
```python
# src/searcher.py
class SemanticSearcher:
    def __init__(self, collection):
        self.collection = collection

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: dict | None = None,
    ):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
        # 整理成易读格式
        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source"),
                "score": 1 - results["distances"][0][i],  # 距离转相似度
            })
        return hits
```

### 今日任务

- [ ] 准备 100+ 条 Markdown 笔记（你自己的或网上找的）
- [ ] 实现完整的 indexer 和 searcher
- [ ] CLI 支持：`search "关键词"`、`index`、`stats`
- [ ] 跑 10 个查询，对比语义搜索 vs 关键词搜索（grep）

---

## Day 7（周日）：效果对比 + 周复盘

**学习目标：** 建立"不同 embedding 模型 + 不同参数"的对比直觉。

### 今日任务

**1. Embedding 模型对比**

用同一份 100 条文档 + 同一批 10 个 query，对比：

| 模型 | Top-1 命中率 | Top-5 命中率 | 延迟 | 成本 |
|------|-------------|-------------|------|------|
| Chroma 默认（all-MiniLM）| | | | |
| OpenAI text-embedding-3-small | | | | |
| OpenAI text-embedding-3-large | | | | |
| BGE-M3（本地）| | | | |

```python
# 评测脚本模板
def evaluate_search(searcher, queries: list[dict]):
    """
    queries: [{"query": "...", "expected_source": "note1.md"}, ...]
    """
    results = []
    for q in queries:
        hits = searcher.search(q["query"], n_results=5)
        top1_hit = hits[0]["source"] == q["expected_source"] if hits else False
        top5_hit = any(h["source"] == q["expected_source"] for h in hits)
        results.append({
            "query": q["query"],
            "top1": top1_hit,
            "top5": top5_hit,
        })
    # 汇总
    n = len(results)
    return {
        "top1_rate": sum(r["top1"] for r in results) / n,
        "top5_rate": sum(r["top5"] for r in results) / n,
    }
```

**2. 写复盘**

- [ ] 写评测报告到 `reports/week-10-embedding-eval.md`
- [ ] 写周复盘到 `notes/week-10-summary.md`
- [ ] 在 phase-3 文档勾选 Week 2 完成项

### 周末复盘问题

1. Embedding 最让你"惊艳"的瞬间是什么？
2. 语义搜索对比关键词搜索，提升有多大？有反例吗？
3. 不同 embedding 模型在你的数据上差异大吗？
4. Chroma 和 Qdrant 你更倾向哪个？为什么？
5. 100 条文档的语义搜索，延迟和成本你能接受吗？如果到 10 万条呢？

---

# Week 3 - RAG 流水线

> **本周目标：** 把 Embedding + 向量库 + LLM 串成完整的文档问答系统。

## Day 1（周一）：文档加载（LangChain Loaders）

**学习目标：** 掌握 LangChain 的文档加载器，支持多种格式。

### 核心概念

**为什么用 LangChain Loaders？**
- 统一接口：PDF、Markdown、网页、Notion 用同一套 API
- 自动提取元数据
- 支持流式加载（大文件）

### 学习内容

**1. 基础 Loaders**
```python
from langchain_community.document_loaders import (
    TextLoader,
    MarkdownLoader,
    PyPDFLoader,
    WebBaseLoader,
    DirectoryLoader,
)

# 加载单个 Markdown
loader = MarkdownLoader("./notes/week-1.md")
docs = loader.load()
print(docs[0].page_content[:200])
print(docs[0].metadata)  # {'source': './notes/week-1.md'}

# 加载 PDF
loader = PyPDFLoader("./paper.pdf")
pages = loader.load()  # 每页一个 Document
print(f"共 {len(pages)} 页")

# 加载网页
loader = WebBaseLoader("https://example.com/article")
docs = loader.load()

# 批量加载目录
loader = DirectoryLoader(
    "./notes",
    glob="**/*.md",
    loader_cls=MarkdownLoader,
    show_progress=True,
)
all_docs = loader.load()
print(f"共加载 {len(all_docs)} 个文档")
```

**2. Document 数据结构**
```python
from langchain_core.documents import Document

# 一个 Document = 一段文本 + 元数据
doc = Document(
    page_content="RAG 是检索增强生成",
    metadata={
        "source": "notes/rag.md",
        "page": 1,
        "author": "wsq",
        "date": "2024-01-01",
    }
)
```

**3. LlamaIndex 对比（了解）**
```python
from llama_index.core import SimpleDirectoryReader

# LlamaIndex 的 Reader 接口类似
docs = SimpleDirectoryReader("./notes").load_data()
# 两者选一即可，风格看个人偏好
```

### 今日任务

- [ ] 用 4 种 Loader 加载不同格式（md / pdf / 网页 / 目录）
- [ ] 把加载的文档存成 JSON（content + metadata）
- [ ] 思考题：元数据（source / page）为什么重要？

### 自检

- [ ] 我会用 LangChain 加载 4+ 种格式
- [ ] 我理解 Document 的结构
- [ ] 我知道 metadata 在后续 RAG 中的作用

---

## Day 2（周二）：固定长度与递归切分

**学习目标：** 掌握文档切分（chunking）的基础策略。

### 核心概念

**为什么必须切分？**
- LLM 上下文有限（即使 200K，塞整本书也贵）
- 长文档 embedding 效果差（语义被稀释）
- 切分后能精准定位

**切分策略对比：**

| 策略 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| 固定长度 | 简单 | 可能切断语义 | 快速原型 |
| 递归切分 | 尽量保留边界 | 仍有损失 | 通用 |
| 语义切分 | 边界自然 | 慢、贵 | 高质量 RAG |
| 父子文档 | 召回小块，返回大块 | 实现复杂 | 长文档 |

### 学习内容

**1. 固定长度切分**
```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,      # 每块约 500 字符
    chunk_overlap=50,    # 重叠 50 字符（避免边界信息丢失）
)

text = "..."  # 长文本
chunks = splitter.split_text(text)
print(f"切分前：{len(text)} 字符 → 切分后：{len(chunks)} 块")
```

**2. 递归切分（推荐）**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 按层级分隔符切：先试 \n\n，不行再试 \n，再不行试 " "
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。", "，", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

# 对 Markdown 特殊处理
md_splitter = RecursiveCharacterTextSplitter.from_language(
    language="markdown",
    chunk_size=500,
    chunk_overlap=50,
)

chunks = md_splitter.split_text(md_text)
```

**3. 参数调优实验**
```python
def experiment_chunk_size(text: str, sizes: list[int]):
    """实验不同 chunk_size 的切分效果"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    for size in sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=size // 5,
        )
        chunks = splitter.split_text(text)
        avg_len = sum(len(c) for c in chunks) / len(chunks)
        print(f"size={size}: {len(chunks)} 块, 平均 {avg_len:.0f} 字符")
```

### 今日任务

- [ ] 跑通固定长度和递归切分
- [ ] 用同一份文档，对比 chunk_size = 200/500/1000/2000 的切分效果
- [ ] 思考题：chunk_overlap 太大会怎样？太小会怎样？

### 自检

- [ ] 我能解释为什么必须切分
- [ ] 我知道 chunk_size 和 chunk_overlap 怎么调
- [ ] 我会根据文档类型选合适的 splitter

---

## Day 3（周三）：语义切分 + 父子文档

**学习目标：** 掌握进阶切分策略，提升 RAG 效果。

### 学习内容

**1. 语义切分（按 Embedding 找边界）**
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# 用 embedding 找语义跳变点
splitter = SemanticChunker(
    OpenAIEmbeddings(model="text-embedding-3-small"),
    breakpoint_threshold_type="percentile",  # 或 "standard_deviation"
    breakpoint_threshold_amount=95,
)

chunks = splitter.split_text(long_text)
# 优点：切分点自然
# 缺点：慢、贵（要算很多 embedding）
```

**2. 父子文档（检索小块，返回大块）**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 思路：用小块做 embedding 召回，但返回包含它的父块
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# 构建父子关系
parent_docs = parent_splitter.split_text(long_text)
store = {}  # parent_id -> parent_doc

for i, parent in enumerate(parent_docs):
    parent_id = f"parent-{i}"
    store[parent_id] = parent
    children = child_splitter.split_text(parent)
    for j, child in enumerate(children):
        # child 入向量库，metadata 记 parent_id
        collection.add(
            documents=[child],
            ids=[f"{parent_id}-child-{j}"],
            metadatas=[{"parent_id": parent_id}],
        )

# 检索：先搜 child，再取 parent
def retrieve_with_parent(query: str, n: int = 3):
    results = collection.query(query_texts=[query], n_results=n)
    parent_ids = [m["parent_id"] for m in results["metadatas"][0]]
    # 去重，返回父文档
    return [store[pid] for pid in dict.fromkeys(parent_ids)]
```

**3. Markdown 按标题切分**
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

# 按 Markdown 标题层级切分，保留结构
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
)
docs = splitter.split_text(md_text)
# 每个 doc 的 metadata 包含标题层级
```

### 今日任务

- [ ] 跑通语义切分（对比效果）
- [ ] 实现父子文档策略
- [ ] 对比：固定切分 vs 语义切分 vs 父子文档，在 10 个 query 上的效果
- [ ] 思考题：父子文档解决了什么问题？

### 自检

- [ ] 我能解释语义切分的原理和代价
- [ ] 我实现了父子文档检索
- [ ] 我知道 Markdown 标题切分的价值

---

## Day 4（周四）：完整 RAG 流水线

**学习目标：** 把加载、切分、Embedding、检索、生成串成完整流水线。

### 学习内容

**1. RAG 流水线全景**
```
离线（Indexing）：
  文档 → Loader → Splitter → Embedding → 向量库

在线（Querying）：
  用户问题 → Embedding → 向量搜索 → Top-K
                                            ↓
                              拼 Prompt → LLM → 回答
```

**2. 完整实现**
```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# === 离线：建库 ===
def build_vectorstore(notes_dir: str, db_path: str):
    loader = DirectoryLoader(notes_dir, glob="**/*.md", show_progress=True)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(docs)

    vs = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=db_path,
    )
    return vs

# === 在线：检索 + 生成 ===
RAG_PROMPT = ChatPromptTemplate.from_template("""
基于以下资料回答用户问题。如果资料中没有答案，明确说"资料中未提到"，不要编造。

资料：
{context}

问题：{question}

回答（每条关键信息后用 [来源: 文件名] 标注）：
""")

def build_rag_chain(vectorstore, model: str = "gpt-5-latest"):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(model=model, temperature=0)

    def format_docs(docs):
        return "\n\n".join(
            f"[来源: {d.metadata.get('source', '?')}]\n{d.page_content}"
            for d in docs
        )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain

# 使用
vs = build_vectorstore("./notes", "./vector_db")
rag = build_rag_chain(vs)
print(rag.invoke("什么是 RAG？"))
```

**3. 检索结果检查**
```python
# 调试技巧：先看检索到什么，再看生成
def debug_retrieve(vectorstore, query: str, k: int = 4):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)
    for i, d in enumerate(docs):
        print(f"--- Top {i+1} (source: {d.metadata.get('source')}) ---")
        print(d.page_content[:200])
        print()
```

### 今日任务

- [ ] 跑通完整 RAG 流水线
- [ ] 用 10 个问题测试，观察检索质量
- [ ] 思考题：为什么"资料中没有"的情况要特别处理？

### 自检

- [ ] 我能画出完整 RAG 流水线
- [ ] 我会用 LangChain 的 LCEL 语法
- [ ] 我会调试检索结果

---

## Day 5（周五）：引用溯源

**学习目标：** 让回答附带来源引用，这是生产级 RAG 的硬要求。

### 学习内容

**1. 让 LLM 输出带引用的回答**
```python
CITATION_PROMPT = """基于以下资料回答问题。每段陈述后必须用 [^N] 标注来源编号。

资料：
[1] 来源: notes/a.md
内容: RAG 是检索增强生成...

[2] 来源: notes/b.md
内容: Embedding 把文本变成向量...

[3] 来源: notes/c.md
内容: ...

问题：{question}

回答格式：
回答内容 [^1]。

参考资料：
[^1]: notes/a.md
[^2]: notes/b.md
"""

# 关键：把检索结果编号后塞进 prompt
def format_with_citations(docs):
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] 来源: {d.metadata.get('source', '?')}\n内容: {d.page_content}")
    return "\n\n".join(parts)
```

**2. 结构化输出（强制引用格式）**
```python
from pydantic import BaseModel, Field

class RAGAnswer(BaseModel):
    """带引用的 RAG 回答"""
    answer: str = Field(description="回答正文，每个事实后用 [N] 引用")
    citations: list[dict] = Field(description="引用列表")
    confidence: float = Field(description="置信度 0-1", ge=0, le=1)

# 用 structured output 强制结构
from openai import OpenAI
client = OpenAI()

def rag_with_citations(question: str, retrieved_docs: list) -> RAGAnswer:
    context = format_with_citations(retrieved_docs)
    resp = client.beta.chat.completions.parse(
        model="gpt-5-latest",
        messages=[{
            "role": "user",
            "content": f"资料：\n{context}\n\n问题：{question}\n\n请回答并标注引用。",
        }],
        response_format=RAGAnswer,
    )
    return resp.choices[0].message.parsed
```

### 今日任务

- [ ] 实现带引用的 RAG
- [ ] 用结构化输出强制引用格式
- [ ] 思考题：引用溯源对用户体验有什么价值？

### 自检

- [ ] 我的 RAG 回答附带来源
- [ ] 我会用 Pydantic 强制结构化输出
- [ ] 我知道引用格式该怎么设计

---

## Day 6（周六）：项目实战日 —— 文档问答机器人 v1

**学习目标：** 把本周内容整合成完整的文档问答系统。

### 项目：Doc QA Bot v1

**功能要求：**
- 支持上传 PDF / Markdown
- 自动切分、Embedding、入库
- 提问 → 检索 → 生成回答
- 回答附带引用（文件名 + 页码）
- 支持多轮对话（记住之前的问题）

**目录结构：**
```
phase-3/
└── doc-qa-bot/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── indexer.py          # 入库流水线
    │   ├── retriever.py        # 检索
    │   ├── generator.py        # 生成
    │   ├── pipeline.py         # RAG 主管线
    │   └── cli.py
    ├── data/
    │   └── uploads/            # 上传的文档
    └── vector_db/
```

### 今日任务

- [ ] 初始化项目：`uv init doc-qa-bot`
- [ ] 实现完整流水线（Loader → Splitter → Embedder → Retriever → Generator）
- [ ] 上传 3+ 份长文档（你自己的笔记或公开 PDF）
- [ ] 跑 10+ 轮问答，记录效果好的和效果差的 case

---

## Day 7（周日）：测试 + 周复盘

**学习目标：** 给 RAG 系统建立评测集，量化效果。

### 今日任务

**1. 构建 RAG 评测集**
```python
# 评测集格式
eval_cases = [
    {
        "question": "什么是 RAG？",
        "expected_keywords": ["检索", "增强", "生成"],
        "expected_source": "notes/rag.md",
    },
    # ... 20+ 条
]

def evaluate_rag(rag_chain, eval_cases):
    results = []
    for case in eval_cases:
        answer = rag_chain.invoke(case["question"])
        keyword_hit = sum(1 for k in case["expected_keywords"] if k in answer) / len(case["expected_keywords"])
        results.append({"question": case["question"], "keyword_hit": keyword_hit, "answer": answer})
    return results
```

- [ ] 构建 20+ 条评测用例
- [ ] 跑评测，记录基线指标
- [ ] 写周复盘到 `notes/week-11-summary.md`

### 周末复盘问题

1. 切分策略对你的 RAG 效果影响有多大？
2. 父子文档策略在你测试中提升了多少？
3. 引用溯源实现起来比想象中难吗？
4. 你遇到的最大"幻觉"案例是什么？怎么减少？
5. LangChain 的 LCEL 语法你用得习惯吗？

---

# Week 4 - RAG 进阶：检索优化

> **本周目标：** 把基础 RAG（60-70% 准确率）优化到 85%+。

## Day 1（周一）：Hybrid Search（BM25 + 向量）

**学习目标：** 掌握混合检索，结合关键词和语义检索的优势。

### 核心概念

**为什么混合？**
- 向量检索：擅长语义（"猫粮" → "宠物食品"）
- 关键词检索（BM25）：擅长精确（产品名、人名、代码）
- 两者互补，融合后效果最好

**融合算法 RRF（Reciprocal Rank Fusion）：**
```
score = sum(1 / (k + rank_i))  for each retriever
```
- k 通常取 60
- 不需要分数归一化，只用排名

### 学习内容

**1. BM25 关键词检索**
```python
from rank_bm25 import BM25Okapi

# 准备语料（中文要先分词）
docs = ["RAG 是检索增强", "向量数据库很重要", "Embedding 把文本变向量"]
tokenized = [doc.split() for doc in docs]  # 中文用 jieba
bm25 = BM25Okapi(tokenized)

scores = bm25.get_scores("RAG 检索".split())
print(scores)  # 每篇文档的相关性分数
```

**2. Hybrid Search 实现**
```python
import chromadb
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    def __init__(self, collection, bm25_docs: list[str], k: int = 60):
        self.collection = collection
        self.bm25 = BM25Okapi([d.split() for d in bm25_docs])
        self.docs = bm25_docs
        self.k = k  # RRF 参数

    def vector_search(self, query: str, n: int = 20):
        results = self.collection.query(query_texts=[query], n_results=n)
        return results["ids"][0]  # 返回 id 列表

    def bm25_search(self, query: str, n: int = 20):
        scores = self.bm25.get_scores(query.split())
        top_idx = np.argsort(scores)[::-1][:n]
        return [str(i) for i in top_idx]

    def rrf_fuse(self, rank_lists: list[list[str]], n: int = 5) -> list[str]:
        """RRF 融合多个排名列表"""
        scores = {}
        for ranks in rank_lists:
            for rank, doc_id in enumerate(ranks):
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (self.k + rank + 1)
        sorted_ids = sorted(scores.items(), key=lambda x: -x[1])
        return [doc_id for doc_id, _ in sorted_ids[:n]]

    def search(self, query: str, n: int = 5):
        v_ranks = self.vector_search(query, n=20)
        b_ranks = self.bm25_search(query, n=20)
        return self.rrf_fuse([v_ranks, b_ranks], n=n)
```

### 今日任务

- [ ] 跑通 BM25 检索
- [ ] 实现 Hybrid Search
- [ ] 对比：纯向量 vs 纯 BM25 vs Hybrid，在 10 个 query 上的效果

### 自检

- [ ] 我能解释为什么混合检索更好
- [ ] 我实现了 RRF 融合
- [ ] 我知道 BM25 擅长什么场景

---

## Day 2（周二）：Reranking 重排序

**学习目标：** 掌握两阶段检索（召回 + 精排），大幅提升准确率。

### 核心概念

**两阶段架构：**
- 第一阶段：向量检索召回 Top-50（高召回率，快）
- 第二阶段：Reranker 精排 Top-5（高准确率，慢但准）

**Reranker vs Embedding 的区别：**
- Embedding：单塔模型，query 和 doc 独立编码
- Reranker：双塔模型，query 和 doc 一起编码，能捕捉细粒度关系

### 学习内容

**1. 用 Cohere Rerank**
```python
import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def rerank(query: str, documents: list[str], top_n: int = 5):
    """用 Cohere Rerank 重排序"""
    r = co.rerank(
        model="rerank-multilingual-v3.0",
        query=query,
        documents=documents,
        top_n=top_n,
    )
    return [documents(result.index) for result in r.results]
```

**2. 用 BGE Reranker（开源）**
```python
from sentence_transformers import CrossEncoder

# 加载开源 reranker
reranker = CrossEncoder("BAAI/bge-reranker-base")

def rerank_local(query: str, documents: list[str], top_n: int = 5):
    pairs = [(query, doc) for doc in documents]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(documents, scores), key=lambda x: -x[1])
    return [doc for doc, _ in ranked[:top_n]]
```

**3. 完整两阶段检索**
```python
def two_stage_retrieve(query: str, vectorstore, top_k: int = 5):
    # Stage 1: 召回 Top-50
    docs = vectorstore.similarity_search(query, k=50)
    # Stage 2: Rerank 精排 Top-5
    reranked = rerank(query, [d.page_content for d in docs], top_n=top_k)
    return reranked
```

### 今日任务

- [ ] 注册 Cohere 或下载 BGE Reranker
- [ ] 跑通两阶段检索
- [ ] 对比：单阶段 vs 两阶段，在 10 个 query 上的准确率

### 自检

- [ ] 我能解释两阶段检索的优势
- [ ] 我会用 Reranker（云服务或本地）
- [ ] 我知道 Reranker 和 Embedding 的区别

---

## Day 3（周三）：Query 改写技术

**学习目标：** 掌握让 query 更"可检索"的几种技巧。

### 核心概念

| 技术 | 思路 | 适用 |
|------|------|------|
| Query Expansion | 扩展同义词 | 专业术语 |
| HyDE | 先假设答案，用答案检索 | 抽象问题 |
| Multi-Query | 生成多个版本的 query | 多角度召回 |
| Step-Back | 先问更宽泛的问题 | 细节问题 |

### 学习内容

**1. Query Expansion**
```python
def expand_query(query: str) -> list[str]:
    """用 LLM 扩展 query"""
    prompt = f"""把以下查询扩展为 3 个语义等价但表达不同的版本，每行一个：
查询：{query}
扩展：
"""
    r = client.chat.completions.create(
        model="gpt-5-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    variants = r.choices[0].message.content.strip().split("\n")
    return [query] + [v.strip() for v in variants if v.strip()]
```

**2. Multi-Query 检索**
```python
def multi_query_retrieve(query: str, vectorstore, n: int = 5):
    """多版本 query 检索，结果合并"""
    variants = expand_query(query)
    all_docs = []
    for v in variants:
        docs = vectorstore.similarity_search(v, k=n)
        all_docs.extend(docs)
    # 去重（按内容 hash）
    seen = set()
    unique = []
    for d in all_docs:
        h = hash(d.page_content[:100])
        if h not in seen:
            seen.add(h)
            unique.append(d)
    return unique[:n * 2]
```

### 今日任务

- [ ] 实现 Query Expansion 和 Multi-Query
- [ ] 对比：原 query vs 扩展后，检索效果差异
- [ ] 思考题：Query 改写什么时候反而会让效果变差？

### 自检

- [ ] 我实现了至少 2 种 Query 改写
- [ ] 我知道每种技术的适用场景
- [ ] 我会评估改写是否真的有效

---

## Day 4（周四）：HyDE 与 Multi-Query

**学习目标：** 深入掌握 HyDE 和 Multi-Query，这是 RAG 进阶的关键技术。

### 核心概念

**HyDE（Hypothetical Document Embeddings）：**
- 思路：query 和 doc 在 embedding 空间分布不同
- 让 LLM 先"假设性回答"问题，用这个假答案去检索
- 假答案比 query 更像文档，检索更准

### 学习内容

**1. HyDE 实现**
```python
def hyde_retrieve(query: str, vectorstore, n: int = 5):
    """HyDE：先生成假答案，再用假答案检索"""
    # Step 1: 让 LLM 假设性回答
    prompt = f"""请用一段话（200 字以内）回答以下问题，即使你不确定也给出最可能的答案：
问题：{query}
回答："""
    r = client.chat.completions.create(
        model="gpt-5-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    hypothetical_answer = r.choices[0].message.content

    # Step 2: 用假答案检索（而不是原 query）
    docs = vectorstore.similarity_search(hypothetical_answer, k=n)
    return docs
```

**2. Step-Back Prompting**
```python
def stepback_query(query: str) -> str:
    """把细节问题变成宽泛问题"""
    prompt = f"""把以下具体问题改写为更宽泛、更通用的问题：
具体问题：{query}
宽泛问题："""
    r = client.chat.completions.create(
        model="gpt-5-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content

# 例："2024 年 Q3 苹果营收" → "苹果公司近期财务表现"
```

### 今日任务

- [ ] 实现 HyDE 和 Step-Back
- [ ] 对比：原 query vs HyDE，在抽象问题上的检索效果
- [ ] 思考题：HyDE 什么时候会失败？

### 自检

- [ ] 我能解释 HyDE 为什么有效
- [ ] 我实现了 HyDE 检索
- [ ] 我知道 HyDE 的失败模式

---

## Day 5（周五）：RAGAS 评测框架

**学习目标：** 学会用 RAGAS 量化评测 RAG 系统的各个维度。

### 核心概念

**RAGAS 评测维度：**

| 维度 | 衡量什么 |
|------|---------|
| Faithfulness | 回答是否忠于检索到的资料（无幻觉）|
| Answer Relevancy | 回答是否切题 |
| Context Precision | 检索的上下文是否精准 |
| Context Recall | 是否召回了所有必要信息 |

### 学习内容

**1. RAGAS 基础用法**
```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# 准备评测数据
eval_data = {
    "question": ["什么是 RAG？"],
    "answer": ["RAG 是检索增强生成..."],  # RAG 系统的回答
    "contexts": [["资料1", "资料2"]],      # 检索到的上下文
    "ground_truth": ["RAG 是..."],         # 标准答案（可选）
}

dataset = Dataset.from_dict(eval_data)

# 跑评测
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(result)
# 输出：{'faithfulness': 0.85, 'answer_relevancy': 0.90, ...}
```

**2. 自定义评测脚本**
```python
def eval_rag_pipeline(rag_chain, eval_cases: list[dict]):
    """完整评测流程"""
    data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
    for case in eval_cases:
        # 跑 RAG，同时拿到检索结果
        docs = retriever.invoke(case["question"])
        answer = rag_chain.invoke(case["question"])
        data["question"].append(case["question"])
        data["answer"].append(answer)
        data["contexts"].append([d.page_content for d in docs])
        data["ground_truth"].append(case.get("expected", ""))

    dataset = Dataset.from_dict(data)
    return evaluate(dataset, metrics=[faithfulness, answer_relevancy])
```

### 今日任务

- [ ] 安装 RAGAS：`uv add ragas datasets`
- [ ] 用 RAGAS 评测 Week 3 的 Doc QA Bot
- [ ] 记录各维度分数到 `reports/week-12-ragas-baseline.md`

### 自检

- [ ] 我能解释 RAGAS 的 4 个评测维度
- [ ] 我会跑 RAGAS 评测
- [ ] 我知道如何根据分数定位问题

---

## Day 6（周六）：项目实战日 —— RAG 策略对比

**学习目标：** 用评测集系统对比不同 RAG 策略的效果。

### 项目：RAG 策略对比报告

**对比矩阵：**

| 版本 | 检索策略 | 生成策略 |
|------|---------|---------|
| Baseline | 纯向量 | 直接生成 |
| V2 | Hybrid（向量+BM25）| 直接生成 |
| V3 | Hybrid + Rerank | 直接生成 |
| V4 | V3 + HyDE | 直接生成 |
| V5 | V3 + Multi-Query | 直接生成 |

**评测脚本：**
```python
def compare_strategies(eval_cases: list[dict]):
    strategies = {
        "baseline": lambda q: basic_rag(q),
        "hybrid": lambda q: hybrid_rag(q),
        "hybrid_rerank": lambda q: hybrid_rerank_rag(q),
        "hybrid_rerank_hyde": lambda q: hyde_rag(q),
    }

    results = {}
    for name, fn in strategies.items():
        data = run_eval(fn, eval_cases)
        score = evaluate_with_ragas(data)
        results[name] = score

    # 生成对比表
    print_comparison_table(results)
```

### 今日任务

- [ ] 实现至少 4 种 RAG 策略
- [ ] 用同一份评测集（30+ 条）跑对比
- [ ] 输出对比报告（准确率、延迟、成本）

---

## Day 7（周日）：对比报告 + 周复盘

**学习目标：** 整理对比报告，形成自己的 RAG 优化方法论。

### 今日任务

**1. 写对比报告**

报告结构：
```markdown
# RAG 策略对比报告

## 评测集说明
- 大小：30 条
- 任务类型：事实问答 / 推理 / 对比
- 数据源：个人笔记

## 对比结果
| 策略 | Faithfulness | Relevancy | 延迟(s) | 成本/查询 |
|------|-------------|-----------|---------|----------|
| Baseline | 0.72 | 0.81 | 1.2 | $0.001 |
| Hybrid | 0.78 | 0.84 | 1.5 | $0.001 |
| Hybrid+Rerank | 0.86 | 0.89 | 2.1 | $0.002 |
| +HyDE | 0.88 | 0.91 | 2.8 | $0.003 |

## 关键发现
1. Rerank 提升最明显（+8% Faithfulness）
2. HyDE 延迟翻倍但提升有限
3. ...

## 推荐配置
生产环境用：Hybrid + Rerank
```

- [ ] 写完整对比报告到 `reports/week-12-rag-comparison.md`
- [ ] 写周复盘到 `notes/week-12-summary.md`

### 周末复盘问题

1. 哪种策略在你的数据上提升最明显？为什么？
2. Rerank 的延迟代价你能接受吗？
3. HyDE 在什么问题上效果最好？什么问题最差？
4. RAGAS 评测和你的主观感受一致吗？
5. 如果只能选一个优化，你选哪个？为什么？

---

# Week 5 - 阶段性整合项目

> **本周目标：** 整合 Function Calling + RAG，做出作品集项目 #1 的雏形。

## Day 1（周一）：项目规划与架构设计

**学习目标：** 做好项目规划，避免"边写边乱"。

### 学习内容

**1. 项目：个人知识助手**

**核心功能：**
- 知识库管理（CRUD：增删改查文档）
- 智能问答（基于知识库的 RAG）
- 工具调用：
  - `search_kb`：查本地知识库
  - `get_weather`：查天气
  - `get_time`：查时间
  - `save_note`：保存笔记到文件
- 跨会话记忆：记住用户偏好

**2. 架构设计**
```
用户输入
   ↓
Agent 决策（LLM）
   ↓
┌────────┬─────────┬────────┐
↓        ↓         ↓        ↓
RAG    weather   time    save_note
检索
   ↓
综合所有结果
   ↓
LLM 生成最终回答
   ↓
输出 + 更新记忆
```

**3. 技术栈**
- LLM：gpt-5-latest 或 claude-sonnet-4-5-latest（主力）+ DeepSeek-R1（复杂推理任务）
- Embedding：text-embedding-3-small
- 向量库：Chroma
- 框架：LangChain（RAG）+ 原生 OpenAI SDK（Agent）
- 评测：RAGAS + Promptfoo
- 可观测：LangSmith

### 今日任务

- [ ] 写项目 README（含架构图）
- [ ] 设计目录结构
- [ ] 列出核心模块的接口定义（不实现）
- [ ] 设计评测集（至少 30 条）

### 自检

- [ ] 我有完整的项目规划文档
- [ ] 我定义了每个模块的接口
- [ ] 我的评测集覆盖核心功能

---

## Day 2（周二）：知识库管理模块

**学习目标：** 实现知识库的完整 CRUD。

### 今日任务

- [ ] 实现 `KnowledgeBase` 类：
  ```python
  class KnowledgeBase:
      def add_document(self, content: str, metadata: dict) -> str: ...
      def update_document(self, doc_id: str, content: str) -> None: ...
      def delete_document(self, doc_id: str) -> None: ...
      def search(self, query: str, n: int = 5) -> list[dict]: ...
      def list_documents(self) -> list[dict]: ...
  ```
- [ ] 支持 Markdown、PDF、纯文本
- [ ] 增量更新（文件改动后重新 index）

---

## Day 3（周三）：RAG + Function Calling 整合

**学习目标：** 把 RAG 作为工具暴露给 Agent。

### 今日任务

- [ ] 把 RAG 检索封装成一个工具：
  ```python
  def search_kb(query: str, n: int = 5) -> str:
      """搜索用户的知识库"""
      docs = kb.search(query, n=n)
      return format_docs(docs)
  ```
- [ ] 把 save_note 封装成工具
- [ ] 让 Agent 能自主决定"查知识库"还是"查互联网"还是"直接回答"
- [ ] 测试 10+ 个问题，观察 Agent 的工具选择

---

## Day 4（周四）：跨会话记忆

**学习目标：** 让助手记住用户的偏好和历史。

### 今日任务

- [ ] 实现用户画像存储：
  ```python
  class UserProfile:
      preferences: dict  # 语言、风格、关注领域
      frequent_topics: list[str]
      feedback_history: list[dict]
  ```
- [ ] 每次对话后自动提取偏好更新到 profile
- [ ] 启动时把 profile 注入 system prompt
- [ ] 测试：跨会话问"你还记得我喜欢什么吗？"

---

## Day 5（周五）：日志、错误处理、LangSmith trace

**学习目标：** 给项目加上生产级的可观测性。

### 今日任务

- [ ] 配置 LangSmith trace：
  ```python
  import os
  os.environ["LANGCHAIN_TRACING_V2"] = "true"
  os.environ["LANGCHAIN_PROJECT"] = "personal-kb-assistant"
  # 每次调用自动上报到 LangSmith
  ```
- [ ] 实现结构化日志（JSON 格式）：
  ```python
  import logging
  import json

  class JsonFormatter(logging.Formatter):
      def format(self, record):
          return json.dumps({
              "time": self.formatTime(record),
              "level": record.levelname,
              "msg": record.getMessage(),
              "extra": getattr(record, "extra", {}),
          })

  logger = logging.getLogger("assistant")
  # 每次工具调用、每次 LLM 调用都记录
  ```
- [ ] 错误处理：
  - API 超时重试（tenacity）
  - 工具执行失败回传给模型
  - 向量库操作失败降级

---

## Day 6（周六）：完整项目开发 + 评测集

**学习目标：** 完成项目核心功能，跑通完整评测。

### 今日任务

- [ ] 整合所有模块：
  - KnowledgeBase（Day 2）
  - Agent + RAG（Day 3）
  - UserProfile（Day 4）
  - Logging + Trace（Day 5）
- [ ] 实现 CLI：
  ```
  ask "什么是 RAG？"          # 单次问答
  chat                         # 多轮对话
  upload ./notes              # 上传文档
  eval                         # 跑评测
  ```
- [ ] 跑评测集（30+ 条），记录基线分数
- [ ] 修复发现的 bug

---

## Day 7（周日）：README + 作品集整理 + 阶段总复盘

**学习目标：** 把项目打磨到"能展示"的程度。

### 今日任务

**1. 写 README（重要！）**

README 结构：
```markdown
# 个人知识助手

一句话介绍。

## 功能
- 知识库管理（CRUD）
- RAG 问答
- 工具调用（天气、时间、保存笔记）
- 跨会话记忆

## 架构图
（mermaid 或图片）

## 快速开始
（安装、配置、运行）

## 使用示例
（3+ 个典型场景的截图或录屏）

## 评测
- 评测集：30 条
- 准确率：85%
- 延迟：平均 2.3s

## 技术栈
- ...

## 路线图
- [ ] Web UI（第 6 阶段做）
- [ ] 多用户
```

- [ ] 写完整 README
- [ ] 录 1-2 分钟的演示视频（可选）
- [ ] 推到 GitHub

**2. 阶段总复盘**

- [ ] 写阶段总复盘到 `notes/phase-3-summary.md`
- [ ] 在 phase-3 文档勾选所有完成项
- [ ] 整理本阶段产出物清单

### 阶段复盘问题（重要）

回答以下问题（至少 500 字）：

1. **认知转变**：这一阶段最大的认知转变是什么？（建议结合"Agent = 工具调用 + 知识检索"展开）
2. **Function Calling**：你最深刻的体会是什么？工程化有哪些坑？
3. **RAG 优化**：哪种优化策略在你项目上效果最好？
4. **评测价值**：没有 RAGAS 之前和之后，你的迭代效率差多少？
5. **作品集**：你的个人知识助手还有哪些不足？第 6 阶段怎么打磨？
6. **卡点回顾**：这 5 周最大的卡点是什么？怎么解决的？
7. **下一步**：进入第 4 阶段（Agent 核心架构 + LangGraph）前，你想补什么？

---

## 常见卡点速查

| 卡点 | 解决方案 |
|------|---------|
| OpenAI 工具调用报 `tool_call_id` 错误 | 检查回传时 id 是否对应，不能漏 |
| Anthropic tool_use 解析失败 | 注意 content 是列表，要遍历找 `type == "tool_use"` |
| 模型不调用工具 | 检查 description 写得清不清楚，加 Few-shot 示例 |
| 模型乱调工具 | 在 description 里明确"什么时候不用" |
| Chroma 报 collection 不存在 | 用 `get_or_create_collection` 而非 `get_collection` |
| Embedding 成本超标 | 用缓存（相同输入不重复 embed），或换 3-small |
| RAG 效果差（幻觉多）| 先查切分，再查 Top-K，最后加"资料中没有就直说" |
| RAG 检索不到相关内容 | 试 Hybrid Search，增加 Top-K，检查 query 改写 |
| 中文 BM25 效果差 | 必须先用 jieba 分词，不能直接 split |
| Reranker 太慢 | 减少召回量（Top-50 → Top-20），或用本地模型 |
| RAGAS 跑不起来 | 检查 datasets 版本，RAGAS 对 LangChain 版本敏感 |
| LangChain LCEL 看不懂 | 先理解 RunnablePassthrough 和 `|` 运算符 |
| LangSmith 看不到 trace | 检查环境变量，确认 Project 名字 |
| 向量库迁移困难 | 一开始就用 Chroma 的 PersistentClient，避免内存模式 |

## 推荐速查资源

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Chroma 官方文档](https://docs.trychroma.com/)
- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [LangChain RAG 教程](https://python.langchain.com/docs/use_cases/question_answering/)
- [LlamaIndex 教程](https://docs.llamaindex.ai/)
- [RAGAS 文档](https://docs.ragas.io/)
- [Cohere Rerank](https://docs.cohere.com/docs/reranking)
- [Advanced RAG 论文](https://arxiv.org/abs/2312.10997)
- [LangSmith 文档](https://docs.smith.langchain.com/)

## 完成标准

第 3 阶段结束时，你应该能：

- [ ] **Function Calling**：能定义复杂的工具 schema，实现多工具编排
- [ ] **协议对比**：能解释 OpenAI 和 Anthropic 工具调用协议的差异
- [ ] **工程化**：能用 ToolExecutor 实现错误处理、重试、日志
- [ ] **Embedding**：理解原理，能选合适的模型
- [ ] **向量数据库**：能用 Chroma / Qdrant 建立知识库
- [ ] **RAG 流水线**：能实现完整的加载-切分-检索-生成
- [ ] **切分策略**：会调 chunk_size，会实现父子文档
- [ ] **引用溯源**：回答附带来源，结构化输出
- [ ] **Hybrid Search**：实现 BM25 + 向量融合
- [ ] **Reranking**：会用 Cohere / BGE 重排序
- [ ] **Query 改写**：实现 HyDE / Multi-Query
- [ ] **RAG 评测**：用 RAGAS 量化评测，能定位问题
- [ ] **整合能力**：Function Calling + RAG 结合
- [ ] **作品集 #1**：个人知识助手雏形可运行、有评测

### 产出物清单

- [ ] 多工具聊天机器人（Week 1）
- [ ] 语义搜索引擎（Week 2）
- [ ] 文档问答机器人 v1（Week 3）
- [ ] RAG 策略对比报告（Week 4）
- [ ] **个人知识助手雏形（Week 5，作品集 #1）**
- [ ] 评测集（30+ 条）
- [ ] RAG 评测报告（含 RAGAS 分数）

### 关键认知

**这一阶段最大的认知转变：**

| 错误认知 | 正确认知 |
|---------|---------|
| Agent 就是聊天 + 工具 | Agent = 决策 + 工具 + 知识 + 记忆 |
| RAG 就是检索 + 生成 | RAG 是系统工程，切分和检索策略决定上限 |
| 效果不好就换大模型 | 先查切分、检索、Prompt，最后才换模型 |
| 评测是 QA 的事 | 评测是开发的一部分，每次改动都要跑 |
| 工具调用就是写函数 | 工具定义就是 API 设计，描述决定准确率 |
| 向量数据库都一样 | 元数据过滤、索引算法差异巨大 |

### 下一步

**重要：** Week 5 的个人知识助手会在第 6 阶段打磨上线，加入 Web UI 和用户系统。本阶段的重点是**后端能力和工程化**，UI 暂时用 CLI 即可。

准备好进入第 4 阶段：[Agent 核心架构 + LangGraph](./phase-4-agent-core-langgraph.md)
