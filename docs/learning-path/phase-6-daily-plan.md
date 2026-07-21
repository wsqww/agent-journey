# 第 6 阶段每日计划：评测 + 部署 + 作品集

> **周期：** 5 周（Phase 6 / Week 1-5，独立编号，非全局周号）

## 学习方法（本阶段专属）

1. **作品优先** — 本阶段所有学习都围绕"让 3 个项目能上线、能展示"展开
2. **前端是放大器** — 每个后端能力都要用前端展示出来，这是你碾压纯后端候选人的地方
3. **以终为始** — 每周末都要问"这周让我的求职竞争力提升了多少？"
4. **不要追求完美** — Demo 能跑、能讲清楚 > 代码精致但没上线

## 进度追踪

- [ ] Week 1 - 工业级评测体系
- [ ] Week 2 - 后端部署与服务化
- [ ] Week 3 - 前端集成（发挥优势）
- [ ] Week 4 - 作品集打磨
- [ ] Week 5 - 求职准备
- [ ] 阶段产出物：3 个上线项目 + 求职材料

---

# Week 1：工业级评测体系

> **本周目标：** 给作品集项目 #1（知识助手）和 #2（研究团队）建立完整评测体系
> **本周产出：** 分层评测 + 50+ 评测用例 + CI 自动化 + 评测报告

## Day 1（周一）：评测分层与单元评测

**学习目标：** 理解工业级评测的分层思路，建立单元评测。

### 核心概念

**评测三层金字塔（从下到上，数量递减）：**

```
        ┌──────────┐
        │ 端到端 E2E │  ← 10-20 条（用户任务级）
        ├──────────┤
        │ 集成测试   │  ← 30-50 条（多组件协作）
        ├──────────┤
        │ 单元测试   │  ← 100+ 条（单工具 / 单 Prompt）
        └──────────┘
```

**单元评测的对象：**
- 单个 Prompt（输入 → 输出）
- 单个工具（参数 → 返回）
- 单个检索器（query → docs）
- 单个解析器（raw → structured）

### 代码示例

**Python：单元评测脚手架**

```python
# tests/unit/test_retriever.py
import pytest
from app.rag.retriever import Retriever

class TestRetriever:
    """检索器单元评测"""

    @pytest.fixture
    def retriever(self):
        return Retriever(collection="test_docs")

    @pytest.mark.parametrize("query,expected_keyword", [
        ("如何配置 FastAPI 的 CORS", "cors"),
        ("Pydantic 怎么校验嵌套模型", "nested"),
        ("async gather 和 wait 区别", "gather"),
    ])
    def test_retrieve_relevant(self, retriever, query, expected_keyword):
        docs = retriever.search(query, top_k=3)
        assert len(docs) > 0
        assert any(expected_keyword in d.content.lower() for d in docs)

    def test_empty_query_returns_empty(self, retriever):
        docs = retriever.search("", top_k=3)
        assert docs == []
```

**TypeScript：前端工具函数的单元评测（对比思维）**

```typescript
// tests/prompt.test.ts
import { describe, it, expect } from 'vitest'
import { buildRagPrompt } from '@/lib/prompt'

describe('buildRagPrompt', () => {
  it('包含检索到的上下文', () => {
    const prompt = buildRagPrompt({
      query: '什么是 RAG',
      context: [{ content: 'RAG 是检索增强生成' }],
    })
    expect(prompt).toContain('RAG 是检索增强生成')
  })

  it('上下文为空时走兜底 Prompt', () => {
    const prompt = buildRagPrompt({ query: 'hi', context: [] })
    expect(prompt).toContain('无法找到相关资料')
  })
})
```

### 今日任务

- [ ] 列出项目 #1 中所有可做单元评测的组件（≥5 个）
- [ ] 给检索器写 5+ 条参数化测试
- [ ] 给 Prompt 构造函数写 3+ 条测试
- [ ] 跑通 `pytest tests/unit -v`

### 自检清单

- [ ] 我能解释为什么评测要分层（而不是只做端到端）
- [ ] 我能区分单元评测和端到端评测的边界
- [ ] 我会使用 `@pytest.mark.parametrize` 做批量测试

---

## Day 2（周二）：集成评测 + 端到端评测

**学习目标：** 给多组件协作和完整用户任务写评测。

### 核心概念

**集成评测关注：**
- 检索器 + LLM 的协作（RAG 端到端）
- 工具选择 + 工具执行的协作
- 记忆模块 + Prompt 构造的协作

**端到端评测关注：**
- 完整用户任务（"帮我总结这个 PDF"）
- 最终输出质量（不只是中间步骤）
- 真实场景的复杂 query

### 代码示例

**Python：端到端评测（带打分）**

```python
# tests/e2e/test_qa_flow.py
import pytest
from app.agent import KnowledgeAgent
from app.eval.scorer import exact_match, fuzzy_match, llm_judge

agent = KnowledgeAgent()

@pytest.mark.asyncio
@pytest.mark.parametrize("question,expected", [
    ("FastAPI 怎么定义 POST 接口？", "@app.post"),
    ("Pydantic v2 怎么序列化？", "model_dump"),
    ("asyncio.gather 的作用？", "并发"),
])
async def test_qa_accuracy(question, expected):
    """准确率评测"""
    answer = await agent.ask(question)
    assert fuzzy_match(expected, answer), f"期望包含 {expected}，实际：{answer}"

@pytest.mark.asyncio
async def test_qa_faithfulness():
    """忠实度评测：答案必须基于检索到的文档"""
    question = "项目用的是什么向量数据库？"
    result = await agent.ask_with_trace(question)

    # 答案中的关键事实必须出现在 source 文档中
    for fact in result.key_facts:
        assert any(fact in doc.content for doc in result.sources), \
            f"事实 {fact} 没有出处"
```

### 今日任务

- [ ] 为项目 #1 设计 10 条端到端评测用例（覆盖高频问题）
- [ ] 实现一个 `fuzzy_match` 函数（允许部分匹配）
- [ ] 为项目 #2 的研究任务设计 5 条端到端用例
- [ ] 记录当前基线分数（如：准确率 60%）

### 自检清单

- [ ] 我能区分集成评测和端到端评测的关注点
- [ ] 我会写"忠实度"评测（防止幻觉）
- [ ] 我有当前项目的基线分数

---

## Day 3（周三）：评测指标体系

**学习目标：** 掌握工业级评测的 5 大核心指标。

### 核心概念

| 指标 | 含义 | 测量方式 |
|------|------|---------|
| Accuracy | 答案正确性 | 精确匹配 / 模糊匹配 / LLM 打分 |
| Faithfulness | 是否基于事实 | 关键事实是否在 source 中 |
| Tool Accuracy | 工具选择正确率 | 选对工具 / 参数正确 |
| Latency | 响应时间 | P50 / P95（毫秒） |
| Cost | 每次调用成本 | token 数 × 单价 |

**为什么这 5 个都要看：**
- 只看 Accuracy → 可能又慢又贵
- 只看 Latency → 可能答案不准
- 只看 Cost → 可能砍掉了关键能力

### 代码示例

**Python：多指标评测器**

```python
# app/eval/metrics.py
import time
from dataclasses import dataclass
from openai import AsyncOpenAI

@dataclass
class EvalResult:
    accuracy: float        # 0-1
    faithfulness: float    # 0-1
    latency_p50: float     # ms
    latency_p95: float     # ms
    cost_usd: float

class MultiMetricEvaluator:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.prices = {"gpt-5-latest": {"in": 0.15, "out": 0.6}}  # per 1M tokens

    async def evaluate(self, agent_fn, test_cases: list[dict]) -> EvalResult:
        latencies, results = [], []
        total_tokens = {"in": 0, "out": 0}

        for case in test_cases:
            t0 = time.perf_counter()
            output = await agent_fn(case["query"])
            latency = (time.perf_counter() - t0) * 1000
            latencies.append(latency)

            # LLM-as-Judge 打分
            accuracy = await self._judge_accuracy(output.answer, case["expected"])
            faithfulness = await self._judge_faithfulness(output.answer, output.sources)

            results.append((accuracy, faithfulness))
            total_tokens["in"] += output.usage.input_tokens
            total_tokens["out"] += output.usage.output_tokens

        latencies.sort()
        return EvalResult(
            accuracy=sum(r[0] for r in results) / len(results),
            faithfulness=sum(r[1] for r in results) / len(results),
            latency_p50=latencies[len(latencies) // 2],
            latency_p95=latencies[int(len(latencies) * 0.95)],
            cost_usd=self._compute_cost(total_tokens),
        )
```

### 今日任务

- [ ] 实现一个 `MultiMetricEvaluator`（至少覆盖 Accuracy + Latency + Cost）
- [ ] 给项目 #1 跑一次完整评测，记录 5 个指标
- [ ] 把结果写成一个 `eval_report.md`

### 自检清单

- [ ] 我能解释为什么不能只看 Accuracy
- [ ] 我会计算 P95 延迟
- [ ] 我会估算每次调用的 LLM 成本

---

## Day 4（周四）：LLM-as-a-Judge 进阶

**学习目标：** 用 LLM 做可靠的主观评测。

### 核心概念

**Judge 选择的 3 个原则：**
1. Judge 模型要比被测模型更强（GPT-4 级别）
2. Judge Prompt 要有清晰的 Rubric（评分标准）
3. 重要场景用多 Judge 投票

**Rubric 设计模板：**
```
维度 1：事实准确性（0-2 分）
  - 2 分：完全正确，有据可查
  - 1 分：部分正确，有小瑕疵
  - 0 分：有错误信息

维度 2：完整性（0-2 分）
  - 2 分：覆盖所有要点
  - 1 分：覆盖主要要点
  - 0 分：严重遗漏

维度 3：表达清晰度（0-1 分）
  - 1 分：结构清晰、易读
  - 0 分：混乱、难懂
```

### 代码示例

**Python：LLM Judge 模板**

```python
# app/eval/judge.py
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

class JudgeResult(BaseModel):
    accuracy: int = Field(ge=0, le=2, description="事实准确性 0-2 分")
    completeness: int = Field(ge=0, le=2, description="完整性 0-2 分")
    clarity: int = Field(ge=0, le=1, description="清晰度 0-1 分")
    reasoning: str = Field(description="打分理由")
    @property
    def total(self) -> float:
        return (self.accuracy + self.completeness + self.clarity) / 5.0

JUDGE_PROMPT = """你是一个严格的评分官。请根据以下 Rubric 打分：

【问题】{question}
【标准答案】{expected}
【待评答案】{actual}
【参考资料】{context}

Rubric：
- 事实准确性（0-2）：2=完全正确 1=部分正确 0=有错误
- 完整性（0-2）：2=覆盖所有要点 1=主要要点 0=严重遗漏
- 清晰度（0-1）：1=结构清晰 0=混乱

请输出 JSON。"""

class LLMJudge:
    def __init__(self, model: str = "gpt-5-latest"):
        self.client = AsyncOpenAI()
        self.model = model

    async def judge(self, question: str, expected: str, actual: str, context: str) -> JudgeResult:
        resp = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(
                question=question, expected=expected, actual=actual, context=context
            )}],
            response_format=JudgeResult,
        )
        return resp.choices[0].message.parsed
```

