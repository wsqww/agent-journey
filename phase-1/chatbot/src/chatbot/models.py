"""Pydantic 数据模型定义。

任务：
1. 定义 MarkdownDocument — 解析后的文档结构
2. 定义 ChatMessage — 对话消息结构
3. 定义 ToolCall — Function Calling 的工具调用结构

说明：
    这些模型在 Phase 1 Week 5（结构化输出）和 Phase 3（Function Calling）会被大量复用，
    这里先给出基础定义，后续阶段会扩展（如增加 ToolResult、StructuredReply 等）。
"""

from typing import Literal

from pydantic import BaseModel, Field


class MarkdownDocument(BaseModel):
    """Markdown 解析结果的数据模型。"""

    title: str | None = Field(default=None, description="文档标题（首个 # 标题）")
    sections: list[str] = Field(default_factory=list, description="各级标题列表")
    code_blocks: list[str] = Field(default_factory=list, description="代码块内容")
    links: list[str] = Field(default_factory=list, description="链接 URL")
    word_count: int = Field(default=0, ge=0, description="字数统计，不能为负")


class ChatMessage(BaseModel):
    """单条对话消息。

    role 取值与 OpenAI/Anthropic 统一：system / user / assistant / tool。
    """

    role: Literal["system", "user", "assistant", "tool"] = Field(description="消息角色")
    content: str = Field(description="消息内容")
    name: str | None = Field(default=None, description="tool 角色时的工具名，可选")


class ToolCall(BaseModel):
    """LLM 工具调用的结构化表示。

    对应 OpenAI 的 tool_calls 和 Anthropic 的 tool_use block，
    这里抽象成统一结构，方便后续 Agent 逻辑处理。
    """

    id: str = Field(description="工具调用唯一 ID，用于把结果回传给 LLM")
    name: str = Field(description="工具名称")
    arguments: dict[str, object] = Field(default_factory=dict, description="调用参数")
    result: str | None = Field(default=None, description="工具返回结果（执行后填充）")
