# 第 1 阶段每日计划：Python 基础 + LLM API 入门

> **周期：** **6 周**（含 1 周缓冲）
> **每日投入：** 工作日约 1-1.5 小时 / 周末 2-3 小时
> **总产出物：** CLI 聊天机器人 v2（支持流式输出 + 结构化指令）

## 进度追踪

- [ ] Week 1 - Python 语法速通（数据结构 + 函数 + OOP + 项目实战）
- [ ] Week 2 - Python 进阶（类型 + Pydantic + 异步 + pytest 入门）
- [ ] Week 3 - Python 工程化（uv + Ruff + mypy + 项目结构 + CI）
- [ ] Week 4 - LLM API 调用 + Prompt 基础
- [ ] Week 5 - 结构化输出 + 错误处理
- [ ] Week 6（缓冲周）- 补作业 / 复盘 / 赶进度
- [ ] 阶段产出物：CLI 聊天机器人 v2 完成

## 学习方法

1. **不要从零学 Python** — 你已经是程序员，用对比学最快
2. **边学边敲** — 每个概念都写代码验证
3. **遇到不理解的先跳过** — 装饰器、asyncio 这些可以后续补
4. **优先掌握 80% 场景的 20% 语法** — 别追求全覆盖

## 环境准备（Day 0，提前一晚）

```bash
# 1. 安装 uv（推荐的 Python 包管理工具）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装 Python 3.12+
uv python install 3.12

# 3. 验证
python3 --version
uv --version

# 4. VS Code 安装扩展
# - Python（Microsoft 官方）
# - Pylance（类型检查）
# - Ruff（代码格式化）
```

**完成标志：** VS Code 能识别 Python 解释器，能运行 `print("hello")`。

---

## Day 0.5（选做但强烈推荐）：5 分钟——跑通你人生中第一次 LLM 调用

> **为什么加在这里：** 你正在转型 Agent 工程师，但前 2 周都在学 Python 语法。这可能会让你产生"我真的在学 AI 吗"的怀疑。花 5 分钟跑通一次 LLM 调用，把那个兴奋感锚定住。**代码不用理解，跑通就行。**

### 操作步骤

```bash
# 1. 安装 OpenAI SDK
uv add openai

# 2. 设置 API Key（申请地址见 Week 4 Day 1）
export OPENAI_API_KEY=sk-your-key-here

# 3. 创建并运行 test_llm.py
cat > test_llm.py << 'PYEOF'
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5-latest",
    messages=[{"role": "user", "content": "你好，用一句话介绍你自己。"}],
    max_tokens=100,
)
print(response.choices[0].message.content)
print(f"\n(这次调用消耗了 {response.usage.total_tokens} 个 token)")
PYEOF

uv run python test_llm.py
```

**如果输出了一段 AI 的自我介绍——恭喜，你已经完成了 Agent 工程师之路的第一个 API 调用。**

> 代码现在不懂没关系，Week 4（LLM API 调用）会逐行拆解。现在只需要记住：**你能让 AI 干活了。** 这个 `test_llm.py` 留着，学到 Week 4 时回来看看，你会发现已经能完全理解它的每一行。

---

### 🅱️ 选项 B（前端友好版）：5 分钟——用 TypeScript 跑通第一次调用

> **为什么加这个选项：** 你是前端工程师，TypeScript 是你的母语。**第一次拿到正反馈的成本越低，越不容易在 Day 1 放弃。** 你可以先用最熟悉的工具跑通，Week 4 再去学 Python 版——两份代码做的事完全一样，对照看你会理解更深。

任选一种最顺手的方式：

#### 方式 1：零依赖，用原生 `fetch`（最直观，没有魔法）

```bash
# 1. 设置 API Key
export OPENAI_API_KEY=sk-your-key-here

# 2. 创建 first-llm.ts
cat > first-llm.ts << 'TSEOF'
const res = await fetch("https://api.openai.com/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
  },
  body: JSON.stringify({
    model: "gpt-5-latest",
    messages: [{ role: "user", content: "你好，用一句话介绍你自己。" }],
    max_tokens: 100,
  }),
});
const data = await res.json();
console.log(data.choices[0].message.content);
console.log(`\n(这次调用消耗了 ${data.usage.total_tokens} 个 token)`);
TSEOF

# 3. 运行（用 tsx 直接跑 .ts，不用编译）
npx tsx first-llm.ts
```

> 这段代码的每一行你都应该看得懂——`fetch` 是前端的日常。**Week 4 的 Python 版用 `openai` SDK 做的是同一件事**，只是把 `fetch` 换成了 SDK 封装。

#### 方式 2：用 Vercel AI SDK（工业级写法，Phase 6 会大量用）

```bash
# 1. 初始化一个最小项目
mkdir first-llm-ai-sdk && cd first-llm-ai-sdk
npm init -y
npm install ai @ai-sdk/openai
npm install -D tsx typescript @types/node

# 2. 设置 Key
export OPENAI_API_KEY=sk-your-key-here

# 3. 创建 index.ts
cat > index.ts << 'TSEOF'
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

const { text, usage } = await generateText({
  model: openai("gpt-5-latest"),
  prompt: "你好，用一句话介绍你自己。",
  maxTokens: 100,
});

console.log(text);
console.log(`\n(这次调用消耗了 ${usage.totalTokens} 个 token)`);
TSEOF

# 4. 运行
npx tsx index.ts
```

> **Vercel AI SDK** 是 Phase 6 前端集成的主力工具。现在先混个脸熟，不用记 API——重点是感受"原来调 LLM 跟调一个普通 async 函数没区别"。

---

**两个选项我该选哪个？**

| 你的情况 | 建议 |
|---------|------|
| 想最快拿到正反馈、Python 一行没写过 | **先选 B（TS 版）** 跑通，再去学 Python |
| 想直接进入主线、不怕前几行 Python 报错 | 选 A（Python 版），Week 4 会重见 |
| 时间够、两个都跑 | **强烈推荐**——同一份请求用两种语言实现一遍，你会对 LLM API 的本质有深刻理解 |

**不管选哪个，目标只有一个：今晚跑通一次 LLM 调用，把兴奋感锚定住。** AI 不是黑盒——你能让它干活了。

---

# Week 1：Python 语法速通

> **目标：** 用 7 天时间，用 JS/TS 思维锚点快速上手 Python
> **产出物：** 用 Python 重写一个你写过的 JS 小工具

---

## Day 1（周一）：数据结构 + 控制流

**学习目标：** 把 JS 的数据结构思维迁移到 Python。

### 核心对比

| JS / TS | Python | 备注 |
|---------|--------|------|
| `Array` | `list` | `[1, 2, 3]` |
| `Object` | `dict` | `{"a": 1}` |
| `Set` | `set` | `{1, 2, 3}` |
| （无） | `tuple` | `(1, 2)`，不可变 |
| `null` / `undefined` | `None` | |
| `true` / `false` | `True` / `False` | 首字母大写 |
| `===` | `==` / `is` | Python 没有 === |

### 学习内容