**多 Judge 投票：**
```python
async def multi_judge(question, expected, actual, context, judges=("gpt-5-latest", "claude-sonnet-4-5-latest")):
    tasks = [LLMJudge(m).judge(question, expected, actual, context) for m in judges]
    results = await asyncio.gather(*tasks)
    avg = sum(r.total for r in results) / len(results)
    return avg
```

### 今日任务

- [ ] 实现一个 `LLMJudge` 类（用旗舰模型如 GPT-5 或 Claude Opus 作为 Judge）
- [ ] 给项目 #1 的 10 条用例跑 LLM Judge 评测
- [ ] 对比 LLM Judge 分数和人工打分（至少校准 5 条）

### 自检清单

- [ ] 我能解释为什么 Judge 模型要比被测模型强
- [ ] 我会设计 Rubric
- [ ] 我意识到 LLM Judge 也有偏差（需要校准）

---

## Day 5（周五）：LangSmith / Braintrust 实操

**学习目标：** 用专业评测平台代替手写脚本。

### 核心概念

**LangSmith 核心能力：**
- **Trace：** 记录每一步（LLM 调用、工具调用、检索）
- **Dataset：** 管理评测用例
- **Experiment：** 对比不同版本的表现
- **Playground：** 在线调试 Prompt

**适用场景对比：**

| 平台 | 选它的理由 |
|------|----------|
| LangSmith | 你用 LangChain / LangGraph |
| Braintrust | 你要做严肃的团队协作评测 |
| Phoenix | 你要自托管、数据敏感 |
| Promptfoo | 你要在 CI 里跑（本地优先） |

### 代码示例

**Python：LangSmith 集成**

```python
# app/eval/langsmith_runner.py
import os
from langsmith import Client
from langsmith.schemas import Example, Run

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "knowledge-assistant"

client = Client()

# 1. 创建评测数据集
dataset = client.create_dataset("qa-baseline", description="知识助手基线")

examples = [
    {"input": "FastAPI 怎么定义路由？", "output": "@app.get/post"},
    {"input": "Pydantic 怎么校验？", "output": "Field 约束 + model_validate"},
]
for ex in examples:
    client.create_example(inputs={"q": ex["input"]}, outputs={"answer": ex["output"]}, dataset_id=dataset.id)

# 2. 自定义评估器
def accuracy_evaluator(run: Run, example: Example) -> dict:
    expected = example.outputs["answer"]
    actual = run.outputs["answer"]
    score = 1.0 if expected.lower() in actual.lower() else 0.0
    return {"key": "accuracy", "score": score}

# 3. 运行实验
def predict(inputs: dict) -> dict:
    from app.agent import KnowledgeAgent
    import asyncio
    agent = KnowledgeAgent()
    answer = asyncio.run(agent.ask(inputs["q"]))
    return {"answer": answer}

experiment_results = client.run_on_dataset(
    dataset_name="qa-baseline",
    llm_or_chain_factory=predict,
    evaluation=[accuracy_evaluator],
    verbose=True,
)
```

### 今日任务

- [ ] 注册 LangSmith 账号（免费层够用）
- [ ] 把项目 #1 接入 LangSmith Trace
- [ ] 创建一个 ≥10 条用例的 Dataset
- [ ] 跑一次 Experiment，截图保存

### 自检清单

- [ ] 我能在 LangSmith 看到完整 Trace
- [ ] 我会创建 Dataset 和运行 Experiment
- [ ] 我能写自定义评估器

---

## Day 6（周六）：Promptfoo + CI 集成

**学习目标：** 把评测集成到 GitHub Actions，每次 PR 自动跑。

### 核心概念

**为什么选 Promptfoo 做 CI：**
- 本地运行，速度快
- 配置文件即文档（YAML）
- 原生支持 GitHub Actions
- 可以对比不同 Prompt / 模型版本

### 代码示例

**Promptfoo 配置（`promptfooconfig.yaml`）：**

```yaml
description: "知识助手评测"

prompts:
  - file://prompts/rag_qa.txt

providers:
  - id: openai:gpt-5-latest
    label: gpt-5-latest-baseline
  - id: openai:gpt-5-latest
    label: gpt-5-latest-compare

tests:
  - vars:
      query: "FastAPI 怎么定义 POST 接口？"
      context: "使用 @app.post 装饰器..."
    assert:
      - type: contains
        value: "@app.post"
      - type: llm-rubric
        value: "答案必须包含示例代码"

  - vars:
      query: "Pydantic 怎么校验嵌套模型？"
      context: "使用嵌套的 BaseModel..."
    assert:
      - type: contains
        value: "BaseModel"
      - type: similar
        value: "嵌套模型通过组合多个 BaseModel 实现"
        threshold: 0.7

  - vars:
      query: "你是谁？"
      context: ""
    assert:
      - type: icontains
        value: "知识助手"
```

**GitHub Actions 评测工作流（`.github/workflows/eval.yml`）：**

```yaml
name: Agent Evaluation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install deps
        run: uv sync

      - name: Run unit tests
        run: uv run pytest tests/unit -v

      - name: Run integration tests
        run: uv run pytest tests/integration -v

      - name: Run Promptfoo eval
        uses: promptfoo/promptfoo-action@v1
        with:
          config: promptfooconfig.yaml
          api-key: ${{ secrets.PROMPTFOO_API_KEY }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload eval results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: promptfoo_results.json
```

### 今日任务

- [ ] 安装 Promptfoo：`npm i -g promptfoo`
- [ ] 为项目 #1 写一个 `promptfooconfig.yaml`（至少 5 条用例）
- [ ] 在本地跑通：`promptfoo eval`
- [ ] 在项目仓库加 GitHub Actions 评测工作流
- [ ] 推一次 PR，观察 Actions 是否触发

### 自检清单

- [ ] 我能在本地跑 Promptfoo 看评测结果
- [ ] 我能写不同类型的 assert（contains / llm-rubric / similar）
- [ ] 我的 PR 会自动触发评测

---

## Day 7（周日）：回归测试 + 周末复盘

**学习目标：** 建立回归测试体系，确保改 Prompt 不会让效果变差。

### 核心概念

**回归测试的 3 个关键：**
1. **评测集要稳定** — 用固定的 Dataset，不要每次换
2. **要有基线** — 每次对比 vs main 分支
3. **要设置阈值** — 退化超过 X% 就阻断合并

### 代码示例

**Python：评测结果对比**

```python
# scripts/compare_with_main.py
import json
import subprocess
from pathlib import Path

def load_eval(ref: str) -> dict:
    """从 git ref 加载评测结果"""
    try:
        content = subprocess.check_output(
            ["git", "show", f"{ref}:eval_results.json"]
        ).decode()
        return json.loads(content)
    except subprocess.CalledProcessError:
        return None

def compare(current: dict, baseline: dict, threshold: float = 0.05) -> bool:
    """对比当前结果和基线，退化超过 threshold 则报警"""
    all_good = True
    for metric in ["accuracy", "faithfulness"]:
        diff = current[metric] - baseline[metric]
        status = "✅" if diff >= -threshold else "❌"
        print(f"{status} {metric}: {baseline[metric]:.2f} → {current[metric]:.2f} ({diff:+.2f})")
        if diff < -threshold:
            all_good = False
    return all_good

if __name__ == "__main__":
    current = json.loads(Path("eval_results.json").read_text())
    baseline = load_eval("origin/main")
    if baseline is None:
        print("⚠️ 没有找到基线，跳过对比")
    else:
        ok = compare(current, baseline)
        exit(0 if ok else 1)
```

### 今日任务

- [ ] 把本周的评测结果存为 `eval_results.json` 并提交
- [ ] 写一个对比脚本，对比当前 vs main 分支
- [ ] 故意改坏一个 Prompt，验证评测能发现退化
- [ ] 写本周学习笔记到 `notes/week-24-notes.md`

### 周末复盘问题

1. 我的评测体系中，哪一层（单元/集成/端到端）最有价值？为什么？
2. LLM Judge 和人工评测的差异有多大？我打算怎么缩小这个差距？
3. 如果我是面试官，看到候选人的项目有 CI 评测，我会问什么问题？
4. 评测帮我发现了项目的哪些隐藏问题？

---

# Week 2：后端部署与服务化

> **本周目标：** 把项目 #1 的 Agent 部署成公开可访问的 API 服务
> **本周产出：** FastAPI 后端 + Docker 镜像 + 公开 Demo URL + 监控

## Day 1（周一）：FastAPI 基础

**学习目标：** 用前端框架思维快速上手 FastAPI。

### 核心对比

| Node.js | Python (FastAPI) |
|---------|------------------|
| `express` / `fastify` | `fastapi` |
| `app.get(path, handler)` | `@app.get(path)` |
| `req.body` | Pydantic 模型自动解析 |
| `express.json()` 中间件 | 自动 |
| `zod` 校验 | Pydantic 校验 |
| Swagger 需手装 | 自动生成 |

### 代码示例

**Python：FastAPI 最小应用**

```python
# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Knowledge Agent API", version="0.1.0")

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return ChatResponse(
        answer=f"你说的是：{req.message}",
        session_id=req.session_id or "new-session",
    )

# 启动：uvicorn app.main:app --reload --port 8000
# 文档：http://localhost:8000/docs
```

### 今日任务

- [ ] 新建 `server/` 目录，初始化 FastAPI 项目
- [ ] `uv add fastapi uvicorn`
- [ ] 实现 `/health` 和 `/api/chat` 两个接口
- [ ] 打开 `http://localhost:8000/docs` 体验自动文档

### 自检清单

- [ ] 我能启动 FastAPI 服务并访问
- [ ] 我能定义 Pydantic 请求 / 响应模型
- [ ] 我会用 `/docs` 测试接口

---

## Day 2（周二）：FastAPI 进阶 + 项目接入

**学习目标：** 把项目 #1 的 Agent 接入 FastAPI。

### 核心概念

**依赖注入（对比 NestJS）：**
- FastAPI 用 `Depends()` 做依赖注入
- 适合管理数据库连接、Agent 实例
- 单例 / 请求级生命周期都支持

### 代码示例

**Python：Agent 接入 FastAPI**

```python
# app/deps.py
from functools import lru_cache
from app.agent import KnowledgeAgent
from app.rag.retriever import Retriever
from app.memory import SessionStore

@lru_cache
def get_retriever() -> Retriever:
    """单例：启动时初始化一次"""
    return Retriever(collection="docs")

@lru_cache
def get_session_store() -> SessionStore:
    return SessionStore(redis_url="redis://localhost:6379")

def get_agent(
    retriever: Retriever = Depends(get_retriever),
    store: SessionStore = Depends(get_session_store),
) -> KnowledgeAgent:
    """请求级：每次请求新建 Agent（复用底层资源）"""
    return KnowledgeAgent(retriever=retriever, memory=store)
```

