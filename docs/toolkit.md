# Agent 工程师工具速查表

> **为什么写这个：** 路线文档里的工具选型信息分散在 6 个阶段、13 份文档里。学到 Phase 5 想回头查"Phase 3 那会儿讲的向量库有哪些来着"，要翻半天。这份单页把**所有用到的工具**按用途汇总，每条标注：主流选择 / 出现阶段 / 免费额度 / 替代品。
>
> **使用方式：** 学习时 bookmark 这一页；做新项目时当选型参考；面试前快速过一遍建立"工具地图"。
>
> **时效说明：** 免费额度和定价会变，以下为 2026-07 量级参考，使用前请查官方最新政策。当期型号 / 价格的唯一数据源是 [versions.md](./versions.md)（每季度校准只改那一个文件）；本表只保留选型知识（比较性论述）。

---

## 1. LLM API（核心）

| 厂商 | 主力模型（2026-07）| 出现阶段 | 免费额度 | 适用场景 |
|------|------|:-------:|---------|---------|
| **OpenAI** | GPT-5 系列（含推理 o 系列）| Phase 1+ | 无（按量计费）| 综合能力最强、生产环境首选 |
| **Anthropic** | Claude 4.5+（Sonnet/Opus）| Phase 1+ | 无（按量计费）| 长文档、Agent、Tool Use 生态友好 |
| **DeepSeek** | R1 / V3 | Phase 1 备选 | 有免费试用额度 | 国内可用、推理强、**最便宜之一** |
| **通义千问** | Qwen 系列 | Phase 1 备选 | 有免费试用额度 | 国内项目、中文场景 |
| **智谱 GLM** | GLM 系列 | Phase 1 备选 | 有免费试用额度 | 国内项目 |
| **Moonshot** | Kimi 系列 | Phase 1 备选 | 有免费试用额度 | 长上下文、国内 |
| **Google** | Gemini 2.x（含 Thinking）| 选学 | 有免费层 | 超长上下文（1M）、多模态 |
| **开源** | Llama / Qwen / DeepSeek 开源版 | Phase 2+ | 免费（自部署）| 本地部署、微调、数据敏感 |

**省钱策略：** 开发调试用经济模型（DeepSeek / Claude Haiku / GPT mini），评测/上线前再用旗舰模型验证。

---

## 2. Python 工程化

| 工具 | 用途 | 出现阶段 | 替代品 | 说明 |
|------|------|:-------:|-------|------|
| **uv** | 包管理 + 虚拟环境 | Phase 1 Week 1 | pip + venv、Poetry、PDM | 2025+ 事实标准，Rust 写的极快 |
| **Ruff** | lint + format | Phase 1 Week 3 | ESLint、Black + isort、flake8 | Rust 写的，集成了多个工具 |
| **mypy** | 类型检查（strict 模式）| Phase 1 Week 3 | Pyright、pyright（Pylance 底层）| Pylance 在 VS Code 里更快 |
| **pytest** | 测试框架 | Phase 1 Week 2 | unittest、nox | fixture + parametrize 是核心 |
| **pydantic** | 数据校验 | Phase 1 Week 2 | dataclass + 手写校验 | Agent 开发必备 |
| **pydantic-settings** | 环境变量配置 | Phase 1 Week 3 | python-dotenv、dynaconf | 自动从 env / .env 加载 |
| **tenacity** | 重试机制 | Phase 1 Week 5 | 自写 for + exponential backoff | Agent 调用 LLM 的标配 |
| **structlog** | 结构化日志 | Phase 1 Week 3 | 标准 logging、loguru | JSON 日志，便于聚合 |
| **rich** | 终端美化 | Phase 1 Week 4 | click、typer | CLI 应用必备 |

---

## 3. Prompt 工程与评测

| 工具 | 用途 | 出现阶段 | 替代品 | 说明 |
|------|------|:-------:|-------|------|
| **tiktoken** | token 计数 | Phase 1 Week 4 | 各家内置 tokenizer | 新模型可能未收录，用 cl100k_base 近似 |
| **Promptfoo** | 本地评测 + CI | Phase 2 Week 4 | LangSmith Evals、自建 | YAML 配置，CI 友好 |
| **LangSmith** | trace + 评测 + 监控 | Phase 4+ | Braintrust、Phoenix、Langfuse | LangChain 配套最强 |
| **Braintrust** | 企业级评测 | Phase 6 Week 1 | LangSmith | 团队协作好 |
| **Phoenix (Arize)** | 开源可观测 | Phase 6 Week 1 | Langfuse、traceloop | 可自托管，数据敏感场景 |
| **RAGAS** | RAG 专用评测 | Phase 3 Week 4 | DeepEval、TruLens | 忠实度 / 答案相关性指标 |
| **DSPy** | 程序化 Prompt 优化 | Phase 2 Week 3（入门）| 自写 grid search | 学术派，学习曲线陡 |
| **instructor** | 结构化输出（跨厂商）| Phase 1 Week 5 | 官方 SDK 直接用 | 统一 OpenAI/Anthropic/Gemini |