**1. List 操作**
```python
nums = [1, 2, 3]
nums.append(4)           # push
nums.pop()               # pop
nums[0]                  # 索引访问
nums[-1]                 # 最后一个（JS 不支持）
nums[1:3]                # 切片 [2, 3]
[nums[i]*2 for i in range(len(nums))]  # 列表推导式
```

**2. Dict 操作**
```python
user = {"name": "wsq", "age": 30}
user["name"]
user.get("email", "default")  # 安全访问
user.keys()
user.values()
user.items()  # Object.entries()
```

**3. 控制流**
- `if / elif / else`（注意冒号和缩进）
- `for x in iterable:`（没有 C 风格 for）
- `while`
- `match` 语句（Python 3.10+，类似 switch）

### 今日任务

- [ ] 跟着 [Learn X in Y minutes (Python)](https://learnxinyminutes.com/docs/python/) 敲一遍
- [ ] 把你写过的一个 JS 工具函数用 Python 重写（推荐：日期格式化、数组去重）

### 自检

- [ ] 我能解释 list / dict / tuple / set 的区别
- [ ] 我知道为什么 `nums[-1]` 能取到最后一个元素
- [ ] 我会写列表推导式

---

## Day 2（周二）：函数 + 模块

**学习目标：** 掌握 Python 函数定义、参数、模块系统。

### 核心对比

| JS / TS | Python | 备注 |
|---------|--------|------|
| `function f() {}` | `def f():` | |
| 箭头函数 `x => x*2` | `lambda x: x*2` | 只能单行 |
| 默认参数 | 默认参数 | Python 还有关键字参数 |
| `import x from 'y'` | `from y import x` | |
| `export` | （无，文件即模块） | |

### 学习内容

**1. 函数定义**
```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"

greet("wsq")                  # 位置参数
greet(name="wsq")             # 关键字参数
greet("wsq", greeting="Hi")   # 混合
```

**2. 关键字参数（Python 独有优势）**
```python
def create_user(*, name: str, age: int, email: str = ""):
    """* 之后必须用关键字参数"""
    pass

create_user(name="wsq", age=30)  # OK
create_user("wsq", 30)            # 报错
```

**3. *args 和 **kwargs**
```python
def f(*args, **kwargs):
    print(args)    # tuple
    print(kwargs)  # dict
```

**4. 模块与包**
```python
# mymodule.py
def hello():
    return "hi"

# main.py
from mymodule import hello
import mymodule as mm
```

### 今日任务

- [ ] 写 3-5 个工具函数（字符串处理、文件操作）
- [ ] 拆成多个模块，互相 import
- [ ] 用 VS Code 调试器打断点跑一遍

### 自检

- [ ] 我能解释位置参数 vs 关键字参数
- [ ] 我会定义带类型注解的函数
- [ ] 我能从另一个文件 import 函数

---

## Day 3（周三）：面向对象

**学习目标：** Python 的 class 系统。

### 核心对比

| JS / TS | Python | 备注 |
|---------|--------|------|
| `class Foo {}` | `class Foo:` | |
| `constructor()` | `__init__()` | |
| `this` | `self` | 必须显式声明 |
| `extends` | `class B(A):` | |
| `super()` | `super().__init__()` | |
| getter / setter | `@property` | |

### 学习内容

**1. 基础类**
```python
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

    def __str__(self) -> str:  # toString()
        return f"User({self.name})"

user = User("wsq", 30)
print(user.greet())
```

**2. 继承**
```python
class Admin(User):
    def __init__(self, name: str, age: int, permissions: list):
        super().__init__(name, age)
        self.permissions = permissions

    def greet(self) -> str:  # 重写
        base = super().greet()
        return f"{base} (Admin)"
```

**3. @property 和 @staticmethod**
```python
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    @property
    def area(self) -> float:
        return 3.14 * self.radius ** 2

    @staticmethod
    def from_diameter(d: float) -> "Circle":
        return Circle(d / 2)
```

**4. Dataclass（推荐）**
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str = ""
```

### 今日任务

- [ ] 用 class 重写 Day 2 的工具函数
- [ ] 实现一个继承关系（如 Animal → Dog / Cat）
- [ ] 用 dataclass 简化代码

### 自检

- [ ] 我理解为什么 Python 要 `self`
- [ ] 我能写 `__init__` 和 `__str__`
- [ ] 我会用 dataclass

---

## Day 4（周四）：项目实战日

**学习目标：** 把前 3 天学的内容整合成一个完整小项目。注意：类型注解和 Pydantic 还没学，**先用纯 Python 数据结构实现**，Week 2 学了类型后再加类型注解升级。

### 项目：Markdown 转换工具

**功能：**
- 读取 Markdown 文件
- 提取标题、代码块、链接
- 转换为 JSON 结构化数据
- 支持批量处理目录下所有 .md 文件
- 输出统计信息（字数、代码块数、链接数）

**要求（Week 1 版本，先不加类型）：**
- 用 class 组织代码
- 有基本的错误处理（文件不存在等）
- 目标约 150-200 行代码

**目录结构：**
```
phase-1/
└── markdown-parser/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   ├── __init__.py
    │   ├── parser.py       # 核心解析逻辑
    │   └── cli.py          # CLI 入口
    └── tests/
        └── test_parser.py
```

### 今日任务

- [ ] 初始化项目：`uv init markdown-parser`
- [ ] 实现核心功能（约 150-200 行代码）
- [ ] 用你自己的笔记 / README 测试

## Day 5-7（周五—周日）：练习 + 预热

**周五：** 继续完善 Markdown 转换工具，或预习 Week 2 的 Pydantic 文档。
**周末：** 休息为主。如果有余力，可以看看 [Pydantic 官方文档](https://docs.pydantic.dev/) 的开头部分。

> **本周不需要正式复盘。** Week 2 末尾会有完整的周复盘。

---

# Week 2：Python 进阶（类型 + Pydantic + 异步 + pytest）

> **目标：** 掌握 Python 对前端最友好的三个能力：类型系统、Pydantic、异步编程。然后给 Week 1 的项目加上类型升级。
> **产出物：** Markdown 转换工具升级版（加类型注解 + Pydantic + pytest 测试）

## 学习方法

- Pydantic 是本周核心——它是后续所有 Agent 开发的基石，类比前端的 Zod
- 异步可以先跑通基本用法，后续 Phase 4-6 会大量用到，不必一次性精通
- 本周结尾的 pytest 是工程化的开始，后续每阶段都要写测试

---

## Day 1（周一）：类型注解 + Pydantic（重点）

**学习目标：** 这是前端转 Python **最顺**的部分。用 TS 思维学 Pydantic。

### 核心对比

| TypeScript | Python + Pydantic |
|-----------|------------------|
| `interface User {}` | `class User(BaseModel):` |
| `z.object({...})` | `class User(BaseModel):` |
| `type User = z.infer<...>` | 自动推断 |
| `schema.parse(x)` | `User(**x)` |

### 学习内容

**1. Type Hints**
```python
def greet(name: str) -> str:
    return f"Hi {name}"

from typing import Optional, Union, List, Dict

def find_user(user_id: str) -> Optional[dict]:
    ...

def process(items: List[int]) -> Dict[str, int]:
    ...

# Python 3.10+ 可以用小写
def process(items: list[int]) -> dict[str, int]:
    ...

# Python 3.10+ 联合类型
def f(x: int | str) -> None:
    ...
```

**2. Pydantic（核心中的核心）**

这是后续 Agent 开发的基石，**必须熟练**。

```python
from pydantic import BaseModel, Field
from typing import Literal

class UserInfo(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: str | None = None
    role: Literal["admin", "user"] = "user"

# 自动校验
user = UserInfo(name="wsq", age=30)
# 序列化
user.model_dump()        # to dict
user.model_dump_json()   # to JSON string
# 反序列化
UserInfo.model_validate_json('{"name":"wsq","age":30}')
```

### 今日任务

- [ ] 安装 pydantic：`uv add pydantic`
- [ ] 为 Week 1 的 Markdown 工具定义 3-5 个 Pydantic 模型
- [ ] 实现一个 JSON 文件解析器（用 Pydantic 校验）

### 自检

- [ ] 我能用 Pydantic 定义带校验的数据模型
- [ ] 我能处理 ValidationError
- [ ] 我能序列化 / 反序列化 Pydantic 模型

---

## Day 2（周二）：异步编程 + 文件 I/O

**学习目标：** Python 异步和 JS 异步的核心差异。

### 核心对比

| JS / TS | Python |
|---------|--------|
| `Promise` | `Coroutine` |
| `async function` | `async def` |
| `await` | `await` |
| 自动事件循环 | 显式事件循环 |
| `fetch()` | `aiohttp` / `httpx` |

### 学习内容

**1. 基础 async/await**
```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)
    return f"data from {url}"

async def main():
    result = await fetch_data("https://example.com")
    print(result)

asyncio.run(main())
```

**2. 并发执行（asyncio.gather = Promise.all）**
```python
results = await asyncio.gather(
    fetch_data("url1"),
    fetch_data("url2"),
    fetch_data("url3"),
)
```

**3. HTTP 请求**
```python
import httpx

async def get_user(user_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.example.com/users/{user_id}")
        return r.json()
```

### 今日任务

- [ ] 写一个异步批量 HTTP 请求脚本（抓 5 个 URL 的标题）
- [ ] 用 asyncio.gather 并行处理
- [ ] 把结果存入 JSON 文件

### 自检

- [ ] 我能解释为什么 Python 需要 `asyncio.run()`
- [ ] 我能用 asyncio.gather 并行执行
- [ ] 我会用 httpx 发异步请求

---

## Day 3（周三）：项目升级 — 给 Week 1 工具加类型

**学习目标：** 把 Week 1 的 Markdown 转换工具用 Pydantic + 类型注解重写。

### 今日任务

- [ ] 给 Week 1 的 Markdown 转换工具加 Pydantic 数据模型（`models.py`）
- [ ] 给所有函数加类型注解
- [ ] 可选：用异步方式重写文件批量处理部分
- [ ] 跑通 `mypy src/` 类型检查

---

## Day 4（周四）：pytest 入门

**学习目标：** 学 pytest，建立测试习惯。

### 学习内容

**1. pytest 基础**
```python
# test_parser.py
from src.parser import parse_markdown

def test_parse_heading():
    result = parse_markdown("# Hello")
    assert result.title == "Hello"

def test_parse_code_block():
    md = "```python\nprint('hi')\n```"
    result = parse_markdown(md)
    assert len(result.code_blocks) == 1
```

**2. 运行测试**
```bash
uv add pytest --dev
uv run pytest -v
```

**3. fixture 和 parametrize**
```python
import pytest

@pytest.fixture
def sample_md():
    return "# Title\n\nSome content"

@pytest.mark.parametrize("md, expected_title", [
    ("# Hello", "Hello"),
    ("## Sub", "Sub"),
])
def test_headings(md, expected_title):
    ...
```

### 今日任务

- [ ] 给 Week 1 的 Markdown 工具写 5+ 个测试
- [ ] 至少用一次 fixture 和 parametrize
- [ ] 跑通 `uv run pytest -v`

### 自检

- [ ] 我能用 pytest 写基础测试
- [ ] 我会使用 fixture 复用测试数据
- [ ] 我会用 parametrize 减少重复测试

---

## Day 5-7（周五—周日）：完善 + 复盘

**周五：** 补充测试覆盖率，或预习 Week 3 的 uv/Ruff/mypy 工具链。
**周末：** 完成以下复盘。

### 周末复盘问题

回答以下问题（写在 notes 里）：
1. Python 和 JS 最大的思维差异是什么？
2. Pydantic 相比 TS 类型，有什么独特优势？
3. Python 异步相比 JS 异步，最不习惯的是什么？
4. 遇到的最大卡点是什么？怎么解决的？

- [ ] 在 [phase-1-python-llm-basics.md](./phase-1-python-llm-basics.md) 勾选 Week 1 和 Week 2 完成项

---

# Week 3：Python 工程化（uv + Ruff + pytest + CI）

> **目标：** 像前端有 ESLint/Prettier/TypeScript 一样，建立 Python 工程化肌肉记忆。
> **产出物：** 项目升级为工程化标准（uv、Ruff+mypy 通过、10+ pytest、GitHub Actions CI）

## 学习方法

- 不要追求完美，先建立"默认配置"
- 每个工具先用默认值，后续再调
- CI 是重点：本地能跑，CI 也要能跑

---

## Day 1（周一）：虚拟环境与依赖管理

**学习目标：** 掌握 `uv` 的使用，理解为什么需要虚拟环境。

### 核心对比

| JS / TS | Python |
|---------|--------|
| `package.json` | `pyproject.toml` |
| `package-lock.json` | `uv.lock` |
| `node_modules/` | `.venv/` |
| `npm install` | `uv sync` |
| `npm add x` | `uv add x` |
| `npx x` | `uv run x` |

### 学习内容

**1. 为什么需要虚拟环境**
- 不同项目依赖不同版本（A 项目要 Django 3，B 项目要 Django 5）
- 避免污染系统 Python
- 类比：node_modules 已经帮你隔离了，Python 需要显式做

**2. uv 基础**
```bash
# 创建项目
uv init my-project
cd my-project

# 添加依赖
uv add httpx pydantic

# 添加开发依赖（类似 devDependencies）
uv add pytest ruff mypy --dev

# 同步依赖（类似 npm install）
uv sync

# 运行命令（在虚拟环境中）
uv run python main.py
uv run pytest
```

**3. pyproject.toml 结构**
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.6.0",
    "mypy>=1.10.0",
]
```

### 今日任务

- [ ] 用 `uv init` 初始化一个新项目 `phase-1/chatbot`
- [ ] 添加依赖：`httpx`、`pydantic`
- [ ] 添加开发依赖：`pytest`、`ruff`、`mypy`
- [ ] 查看 `pyproject.toml` 和 `uv.lock`，理解每个字段

### 自检

- [ ] 我能解释为什么不用系统 Python
- [ ] 我会用 `uv add` 和 `uv sync`
- [ ] 我理解 `pyproject.toml` 的基本结构

---

## Day 2（周二）：代码质量工具（Ruff + mypy）

**学习目标：** 配置代码格式化和类型检查。

### 核心对比

| JS / TS | Python |
|---------|--------|
| ESLint | Ruff（lint） |
| Prettier | Ruff（format） |
| TypeScript Compiler | mypy / Pyright |
| `.eslintrc.js` | `ruff.toml` / `pyproject.toml` |

### 学习内容

**1. Ruff 配置**
```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
]
ignore = ["E501"]  # 行长度交给 format 处理

[tool.ruff.format]
quote-style = "double"
```

**2. 常用命令**
```bash
uv run ruff check .          # 检查（类似 eslint）
uv run ruff check . --fix    # 自动修复
uv run ruff format .         # 格式化（类似 prettier）
```

**3. mypy 配置**
```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

# 对第三方库放宽
[[tool.mypy.overrides]]
module = ["httpx.*"]
ignore_missing_imports = true
```

**4. VS Code 集成**
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "python.languageServer": "Pylance",
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  }
}
```

### 今日任务

- [ ] 配置 `ruff.toml` 或在 `pyproject.toml` 中加 `[tool.ruff]`
- [ ] 配置 mypy
- [ ] 在 VS Code 中启用保存自动格式化
- [ ] 故意写一行不规范的代码，看 Ruff 是否报错

### 自检

- [ ] 我能用 Ruff 检查和格式化代码
- [ ] 我能用 mypy 做类型检查
- [ ] VS Code 保存时自动格式化生效

---

## Day 3（周三）：pytest 基础

**学习目标：** 学会用 pytest 写测试，建立测试习惯。

### 核心对比

| JS / TS (Jest) | Python (pytest) |
|---------------|----------------|
| `test('xxx', () => {})` | `def test_xxx():` |
| `expect(x).toBe(y)` | `assert x == y` |
| `beforeEach` | `@pytest.fixture` |
| `describe` | （无，用文件/类组织） |
| `jest.fn()` | `unittest.mock.MagicMock` |

### 学习内容

**1. 基础测试**
```python
# src/calculator.py
def add(a: int, b: int) -> int:
    return a + b

