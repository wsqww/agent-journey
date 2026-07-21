"""研究助手 Agent — Phase 4 产出物（LangGraph 版）。

LangGraph 工作流：
    Planner → Researcher → Synthesizer → Reviewer
                          ↑                   │
                          └── 不通过，回 Researcher

核心概念（前端类比）：
    State   ~ useState / useReducer 的 state
    Node    ~ 状态转换函数（接收 State，返回 Update）
    Edge    ~ 节点间的连线
    CondEdge ~ 条件分支（类似 if/switch）

Phase 4（雏形）：CLI 版，节点清晰、有 trace
Phase 5（升级）：Multi-Agent 版（分角色协作）
Phase 6（打磨）：FastAPI + Next.js 上线

启动方式：
    cd phase-4/research-agent
    uv sync
    uv run python -m research_agent
"""