---

## 4. 向量数据库 / Embedding

### 向量库

| 工具 | 出现阶段 | 部署 | 适用场景 |
|------|:-------:|------|---------|
| **Chroma** | Phase 3 Week 2 | 本地 / 嵌入式 | **学习首选**、原型 |
| **Qdrant** | Phase 3 Week 2 | 本地 / 云 / 自托管 | 生产、性能强、Rust 写的 |
| **pgvector** | Phase 6 | PostgreSQL 扩展 | 已有 PG 的项目、SQL 友好 |
| **Milvus** | 进阶 | 分布式 | 大规模（亿级以上）|
| **Pinecone** | 选学 | 托管 SaaS | 不想运维、贵 |
| **Weaviate** | 选学 | 自托管 / 托管 | 多模态、GraphQL API |

### Embedding 模型

| 模型 | 厂商 | 维度 | 出现阶段 | 适用 |
|------|------|:----:|:-------:|------|
| **text-embedding-3-small** | OpenAI | 1536 | Phase 3 Week 2 | **通用首选**，便宜效果好 |
| **text-embedding-3-large** | OpenAI | 3072 | Phase 3 Week 2 | 高精度场景 |
| **BGE-M3** | 智源 | 1024 | Phase 3 Week 2 | 开源、中文好、可本地 |
| **Cohere embed-v3** | Cohere | 1024 | Phase 3 Week 2 | 多语言 |
| **Voyage AI** | Voyage | 多种 | 选学 | 2025+ 黑马，部分榜单 SOTA |

---

## 5. RAG / 检索增强

| 工具 | 用途 | 出现阶段 | 替代品 |
|------|------|:-------:|-------|
| **LangChain** | LLM 应用框架 | Phase 3+ | LlamaIndex |
| **LlamaIndex** | RAG 专用框架 | Phase 3 | LangChain |
| **Cohere Rerank** | 重排序 | Phase 3 Week 4 | BGE Reranker、Voyage Rerank |
| **BGE Reranker** | 开源重排序 | Phase 3 Week 4 | Cohere Rerank |
| **Unstructured** | 文档解析（PDF 等）| Phase 3 Week 3 | LangChain Loaders |

---

## 6. Agent 框架

| 框架 | 出现阶段 | 设计哲学 | 适用场景 |
|------|:-------:|---------|---------|
| **LangGraph** | Phase 4 | 状态机、完全可控 | **生产首选**、复杂工作流 |
| **LangChain Agent** | Phase 4 Week 2 | 封装好的循环 | 快速原型、简单 Agent |
| **CrewAI** | Phase 5 Week 2 | 角色化、易用 | 内容生产、快速 demo |
| **AutoGen** | Phase 5 Week 2 | 对话式、多 Agent | 研究、对话场景 |
| **OpenAI Swarm** | Phase 5 Week 1 | 极简、实验性 | 学习、轻量场景 |
| **OpenAI Agents SDK** | 选学 | 官方一体化 | 2025+ 官方主推 |
| **Mastra**（TS）| 选学 | TS 全栈 | 前端友好、JS 生态 |

**选型口诀：** 先 LangGraph（通用），需角色化用 CrewAI，研究探索用 AutoGen。

---

## 7. 工具生态 / 外部能力

### Web 搜索

| 工具 | 出现阶段 | 免费额度 | 说明 |
|------|:-------:|---------|------|
| **Tavily** | Phase 4 Week 5 | 1000 次/月免费 | **AI 专用搜索**，效果最好 |
| **Brave Search API** | Phase 5 Week 3 | 2000 次/月免费 | 通用、独立搜索引擎 |
| **SerpAPI** | 选学 | 100 次/月免费 | Google 结果抓取 |
| **DuckDuckGo** | Phase 5 Week 3 | 免费（非官方）| 不稳定、限流严 |

### 浏览器自动化

| 工具 | 出现阶段 | 说明 |
|------|:-------:|------|
| **Playwright** | Phase 5 Week 3 | 微软出品，跨浏览器，前端老手最熟 |
| **Browser Use** | Phase 5 Week 3 | AI 原生浏览器控制，2025 黑马 |
| **Anthropic Computer Use** | Phase 5 Week 4 | 截图 + 键鼠，最接近"人操作" |

### 代码执行沙箱

| 工具 | 出现阶段 | 说明 |
|------|:-------:|------|
| **E2B** | Phase 5 Week 3 | **云沙箱首选**，秒级启动 |
| **Daytona** | Phase 5 Week 3 | 类似 E2B，开源可自托管 |
| **Docker** | Phase 5 Week 3 / Phase 6 | 本地沙箱、部署 |