# tests/test_calculator.py
from src.calculator import add

def test_add_basic():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -2) == -3

def test_add_zero():
    assert add(0, 0) == 0
```

**2. 运行测试**
```bash
uv run pytest                 # 跑所有
uv run pytest -v              # 详细模式
uv run pytest tests/test_x.py # 指定文件
uv run pytest -k "add"        # 按名称过滤
uv run pytest --cov=src       # 覆盖率
```

**3. fixture（重点）**
```python
import pytest
from src.user import User

@pytest.fixture
def sample_user():
    return User(name="wsq", age=30)

def test_user_name(sample_user):
    assert sample_user.name == "wsq"

def test_user_greet(sample_user):
    assert "wsq" in sample_user.greet()
```

**4. 参数化测试**
```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, -2, -3),
    (0, 0, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**5. Mock**
```python
from unittest.mock import MagicMock, patch

def test_fetch_user():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "wsq"}

    with patch("httpx.get", return_value=mock_response):
        result = fetch_user("123")
        assert result["name"] == "wsq"
```

### 今日任务

- [ ] 把 Day 1 的项目加 `tests/` 目录
- [ ] 写 5+ 个基础测试
- [ ] 至少用一次 fixture 和 parametrize
- [ ] 跑 `uv run pytest -v` 全部通过

### 自检

- [ ] 我能用 pytest 写基础测试
- [ ] 我会使用 fixture 复用测试数据
- [ ] 我会用 parametrize 减少重复测试

---

## Day 4（周四）：项目结构 + 模块化

**学习目标：** 组织一个清晰的 Python 项目结构。

### 学习内容

**1. 推荐项目结构**
```
chatbot/
├── pyproject.toml
├── README.md
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── main.py           # 入口
│       ├── config.py         # 配置
│       ├── models.py         # Pydantic 模型
│       ├── services/         # 业务逻辑
│       │   ├── __init__.py
│       │   └── llm.py
│       └── utils/            # 工具函数
│           ├── __init__.py
│           └── logging.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_services.py
```

**2. src 布局的好处**
- 避免导入歧义
- 强制安装后才能导入（更接近生产环境）
- 类比前端的 `src/` 目录

**3. `__init__.py` 的作用**
- 标记一个目录是 Python 包
- 可以用来导出公共接口
```python
# src/chatbot/__init__.py
from .main import main

__all__ = ["main"]
```

**4. 配置管理**
```python
# src/chatbot/config.py
from pydantic import BaseModel
from pathlib import Path

class Config(BaseModel):
    api_key: str
    model: str = "gpt-5-latest"
    max_tokens: int = 1000

# 从环境变量加载
import os
config = Config(
    api_key=os.environ["OPENAI_API_KEY"],
)
```

更好的方式：`pydantic-settings`
```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    api_key: str
    model: str = "gpt-5-latest"

    model_config = {"env_prefix": "CHATBOT_", "env_file": ".env"}

config = Config()
# 自动从 CHATBOT_API_KEY 环境变量加载
```

### 今日任务

- [ ] 把现有代码重构为 src 布局
- [ ] 拆分至少 3 个模块（main / models / services）
- [ ] 用 pydantic-settings 管理配置
- [ ] 创建 `.env.example` 模板

### 自检

- [ ] 我的项目结构清晰、模块化
- [ ] 配置通过环境变量加载，不硬编码
- [ ] 所有测试仍然通过

---

## Day 5（周五）：日志与错误处理

**学习目标：** 建立工业级的日志和错误处理习惯。

### 学习内容

**1. 为什么不用 print**
- 无法控制级别（INFO/WARNING/ERROR）
- 无法输出到文件
- 无法关闭
- 没有时间戳和上下文

**2. 标准 logging**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Starting app")
logger.warning("This is a warning")
logger.error("Something went wrong", exc_info=True)
```

**3. structlog（推荐，结构化日志）**
```python
import structlog

logger = structlog.get_logger()

logger.info("user_login", user_id="123", ip="1.2.3.4")
logger.error("api_call_failed", endpoint="/users", status=500)
```

**4. 错误处理最佳实践**
```python
# 不要这样
try:
    do_something()
except:
    pass  # 吞掉所有错误

# 要这样
class MyAppError(Exception):
    """所有应用异常的基类"""

class UserNotFoundError(MyAppError):
    pass

def get_user(user_id: str):
    user = db.find(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return user

# 调用方
try:
    user = get_user("123")
except UserNotFoundError as e:
    logger.warning("user_not_found", user_id="123")
    return None
except MyAppError as e:
    logger.error("app_error", error=str(e))
    raise
```

**5. 自定义异常层级**
```
MyAppError（基类）
├── UserError
│   ├── UserNotFoundError
│   └── InvalidUserError
├── APIError
│   ├── RateLimitError
│   └── ServerError
└── ConfigError
```

### 今日任务

- [ ] 替换所有 `print` 为 `logging` 或 `structlog`
- [ ] 定义 3+ 个自定义异常
- [ ] 给关键函数加错误处理
- [ ] 把日志输出到文件（`logging.FileHandler`）

### 自检

- [ ] 我不再用 `print` 调试
- [ ] 我有清晰的异常层级
- [ ] 关键错误被记录，而不是被吞掉

---

## Day 6（周六）：项目实战日

**学习目标：** 整合 Week 1-2 所学，做出一个工程化的项目。

### 项目：URL 短链生成器（CLI）

**功能：**
- 输入长 URL，生成短链
- 支持自定义短码
- 支持查询短链对应的原始 URL
- 数据持久化到 JSON 文件

**要求：**
- 用 `uv` 管理依赖
- Ruff + mypy 通过
- 至少 10 个 pytest 测试
- 用 structlog 记录日志
- 清晰的模块拆分（main / models / services / storage）
- 自定义异常
- 用 pydantic-settings 管理配置

**目录结构：**
```
phase-1/
└── url-shortener/
    ├── pyproject.toml
    ├── README.md
    ├── .env.example
    ├── src/
    │   └── url_shortener/
    │       ├── __init__.py
    │       ├── main.py
    │       ├── config.py
    │       ├── models.py
    │       ├── services.py
    │       ├── storage.py
    │       └── exceptions.py
    └── tests/
        ├── test_services.py
        └── test_storage.py
```

### 今日任务

- [ ] 完整实现这个项目（约 300-400 行代码）
- [ ] 跑通所有测试
- [ ] 写 README 说明如何使用

---

## Day 7（周日）：CI/CD + 复盘

**学习目标：** 用 GitHub Actions 自动化质量检查。

### 学习内容

**1. GitHub Actions 基础**
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest --cov
```

**2. pre-commit hooks（可选）**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### 今日任务

- [ ] 给 Day 6 的项目加 GitHub Actions CI
- [ ] 推送到 GitHub，观察 CI 运行
- [ ] 故意提交一个 lint 错误，看 CI 是否拦截
- [ ] 在 [phase-1-python-llm-basics.md](./phase-1-python-llm-basics.md) 勾选 Week 3 完成项

### 周末复盘问题

1. Python 的工程化工具链和前端（npm + ESLint + TypeScript + Jest）的对应关系，你理清了吗？
2. uv 相比 pip/poetry 的优势是什么？
3. pytest 相比 Jest，你最不习惯的是什么？
4. 遇到的最大卡点是什么？

---

# Week 4：LLM API 调用 + Prompt 基础

> **目标：** 第一次真正接触 LLM，重点是理解 API 协议，不急着学 Prompt 技巧。
> **产出物：** CLI 聊天机器人 v1（支持流式输出）

## 学习方法

- 先用一家 API，跑通后再换另一家对比
- 重点理解 messages 结构和参数含义
- 流式输出是必学的，所有生产应用都用

---

## Day 1（周一）：API Key 准备 + 第一次调用

**学习目标：** 申请 API Key，跑通第一个 LLM 调用。

### 学习内容

**1. API Key 申请**
- **OpenAI：** https://platform.openai.com/api-keys（需要科学上网）
- **Anthropic：** https://console.anthropic.com/
- **国内备选（推荐先备一个）：**
  - 通义千问：https://dashscope.aliyun.com/
  - DeepSeek：https://platform.deepseek.com/
  - 智谱：https://open.bigmodel.cn/
  - Moonshot：https://platform.moonshot.cn/

**2. 环境变量管理**
```bash
# .env
OPENAI_API_KEY=sk-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx

# .gitignore 必须包含
.env
```

```python
# src/config.py
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str | None = None

    model_config = {"env_file": ".env"}

config = Config()
```

**3. 第一次调用（OpenAI）**
```python
from openai import OpenAI

client = OpenAI()  # 自动从 OPENAI_API_KEY 环境变量读取

response = client.chat.completions.create(
    model="gpt-5-latest",
    messages=[
        {"role": "system", "content": "你是一个友好的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"},
    ],
    temperature=0.7,
    max_tokens=500,
)

print(response.choices[0].message.content)
print(f"用了 {response.usage.total_tokens} tokens")
```

**4. 第一次调用（Anthropic）**
```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-latest",
    max_tokens=500,
    system="你是一个友好的助手。",
    messages=[
        {"role": "user", "content": "你好，请介绍一下自己。"},
    ],
)

print(response.content[0].text)
print(f"输入 {response.usage.input_tokens}，输出 {response.usage.output_tokens}")
```

### 今日任务

- [ ] 至少申请 2 家 API Key
- [ ] 配置 `.env` 和 `.gitignore`
- [ ] 跑通 OpenAI 和 Anthropic 的基础调用
- [ ] 观察响应结构，理解每个字段

### 自检

- [ ] 我能用 Python 调用 LLM API
- [ ] 我理解 messages 数组的结构
- [ ] 我能从响应中提取生成的文本

---

## Day 2（周二）：messages 结构 + 参数详解

**学习目标：** 深入理解请求参数。

### 学习内容

**1. messages 结构**
```python
messages = [
    {"role": "system", "content": "你是一个 Python 专家"},     # 全局设定
    {"role": "user", "content": "怎么读文件？"},               # 用户提问
    {"role": "assistant", "content": "可以用 open()..."},     # AI 上次回答
    {"role": "user", "content": "能写个例子吗？"},             # 继续提问
]
```

**2. 核心参数**
| 参数 | 作用 | 推荐值 |
|------|------|--------|
| `temperature` | 随机性（0=确定，2=混乱） | 代码：0；创意：0.7；头脑风暴：1.0 |
| `max_tokens` | 最大输出长度 | 根据任务，通常 500-2000 |
| `top_p` | 核采样（和 temperature 二选一） | 通常用 1.0 |
| `stop` | 停止序列 | 需要时设置 |
| `frequency_penalty` | 抑制重复词 | 0-2，通常 0 |
| `presence_penalty` | 鼓励新话题 | 0-2，通常 0 |

**3. system 消息的作用**
- 设定 AI 的角色、能力、约束
- 对所有后续消息生效
- OpenAI：放在 messages 数组开头
- Anthropic：单独的 `system` 参数

**4. 多轮对话管理**
```python
class ChatSession:
    def __init__(self, system_prompt: str = "你是助手"):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def chat(self, user_input: str) -> str:
        self.add_user(user_input)
        response = client.chat.completions.create(
            model="gpt-5-latest",
            messages=self.messages,
        )
        reply = response.choices[0].message.content
        self.add_assistant(reply)
        return reply
```

### 今日任务

- [ ] 实现一个 ChatSession 类
- [ ] 测试多轮对话（上下文能记住）
- [ ] 实验不同 temperature 的差异（同一问题问 5 次）
- [ ] 实验不同 system prompt 的差异

### 自检

- [ ] 我理解 messages 数组的流转
- [ ] 我知道什么时候用低/高 temperature
- [ ] 我能维护多轮对话的上下文

---

## Day 3（周三）：Token 与计费

**学习目标：** 理解 token，能估算成本。

### 学习内容

**1. Token 是什么**
- LLM 不是按"字"处理，是按 token
- 英文：约 1 词 = 1.3 token
- 中文：1 字 ≈ 1-2 token
- 代码：更多（每个符号都算）

**2. 用 tiktoken 数 token**
```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # 新模型 tiktoken 可能不识别，用通用编码做近似
tokens = enc.encode("你好，世界！Hello, world!")
print(len(tokens))  # 大约 9-10 个 token
print(tokens)        # [151331, 100013, 99352, ...]
```

**3. 计费模型**
- 输入 token 和输出 token 价格不同
- 输出通常贵 3-4 倍
- **价格随时在变**，且各厂每隔几个月会调价。请直接查官方定价页，不要记具体数字：
  - OpenAI：https://developers.openai.com/api/docs/pricing
  - Anthropic：https://platform.claude.com/docs/pricing
  - DeepSeek：https://platform.deepseek.com/pricing
- 粗略量级感（2026-07，仅做直觉参考）：旗舰模型输入约 $1-5/1M、输出 $5-30/1M；经济型模型约便宜 10-20 倍；国内 DeepSeek 等更便宜。

**4. 成本估算**
```python
def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price: float,  # $/1M
    output_price: float,
) -> float:
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000

# 一次经济型模型调用示例，1000 输入 + 500 输出
# 价格请用你查询到的当日实际价格填入
cost = estimate_cost(1000, 500, input_price=0.15, output_price=0.6)
# 按示例价格 = $0.00045，约 0.003 人民币
```

### 今日任务

- [ ] 安装 tiktoken：`uv add tiktoken`
- [ ] 数一下你最近 5 次 API 调用的 token
- [ ] 写一个成本计算器函数
- [ ] 估算"如果每天调用 1000 次，月成本多少"

### 自检

- [ ] 我能解释 token 和字的区别
- [ ] 我会用 tiktoken 数 token
- [ ] 我能估算 API 调用成本

---

## Day 4（周四）：流式输出

**学习目标：** 实现打字机效果，所有生产应用必备。

### 学习内容

**1. 为什么需要流式**
- 用户体验：等待 10 秒看到完整回答 vs 立刻开始看到逐字输出
- 长输出场景：避免超时
- 类似前端的 SSR 流式渲染

**2. OpenAI 流式**
```python
stream = client.chat.completions.create(
    model="gpt-5-latest",
    messages=[{"role": "user", "content": "写一首关于秋天的诗"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

**3. Anthropic 流式**
```python
with client.messages.stream(
    model="claude-sonnet-4-5-latest",
    max_tokens=500,
    messages=[{"role": "user", "content": "写一首诗"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**4. Python 生成器封装**
```python
from typing import Iterator

def stream_chat(messages: list[dict], model: str = "gpt-5-latest") -> Iterator[str]:
    """流式聊天，yield 每个文本块"""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content

# 使用
for chunk in stream_chat([{"role": "user", "content": "你好"}]):
    print(chunk, end="", flush=True)
```

**5. SSE 协议（了解）**
- Server-Sent Events
- 后续 FastAPI 部分会用
- 数据格式：`data: {...}\n\n`

### 今日任务

- [ ] 实现流式聊天函数
- [ ] 实现打字机效果（用 `time.sleep` 减慢）
- [ ] 同时支持 OpenAI 和 Anthropic 流式
- [ ] 测试流式中途取消（`KeyboardInterrupt`）

### 自检

- [ ] 我能实现流式输出
- [ ] 我会用 Python 生成器
- [ ] 我理解 SSE 的基本概念

---

## Day 5（周五）：CLI 聊天机器人 v1

**学习目标：** 整合 Day 1-4 所学，做出第一个完整作品。

### 项目：CLI 聊天机器人 v1

**功能：**
- 命令行交互（类似 ChatGPT 的终端版）
- 支持多轮对话
- 支持流式输出
- 支持切换模型（OpenAI / Anthropic）
- 支持命令：`/quit`、`/clear`、`/model <name>`

**核心代码结构**
```python
# src/chatbot/__main__.py
from rich.console import Console
from chatbot.session import ChatSession
from chatbot.config import Config

console = Console()

def main():
    config = Config()
    session = ChatSession(config)

    console.print("[bold green]CLI 聊天机器人 v1[/]")
    console.print("输入 /quit 退出，/clear 清空对话\n")

    while True:
        try:
            user_input = console.input("[bold blue]你>[/] ")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input == "/quit":
            break
        if user_input == "/clear":
            session.clear()
            continue
        if user_input.startswith("/model "):
            session.switch_model(user_input[7:])
            continue

        # 流式输出：stream_chat 返回生成器，必须用 for 循环迭代才会真正产生输出。
        # 漏掉 for 循环是最常见的坑（生成器惰性求值，不迭代 = 什么都不发生）。
        console.print("[bold green]AI>[/] ", end="")
        try:
            for chunk in session.stream_chat(user_input):
                console.print(chunk, end="")
            console.print()  # 换行
        except Exception as e:
            console.print(f"\n[red]错误: {e}[/]")  # 单次失败不退出整个会话

if __name__ == "__main__":
    main()
```

> 💡 **关键点：** `stream_chat()` 返回的是 Python 生成器（`Generator[str, None, None]`）。**生成器是惰性的**——只有被 `for` 循环迭代时，函数体才会真正执行。直接 `reply = session.stream_chat(user_input)` 不做迭代，等于什么都没发生。
>
> 这个坑很常见，**前端类比**：生成器 ≈ RxJS 的 Observable 或 Node.js 的 Readable Stream——光创建不订阅，里面什么都不会跑。

### 今日任务

- [ ] 完整实现 CLI 聊天机器人 v1
- [ ] 用 `rich` 库美化输出（彩色提示符、错误高亮）
- [ ] 测试所有命令（`/quit`、`/clear`、`/model <name>`）
- [ ] 在 README 写使用说明

> 📝 **关于 Markdown 渲染：** 流式过程中渲染 Markdown 需要用 `rich.live.Live` 实时刷新整段内容，属于进阶技能。v1 先做到"彩色输出 + 流式打字机"即可；Markdown 渲染放到 Week 5（结构化输出）或 Phase 6（前端集成）再处理。

---

## Day 6（周六）：增强功能 + 测试

**学习目标：** 给聊天机器人加测试和一些增强功能。

### 学习内容

**1. 给 LLM 调用加测试（mock）**
```python
# tests/test_session.py
from unittest.mock import MagicMock, patch
from chatbot.session import ChatSession

@patch("chatbot.session.OpenAI")
def test_chat(mock_openai_class):
    # 准备 mock
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "你好！"
    mock_client.chat.completions.create.return_value = mock_response

    # 测试
    session = ChatSession(...)
    reply = session.chat("你好")

    assert reply == "你好！"
    # 参考实现里 ChatSession.messages 只存 user/assistant 两条，
    # system prompt 由 Provider 内部处理（不进 messages 数组）。
    # 如果你把 system 也存进 messages，这里应该是 3。
    assert len(session.messages) == 2  # user + assistant
```

**2. 增强功能**
- 对话历史持久化（JSON 文件）
- 显示 token 使用量
- 彩色输出（用 `rich`）
- 代码块语法高亮
- 支持粘贴多行输入

**3. 错误处理增强**
```python
import time
from openai import RateLimitError, APIConnectionError

def safe_chat(self, user_input: str) -> str:
    for attempt in range(3):
        try:
            return self.chat(user_input)
        except RateLimitError:
            time.sleep(2 ** attempt)  # 指数退避：1s, 2s, 4s
        except APIConnectionError as e:
            console.print(f"[red]连接失败: {e}[/]")
            return ""
    return "[请求失败，请重试]"
```

### 今日任务

- [ ] 给聊天机器人写 5+ 个测试（mock LLM 调用）
- [ ] 实现对话历史持久化
- [ ] 实现错误重试（限流、超时）
- [ ] 显示每次对话的 token 消耗

---

## Day 7（周日）：复盘 + 文档

### 今日任务

- [ ] 完整测试 CLI 聊天机器人 v1
- [ ] 写 README（包含安装、使用、截图）
- [ ] 提交到 GitHub
- [ ] 在 [phase-1-python-llm-basics.md](./phase-1-python-llm-basics.md) 勾选 Week 4 完成项

### 周末复盘问题

1. OpenAI 和 Anthropic 的 API 设计，你觉得哪个更优雅？为什么？
2. temperature 这个参数，你怎么理解它的作用？
3. 流式输出相比一次性返回，实现复杂度增加了多少？
4. 成本估算后，你对"AI 应用成本"有什么新认识？

---

# Week 5：结构化输出 + 错误处理

> **目标：** 真正的 Agent 应用 99% 都需要结构化输出，这是从"玩具"到"工程"的关键一步。
> **产出物：** CLI 聊天机器人 v2（支持结构化指令）

## 学习方法

- 重点理解 Pydantic 与 LLM 输出的结合
- 错误处理是这一周的核心
- 重试机制要做到"智能"（不是盲目重试）

---

## Day 1（周一）：JSON Mode 与 Structured Outputs

**学习目标：** 让 LLM 稳定输出 JSON。

### 学习内容

**1. 为什么需要结构化输出**
- 自然语言输出无法被程序解析
- LLM 经常"跑题"，输出多余内容
- 下游程序（前端、数据库）需要结构化数据

**2. JSON Mode（基础）**
```python
response = client.chat.completions.create(
    model="gpt-5-latest",
    messages=[{
        "role": "user",
        "content": "提取这句话的人名和年龄：'张三今年 30 岁'",
    }],
    response_format={"type": "json_object"},
)
# 输出保证是合法 JSON
```

**注意：** 必须在 prompt 中明确要求输出 JSON，否则会报错。

**3. Structured Outputs（强约束，推荐）**
```python
from pydantic import BaseModel

class PersonInfo(BaseModel):
    name: str
    age: int

response = client.beta.chat.completions.parse(
    model="gpt-5-latest",
    messages=[{
        "role": "user",
        "content": "提取：'张三今年 30 岁'",
    }],
    response_format=PersonInfo,
)

person = response.choices[0].message.parsed
# PersonInfo(name='张三', age=30)
```

**4. Anthropic 的方式（通过 tool use）**
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-latest",
    max_tokens=1024,
    tools=[{
        "name": "extract_person",
        "description": "提取人物信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }],
    tool_choice={"type": "tool", "name": "extract_person"},
    messages=[{"role": "user", "content": "张三今年 30 岁"}],
)

import json
person_data = json.loads(response.content[0].input)
# {"name": "张三", "age": 30}
```

### 今日任务

- [ ] 用 JSON Mode 实现一个简单的信息提取
- [ ] 用 Structured Outputs（Pydantic）实现同样的功能
- [ ] 对比两种方式的稳定性
- [ ] 故意输入模糊的句子，看 LLM 如何处理

### 自检

- [ ] 我能用 JSON Mode 让 LLM 输出合法 JSON
- [ ] 我会用 Pydantic 模型约束 LLM 输出
- [ ] 我理解 OpenAI 和 Anthropic 实现结构化输出的差异

---

## Day 2（周二）：Pydantic 输出校验 + 重试

**学习目标：** 处理 LLM 输出不符合 schema 的情况。

### 学习内容

**1. 输出校验**
```python
from pydantic import BaseModel, Field, ValidationError

class Summary(BaseModel):
    title: str = Field(description="简洁标题")
    summary: str = Field(description="100 字以内摘要")
    keywords: list[str] = Field(description="3-5 个关键词")

def generate_summary(text: str) -> Summary:
    response = client.beta.chat.completions.parse(
        model="gpt-5-latest",
        messages=[{
            "role": "user",
            "content": f"请总结以下内容：\n\n{text}",
        }],
        response_format=Summary,
    )
    return response.choices[0].message.parsed
```

**2. 用 tenacity 做重试**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ValidationError, APIError)),
)
def generate_summary_robust(text: str) -> Summary:
    try:
        return generate_summary(text)
    except ValidationError as e:
        logger.warning("validation_failed", error=str(e))
        raise
```

**3. 自修复 Prompt**
```python
def generate_with_repair(text: str, max_attempts: int = 3) -> Summary:
    messages = [
        {"role": "user", "content": f"总结：\n\n{text}"},
    ]

    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model="gpt-5-latest",
            messages=messages,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content

        try:
            return Summary.model_validate_json(raw)
        except ValidationError as e:
            # 让 LLM 看到自己的错误，修复后重试
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"你的输出格式有问题：{e}\n请修正后重新输出。",
            })

    raise ValueError(f"Failed after {max_attempts} attempts")
```

### 今日任务

- [ ] 定义 3+ 个 Pydantic 输出模型
- [ ] 实现 tenacity 重试
- [ ] 实现自修复 Prompt
- [ ] 测试：故意构造难以解析的输入

### 自检

- [ ] 我能用 Pydantic 校验 LLM 输出
- [ ] 我会用 tenacity 做指数退避重试
- [ ] 我能实现"自修复"重试逻辑

---

## Day 3（周三）：Function Calling 入门

**学习目标：** 理解 Function Calling / Tool Use 的概念和协议。

### 学习内容

**1. Function Calling 是什么**
- 让 LLM "调用函数"
- LLM 决定调用哪个函数、传什么参数
- 实际执行由你的代码完成
- 这是 Agent 的基石

**2. OpenAI Function Calling**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名"},
            },
            "required": ["city"],
        },
    },
}]

response = client.chat.completions.create(
    model="gpt-5-latest",
    messages=[{"role": "user", "content": "北京天气怎么样？"}],
    tools=tools,
)

# LLM 决定调用 get_weather
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name)       # "get_weather"
print(tool_call.function.arguments)  # '{"city": "北京"}'
```

**3. 完整的调用循环**
```python
import json

