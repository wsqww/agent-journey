# CLI 聊天机器人（Phase 1 参考实现）

> 这是 Phase 1 的**参考实现**，对应 daily plan 的 Week 4（LLM API）+ Week 5（结构化输出）。
>
> **给学习者的建议：** 推荐你先按 daily plan 自己写一遍，卡住了再回来看这份代码。
> 直接复制粘贴跑通 ≠ 学会，但读一份可运行的参考代码比看零散的片段更容易建立整体感。

## 功能

- ✅ 多轮对话（维护 messages 数组）
- ✅ 流式输出（打字机效果，逐字打印）
- ✅ 多 Provider 支持（OpenAI / Anthropic，通过模型名前缀自动分发）
- ✅ 切换模型：`/model claude-sonnet-4-5-latest`
- ✅ 清空对话：`/clear`
- ✅ API Key 缺失时给出清晰错误，而非让 SDK 报模糊的 401
- ✅ 彩色命令行输出（用 `rich`）
- 🧪 12 个单元测试，覆盖正常流程 + 错误路径

## 快速开始

```bash
cd phase-1/chatbot
cp .env.example .env  # 填入真实 API Key
uv sync
uv run python -m chatbot
```

## 目录结构

```
chatbot/
├── pyproject.toml
├── .env.example
├── README.md                    # 本文件
├── src/chatbot/
│   ├── __init__.py
│   ├── __main__.py              # CLI 入口（主循环 + 命令分发）
│   ├── config.py                # Pydantic Settings 配置 + Key 校验
│   ├── session.py               # ChatSession 核心（Provider 分发 + 流式）
│   └── models.py                # 数据模型（Week 5 结构化输出复用）
└── tests/
    └── test_session.py          # 12 个测试
```

## 设计要点（面试可讲）

| 设计点 | 选择 | 理由 |
|--------|------|------|
| Provider 分发 | 通过模型名前缀（`claude*` → Anthropic）| 避免引入额外配置项，开箱即用 |
| SDK 导入 | 延迟 import（在 Provider `__init__` 里）| 测试时可 mock，未装 SDK 也能 import 模块 |
| 流式与 messages | 流式结束后才把完整回复 append | 流式中途失败不污染历史，下次调用可重试 |
| 配置校验 | `require_openai()` / `require_anthropic()` | 尽早失败，错误信息比 SDK 的 401 清晰 |
| 错误处理 | CLI 顶层 try/except 兜底 | 一次请求失败不应崩溃整个会话 |

## 测试

```bash
uv run pytest -v
```

测试全部用 `monkeypatch` 注入假的 `openai` / `anthropic` 模块，**不依赖网络也不需要真实 API Key**——可以在 CI 里零成本运行。

## 下一步（Week 5 之后）

参考实现目前只到 Week 4 的"聊天机器人 v1"。Week 5 的"v2（结构化输出）"建议你在 `models.py` 的基础上自己扩展：
- 加 `_translate / _summarize / _sentiment` 三个结构化指令方法
- 用 `response_format=PydanticModel` 约束输出
- 加 tenacity 重试 + 自修复 Prompt
