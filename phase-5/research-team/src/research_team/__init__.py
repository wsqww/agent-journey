"""自动化研究团队 — 作品集项目 #2。

Multi-Agent 架构（Supervisor 模式）：
    Planner → Researcher × N → Writer → Reviewer ↔ Critic → Editor

核心流程：
    用户问题 → Planner 分解 → 并行 Researcher 搜索
    → Writer 综合 → Reviewer 审校 → Editor 定稿

Phase 5（完整版）：LangGraph 实现，多 Agent 协作
Phase 6（打磨）：FastAPI + Next.js + 成本面板上线

启动方式：
    cd phase-5/research-team
    uv sync
    uv run python -m research_team
"""