def get_weather(city: str) -> str:
    # 实际调用天气 API
    return f"{city} 今天 25 度，晴"

# 第一次调用：LLM 决定调用工具
messages = [{"role": "user", "content": "北京天气怎么样？"}]
response = client.chat.completions.create(
    model="gpt-5-latest",
    messages=messages,
    tools=tools,
)
message = response.choices[0].message

# 执行工具
if message.tool_calls:
    messages.append(message)
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # 第二次调用：LLM 根据工具结果生成最终回答
    final = client.chat.completions.create(
        model="gpt-5-latest",
        messages=messages,
        tools=tools,
    )
    print(final.choices[0].message.content)
    # "北京今天 25 度，晴天。"
```

### 今日任务

- [ ] 实现 1 个完整的 Function Calling 流程
- [ ] 用 mock 函数测试
- [ ] 用真实的免费 API（如 wttr.in 天气）替换 mock

### 自检

- [ ] 我能定义一个 function schema
- [ ] 我能解析 LLM 的 tool_call
- [ ] 我能执行工具并把结果返回给 LLM

---

## Day 4（周四）：多工具编排

**学习目标：** 让 LLM 在多个工具中选择和组合。

### 学习内容

**1. 定义多个工具**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
```

**2. 工具注册表（重要模式）**
```python
from typing import Callable, Any

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: list[dict] = []

    def register(self, name: str, description: str, parameters: dict):
        def decorator(func: Callable):
            self._tools[name] = func
            self._schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            })
            return func
        return decorator

    def execute(self, name: str, **kwargs) -> Any:
        return self._tools[name](**kwargs)

    @property
    def schemas(self) -> list[dict]:
        return self._schemas


registry = ToolRegistry()

@registry.register(
    name="get_weather",
    description="获取天气",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
)
def get_weather(city: str) -> str:
    return f"{city} 25 度晴"
```

