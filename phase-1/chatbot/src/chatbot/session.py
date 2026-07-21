"""对话会话管理——维护 messages 数组，支持流式输出。

任务：实现 ChatSession 类，完成以下功能：
1. chat() — 发送消息，普通（非流式）调用
2. stream_chat() — 流式调用，yield 每个文本块
3. clear() — 清空对话历史
4. switch_model() — 切换模型
"""
from __future__ import annotations

from typing import Iterator


class ChatSession:
    """管理一次 LLM 对话的上下文（messages 数组）。"""

    def __init__(self, config) -> None:
        """初始化会话。

        Args:
            config: Config 实例，包含 API Key 和模型配置。
        """
        self.config = config
        self.messages: list[dict] = []

    def chat(self, user_input: str) -> str:
        """发送消息并获取回复（非流式）。

        Args:
            user_input: 用户输入文本。

        Returns:
            LLM 的回复文本。
        """
        # TODO: 实现 OpenAI / Anthropic 调用
        raise NotImplementedError("请实现 chat() 方法")

    def stream_chat(self, user_input: str) -> Iterator[str]:
        """流式发送消息，yield 每个文本块。

        Args:
            user_input: 用户输入文本。

        Yields:
            每个文本块（token 或 chunk）。
        """
        # TODO: 实现流式调用
        raise NotImplementedError("请实现 stream_chat() 方法")

    def clear(self) -> None:
        """清空对话历史。"""
        self.messages = []

    def switch_model(self, model_name: str) -> None:
        """切换模型。

        Args:
            model_name: 模型名称，如 'gpt-5-latest'、'claude-sonnet-4-5-latest'。
        """
        self.config.default_model = model_name