```python
# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_agent
from app.agent import KnowledgeAgent

router = APIRouter()

@router.post("/chat")
async def chat(
    req: ChatRequest,
    agent: KnowledgeAgent = Depends(get_agent),
):
    try:
        result = await agent.ask(req.message, session_id=req.session_id)
        return {
            "answer": result.answer,
            "sources": [{"title": s.title, "url": s.url} for s in result.sources],
            "session_id": result.session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 今日任务

- [ ] 把项目 #1 的 Agent 改造成可注入的依赖
- [ ] 实现 `/api/chat` 接口，返回真实答案 + sources
- [ ] 测试：用 `/docs` 发一条请求，验证返回
- [ ] 加错误处理（超时、限流、模型异常）

### 自检清单

- [ ] 我会用 `Depends()` 做依赖注入
- [ ] 我理解单例 vs 请求级的区别
- [ ] 我的 Agent 能通过 HTTP 被访问

---

## Day 3（周三）：SSE 流式接口（核心）

**学习目标：** 实现 Server-Sent Events 流式输出，让前端能打字机渲染。

### 核心概念

**为什么用 SSE 而不是 WebSocket：**
- 单向通信（服务器 → 客户端）足够
- 基于 HTTP，穿透代理友好
- 自动重连
- LLM API 本身就是 SSE

**SSE 数据格式：**
```
data: {"token": "你"}

data: {"token": "好"}

data: [DONE]
```

### 代码示例

**Python：FastAPI SSE 接口**

```python
# app/routes/chat_stream.py
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.deps import get_agent

router = APIRouter()

@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, agent = Depends(get_agent)):
    async def event_generator():
        try:
            async for chunk in agent.ask_stream(req.message, session_id=req.session_id):
                # 不同类型的 chunk
                if chunk.type == "token":
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                elif chunk.type == "tool_call":
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': chunk.name, 'args': chunk.args})}\n\n"
                elif chunk.type == "tool_result":
                    yield f"data: {json.dumps({'type': 'tool_result', 'name': chunk.name, 'result': chunk.result})}\n\n"
                elif chunk.type == "sources":
                    yield f"data: {json.dumps({'type': 'sources', 'docs': chunk.docs})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 关闭 Nginx 缓冲
        },
    )
```

**Agent 的流式生成器（伪代码）：**
```python
# app/agent.py
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

@dataclass
class StreamChunk:
    type: Literal["token", "tool_call", "tool_result", "sources"]
    content: str = ""
    name: str = ""
    args: dict = None
    result: str = ""
    docs: list = None

class KnowledgeAgent:
    async def ask_stream(self, query: str, session_id: str) -> AsyncIterator[StreamChunk]:
        # 1. 先检索
        docs = await self.retriever.search(query, top_k=3)
        yield StreamChunk(type="sources", docs=[{"title": d.title, "url": d.url} for d in docs])

        # 2. 判断是否需要工具
        if await self._needs_tool(query):
            tool_name, tool_args = await self._plan_tool(query)
            yield StreamChunk(type="tool_call", name=tool_name, args=tool_args)
            result = await self.tools[tool_name].run(**tool_args)
            yield StreamChunk(type="tool_result", name=tool_name, result=result)

        # 3. 流式生成答案
        async for token in self.llm.stream(query, context=docs):
            yield StreamChunk(type="token", content=token)
```

### 今日任务

- [ ] 实现 `/api/chat/stream` SSE 接口
- [ ] 让 Agent 支持 `ask_stream` 方法（yield chunk）
- [ ] 用 `curl -N` 测试 SSE 输出
- [ ] 在前端用 `fetch` 接收（暂时不用 SDK）

### 自检清单

- [ ] 我能解释 SSE 和 WebSocket 的差异
- [ ] 我会写 `StreamingResponse` + `event_generator`
- [ ] 我能区分 token / tool_call / sources 等不同事件类型

---

## Day 4（周四）：Docker 化

**学习目标：** 用 Docker 把项目打包，保证部署一致性。

### 核心概念

**多阶段构建（前端工程师类比）：**
- 类似 Vite 的 build 阶段和运行阶段分离
- 构建阶段装完整工具链（编译、装依赖）
- 运行阶段只保留最小运行时
- 镜像体积能小 5-10 倍

### 代码示例

**Dockerfile（多阶段构建）：**

```dockerfile
# ---------- 构建阶段 ----------
FROM python:3.12-slim AS builder

# 安装 uv（快速包管理）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先拷贝依赖清单（利用 Docker 缓存）
COPY pyproject.toml uv.lock ./

# 安装依赖到虚拟环境
RUN uv sync --frozen --no-dev

# ---------- 运行阶段 ----------
FROM python:3.12-slim AS runner

WORKDIR /app

# 拷贝虚拟环境
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 拷贝源码
COPY app ./app
COPY prompts ./prompts

# 非 root 用户运行
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**docker-compose（本地开发）：**

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgres://app:app@db:5432/app
    depends_on:
      - redis
      - db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=app
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 今日任务

- [ ] 写 `Dockerfile`（多阶段）
- [ ] 写 `docker-compose.yml`（含 Postgres + Redis）
- [ ] 本地构建：`docker compose up --build`
- [ ] 验证：服务能正常响应，数据库能连接
- [ ] 优化镜像大小（目标 < 500MB）

### 自检清单

- [ ] 我能解释为什么要多阶段构建
- [ ] 我会用 `uv sync` 在 Docker 里装依赖
- [ ] 我的 compose 能一键起所有服务

---

## Day 5（周五）：部署到 Fly.io / Railway

**学习目标：** 把 Docker 镜像部署到云平台，得到公开 URL。

### 核心概念

**平台选择建议：**
- **Fly.io**：全球节点、支持长任务、有免费额度，个人项目首选
- **Railway**：UI 友好、自动部署，适合快速上线
- **Render**：免费层够 Demo
- **阿里云函数计算**：国内访问快

### 代码示例

**Fly.io 部署配置（`fly.toml`）：**

```toml
app = "knowledge-agent-你的名字"
primary_region = "nrt"  # 东京节点，亚洲访问快

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true   # 空闲自动停机（省钱）
  auto_start_machines = true
  min_machines_running = 0

  [http_service.concurrency]
    type = "requests"
    hard_limit = 100
    soft_limit = 20

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512

# 持久化存储（如需）
[[mounts]]
  source = "data"
  destination = "/data"
```

**部署命令：**
```bash
# 1. 安装 flyctl
brew install flyctl

# 2. 登录
fly auth login

# 3. 创建应用
fly launch --no-deploy

# 4. 设置密钥
fly secrets set OPENAI_API_KEY=sk-xxx
fly secrets set LANGSMITH_API_KEY=lsv2_xxx

# 5. 部署
fly deploy

# 6. 查看日志
fly logs
fly status
```

**Railway 部署（更简单）：**
```bash
# 1. 安装 Railway CLI
npm i -g @railway/cli

# 2. 登录
railway login

# 3. 初始化项目
railway init

# 4. 添加 Postgres / Redis
railway add --plugin postgresql
railway add --plugin redis

# 5. 设置环境变量
railway variables set OPENAI_API_KEY=sk-xxx

# 6. 部署
railway up
```

### 今日任务

- [ ] 选一个平台（推荐 Fly.io），注册账号
- [ ] 写 `fly.toml`
- [ ] 把所有密钥设置到云端（不要写进代码）
- [ ] 部署成功，拿到公开 URL
- [ ] 用浏览器访问 `/docs` 验证

### 自检清单

- [ ] 我的 API 有公开 URL（如 `https://xxx.fly.dev`）
- [ ] 我的密钥没有泄露到代码里
- [ ] 我能在云端日志里看到请求

---

## Day 6（周六）：成本控制与监控

**学习目标：** 让服务既不超支又能用，出问题能第一时间发现。

### 核心概念

**成本控制 4 件套：**
1. **缓存** — 重复请求直接返回
2. **模型路由** — 简单任务用便宜模型
3. **限流** — 防止恶意调用
4. **监控告警** — 成本超限通知

**监控 3 个核心指标：**
- 错误率（5xx 占比）
- 延迟（P95）
- 每日成本

### 代码示例

**Python：缓存 + 模型路由 + 限流**

```python
# app/middleware/cost_control.py
import hashlib
import time
from functools import lru_cache

# 1. 语义缓存（基于 query hash）
class SemanticCache:
    def __init__(self, redis, ttl: int = 3600):
        self.redis = redis
        self.ttl = ttl

    async def get(self, query: str) -> dict | None:
        key = self._key(query)
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set(self, query: str, value: dict):
        await self.redis.setex(self._key(query), self.ttl, json.dumps(value))

    def _key(self, query: str) -> str:
        normalized = query.strip().lower()
        return f"qa:{hashlib.sha256(normalized.encode()).hexdigest()}"


# 2. 模型路由（简单任务用便宜模型）
class ModelRouter:
    def select(self, query: str) -> str:
        if len(query) < 50 and not any(c in query for c in "为什么|分析|对比"):
            return "claude-haiku-4-5-latest"  # 简单任务用经济模型（便宜约 10x）
        return "claude-sonnet-4-5-latest"     # 复杂任务用旗舰模型


# 3. 限流（每用户每分钟 10 次）
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest, agent = Depends(get_agent)):
    ...
```

**Python：监控（用 Logfire 或 Loguru）**

```python
# app/middleware/observability.py
import logfire
from fastapi import Request
from time import perf_counter

logfire.configure(token=os.environ["LOGFIRE_TOKEN"])

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    t0 = perf_counter()
    response = await call_next(request)
    duration = (perf_counter() - t0) * 1000

    logfire.log(
        level="info",
        message="request",
        attrs={
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration,
            "user_id": request.headers.get("X-User-ID"),
        },
    )
    return response
```

### 今日任务

- [ ] 给 `/api/chat` 加语义缓存（Redis）
- [ ] 实现 ModelRouter，简单 query 走 mini 模型
- [ ] 加限流（每 IP 每分钟 10 次）
- [ ] 接入一个监控（Logfire / Loguru + Sentry）
- [ ] 估算：1000 次调用大概多少钱？

### 自检清单

- [ ] 我有缓存层，重复请求秒返
- [ ] 我有模型路由，便宜任务用便宜模型
- [ ] 我有限流，不会被刷爆
- [ ] 我有监控，能在仪表盘看请求量

---

## Day 7（周日）：API 测试 + 周末复盘

**学习目标：** 给 API 写完整的集成测试，保证上线质量。

### 代码示例