**3. Agent 循环（雏形）**
```python
def run_agent(user_input: str, max_turns: int = 5):
    messages = [{"role": "user", "content": user_input}]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-5-latest",
            messages=messages,
            tools=registry.schemas,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content  # LLM 给出最终答案

        # 执行所有工具调用
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = registry.execute(tool_call.function.name, **args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "达到最大轮数"
```

### 今日任务

- [ ] 实现 ToolRegistry
- [ ] 注册 3+ 个工具
- [ ] 实现 Agent 循环
- [ ] 测试组合调用（如"北京天气 + 计算 25 + 17"）

### 自检

- [ ] 我能用注册表模式管理多个工具
- [ ] 我能实现基本的 Agent 循环
- [ ] 我理解 LLM 如何决定调用哪个工具

---

## Day 5（周五）：CLI 聊天机器人 v2

**学习目标：** 把结构化输出和 Function Calling 整合到聊天机器人。

### 项目：CLI 聊天机器人 v2

**新增功能（在 v1 基础上）：**
- `/translate <text>` → 返回 JSON `{"original": ..., "translation": ...}`
- `/summarize <url>` → 返回 JSON `{"title": ..., "summary": ..., "keywords": [...]}`
- `/sentiment <text>` → 返回 JSON `{"sentiment": "positive|negative|neutral", "score": 0.8}`
- `/tools` → 进入工具模式，LLM 自动决定调用哪个工具

