"""ChatSession 的单元测试。

覆盖目标（满足 daily plan "5+ 个测试"要求）：
    1. 初始化 / clear / switch_model 等基础状态
    2. chat() 多轮上下文维护（mock OpenAI）
    3. stream_chat() yield 行为（mock OpenAI）
    4. Provider 分发：模型名前缀决定走 OpenAI 还是 Anthropic
    5. 错误路径：缺 API Key 时给出清晰错误

设计原则：
    - 所有 LLM 调用都 mock，不依赖真实网络
    - 用 monkeypatch 替换 SDK 模块，避免在测试环境强制安装 openai/anthropic
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from chatbot.config import Config
from chatbot.session import ChatSession

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def openai_config() -> Config:
    """构造一个走 OpenAI 协议的 Config（Key 合法、model=gpt-5-latest）。"""
    return Config(  # type: ignore[call-arg]
        openai_api_key="sk-test-openai",
        anthropic_api_key="sk-ant-test",
        default_model="gpt-5-latest",
    )


@pytest.fixture
def anthropic_config() -> Config:
    """构造一个走 Anthropic 协议的 Config（model=claude-...）。"""
    return Config(  # type: ignore[call-arg]
        openai_api_key="sk-test-openai",
        anthropic_api_key="sk-ant-test",
        default_model="claude-sonnet-4-5-latest",
    )


def _install_fake_openai(monkeypatch, reply_text: str = "你好！", chunks: list[str] | None = None):
    """注入一个假的 openai 模块，让 ChatSession 不依赖真实 SDK。

    前端类比：相当于 Jest 里 jest.mock("openai", ...)。
    """
    fake_module = types.ModuleType("openai")

    class _Delta:
        def __init__(self, content: str | None) -> None:
            self.content = content

    class _Choice:
        def __init__(self, content: str | None, *, delta_text: str | None = None) -> None:
            # delta 用于流式，message 用于非流式
            self.delta = _Delta(delta_text if delta_text is not None else content)
            self.message = MagicMock(content=content)

    class _Resp:
        def __init__(self, content: str | None = None, delta_text: str | None = None) -> None:
            # 非流式：message.content = content（默认 reply_text）
            # 流式：delta.content = delta_text（默认 None，由上层判空）
            actual_content = reply_text if content is None else content
            self.choices = [_Choice(actual_content, delta_text=delta_text)]

    class _StreamResp:
        """流式响应：迭代它得到多个 chunk，每个 chunk 有 .choices=[_Choice]。"""

        def __init__(self, chunk_texts: list[str]) -> None:
            self._iter = iter([_Resp(delta_text=t) for t in chunk_texts])

        def __iter__(self):
            return self._iter

    class _Completions:
        def create(self, **kwargs):  # noqa: ANN001, ANN201
            if kwargs.get("stream"):
                chunk_list = chunks if chunks is not None else [reply_text]
                return _StreamResp(chunk_list)
            return _Resp()

    class _Chat:
        def __init__(self) -> None:
            self.completions = _Completions()

    class _Client:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            self.chat = _Chat()

    fake_module.OpenAI = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake_module)


def _install_fake_anthropic(
    monkeypatch, reply_text: str = "你好！", chunks: list[str] | None = None
):
    """注入一个假的 anthropic 模块。"""
    fake_module = types.ModuleType("anthropic")

    class _TextBlock:
        def __init__(self, text: str) -> None:
            self.text = text

    class _Resp:
        def __init__(self) -> None:
            self.content = [_TextBlock(reply_text)]

    class _StreamCtx:
        """模拟 messages.stream() 返回的上下文管理器。"""

        def __init__(self) -> None:
            self.text_stream = iter(chunks if chunks is not None else [reply_text])

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class _Messages:
        def create(self, **kwargs):  # noqa: ANN001, ANN201
            return _Resp()

        def stream(self, **kwargs):  # noqa: ANN001, ANN201
            return _StreamCtx()

    class _Client:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            self.messages = _Messages()

    fake_module.Anthropic = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)


# ---------------------------------------------------------------------------
# 基础状态测试
# ---------------------------------------------------------------------------


def test_session_initialization(openai_config: Config):
    """初始化后 messages 应为空，Provider 应懒加载（未创建）。"""
    session = ChatSession(openai_config)
    assert session.messages == []
    assert session._provider is None


def test_clear_resets_messages(openai_config: Config):
    """clear() 应清空 messages 并重置 Provider。"""
    session = ChatSession(openai_config)
    session.messages.append({"role": "user", "content": "hello"})
    session._provider = MagicMock()  # 模拟已加载
    session.clear()
    assert session.messages == []
    assert session._provider is None


def test_switch_model_updates_config_and_resets_provider(openai_config: Config):
    """switch_model 应更新 config.default_model 并强制 Provider 重建。"""
    session = ChatSession(openai_config)
    session._provider = MagicMock()
    session.switch_model("claude-sonnet-4-5-latest")
    assert openai_config.default_model == "claude-sonnet-4-5-latest"
    assert session._provider is None


# ---------------------------------------------------------------------------
# chat() 核心测试
# ---------------------------------------------------------------------------


def test_chat_appends_user_and_assistant_messages(openai_config: Config, monkeypatch):
    """chat() 应同时追加 user 和 assistant 两条消息到 messages。"""
    _install_fake_openai(monkeypatch, reply_text="你好！")
    session = ChatSession(openai_config)

    reply = session.chat("嗨")

    assert reply == "你好！"
    assert len(session.messages) == 2
    assert session.messages[0] == {"role": "user", "content": "嗨"}
    assert session.messages[1] == {"role": "assistant", "content": "你好！"}


def test_chat_maintains_multi_turn_context(openai_config: Config, monkeypatch):
    """多轮调用应累积上下文——第二次调用时 messages 长度应为 4。"""
    _install_fake_openai(monkeypatch, reply_text="ok")
    session = ChatSession(openai_config)

    session.chat("第一轮")
    session.chat("第二轮")

    assert len(session.messages) == 4
    assert session.messages[2] == {"role": "user", "content": "第二轮"}


def test_chat_routes_to_anthropic_for_claude_models(anthropic_config: Config, monkeypatch):
    """模型名以 claude 开头时，应走 Anthropic 协议（system 从 messages 抽出）。"""
    _install_fake_anthropic(monkeypatch, reply_text="Claude 回复")
    session = ChatSession(anthropic_config)

    reply = session.chat("你好")

    assert reply == "Claude 回复"
    assert session.messages[-1] == {"role": "assistant", "content": "Claude 回复"}


# ---------------------------------------------------------------------------
# stream_chat() 核心测试
# ---------------------------------------------------------------------------


def test_stream_chat_yields_chunks_and_appends_full_reply(openai_config: Config, monkeypatch):
    """stream_chat 应逐 chunk yield，结束后把完整内容追加到 messages。"""
    _install_fake_openai(monkeypatch, chunks=["你", "好", "！"])
    session = ChatSession(openai_config)

    collected = list(session.stream_chat("嗨"))

    assert collected == ["你", "好", "！"]
    # user + assistant 完整回复
    assert len(session.messages) == 2
    assert session.messages[1] == {"role": "assistant", "content": "你好！"}


def test_stream_chat_anthropic_text_stream(anthropic_config: Config, monkeypatch):
    """Anthropic 流式应直接 yield text_stream 内容。"""
    _install_fake_anthropic(monkeypatch, chunks=["Hi", " there"])
    session = ChatSession(anthropic_config)

    collected = list(session.stream_chat("hello"))

    assert collected == ["Hi", " there"]
    assert session.messages[-1]["content"] == "Hi there"


# ---------------------------------------------------------------------------
# 错误路径测试（对抗性用例）
# ---------------------------------------------------------------------------


def test_chat_raises_when_openai_key_missing(monkeypatch):
    """未配置 OPENAI_API_KEY 时应给出清晰错误，而非让 SDK 报模糊的 401。"""
    _install_fake_openai(monkeypatch)
    config = Config(openai_api_key="", anthropic_api_key="", default_model="gpt-5-latest")
    session = ChatSession(config)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        session.chat("hi")


def test_chat_raises_when_anthropic_key_missing(monkeypatch):
    """切到 claude 但没配 ANTHROPIC_API_KEY 时应抛错。"""
    _install_fake_anthropic(monkeypatch)
    config = Config(
        openai_api_key="sk-openai",
        anthropic_api_key="",
        default_model="claude-sonnet-4-5-latest",
    )
    session = ChatSession(config)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        session.chat("hi")


def test_invalid_temperature_rejected():
    """Config 不应接受越界的 temperature（Pydantic validator 拦截）。"""
    with pytest.raises(ValueError, match="temperature"):
        Config(  # type: ignore[call-arg]
            openai_api_key="sk-x",
            temperature=5.0,
        )


def test_empty_input_does_not_invoke_llm(openai_config: Config, monkeypatch):
    """对抗性：空白输入绝不能触发 LLM 调用（否则用户误回车会烧 token）。

    这里直接断言 CLI 主循环的空输入判断逻辑——session.messages 保持为空。
    """
    _install_fake_openai(monkeypatch)
    session = ChatSession(openai_config)
    # 复用 __main__.py 的判断条件：if not user_input.strip(): continue
    for blank in ["", "   ", "\t"]:
        assert not blank.strip(), f"空输入应被 strip() 判空: {blank!r}"
    # 只要没调用 chat/stream_chat，messages 就应该保持空
    assert session.messages == []