**Python：FastAPI 集成测试**

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_chat_returns_answer(client):
    r = await client.post("/api/chat", json={"message": "FastAPI 是什么？"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert len(data["answer"]) > 0

@pytest.mark.asyncio
async def test_chat_stream_yields_events(client):
    async with client.stream("POST", "/api/chat/stream", json={"message": "你好"}) as r:
        events = []
        async for line in r.aiter_lines():
            if line.startswith("data: "):
                events.append(line[6:])
        assert events[-1] == "[DONE]"
        assert any("token" in e for e in events)
```

### 今日任务

- [ ] 给所有 API 接口写集成测试（≥10 条）
- [ ] 测试 SSE 流式接口（用 `httpx.AsyncClient.stream`）
- [ ] 把 API 测试加入 GitHub Actions
- [ ] 写本周学习笔记到 `notes/week-25-notes.md`

### 周末复盘问题

1. FastAPI 相比 Express / NestJS，最让我惊艳的是什么？
2. SSE 流式输出最难调试的地方在哪？
3. 我的部署成本估算多少？能否承受 1000 DAU？
4. 如果服务挂了，我能在多久内发现？监控够不够？

---

# Week 3：前端集成（发挥你的优势）

> **本周目标：** 用 Next.js + Vercel AI SDK 给 Agent 做出**碾压纯后端候选人**的前端
> **本周产出：** 完整聊天 UI + 工具调用可视化 + 思考过程展示 + 移动端适配

## Day 1（周一）：Vercel AI SDK Core

**学习目标：** 用前端工程师思维快速上手 AI SDK。

### 核心概念

**AI SDK 三层架构：**

| 模块 | 作用 | 类比 |
|------|------|------|
| AI SDK Core | 统一调用 LLM | `fetch` 之于 HTTP |
| AI SDK UI | React/Vue/Svelte Hooks | `swr` / `react-query` |
| AI SDK RSC | Server Components 集成 | Next.js App Router |

**Provider 抽象：**
```typescript
// 一个接口，多个 Provider
import { generateText } from "ai"
import { openai } from "@ai-sdk/openai"
import { anthropic } from "@ai-sdk/anthropic"

await generateText({
  model: openai("gpt-5-latest"),       // 或 anthropic("claude-sonnet-4-5-latest")
  prompt: "你好",
})
```

### 代码示例

**TypeScript：调用后端 + Core 调用**

```typescript
// app/api/parse/route.ts —— 用 AI SDK Core 做结构化提取
import { generateObject } from "ai"
import { openai } from "@ai-sdk/openai"
import { z } from "zod"

export async function POST(req: Request) {
  const { text } = await req.json()

  const { object } = await generateObject({
    model: openai("gpt-5-latest"),
    schema: z.object({
      intent: z.enum(["question", "command", "chitchat"]),
      keywords: z.array(z.string()),
      suggestedTools: z.array(z.string()),
    }),
    prompt: `分析以下用户输入：\n${text}`,
  })

  return Response.json(object)
}
```

```typescript
// lib/agent-client.ts —— 调用你自己的后端
export async function callBackend(message: string, sessionId?: string) {
  const res = await fetch(`${process.env.API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  return res.json()
}
```

### 今日任务

- [ ] 用 `pnpm create next-app` 新建前端项目（App Router + TS + Tailwind）
- [ ] 安装：`pnpm add ai @ai-sdk/openai @ai-sdk/anthropic zod`
- [ ] 实现 `/api/parse` 接口（用 `generateObject` 做意图识别）
- [ ] 在浏览器测试

### 自检清单

- [ ] 我能解释 AI SDK 的三层架构
- [ ] 我会用 `generateObject` 做结构化输出
- [ ] 我能区分"调 AI SDK Core"和"调我自己的后端"

---

## Day 2（周二）：AI SDK UI + 流式渲染

**学习目标：** 用 `useChat` Hook 实现流式聊天界面（10 行代码搞定打字机）。

### 核心概念

**为什么用 `useChat`：**
- 自动管理消息列表
- 自动处理 SSE 流
- 自动处理 loading 状态
- 自动处理错误
- 你只需要关心 UI

### 代码示例

**TypeScript：服务端流式接口**

```typescript
// app/api/chat/route.ts
import { openai } from "@ai-sdk/openai"
import { streamText } from "ai"

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = streamText({
    model: openai("gpt-5-latest"),
    messages,
  })

  return result.toDataStreamResponse()
}
```

**TypeScript：客户端聊天 UI**

```tsx
// app/page.tsx
"use client"
import { useChat } from "@ai-sdk/react"

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",
  })

  return (
    <div className="mx-auto max-w-2xl h-screen flex flex-col">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`rounded-2xl px-4 py-2 max-w-[80%] ${
                m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <MarkdownRenderer content={m.content} />
            </div>
          </div>
        ))}
      </div>

      {/* 输入框 */}
      <form onSubmit={handleSubmit} className="border-t p-4 flex gap-2">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="输入消息..."
          className="flex-1 rounded-full border px-4 py-2"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input}
          className="rounded-full bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
        >
          发送
        </button>
      </form>
    </div>
  )
}
```

**Markdown 流式渲染组件（关键）：**
```tsx
// components/MarkdownRenderer.tsx
"use client"
import ReactMarkdown from "react-markdown"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        code({ inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "")
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>{children}</code>
          )
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
```

### 今日任务

- [ ] 实现 `/api/chat` 流式接口（先用 OpenAI，后接自己的后端）
- [ ] 用 `useChat` 写一个最小聊天 UI
- [ ] 集成 Markdown + 代码高亮
- [ ] 体验打字机效果

### 自检清单

- [ ] 我能 10 行代码实现流式聊天
- [ ] 我会处理 loading 状态
- [ ] 我的 Markdown 在流式过程中也能正常渲染

---

## Day 3（周三）：工具调用 UI（你的杀手锏）

**学习目标：** 把 Agent 的工具调用过程可视化出来。

### 核心概念

**为什么要做工具调用 UI：**
- 用户看到 Agent 在"做事"会更有信任感
- 调试时能快速定位哪一步出问题
- **这是纯后端候选人做不出来的能力**

**UI 设计参考：**
- ChatGPT 的 "Searching the web..." 折叠面板
- Claude 的工具调用卡片
- Cursor 的命令执行展示

### 代码示例

**TypeScript：工具调用卡片组件**

```tsx
// components/ToolCall.tsx
"use client"
import { useState } from "react"
import { ChevronDown, ChevronRight, Loader2, Check, X } from "lucide-react"

interface ToolCallProps {
  name: string         // 工具名：search_web
  args: Record<string, unknown>
  result?: unknown
  status: "running" | "success" | "error"
}

const TOOL_LABELS: Record<string, { label: string; icon: string }> = {
  search_web: { label: "搜索网络", icon: "🔍" },
  read_file: { label: "读取文件", icon: "📄" },
  run_code: { label: "执行代码", icon: "⚡" },
  query_db: { label: "查询数据库", icon: "🗄️" },
}