**实现要点：**
```python
class ChatBotV2:
    def __init__(self, config: Config):
        self.session = ChatSession(config)
        self.registry = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        # 注册天气、计算、时间等工具
        ...

    def handle_command(self, user_input: str) -> str:
        if user_input.startswith("/translate "):
            return self._translate(user_input[11:])
        if user_input.startswith("/summarize "):
            return self._summarize(user_input[11:])
        # ...
        return self.session.chat(user_input)

    def _translate(self, text: str) -> str:
        class Translation(BaseModel):
            original: str
            translation: str

        result = self.session.structured_chat(
            f"翻译为英文：{text}",
            response_format=Translation,
        )
        return result.model_dump_json(indent=2)
```

### 今日任务

- [ ] 在 v1 基础上实现 v2
- [ ] 实现 3+ 个结构化指令
- [ ] 实现工具模式
- [ ] 所有结构化输出都有 Pydantic 校验

---

## Day 6（周六）：增强 + 测试

### 今日任务

- [ ] 给 v2 写完整测试（mock LLM 调用）
- [ ] 实现错误重试（限流、解析失败）
- [ ] 加日志记录（每次调用、token、耗时）
- [ ] 实现"自修复"重试机制

---

## Day 7（周日）：阶段总结 + 复盘

### 今日任务

