"""Tests for app.config.Config"""

import os
import pytest
from unittest.mock import patch


def test_default_base_url():
    from app.config import Config
    assert "openrouter" in Config.LLM_BASE_URL


def test_default_model():
    from app.config import Config
    assert Config.LLM_MODEL_NAME == "openai/gpt-4o-mini"


def test_validate_missing_llm_key():
    from app.config import Config
    original = Config.LLM_API_KEY
    try:
        Config.LLM_API_KEY = None
        errors = Config.validate()
        assert any("LLM_API_KEY" in e for e in errors)
    finally:
        Config.LLM_API_KEY = original


def test_validate_missing_zep_key():
    from app.config import Config
    original = Config.ZEP_API_KEY
    try:
        Config.ZEP_API_KEY = None
        errors = Config.validate()
        assert any("ZEP_API_KEY" in e for e in errors)
    finally:
        Config.ZEP_API_KEY = original


def test_validate_all_set():
    from app.config import Config
    orig_llm = Config.LLM_API_KEY
    orig_zep = Config.ZEP_API_KEY
    try:
        Config.LLM_API_KEY = "test-key"
        Config.ZEP_API_KEY = "test-zep"
        errors = Config.validate()
        assert errors == []
    finally:
        Config.LLM_API_KEY = orig_llm
        Config.ZEP_API_KEY = orig_zep