export function ToolCall({ name, args, result, status }: ToolCallProps) {
  const [expanded, setExpanded] = useState(false)
  const meta = TOOL_LABELS[name] ?? { label: name, icon: "🛠️" }

  return (
    <div className="border rounded-lg bg-gray-50 my-2 text-sm">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 p-2 hover:bg-gray-100"
      >
        <span>{meta.icon}</span>
        <span className="font-medium">{meta.label}</span>

        {status === "running" && <Loader2 className="animate-spin w-3 h-3 ml-auto" />}
        {status === "success" && <Check className="w-3 h-3 ml-auto text-green-500" />}
        {status === "error" && <X className="w-3 h-3 ml-auto text-red-500" />}

        {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>

      {expanded && (
        <div className="border-t p-2 space-y-2">
          <div>
            <div className="text-xs text-gray-500 mb-1">参数</div>
            <pre className="bg-gray-800 text-gray-100 p-2 rounded text-xs overflow-x-auto">
              {JSON.stringify(args, null, 2)}
            </pre>
          </div>
          {result !== undefined && (
            <div>
              <div className="text-xs text-gray-500 mb-1">结果</div>
              <pre className="bg-gray-800 text-gray-100 p-2 rounded text-xs overflow-x-auto max-h-40">
                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

**TypeScript：消费 SSE 的工具调用事件**

```tsx
// hooks/useAgentChat.ts
"use client"
import { useState, useCallback } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  toolCalls?: Array<{
    id: string
    name: string
    args: Record<string, unknown>
    result?: unknown
    status: "running" | "success" | "error"
  }>
  sources?: Array<{ title: string; url: string }>
}

export function useAgentChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const send = useCallback(async (input: string) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: input }
    const assistantMsg: Message = { id: crypto.randomUUID(), role: "assistant", content: "", toolCalls: [] }
    setMessages((m) => [...m, userMsg, assistantMsg])
    setIsLoading(true)

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    })

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // 解析 SSE
      const lines = buffer.split("\n\n")
      buffer = lines.pop() || ""

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue
        const data = JSON.parse(line.slice(6))

        setMessages((prev) => {
          const next = [...prev]
          const msg = next[next.length - 1]

          if (data.type === "token") msg.content += data.content
          else if (data.type === "sources") msg.sources = data.docs
          else if (data.type === "tool_call") {
            msg.toolCalls!.push({
              id: crypto.randomUUID(),
              name: data.name,
              args: data.args,
              status: "running",
            })
          }
          else if (data.type === "tool_result") {
            const tc = msg.toolCalls!.find((t) => t.name === data.name)
            if (tc) {
              tc.result = data.result
              tc.status = "success"
            }
          }
          return next
        })
      }
    }
    setIsLoading(false)
  }, [])

  return { messages, send, isLoading }
}
```

### 今日任务

- [ ] 实现 `ToolCall` 折叠卡片组件
- [ ] 实现 `useAgentChat` Hook 消费自定义 SSE
- [ ] 在聊天 UI 中渲染工具调用过程
- [ ] 联调你的后端，触发工具调用看效果

### 自检清单

- [ ] 我能解析多类型 SSE 事件
- [ ] 我的工具调用 UI 有 running / success / error 三种状态
- [ ] 我能折叠 / 展开看参数和结果

---

## Day 4（周四）：Agent 思考过程可视化

**学习目标：** 做类似 Claude "Thinking" 的思考过程展示。

### 核心概念

**思考过程可视化的 3 种形态：**
1. **单 Agent 思考链** — 折叠面板展示 Thought → Action → Observation
2. **Multi-Agent 协作树** — 树形展示多个 Agent 的分工
3. **时间线** — 横向展示每个步骤耗时

**为什么这是稀缺能力：**
- 后端候选人通常只返回最终结果
- 你能让用户"看到"Agent 的工作
- 这是产品差异化的关键

> ⚠️ **安全分层——不要暴露原始思考给终端用户：**
> 完整的 Thought / Action / Observation 可能包含系统提示词片段、私有工具参数（如 API Key）、
> 或从知识库检索到的敏感文档内容。直接展示给用户意味着数据泄露和提示词被逆向的风险。
>
> **正确做法——双层输出：**
> - **用户侧（公开）：** 仅展示安全的**进度事件**——`正在检索资料…` `已找到 3 篇相关文档`
>   `正在调用天气工具查询北京…` `正在生成答案…`
> - **开发者侧（受权限控制）：** 完整 Thought/Action/Observation trace，仅在调试模式或
>   经过脱敏后可见——过滤掉系统提示、API Key、用户 PII、工具返回的敏感数据
> - **产品层面的收益：** 用户看到的是"Agent 在干什么"而不是"Agent 在想什么"，
>   既保护了安全隐私，也避免了原始推理过程带来的困惑（LLM 的 thought 经常包含错误假设和修正）

### 代码示例

**TypeScript：思考过程折叠面板**

```tsx
// components/ThinkingTrace.tsx
"use client"
import { useState } from "react"
import { Brain, ChevronDown } from "lucide-react"

interface Trace {
  thought: string
  action?: string
  observation?: string
  durationMs?: number
}

export function ThinkingTrace({ traces, totalMs }: { traces: Trace[]; totalMs?: number }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border border-purple-200 bg-purple-50 rounded-lg my-2 text-sm">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 p-2 text-purple-900"
      >
        <Brain className="w-4 h-4" />
        <span className="font-medium">思考过程</span>
        <span className="text-xs text-purple-600 ml-auto">
          {traces.length} 步{totalMs ? ` · ${totalMs}ms` : ""}
        </span>
        <ChevronDown className={`w-4 h-4 transition ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="border-t border-purple-200 p-3 space-y-3 bg-white">
          {traces.map((t, i) => (
            <div key={i} className="space-y-1">
              <div className="text-xs text-gray-500">第 {i + 1} 步</div>
              <div className="text-purple-900">
                <span className="font-medium">思考：</span>
                {t.thought}
              </div>
              {t.action && (
                <div className="text-blue-700">
                  <span className="font-medium">行动：</span>
                  <code className="bg-blue-50 px-1 rounded">{t.action}</code>
                </div>
              )}
              {t.observation && (
                <div className="text-gray-700">
                  <span className="font-medium">观察：</span>
                  {t.observation}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

**TypeScript：Multi-Agent 协作树（简化版）**

```tsx
// components/AgentTree.tsx
"use client"
interface AgentNode {
  id: string
  name: string        // "Researcher"
  status: "running" | "done"
  output?: string
  children?: AgentNode[]
}

export function AgentTree({ root }: { root: AgentNode }) {
  return (
    <div className="border rounded-lg p-3 bg-gray-50">
      <AgentTreeNode node={root} depth={0} />
    </div>
  )
}

function AgentTreeNode({ node, depth }: { node: AgentNode; depth: number }) {
  return (
    <div style={{ marginLeft: depth * 20 }} className="border-l-2 border-blue-300 pl-3 my-2">
      <div className="flex items-center gap-2">
        <span className="font-medium">{node.name}</span>
        {node.status === "running" && (
          <span className="text-xs text-yellow-600 animate-pulse">运行中...</span>
        )}
        {node.status === "done" && <span className="text-xs text-green-600">✓ 完成</span>}
      </div>
      {node.output && (
        <div className="text-xs text-gray-600 mt-1 line-clamp-2">{node.output}</div>
      )}
      {node.children?.map((c) => (
        <AgentTreeNode key={c.id} node={c} depth={depth + 1} />
      ))}
    </div>
  )
}
```

### 今日任务

- [ ] 实现 `ThinkingTrace` 折叠面板
- [ ] 让后端在 SSE 中输出 thought 事件
- [ ] （可选）实现 `AgentTree` 展示 Multi-Agent 协作
- [ ] 在项目 #2 研究团队中接入

### 自检清单

- [ ] 我能展示 Thought → Action → Observation 链条
- [ ] 我的思考面板默认折叠（不打扰用户）
- [ ] 我意识到这是产品差异化的关键

---

## Day 5（周五）：文件上传 + RAG UI

**学习目标：** 让用户能上传文档，构建完整的 RAG 用户体验。

### 核心概念

**文件上传的关键点：**
- 大文件分片上传
- 上传进度展示
- 支持 drag & drop
- 文档解析状态展示（解析中 / 解析完成 / 失败）

### 代码示例

**TypeScript：文件上传组件（drag & drop）**

```tsx
// components/FileUpload.tsx
"use client"
import { useState, useCallback } from "react"
import { UploadCloud, FileText, Loader2, Check, X } from "lucide-react"

interface UploadedFile {
  name: string
  size: number
  status: "uploading" | "parsing" | "done" | "error"
  progress: number
  docId?: string
  error?: string
}

export function FileUpload({ onUploaded }: { onUploaded: (docId: string) => void }) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragging, setDragging] = useState(false)

  const upload = useCallback(async (file: File) => {
    const fileId = crypto.randomUUID()
    setFiles((f) => [...f, { name: file.name, size: file.size, status: "uploading", progress: 0 }])

    const formData = new FormData()
    formData.append("file", file)

    // 用 XMLHttpRequest 才能监听上传进度
    const xhr = new XMLHttpRequest()
    xhr.open("POST", `${process.env.NEXT_PUBLIC_API_URL}/api/documents`)

    xhr.upload.onprogress = (e) => {
      const progress = (e.loaded / e.total) * 100
      setFiles((f) => f.map((x) => x.name === file.name ? { ...x, progress } : x))
    }

    xhr.onload = () => {
      const docId = JSON.parse(xhr.responseText).doc_id
      setFiles((f) => f.map((x) => x.name === file.name ? { ...x, status: "parsing", docId } : x))

      // 轮询解析状态
      const poll = setInterval(async () => {
        const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/documents/${docId}`)
        const data = await r.json()
        if (data.status === "ready") {
          clearInterval(poll)
          setFiles((f) => f.map((x) => x.docId === docId ? { ...x, status: "done" } : x))
          onUploaded(docId)
        } else if (data.status === "failed") {
          clearInterval(poll)
          setFiles((f) => f.map((x) => x.docId === docId ? { ...x, status: "error", error: data.error } : x))
        }
      }, 2000)
    }

    xhr.send(formData)
  }, [onUploaded])

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        Array.from(e.dataTransfer.files).forEach(upload)
      }}
      className={`border-2 border-dashed rounded-lg p-6 text-center ${
        dragging ? "border-blue-500 bg-blue-50" : "border-gray-300"
      }`}
    >
      <UploadCloud className="w-8 h-8 mx-auto text-gray-400 mb-2" />
      <p className="text-sm text-gray-600">拖拽文件到这里，或点击上传</p>
      <p className="text-xs text-gray-400">支持 PDF, DOCX, MD（单文件 ≤ 10MB）</p>

      <input
        type="file"
        multiple
        accept=".pdf,.docx,.md,.txt"
        onChange={(e) => Array.from(e.target.files || []).forEach(upload)}
        className="hidden"
        id="file-input"
      />
      <label htmlFor="file-input" className="mt-2 inline-block text-sm text-blue-600 cursor-pointer">
        选择文件
      </label>

      {/* 文件列表 */}
      <div className="mt-4 space-y-2 text-left">
        {files.map((f) => (
          <div key={f.name} className="flex items-center gap-2 text-sm border rounded p-2">
            <FileText className="w-4 h-4 text-gray-500" />
            <span className="flex-1 truncate">{f.name}</span>

            {f.status === "uploading" && (
              <div className="w-24 h-2 bg-gray-200 rounded">
                <div className="h-2 bg-blue-500 rounded" style={{ width: `${f.progress}%` }} />
              </div>
            )}
            {f.status === "parsing" && <Loader2 className="w-4 h-4 animate-spin text-yellow-500" />}
            {f.status === "done" && <Check className="w-4 h-4 text-green-500" />}
            {f.status === "error" && <X className="w-4 h-4 text-red-500" />}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 今日任务

- [ ] 实现文件上传组件（带进度 + 拖拽）
- [ ] 后端实现 `/api/documents` POST 接口
- [ ] 后端实现文档解析（异步任务 + 状态轮询）
- [ ] 前端展示文档列表 + 删除

### 自检清单

- [ ] 我能拖拽上传文件
- [ ] 我能展示上传进度和解析状态
- [ ] 我的 RAG UI 闭环：上传 → 解析 → 提问 → 拿到带引用的答案

---

## Day 6（周六）：前端工程化 + 部署

**学习目标：** 用现代前端工程化方法上线你的 Agent UI。

### 核心概念

**技术栈推荐：**
- 框架：Next.js 14+（App Router）
- 样式：Tailwind CSS + shadcn/ui
- 状态：Zustand（轻量）或 Jotai
- 表单：react-hook-form + zod
- 部署：Vercel（前端）+ Fly.io（后端）

**前后端分离 vs 一体化：**
- 一体化：用 Next.js 的 Route Handler 当后端（简单项目）
- 分离：Next.js 前端 + FastAPI 后端（推荐，后端可独立扩展）

### 代码示例

**TypeScript：Zustand 全局状态（会话 + 设置）**

```typescript
// store/chat-store.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"

interface ChatState {
  sessions: Record<string, Message[]>
  currentSessionId: string | null
  settings: {
    model: "gpt-5-latest" | "gpt-5-latest"
    showThinking: boolean
    showSources: boolean
  }
  createSession: () => string
  setSetting: <K extends keyof ChatState["settings"]>(k: K, v: ChatState["settings"][K]) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      sessions: {},
      currentSessionId: null,
      settings: { model: "gpt-5-latest", showThinking: true, showSources: true },

      createSession: () => {
        const id = crypto.randomUUID()
        set((s) => ({ sessions: { ...s.sessions, [id]: [] }, currentSessionId: id }))
        return id
      },

      setSetting: (k, v) => set((s) => ({ settings: { ...s.settings, [k]: v } })),
    }),
    { name: "chat-store" }
  )
)
```

**Vercel 部署配置（`next.config.js`）：**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 后端 API 的反向代理（避免前端跨域）
  async rewrites() {
    return [
      {
        source: "/api/agent/:path*",
        destination: `${process.env.API_URL}/api/:path*`,
      },
    ]
  },
  // 输出 standalone（适配 Docker）
  output: "standalone",
}

module.exports = nextConfig
```

### 今日任务

- [ ] 引入 Tailwind + shadcn/ui，替换手写样式
- [ ] 用 Zustand 管理会话列表 + 用户设置
- [ ] 加设置面板（模型选择 / 显示开关）
- [ ] 部署到 Vercel，拿到公开 URL
- [ ] 前后端联调，验证完整流程

### 自检清单

- [ ] 我的前端有公开 URL（如 `https://xxx.vercel.app`）
- [ ] 我的 UI 在移动端能正常显示
- [ ] 我能切换模型 / 开关思考过程展示

---

## Day 7（周日）：打磨 + 周末复盘

**学习目标：** 把本周做的所有 UI 整合成一个完整的产品体验。

### 核心概念

**产品体验的 3 个层次：**
1. **能用** — 功能完整、没有 bug
2. **好用** — 交互流畅、响应快
3. **爱用** — 有惊喜细节（动画、空状态、错误提示）

**打磨 checklist：**
- [ ] 加载状态（骨架屏 / Spinner）
- [ ] 空状态（没有消息时的引导）
- [ ] 错误状态（网络异常、超时）
- [ ] 快捷键（Enter 发送 / Shift+Enter 换行）
- [ ] 自动滚动到底部
- [ ] 复制答案按钮
- [ ] 重新生成按钮

### 代码示例

**TypeScript：消息组件（含交互细节）**

```tsx
// components/MessageItem.tsx
"use client"
import { Copy, RotateCcw, Check } from "lucide-react"
import { useState } from "react"

export function MessageItem({ msg, onRegenerate }: {
  msg: Message
  onRegenerate?: () => void
}) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(msg.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`group flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
      <div className="max-w-[80%]">
        <div className={`rounded-2xl px-4 py-2 ${
          msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100"
        }`}>
          <MarkdownRenderer content={msg.content} />
        </div>

        {/* Sources 引用 */}
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {msg.sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
              >
                [{i + 1}] {s.title}
              </a>
            ))}
          </div>
        )}

        {/* Hover 工具栏（只有 Assistant 显示） */}
        {msg.role === "assistant" && (
          <div className="mt-1 opacity-0 group-hover:opacity-100 transition flex gap-2 text-xs text-gray-500">
            <button onClick={copy} className="hover:text-gray-900 flex items-center gap-1">
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? "已复制" : "复制"}
            </button>
            {onRegenerate && (
              <button onClick={onRegenerate} className="hover:text-gray-900 flex items-center gap-1">
                <RotateCcw className="w-3 h-3" /> 重新生成
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
```

### 今日任务

- [ ] 对照"打磨 checklist"逐项检查
- [ ] 至少修复 5 个体验细节
- [ ] 录一个 30 秒的产品 Demo 视频
- [ ] 写本周学习笔记到 `notes/week-26-notes.md`

### 周末复盘问题

1. 我做的 UI 相比 ChatGPT / Claude，差异化在哪？
2. 哪些细节是"前端工程师才能做出来"的？
3. 工具调用可视化给用户带来了什么价值？
4. 如果给面试官演示，我会从哪开始讲？

---

# Week 4：作品集打磨

> **本周目标：** 让 3 个项目都达到"能讲、能看、能问"的水平
> **本周产出：** 3 个完整作品集项目（上线 + README + 博客草稿）

## Day 1（周一）：项目 #1 - 知识助手收尾

**学习目标：** 把知识助手项目从"能跑"打磨到"能展示"。

### 核心概念

**项目 #1 完成标准（对照表）：**
- [ ] 完整 Web UI（Next.js + FastAPI）
- [ ] 用户系统（登录、个人空间）
- [ ] 数据持久化（PostgreSQL + pgvector）
- [ ] 文档管理（上传、删除、列表）
- [ ] 智能问答（RAG + 引用溯源）
- [ ] 工具调用（至少 3 个外部工具）
- [ ] 跨会话记忆
- [ ] 部署上线（公开 Demo 链接）
- [ ] 完整 README（架构图、技术栈、使用说明）

### 代码示例

**README 架构图模板（Meridian）：**

```markdown
# 知识助手 - 项目说明

## 架构

\`\`\`mermaid
graph LR
    A[Next.js 前端] -->|SSE| B[FastAPI]
    B --> C[Agent 核心]
    C --> D[Retriever]
    C --> E[Tools]
    C --> F[Memory]
    D --> G[(pgvector)]
    F --> H[(Redis)]
    E --> I[外部 API]
\`\`\`

## 技术栈
- 前端：Next.js 14 / Tailwind / Zustand
- 后端：FastAPI / Pydantic / LangGraph
- 存储：PostgreSQL + pgvector / Redis
- 部署：Vercel + Fly.io
- 评测：LangSmith + Promptfoo
- 监控：Logfire + Sentry

## 核心指标
- 准确率：92%（50 条评测集）
- 平均延迟：1.8s（P95：3.2s）
- 单次调用成本：$0.003

## 快速开始
\`\`\`bash
# 后端
cd server && uv sync && uvicorn app.main:app --reload

# 前端
cd web && pnpm i && pnpm dev
\`\`\`
```

### 今日任务

- [ ] 对照完成标准，列出未完成项
- [ ] 补齐用户系统（可用 Clerk / NextAuth 简化）
- [ ] 补齐文档管理（上传、删除、列表）
- [ ] 优化 RAG 准确率到 ≥85%

### 自检清单

- [ ] 项目 #1 的完成标准全部打勾
- [ ] 有公开 Demo 链接
- [ ] README 包含架构图和技术栈

---

## Day 2（周二）：项目 #1 - 博客写作

**学习目标：** 把项目 #1 写成一篇有深度的技术博客。

### 核心概念

**讲故事的 STAR 法则：**
- **Situation**：我为什么要做这个？（个人知识管理痛点）
- **Task**：目标是什么？（能用的 RAG 助手）
- **Action**：怎么做的？（技术选型 + 优化路径）
- **Result**：结果如何？（准确率 60% → 90%）

**前端工程师的独特视角：**
- 强调"前端工程师做 Agent 的优势"
- 讲清楚如何用前端能力做工具调用可视化
- 对比纯后端做法的差异

### 代码示例

**博客大纲模板（`posts/rag-from-60-to-90.md`）：**

```markdown
# RAG 从 60% 到 90%：我的优化实录

## 背景
作为前端工程师，我用 4 周做了一个个人知识助手。
初始准确率只有 60%，经过 X 轮优化到 90%。
本文记录每一轮优化做了什么、效果如何。

## 初始版本（60%）
- 最朴素的 RAG：embedding + top-k + 直接拼 Prompt
- 主要问题：
  1. 检索不准（相关文档排不上）
  2. 幻觉严重（没有 source 约束）
  3. 长 query 效果差

## 优化 1：HyDE（70%）
- 思路：让 LLM 先生成假设答案，用答案去检索
- 效果：+10%
- 代码示例

## 优化 2：Reranker（78%）
- 思路：top-k=20 → rerank → top-3
- 效果：+8%
- 代码示例

## 优化 3：Prompt 工程（85%）
- 思路：加 source 约束、加示例、加拒绝策略
- 效果：+7%

## 优化 4：查询分类 + 路由（90%）
- 思路：简单问题走小模型 + 缓存
- 效果：+5% + 成本下降 60%

## 复盘
- 评测驱动是关键
- 不要过早优化
- 前端能力让我做出了更好的调试 UI
```

### 今日任务

- [ ] 列出你做过的所有优化（按时间顺序）
- [ ] 用 STAR 法则写博客大纲
- [ ] 写完初稿（≥2000 字）
- [ ] 配 3-5 张图（架构图 / 指标对比 / UI 截图）

### 自检清单

- [ ] 博客有清晰的故事线（不是流水账）
- [ ] 有量化指标（准确率、延迟、成本）
- [ ] 有代码片段（不是纯理论）

---

## Day 3（周三）：项目 #2 - 研究团队收尾

**学习目标：** 把 Multi-Agent 研究团队项目打磨到完整。

### 核心概念

**项目 #2 完成标准：**
- [ ] LangGraph 实现的 Multi-Agent
- [ ] 完整 trace 可视化（Web UI 展示协作过程）
- [ ] 成本分析面板
- [ ] 对比报告（单 Agent vs Multi-Agent）
- [ ] 5+ 真实研究报告示例
- [ ] 评测体系（准确率、忠实度、成本）
- [ ] 部署上线
- [ ] 完整 README
- [ ] 技术博客

**讲故事的角度：**
"Multi-Agent 真的有效吗？我用一个研究助手项目做了对照实验"

### 代码示例

**Python：单 Agent vs Multi-Agent 对照实验**

```python
# experiments/compare_agents.py
import asyncio
import time
from app.single_agent import SingleAgent
from app.multi_agent import MultiAgentTeam
from app.eval.metrics import compute_all

async def run_experiment(questions: list[str]):
    single = SingleAgent()
    multi = MultiAgentTeam()

    results = {"single": [], "multi": []}
    for q in questions:
        # 单 Agent
        t0 = time.perf_counter()
        single_ans = await single.research(q)
        single_dur = time.perf_counter() - t0

        # Multi-Agent
        t0 = time.perf_counter()
        multi_ans = await multi.research(q)
        multi_dur = time.perf_counter() - t0

        results["single"].append({
            "answer": single_ans.text, "cost": single_ans.cost,
            "duration": single_dur, "trace": single_ans.trace,
        })
        results["multi"].append({
            "answer": multi_ans.text, "cost": multi_ans.cost,
            "duration": multi_dur, "trace": multi_ans.trace,
        })
    return results

# 输出对比报告
def report(results):
    print(f"{'指标':<15} {'单 Agent':<15} {'Multi-Agent':<15} {'差异':<15}")
    for metric in ["accuracy", "faithfulness", "cost", "duration"]:
        s = sum(r[metric] for r in results["single"]) / len(results["single"])
        m = sum(r[metric] for r in results["multi"]) / len(results["multi"])
        print(f"{metric:<15} {s:<15.2f} {m:<15.2f} {(m-s)/s*100:+.1f}%")
```

### 今日任务

- [ ] 对照完成标准，列出未完成项
- [ ] 补齐 trace 可视化（用 Week 3 的 `AgentTree` 组件）
- [ ] 加成本分析面板（显示每次任务的 token / 成本）
- [ ] 跑一次单 Agent vs Multi-Agent 对照实验

### 自检清单

- [ ] 项目 #2 的完成标准全部打勾
- [ ] 有对照实验数据
- [ ] 有 5+ 真实研究报告示例

---

## Day 4（周四）：项目 #2 - 博客写作

**学习目标：** 把 Multi-Agent 项目写成有洞察的博客。

### 核心概念

**这篇博客要回答的核心问题：**
- Multi-Agent 真的比单 Agent 好吗？
- 在什么场景下好？
- 代价是什么（成本、延迟）？
- 什么时候不该用？

### 代码示例

**博客大纲（`posts/multi-agent-real-value.md`）：**

```markdown
# Multi-Agent 真的有效吗？我用对照实验回答

## 背景
- 看了很多文章说 Multi-Agent 好
- 但很少有真实数据对比
- 我做了一个研究助手，跑了一组对照实验

## 实验设计
- 任务：技术调研（5 类问题 × 每类 5 个）
- 对比：单 Agent（ReAct）vs Multi-Agent（Planner + Researcher + Writer）
- 指标：准确率、忠实度、成本、延迟

## 实验结果
| 指标 | 单 Agent | Multi-Agent | 差异 |
|------|---------|------------|------|
| 准确率 | 75% | 82% | +9.3% |
| 忠实度 | 88% | 92% | +4.5% |
| 成本 | $0.02 | $0.08 | +300% |
| 延迟 | 8s | 22s | +175% |

## 结论
- Multi-Agent 在复杂任务上有显著优势
- 但成本和延迟是 3-4 倍
- 简单任务不值得

## 什么时候用 Multi-Agent？
1. 任务可拆分（多角度调研）
2. 质量比成本重要（如医疗、法律）
3. 能并行执行（节省时间）

## 复盘
- 别被概念忽悠，看数据
- 评测是唯一真相
- 前端能力让我做出了 trace 可视化，调试快了 10 倍
```

### 今日任务

- [ ] 用真实数据填充博客大纲
- [ ] 写完初稿（≥2000 字）
- [ ] 做一张对比图表（可用 Recharts 或 Excalidraw）
- [ ] 给一个朋友讲一遍，收集反馈

### 自检清单

- [ ] 博客有明确观点（不是模棱两可）
- [ ] 有真实数据支撑
- [ ] 能给读者启发（什么时候用 / 不用）

---

## Day 5（周五）：项目 #3 - 创新项目启动

**学习目标：** 启动第 3 个创新项目（体现差异化）。

### 核心概念

**选题建议（选一个，避免贪多）：**

1. **MCP Server 项目** — 为常用服务写 MCP Server
2. **浏览器 Agent** — 自动完成某类网页任务
3. **AI Coding 工具** — 针对特定场景的代码助手
4. **垂直领域 Copilot** — 你熟悉领域的 AI 助手

**选题原则：**
- 发挥前端优势（要有好 UI）
- 体现 Agent 工程能力（不只调 API）
- 有清晰差异化（不是抄 ChatGPT）

### 代码示例

**MCP Server 最小示例（Python）：**

```python
# mcp_server_notion/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("notion-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_pages",
            description="搜索 Notion 中的页面",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="create_page",
            description="在 Notion 创建新页面",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_pages":
        results = await notion_client.search(arguments["query"])
        return [TextContent(type="text", text=str(results))]
    elif name == "create_page":
        page = await notion_client.create_page(**arguments)
        return [TextContent(type="text", text=f"已创建：{page.url}")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
```

### 今日任务

- [ ] 选定一个创新方向（写下 3 个候选，选 1 个）
- [ ] 写一页项目说明（定位 / 差异化 / 核心功能）
- [ ] 搭建项目骨架（前后端 + Dockerfile）
- [ ] 实现 MVP 的最小功能

### 自检清单

- [ ] 我的创新项目有清晰差异化
- [ ] 能用一句话讲清楚"为什么做这个"
- [ ] MVP 能跑

---

## Day 6（周六）：项目 #3 - 完整实现

**学习目标：** 把创新项目做到能演示的程度。

### 核心概念

**MVP 的 3 个层次：**
1. **能跑** — 核心流程走通
2. **能用** — 真实数据、真实场景
3. **能演示** — 有 UI、有 Demo 数据、能讲故事

### 代码示例

**浏览器 Agent 示例（用 Browser Use）：**

```python
# browser_agent/agent.py
from browser_use import Agent
from langchain_openai import ChatOpenAI

class ShoppingAgent:
    """比价助手：给定商品，自动比较多个电商网站价格"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5-latest")
        self.agent = Agent(llm=self.llm)

    async def compare_price(self, product: str) -> dict:
        task = f"""
        比较商品"{product}"在以下网站的价格：
        1. 京东：https://search.jd.com
        2. 淘宝：https://s.taobao.com
        3. 拼多多：https://mobile.yangkeduo.com

        返回每个网站的价格和商品链接。
        """

        result = await self.agent.run(task)
        return {"product": product, "results": result}
```

### 今日任务

- [ ] 实现核心功能（能让用户跑完一个完整流程）
- [ ] 加最小 UI（哪怕只是一个表单 + 结果展示）
- [ ] 准备 3 个 Demo 场景数据
- [ ] 自己跑一遍，记录卡点

### 自检清单

- [ ] 我的项目能给陌生人演示
- [ ] Demo 场景真实、能打动人
- [ ] 我知道怎么讲这个项目的故事

---

## Day 7（周日）：作品集整合 + 周末复盘

**学习目标：** 让 3 个项目串成一个完整的"成长故事"。

### 核心概念

**3 个项目讲 3 个故事：**
- 项目 #1：**我能做生产级 Agent**（RAG + 工具调用 + 评测）
- 项目 #2：**我能做复杂 Agent**（Multi-Agent + 实验对比）
- 项目 #3：**我有创新和差异化**（MCP / 浏览器 / 垂直领域）

### 代码示例

**作品集主页模板（Next.js）：**

```tsx
// app/portfolio/page.tsx
const PROJECTS = [
  {
    title: "知识助手",
    tagline: "RAG + Function Calling，准确率 60% → 90%",
    stack: ["Next.js", "FastAPI", "pgvector", "LangGraph"],
    demo: "https://knowledge.fly.dev",
    github: "https://github.com/xxx/knowledge-agent",
    highlights: [
      "完整评测体系（单元 + 集成 + E2E）",
      "SSE 流式 + 工具调用可视化",
      "成本优化：单次 $0.003",
    ],
  },
  {
    title: "研究团队",
    tagline: "Multi-Agent 对照实验，用数据说话",
    stack: ["LangGraph", "FastAPI", "Next.js"],
    demo: "https://research.fly.dev",
    github: "https://github.com/xxx/research-team",
    highlights: [
      "单 vs Multi-Agent 对比报告",
      "完整 trace 可视化",
      "成本分析面板",
    ],
  },
  {
    title: "Notion MCP Server",
    tagline: "前端工程师视角的 Agent 生态",
    stack: ["Python", "MCP", "Notion API"],
    demo: "https://github.com/xxx/notion-mcp",
    github: "https://github.com/xxx/notion-mcp",
    highlights: [
      "发布到 MCP Hub",
      "支持搜索 / 创建 / 更新",
      "已被 N 个项目使用",
    ],
  },
]

export default function PortfolioPage() {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">wsq - Agent Engineer</h1>
      <p className="text-gray-600 mb-8">
        前端工程师转型 Agent 工程师，6 个月完成 3 个生产级项目。
      </p>

      <div className="space-y-6">
        {PROJECTS.map((p) => (
          <div key={p.title} className="border rounded-lg p-6 hover:shadow-lg transition">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-semibold">{p.title}</h2>
                <p className="text-gray-600 text-sm mt-1">{p.tagline}</p>
              </div>
              <div className="flex gap-2 text-sm">
                <a href={p.demo} className="text-blue-600 hover:underline">Demo</a>
                <a href={p.github} className="text-gray-700 hover:underline">Code</a>
              </div>
            </div>

            <ul className="mt-4 space-y-1 text-sm text-gray-700">
              {p.highlights.map((h, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-green-500">✓</span> {h}
                </li>
              ))}
            </ul>

            <div className="mt-4 flex gap-2 flex-wrap">
              {p.stack.map((s) => (
                <span key={s} className="text-xs bg-gray-100 px-2 py-1 rounded">{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 今日任务

- [ ] 做一个作品集主页（Next.js，部署到 Vercel）
- [ ] 3 个项目都有：Demo 链接 + GitHub + README
- [ ] 录一个 3 分钟总览视频（3 个项目各 1 分钟）
- [ ] 写本周学习笔记到 `notes/week-27-notes.md`

### 周末复盘问题

1. 3 个项目放在一起，能看出我的成长轨迹吗？
2. 哪个项目最值得拿出来讲故事？为什么？
3. 我的差异化在哪？（前端 + Agent 的复合优势）
4. 面试官看完我的作品集，会记住我什么？

---

# Week 5：求职准备

> **本周目标：** 把学习成果转化为求职竞争力，开始投递
> **本周产出：** 简历 + GitHub Profile + 3-5 篇博客 + 面试准备 + 目标公司清单

## Day 1（周一）：简历优化

**学习目标：** 把前端经验包装成"AI 工程优势"，而不是淡化它。

### 核心概念

**简历的 3 个关键：**
1. **定位明确** — "前端工程师 + Agent 工程能力"
2. **项目亮眼** — 3 个项目 + 量化指标
3. **故事一致** — 整份简历讲"为什么转 Agent"的故事

**前端经验的"AI 包装"：**

| 前端经验 | AI 工程视角包装 |
|---------|---------------|
| 5 年前端经验 | "5 年用户产品经验，擅长把 AI 能力转化为产品体验" |
| React / Next.js 熟练 | "能独立构建 Agent 产品的完整前端（流式 UI、工具调用可视化）" |
| 前端工程化 | "具备把 AI 原型打磨成上线产品的工程能力" |
| 团队协作 | "能在 AI 团队承担前端 + Agent 桥梁角色" |

### 代码示例

**简历项目描述模板（STAR + 量化）：**

```markdown
## 项目经历

### 个人知识助手 | github.com/xxx/knowledge-agent
**背景：** 个人知识管理效率低，市面工具不够智能
**目标：** 构建一个准确率 ≥90% 的 RAG 知识助手

**做了什么：**
- 设计并实现基于 FastAPI + LangGraph 的 Agent 后端
- 用 HyDE + Reranker + Prompt 工程把准确率从 60% 提升到 92%
- 用 Next.js + Vercel AI SDK 构建流式 UI + 工具调用可视化
- 建立分层评测体系（50 条用例 + GitHub Actions CI）
- 部署到 Fly.io，集成 LangSmith + Logfire 监控

**结果：**
- 准确率：60% → 92%（+53%）
- 单次调用成本：$0.003（优化后降 60%）
- P95 延迟：3.2s
- Demo：xxx.fly.dev（已上线 X 个月）
```

### 今日任务

- [ ] 写一版简历初稿（中英文各一份）
- [ ] 用 STAR + 量化重写 3 个项目描述
- [ ] 把前端经验按"AI 包装"表重写
- [ ] 找 2 个朋友 review，收集反馈

### 自检清单

- [ ] 我的简历定位是"前端 + Agent 复合人才"
- [ ] 每个项目都有量化指标
- [ ] 没有"精通 XXX"这种空话

---

## Day 2（周二）：GitHub Profile 打磨

**学习目标：** 让 GitHub Profile 成为第二份简历。

### 核心概念

**GitHub Profile 的 4 个关键：**
1. **Profile README** — 自我介绍 + 技能栈 + 项目链接
2. **置顶仓库** — 3 个作品集项目
3. **贡献记录** — 参与 Agent 开源项目（哪怕是改文档）
4. **Star 列表** — Star 一些重要的 Agent 项目（体现品味）

### 代码示例

**GitHub Profile README 模板（`<username>/README.md`）：**

```markdown
# 你好，我是 wsq 👋

## 🚀 转型故事
前端工程师 → Agent 工程师，6 个月完成 3 个生产级 AI 项目。

## 🔥 最新项目
- 🔗 [知识助手](https://github.com/xxx/knowledge-agent) - RAG + Function Calling，准确率 92%
- 🔗 [研究团队](https://github.com/xxx/research-team) - Multi-Agent 对照实验
- 🔗 [Notion MCP](https://github.com/xxx/notion-mcp) - MCP Server，已被 N+ 项目使用

## 🛠 技术栈
**Agent：** LangGraph / LangChain / MCP / Function Calling / RAG
**LLM：** OpenAI / Anthropic / 本地模型
**前端：** React / Next.js / TypeScript / Tailwind
**后端：** FastAPI / PostgreSQL / Redis / Docker
**评测：** LangSmith / Promptfoo / 自建评测体系

## 📝 技术博客
- [RAG 从 60% 到 90%](https://xxx)
- [Multi-Agent 真的有效吗？](https://xxx)
- [前端工程师视角学 Agent](https://xxx)

## 📫 联系我
- Email：xxx
- LinkedIn：xxx
- 博客：xxx
```

### 今日任务

- [ ] 创建 `<你的用户名>/<你的用户名>` 仓库
- [ ] 写 Profile README
- [ ] 置顶 3 个作品集项目
- [ ] Star 至少 20 个 Agent 相关项目（LangChain、CrewAI、Vercel AI SDK 等）
- [ ] 给 1-2 个开源项目提 PR（哪怕改 typo）

### 自检清单

- [ ] 我的 GitHub Profile 第一眼能看出"做 Agent 的"
- [ ] 3 个置顶项目都有 README + Demo
- [ ] 近期有贡献记录（不是 0 commit）

---

## Day 3（周三）：技术博客发布

**学习目标：** 把本周草稿打磨成可发布的文章。

### 核心概念

**博客发布的 3 个平台：**
- **掘金 / 知乎** — 国内技术圈，HR 会看
- **Medium / Dev.to** — 国际化，外企会看
- **个人博客** — 长期资产，简历链接

**好博客的 5 个要素：**
1. 有观点（不是教程翻译）
2. 有数据（量化指标）
3. 有代码（可复现）
4. 有图（架构图 / 对比图）
5. 有故事（个人经历）

### 今日任务

- [ ] 把 Week 4 写的 2 篇博客打磨到可发布
- [ ] 再写 1 篇《前端工程师视角学 Agent：30 周转型记》
- [ ] 在掘金 / 知乎 / 个人博客同步发布
- [ ] 在朋友圈 / 即刻 / X 分享

### 自检清单

- [ ] 我有 3+ 篇已发布的技术博客
- [ ] 每篇都有量化指标和代码
- [ ] 简历里有博客链接

---

## Day 4（周四）：面试题准备 - 基础篇

**学习目标：** 准备 Agent 工程师常见的基础面试题。

### 核心概念

**Agent 工程师基础题分类：**
1. Prompt 工程：如何系统化提升效果？
2. 评测：怎么知道你的 Agent 好不好？
3. 成本：如何控制？
4. 幻觉：如何减少？
5. 工具调用：如何提高准确率？

### 代码示例

**面试题回答模板（以"评测"为例）：**

```markdown
## Q：你怎么知道你的 Agent 好不好？

### 回答框架
1. **分层评测思路** — 单元 / 集成 / E2E
2. **多指标体系** — Accuracy / Faithfulness / Latency / Cost
3. **LLM-as-Judge** — 主观指标的客观化
4. **回归测试** — 改 Prompt 不退化
5. **CI 集成** — 每次提交自动评测

### 项目举例
"我在知识助手项目中建立了完整的评测体系：
- 50 条 E2E 用例
- LLM Judge（旗舰模型如 GPT-5 / Claude Opus）打分
- GitHub Actions 每次 PR 自动跑
- 发现了 3 次退化，避免了上线问题"

### 反问面试官
- 你们团队的评测集多大？
- 评测是离线还是在线？
- 怎么处理 Long Tail Query？
```

### 今日任务

- [ ] 准备 10 个基础题的回答（用上面框架）
- [ ] 每个回答都结合自己的项目举例
- [ ] 每个回答准备 1 个反问
- [ ] 找朋友模拟面试 1 小时

### 自检清单

- [ ] 我能流利回答 10 个基础题
- [ ] 每个回答都有项目案例
- [ ] 我能在 2 分钟内讲清楚一个技术点

---

## Day 5（周五）：面试题准备 - 进阶篇

**学习目标：** 准备 Agent 工程师的进阶面试题。

### 核心概念

**进阶题分类：**
1. Multi-Agent：什么场景该用 / 不该用？
2. 长文本：Long Context vs RAG 怎么选？
3. 记忆：如何设计 Agent 记忆系统？
4. 部署：并发、成本、监控怎么做？
5. 架构：如何设计一个生产级 Agent 系统？

### 代码示例

**进阶题回答示例（Multi-Agent）：**

```markdown
## Q：Multi-Agent 什么场景该用，什么场景不该？

### 该用的场景
1. 任务可拆分（多角度调研、并行执行）
2. 单 Agent 上下文太长（每个 Agent 聚焦）
3. 需要不同角色（Planner / Executor / Reviewer）
4. 质量比成本重要（医疗、法律、金融）

### 不该用的场景
1. 简单任务（成本是 3-5 倍）
2. 强实时（延迟会显著增加）
3. 任务不可拆分
4. 没有评测体系（无法判断是否更好）

### 项目数据
"我做过对照实验：
- 准确率：单 Agent 75% → Multi-Agent 82%（+9.3%）
- 成本：$0.02 → $0.08（+300%）
- 延迟：8s → 22s（+175%）

结论：复杂调研任务用 Multi-Agent 值得，简单问答不值得。"
```

**进阶题回答示例（Long Context vs RAG）：**

```markdown
## Q：Long Context vs RAG 怎么选？

### Long Context 适合
- 文档量 < 200K tokens
- 文档是静态的（不频繁更新）
- 需要全局理解（跨文档推理）
- 实时性要求高

### RAG 适合
- 文档量大（> 1M tokens）
- 文档频繁更新
- 需要精确引用溯源
- 成本敏感

### 混合方案
- RAG 做初筛 → Long Context 做精读
- 用 Long Context 处理 Top-K 文档

### 我的实践
"知识助手用 RAG（pgvector + HyDE + Reranker），
因为文档量大（> 1000 篇）且频繁更新。"
```

### 今日任务

- [ ] 准备 8 个进阶题的回答
- [ ] 每个回答都有数据 / 项目案例
- [ ] 准备 3 个"反问面试官"的问题
- [ ] 录一段 5 分钟的自我介绍视频（自查）

### 自检清单

- [ ] 我能流利回答进阶题
- [ ] 我有数据支撑每个观点
- [ ] 我能在被追问时不慌

---

## Day 6（周六）：目标公司 + 投递准备

**学习目标：** 建立求职管道，开始系统化投递。

### 核心概念

**公司分类（找最匹配的）：**

| 类型 | 适合度 | 例子 |
|------|-------|------|
| AI Native 公司 | ⭐⭐⭐⭐⭐ | Cursor、Perplexity、Anthropic、OpenAI |
| 大厂 AI 团队 | ⭐⭐⭐⭐ | 字节豆包、阿里通义、腾讯元宝 |
| AI 应用创业公司 | ⭐⭐⭐⭐ | 各类垂直 AI SaaS |
| 传统公司转型 | ⭐⭐⭐ | 需要"AI + 前端"复合人才 |

**求职渠道：**
- 国内：BOSS 直聘、拉勾、猎聘
- 国际：LinkedIn、Y Combinator Jobs
- 远程：Remote.co、We Work Remotely
- 社区：即刻、X（Twitter）、AI 工程师 Discord

### 代码示例

**求职追踪表（`job-hunting.md`）：**

```markdown
# 求职追踪

## 目标公司清单（20+）

| 公司 | 岗位 | 渠道 | 投递日期 | 状态 | 备注 |
|------|------|------|---------|------|------|
| Cursor | FE/Agent Engineer | 官网 | 2026-08-01 | 待投 | 需要 AI IDE 经验 |
| 字节豆包 | AI 应用工程师 | BOSS | - | 准备中 | 朋友内推 |
| ... | ... | ... | ... | ... | ... |

## 投递状态说明
- 待投：已研究岗位，准备投
- 已投：已投递
- 笔试：收到笔试
- 面试中：收到面试邀请
- Offer：拿到 offer
- Reject：被拒（记录原因）

## 每周复盘
- 投递数：X
- 响应率：X%
- 面试通过率：X%
- 主要问题：XXX
```

### 今日任务

- [ ] 列出 20+ 目标公司清单
- [ ] 每个公司标注：岗位、要求、差异化卖点
- [ ] 针对性准备 3 份不同版本的简历（AI Native / 大厂 / 创业公司）
- [ ] 投出第一批 5 个公司

### 自检清单

- [ ] 我有 20+ 目标公司清单
- [ ] 每个公司都研究过岗位要求
- [ ] 我开始投递了（不再准备）

---

## Day 7（周日）：模拟面试 + 最终复盘

**学习目标：** 通过模拟面试发现盲点，完成 28 周学习的最终复盘。

### 核心概念

**模拟面试的 3 个层次：**
1. **自我模拟** — 录视频看自己
2. **朋友模拟** — 找懂技术的朋友
3. **付费模拟** — pramp.io、专业服务

### 今日任务

- [ ] 做一次完整的 1 小时模拟面试（让朋友当面试官）
- [ ] 录像并回看，记录 3 个改进点
- [ ] 写一篇《30 周转型记》总结博客
- [ ] 写本周学习笔记到 `notes/week-28-notes.md`

### 周末复盘问题

1. 我的简历能在 10 秒内让 HR 看出我是 Agent 工程师吗？
2. 我的 3 个项目，哪个最强？哪个最弱？
3. 面试中我最容易卡壳的问题是什么？
4. 接下来 3 个月的求职目标是什么？

---

# 附录

## 常见卡点速查表

| 卡点 | 现象 | 解决方案 |
|------|------|---------|
| LangSmith trace 不显示 | 配置后没有数据 | 检查 `LANGSMITH_TRACING=true` + API Key |
| Promptfoo 评测超时 | 跑不完 | 减少用例数 / 用更便宜模型跑 Judge |
| CI 评测太慢 | Actions 跑 10 分钟+ | 只在 PR 触发，不每次 push；分级跑 |
| FastAPI SSE 卡住 | 浏览器收不到流 | 检查 Nginx 缓冲 / 加 `X-Accel-Buffering: no` |
| Docker 镜像太大 | > 1GB | 用多阶段构建 + python:slim 基础镜像 |
| Fly.io 部署失败 | 密钥 / 端口问题 | 用 `fly secrets set`，检查 `internal_port` |
| Vercel AI SDK useChat 不流式 | 一次性返回 | 检查 `streamText` + `toDataStreamResponse` |
| 工具调用 UI 闪烁 | 状态切换抖动 | 用稳定 key + React.memo |
| 文件上传 CORS | 跨域被拦 | 后端加 CORS 中间件 + Vercel rewrites |
| Multi-Agent 死循环 | Agent 互相调用 | 设置 max_iterations + 终止条件 |

## 完成标准

第 6 阶段结束时，你应该能：

- [ ] 给项目建立分层评测体系（单元 + 集成 + E2E）
- [ ] 用 LangSmith / Promptfoo 做严肃评测
- [ ] 评测集成到 CI（每次 PR 自动跑）
- [ ] 用 FastAPI 写出 SSE 流式 API
- [ ] 用 Docker 打包、部署到 Fly.io / Railway
- [ ] 用 Next.js + Vercel AI SDK 做出聊天 UI
- [ ] 实现工具调用可视化 + 思考过程展示
- [ ] 3 个作品集项目都上线、有 Demo
- [ ] 简历完成、突出 AI 工程优势
- [ ] GitHub Profile 专业
- [ ] 3+ 篇技术博客已发布
- [ ] 能回答常见 Agent 工程师面试题

## 转型完成的核心标志

### 能力层面
- 能独立设计、实现、部署、评测一个 Agent 系统
- 前端能力让你能把 Agent 做成好产品（稀缺优势）

### 作品层面
- 有 3 个可展示的项目，覆盖单 Agent / Multi-Agent / 创新
- 每个项目都有：Demo + 评测 + 博客

### 认知层面
- 能清晰讲述"为什么这么设计"、"如何评测"、"成本如何"
- 能区分 hype 和 reality（不被概念忽悠）

### 市场层面
- 简历能通过 Agent 工程师职位的简历筛选
- 面试中能用项目和数据说话
- 有清晰的"前端 + Agent"差异化定位

## 转型后的持续成长

完成 28 周路线只是起点。持续成长的方向：

- **深度**：关注 arXiv 新论文、复现 SOTA
- **广度**：学习多模态、语音、图像 Agent
- **生态**：参与 LangChain / CrewAI 等开源项目
- **商业**：尝试做自己的 AI 产品（独立开发者路线）

---

**从前端工程师到 Agent 工程师，你完成了身份转换。**

**接下来的路，靠作品说话。**