- [ ] 完整测试 CLI 聊天机器人 v2
- [ ] 更新 README
- [ ] 提交到 GitHub
- [ ] 在 [phase-1-python-llm-basics.md](./phase-1-python-llm-basics.md) 勾选所有完成项
- [ ] 写阶段总结到 `notes/phase-1-summary.md`

### 阶段复盘问题

回答以下问题（写进 notes）：
1. 从前端转 Python，最大的思维转变是什么？
2. Pydantic 在你的项目中扮演了什么角色？
3. LLM API 的"不确定性"（同样输入不同输出），你怎么看待？
4. Function Calling 让你想起了前端的什么模式？
5. 如果重学这 5 周，你会怎么调整？

---

# Week 6（缓冲周）：补作业 / 复盘 / 赶进度

> **目标：** 这一周不安排新内容。用于查漏补缺、补充测试、写阶段总结。**多数兼职学习的人会用到这里。**

## 建议任务

- [ ] 回顾 Week 1-5 所有带 `[ ]` 的勾选框，补上漏掉的任务
- [ ] 给 CLI 聊天机器人 v2 写完整测试
- [ ] 整理代码，确保 `ruff check . && mypy src/ && pytest` 全部通过
- [ ] 写阶段总结到 `notes/phase-1-summary.md`（回答 Week 5 Day 7 的复盘问题）
- [ ] 在 [phase-1-python-llm-basics.md](./phase-1-python-llm-basics.md) 勾选所有完成项
- [ ] 更新 GitHub，让项目 README 完整

