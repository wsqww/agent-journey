"""Prompt 模式手册 — Phase 2 产出物。

目录：
    patterns/    — 每种 Prompt 模式的文档（zero-shot / few-shot / cot / react / defense）
    templates/   — 可复用的 Python 提示词模板
    evals/       — 评测集和评测脚本
    prompts/     — 不同版本的 Prompt 文件（v1.md, v2.md, v3.md）

使用方式：
    cd phase-2/prompt-handbook
    uv sync
    uv run python -c "from templates.classification import classify; ..."
"""
