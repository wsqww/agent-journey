"""对话会话管理——维护 messages 数组，支持流式输出。

这是 ChatSession 的**参考实现**，对应 daily plan Week 4 Day 2（多轮对话）+ Day 4（流式输出）。
你可以先自己写一遍，再回来对照；也可以直接用这份代码把 CLI 跑起来，边读边学。

核心设计：
    - 用一个 messages 列表维护完整多轮对话（前端类比：useState 的数组）
    - 通过 provider 字符串分发到 OpenAI / Anthropic（前端类比：策略模式 / Provider Pattern）
    - 流式用 Python 生成器（前端类比：AsyncGenerator + yield）
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Protocol, cast

from chatbot.config import Config

# messages 用 Mapping[str, str] / Sequence[...] 而非 dict/list，
# 以兼容 OpenAI/Anthropic SDK 的复杂联合类型——既保证类型安全，
# 又避免在初学者代码里塞一堆 SDK 内部类型。


class _LLMClient(Protocol):
    """LLM 客户端的最小接口定义，便于 mock 和类型提示。"""

    def chat(self, messages: Sequence[Mapping[str, str]]) -> str: ...
    def stream_chat(self, messages: Sequence[Mapping[str, str]]) -> Iterator[str]: ...


def _is_anthropic(model_name: str) -> bool:
    """通过模型名前缀判断是否走 Anthropic 协议。"""
    return model_name.lower().startswith("claude")


class OpenAIProvider(_LLMClient):
    """OpenAI 调用封装。把 SDK 细节隔离在这一层，Session 只关心 messages。"""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        """延迟导入 openai：避免没装 SDK 时整个模块 import 失败（也便于测试 mock）。"""
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        # 延迟导入：让单元测试不强制安装 openai
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)

    def chat(self, messages: Sequence[Mapping[str, str]]) -> str:
        """非流式调用：一次性返回完整回复。"""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=list(messages),  # type: ignore[arg-type]  # SDK 期望复杂联合类型，这里简化用 dict
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        return response.choices[0].message.content or ""

    def stream_chat(self, messages: Sequence[Mapping[str, str]]) -> Iterator[str]:
        """流式调用：yield 每个文本块（SSE 协议在 SDK 层已解析）。"""
        # stream=True 时 SDK 返回 Iterable[ChatCompletionChunk]，
        # 但 mypy 对 create() 的重载推断会把它跟非流式签名混淆，这里显式断言。
        stream = cast(
            "Iterator[object]",
            self._client.chat.completions.create(
                model=self._model,
                messages=list(messages),  # type: ignore[arg-type]  # 同上
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                stream=True,
            ),
        )
        for chunk in stream:
            # chunk.choices 可能为空（如最后一个 [DONE] 包），需要防御
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            content = getattr(delta, "content", None)
            if content:  # None 表示中间帧没有文本
                yield content


class AnthropicProvider(_LLMClient):
    """Anthropic 调用封装。

    注意 Anthropic 与 OpenAI 的 API 结构差异：
        - system 是顶层参数，不混在 messages 里
        - messages 数组里只有 user / assistant
        - 流式用 .messages.stream() 上下文管理器
    """

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)

    @staticmethod
    def _split_system(messages: Sequence[Mapping[str, str]]) -> tuple[str, list[dict[str, str]]]:
        """把 system 消息从 messages 数组里抽出来。

        OpenAI 把 system 放在 messages 开头，Anthropic 用独立参数——这里做转换。
        """
        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        rest = [
            {"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"
        ]
        return "\n\n".join(system_parts), rest

    def chat(self, messages: Sequence[Mapping[str, str]]) -> str:
        """非流式调用。"""
        system, rest = self._split_system(messages)
        response = self._client.messages.create(
            model=self._model,
            system=system,
            messages=rest,  # type: ignore[arg-type]  # SDK 期望 MessageParam 联合，这里简化用 dict
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        # Anthropic 的 content 是 list[Block]，文本块取 .text
        return "".join(getattr(block, "text", "") for block in response.content)

    def stream_chat(self, messages: Sequence[Mapping[str, str]]) -> Iterator[str]:
        """流式调用：text_stream 已经把事件流拼成了文本块，直接 yield。"""
        system, rest = self._split_system(messages)
        with self._client.messages.stream(
            model=self._model,
            system=system,
            messages=rest,  # type: ignore[arg-type]  # 同上
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        ) as stream:
            yield from stream.text_stream


class ChatSession:
    """管理一次 LLM 对话的上下文（messages 数组）。

    前端类比：这个类就像一个聊天 store——维护 messages state，
    暴露 chat/stream_chat 两个 action，clear/switch_model 是工具方法。
    """

    def __init__(self, config: Config) -> None:
        """初始化会话，懒加载对应 Provider。

        Args:
            config: Config 实例，包含 API Key 和模型配置。
        """
        self.config = config
        self.messages: list[dict[str, str]] = []
        self._provider: _LLMClient | None = None  # 懒加载，切换 model 时重置

    def _get_provider(self) -> _LLMClient:
        """根据当前 model 名返回（或重建）Provider 实例。

        切换 model 时会重建，确保新 Provider 用新的 model/api_key。
        """
        if self._provider is not None:
            return self._provider

        model = self.config.default_model
        if _is_anthropic(model):
            provider: _LLMClient = AnthropicProvider(
                api_key=self.config.require_anthropic(),
                model=model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
        else:
            provider = OpenAIProvider(
                api_key=self.config.require_openai(),
                model=model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
        self._provider = provider
        return provider

    def chat(self, user_input: str) -> str:
        """发送消息并获取回复（非流式）。

        Args:
            user_input: 用户输入文本。

        Returns:
            LLM 的回复文本。

        Side effect: 把 user/assistant 两条消息追加到 self.messages。
        """
        self.messages.append({"role": "user", "content": user_input})
        reply = self._get_provider().chat(self.messages)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def stream_chat(self, user_input: str) -> Iterator[str]:
        """流式发送消息，yield 每个文本块。

        注意：messages 只在生成器**开始迭代时**才追加 assistant 完整内容，
        这样流式中途失败时不会污染历史。

        Args:
            user_input: 用户输入文本。

        Yields:
            每个文本块（token 或 chunk）。
        """
        self.messages.append({"role": "user", "content": user_input})
        collected: list[str] = []

        for chunk in self._get_provider().stream_chat(self.messages):
            collected.append(chunk)
            yield chunk

        # 流式结束后，把完整回复落回 messages（保证下次调用上下文完整）
        self.messages.append({"role": "assistant", "content": "".join(collected)})

    def clear(self) -> None:
        """清空对话历史。同时重置 Provider，下次调用时按当前 model 重建。"""
        self.messages = []
        self._provider = None

    def switch_model(self, model_name: str) -> None:
        """切换模型。

        Args:
            model_name: 模型名称，如 'gpt-5-latest'、'claude-sonnet-4-5-latest'。
        """
        self.config.default_model = model_name
        self._provider = None  # 强制下次 _get_provider 重建