**如果你提前做完了以上所有——直接进入第 2 阶段，你已经领先了 90% 的人。**

---

## 常见卡点速查

| 卡点 | 解决方案 |
|------|---------|
| 缩进报错 `IndentationError` | 检查是否混用空格和 Tab，统一用 4 空格 |
| `ModuleNotFoundError` | 检查 PYTHONPATH、是否在虚拟环境中 |
| 类型注解不生效 | VS Code 装 Pylance，检查 Python 解释器 |
| Pydantic v1 vs v2 报错 | 确认版本，v2 用 `model_dump()` 不是 `dict()` |
| asyncio 报 "coroutine never awaited" | 检查是否漏了 `await` |
| 装饰器看不懂 | 暂时跳过，Week 3 再补 |
| API Key 不稳定 | 多备几家，写个 provider 切换函数 |
| Function Calling 不触发 | 检查工具 description 是否清晰 |
| Structured Outputs 报错 | 确认模型支持（gpt-5-latest 及以上） |
| Token 超限 | 截断历史对话，或用摘要压缩 |

## 推荐速查资源

- [Python vs JavaScript 语法对照表](https://hyperpolyglot.org/scripting)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [Real Python 异步教程](https://realpython.com/async-io-python/)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

## 第 1 阶段完成标准

- [ ] 能熟练用 `uv` 创建项目、管理依赖
- [ ] 能用 pytest 写基础测试
- [ ] 能用 OpenAI / Anthropic SDK 发起请求
- [ ] 能处理流式输出
- [ ] 能用 Pydantic 定义输出 schema
- [ ] 能实现 Function Calling 基础逻辑
- [ ] 能写带重试和错误处理的 API 调用
- [ ] CLI 聊天机器人 v2 可运行、有测试、已部署到 GitHub

**准备好进入第 2 阶段：[LLM 原理 + Prompt 工程](./phase-2-daily-plan.md)**
