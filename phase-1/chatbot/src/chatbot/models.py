"""Pydantic 数据模型定义。

任务：
1. 定义 MarkdownDocument — 解析后的文档结构
2. 定义 ChatMessage — 对话消息结构
3. 定义 ToolCall — Function Calling 的工具调用结构
"""
from pydantic import BaseModel, Field


class MarkdownDocument(BaseModel):
    """Markdown 解析结果的数据模型。"""
    title: str | None = Field(default=None, description="文档标题（首个 # 标题）")
    sections: list[str] = Field(default_factory=list, description="各级标题列表")
    code_blocks: list[str] = Field(default_factory=list, description="代码块内容")
    links: list[str] = Field(default_factory=list, description="链接 URL")
    word_count: int = Field(default=0, description="字数统计")


class ChatMessage(BaseModel):
    """单条对话消息。"""
    role: str = Field(description="system / user / assistant / tool")
    content: str = Field(description="消息内容")


class ToolCall(BaseModel):
    """LLM 工具调用的结构化表示。"""
    name: str = Field(description="工具名称")
    arguments: dict = Field(default_factory=dict, description="调用参数")
    result: str | None = Field(default=None, description="工具返回结果")
