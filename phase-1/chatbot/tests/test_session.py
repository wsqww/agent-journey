""""测试 ChatSession 的 mock 示例。

任务：为 session.py 中的 ChatSession 写至少 5 个测试。
提示：用 unittest.mock.patch 模拟 OpenAI/Anthropic 的 API 调用。
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_config():
    """创建模拟的 Config 对象。"""
    config = MagicMock()
    config.openai_api_key = "sk-test"
    config.default_model = "gpt-5-latest"
    return config


def test_session_initialization(mock_config):
    """测试 ChatSession 初始化后 messages 为空。"""
    from chatbot.session import ChatSession

    session = ChatSession(mock_config)
    assert session.messages == []


def test_clear_resets_messages(mock_config):
    """测试 clear() 清空对话历史。"""
    from chatbot.session import ChatSession

    session = ChatSession(mock_config)
    session.messages.append({"role": "user", "content": "hello"})
    session.clear()
    assert session.messages == []


def test_switch_model_updates_config(mock_config):
    """测试 switch_model() 更新模型名称。"""
    from chatbot.session import ChatSession

    session = ChatSession(mock_config)
    session.switch_model("claude-sonnet-4-5-latest")
    assert mock_config.default_model == "claude-sonnet-4-5-latest"


# TODO: 补充以下测试
# - test_chat_with_mock_openai — mock OpenAI 调用，验证返回内容
# - test_stream_chat_yields_chunks — mock 流式调用，验证 yield 行为