### MCP 生态

| 资源 | 类型 | 出现阶段 |
|------|------|:-------:|
| [官方 Servers](https://github.com/modelcontextprotocol/servers) | 参考实现 | Phase 5 Week 4 |
| [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) | 社区聚合 | Phase 5 Week 4 |
| [Smithery.ai](https://smithery.ai/) | 包管理器 | Phase 5 Week 4 |
| [mcp.so](https://mcp.so/) | 在线 Hub | Phase 5 Week 4 |

---

## 8. 后端 / API

| 工具 | 用途 | 出现阶段 | 替代品 |
|------|------|:-------:|-------|
| **FastAPI** | Python API 框架 | Phase 6 Week 2 | Flask、Litestar、Django Ninja |
| **uvicorn** | ASGI 服务器 | Phase 6 Week 2 | gunicorn + uvicorn worker |
| **Docker** | 容器化 | Phase 6 Week 2 | Podman |
| **PostgreSQL** | 关系型数据库 | Phase 6 | SQLite（学习）、MySQL |
| **Redis** | 缓存 / 队列 | Phase 6（进阶）| Memcached、KeyDB |

---

## 9. 前端 / 全栈

| 工具 | 用途 | 出现阶段 | 替代品 |
|------|------|:-------:|-------|
| **Next.js** | React 全栈框架 | Phase 6 Week 3 | Remix、Nuxt |
| **Vercel AI SDK** | 前端 LLM 集成 | Phase 1 Day 0.5 / Phase 6 Week 3 | 自写 SSE |
| **shadcn/ui** | UI 组件库 | Phase 6 Week 3 | Mantine、Chakra UI |
| **Tailwind CSS** | 原子化 CSS | Phase 6 Week 3 | CSS Modules、styled-components |
| **Zustand** | 状态管理 | Phase 6 Week 3 | Jotai、Redux Toolkit |
| **Jotai** | 原子状态 | Phase 6 Week 3 | Zustand、Recoil |

---

## 10. 部署 / 运维

| 平台 | 出现阶段 | 免费额度 | 适用场景 |
|------|:-------:|---------|---------|
| **Fly.io** | Phase 6 Week 2 | 有限免费 | **个人项目首选**、全球节点、支持长任务 |
| **Railway** | Phase 6 Week 2 | 有限免费 | 易用、自动部署 |
| **Render** | Phase 6 Week 2 | 免费层 | 简单 Demo |
| **Vercel** | Phase 6 Week 3 | 免费层充足 | **前端首选**、边缘部署 |
| **Cloudflare Workers** | 选学 | 免费层 | AI Workers、边缘计算 |
| **阿里云函数计算** | Phase 6 Week 2 | 按量 | 国内项目 |
| **Hugging Face Spaces** | 选学 | 免费层 | AI Demo 托管 |

---

## 11. 监控 / 可观测性

| 工具 | 用途 | 出现阶段 | 替代品 |
|------|------|:-------:|-------|
| **LangSmith** | Agent trace + 评测 | Phase 4+ | Langfuse（开源自托管）|
| **Langfuse** | 开源 trace | 选学 | LangSmith |
| **Sentry** | 错误追踪 | Phase 6 Week 2 | 自建（Sentry 自托管）|
| **Grafana + Prometheus** | 指标监控 | 进阶 | Datadog（贵）|
| **Helicone** | LLM 调用日志 / 成本 | 选学 | 自建代理 |

---

## 选型决策树（快速判断）

### "我要做 RAG，用什么？"
```
学习阶段 → Chroma + OpenAI text-embedding-3-small + LangChain
生产环境 → Qdrant + 同上 + Rerank（Cohere 或 BGE）
已有 PostgreSQL → pgvector + 同上
```

### "我要做 Agent，用什么框架？"
```
第一次做 → LangGraph（学一次受用）
快速 demo / 内容生产 → CrewAI
研究多 Agent 协作 → AutoGen
全 TS 栈 → Mastra
```

### "我要上线，怎么部署？"
```
纯前端 Demo → Vercel
Python 后端 API → Fly.io 或 Railway
国内访问 → 阿里云函数计算
需要 GPU / 长任务 → Fly.io Machines 或 自建
```

### "我怎么知道 Agent 效果好不好？"
```
开发期本地评测 → Promptfoo（CI 友好）
LangChain 项目 → LangSmith
企业团队 → Braintrust
数据敏感 → Phoenix 自托管
RAG 专项 → RAGAS
```

---

## 配套阅读

- 📋 [学习路线总览](./learning-path/README.md) — 各阶段详细安排
- 🚫 [反模式库](./anti-patterns.md) — 18 个真实工程坑
- 🔧 本速查表 — 工具一页全览

> **更新本表：** 发现新工具 / 某个工具过时了，欢迎 PR。每季度建议重审一次（AI 生态变化太快）。
