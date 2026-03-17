"""Tests for app.utils.llm_client.LLMClient"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_config():
    """Patch Config with test defaults."""
    with patch("app.utils.llm_client.Config") as cfg:
        cfg.LLM_API_KEY = "cfg-api-key"
        cfg.LLM_BASE_URL = "https://cfg.example.com/v1"
        cfg.LLM_MODEL_NAME = "cfg-model"
        cfg.OPENROUTER_HTTP_REFERER = ""
        cfg.OPENROUTER_X_TITLE = ""
        yield cfg


@pytest.fixture
def mock_openai(mock_config):
    """Patch the OpenAI class used inside llm_client."""
    with patch("app.utils.llm_client.OpenAI") as MockOpenAI:
        yield MockOpenAI


def _make_response(content, finish_reason="stop"):
    """Helper: build a mock chat completion response."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    choice.finish_reason = finish_reason
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ── constructor tests ──────────────────────────────────────────────

def test_init_uses_config_defaults(mock_openai, mock_config):
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    assert client.api_key == "cfg-api-key"
    assert client.base_url == "https://cfg.example.com/v1"
    assert client.model == "cfg-model"


def test_init_raises_without_api_key(mock_openai, mock_config):
    mock_config.LLM_API_KEY = None
    from app.utils.llm_client import LLMClient
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        LLMClient(api_key=None)


def test_openrouter_headers_set(mock_openai, mock_config):
    mock_config.OPENROUTER_HTTP_REFERER = "https://example.com"
    mock_config.OPENROUTER_X_TITLE = "TestApp"
    from app.utils.llm_client import LLMClient
    LLMClient()
    call_kwargs = mock_openai.call_args[1]
    assert call_kwargs["default_headers"]["HTTP-Referer"] == "https://example.com"
    assert call_kwargs["default_headers"]["X-Title"] == "TestApp"


def test_openrouter_headers_not_set_when_empty(mock_openai, mock_config):
    mock_config.OPENROUTER_HTTP_REFERER = ""
    mock_config.OPENROUTER_X_TITLE = ""
    from app.utils.llm_client import LLMClient
    LLMClient()
    call_kwargs = mock_openai.call_args[1]
    assert call_kwargs["default_headers"] is None


# ── chat() tests ───────────────────────────────────────────────────

def test_chat_returns_content(mock_openai, mock_config):
    mock_openai.return_value.chat.completions.create.return_value = _make_response("hello")
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    result = client.chat([{"role": "user", "content": "hi"}])
    assert result == "hello"


def test_chat_strips_think_tags(mock_openai, mock_config):
    raw = "<think>reasoning</think>actual content"
    mock_openai.return_value.chat.completions.create.return_value = _make_response(raw)
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    result = client.chat([{"role": "user", "content": "hi"}])
    assert result == "actual content"


# ── chat_json() tests ─────────────────────────────────────────────

def test_chat_json_returns_dict(mock_openai, mock_config):
    mock_openai.return_value.chat.completions.create.return_value = _make_response('{"key": "value"}')
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    result = client.chat_json([{"role": "user", "content": "give json"}])
    assert result == {"key": "value"}


def test_chat_json_strips_markdown_fences(mock_openai, mock_config):
    raw = '```json\n{"key": "value"}\n```'
    mock_openai.return_value.chat.completions.create.return_value = _make_response(raw)
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    result = client.chat_json([{"role": "user", "content": "give json"}])
    assert result == {"key": "value"}


def test_chat_json_raises_on_invalid_json(mock_openai, mock_config):
    mock_openai.return_value.chat.completions.create.return_value = _make_response("not json")
    from app.utils.llm_client import LLMClient
    client = LLMClient()
    with pytest.raises(ValueError, match="Invalid JSON"):
        client.chat_json([{"role": "user", "content": "give json"}])
