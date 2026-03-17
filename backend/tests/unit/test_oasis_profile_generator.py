"""Tests for app.services.oasis_profile_generator"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.oasis_profile_generator import OasisAgentProfile


@pytest.fixture
def generator():
    """Create an OasisProfileGenerator with mocked LLMClient and Zep."""
    with patch("app.services.oasis_profile_generator.LLMClient") as MockLLM, \
         patch("app.services.oasis_profile_generator.Zep"):
        mock_llm = MagicMock()
        MockLLM.return_value = mock_llm
        from app.services.oasis_profile_generator import OasisProfileGenerator
        gen = OasisProfileGenerator(api_key="fake-key", zep_api_key="fake-zep")
        yield gen


# ── _normalize_gender ─────────────────────────────────────────────

class TestNormalizeGender:
    def test_male(self, generator):
        assert generator._normalize_gender("male") == "male"

    def test_female(self, generator):
        assert generator._normalize_gender("female") == "female"

    def test_male_uppercase(self, generator):
        assert generator._normalize_gender("Male") == "male"

    def test_other(self, generator):
        assert generator._normalize_gender("other") == "other"

    def test_chinese_male(self, generator):
        assert generator._normalize_gender("\u7537") == "male"

    def test_chinese_female(self, generator):
        assert generator._normalize_gender("\u5973") == "female"

    def test_none(self, generator):
        assert generator._normalize_gender(None) == "other"

    def test_unknown_string(self, generator):
        assert generator._normalize_gender("nonbinary") == "other"


# ── _generate_username ────────────────────────────────────────────

def test_generate_username_non_empty(generator):
    username = generator._generate_username("John Doe")
    assert len(username) > 0
    assert "john" in username.lower()


def test_generate_username_special_chars(generator):
    username = generator._generate_username("Dr. Jane O'Brien")
    assert len(username) > 0
    # Should only contain alphanumeric and underscores
    base = username.rsplit("_", 1)[0]  # strip random suffix
    assert all(c.isalnum() or c == '_' for c in base)


# ── OasisAgentProfile dataclass ───────────────────────────────────

def test_profile_dataclass_defaults():
    profile = OasisAgentProfile(
        user_id=1,
        user_name="test_user",
        name="Test User",
        bio="A test bio",
        persona="A test persona",
    )
    assert profile.user_id == 1
    assert profile.karma == 1000
    assert profile.friend_count == 100
    assert profile.follower_count == 150
    assert profile.statuses_count == 500
    assert profile.age is None
    assert profile.gender is None
    assert profile.interested_topics == []


def test_profile_to_dict():
    profile = OasisAgentProfile(
        user_id=42,
        user_name="alice",
        name="Alice",
        bio="bio",
        persona="persona",
        age=25,
        gender="female",
    )
    d = profile.to_dict()
    assert d["user_id"] == 42
    assert d["name"] == "Alice"
    assert d["age"] == 25
    assert d["gender"] == "female"


def test_profile_to_twitter_format():
    profile = OasisAgentProfile(
        user_id=1,
        user_name="bob",
        name="Bob",
        bio="bio",
        persona="persona",
    )
    tw = profile.to_twitter_format()
    assert tw["username"] == "bob"
    assert "friend_count" in tw
    assert "follower_count" in tw


def test_profile_to_reddit_format():
    profile = OasisAgentProfile(
        user_id=2,
        user_name="carol",
        name="Carol",
        bio="bio",
        persona="persona",
    )
    rd = profile.to_reddit_format()
    assert rd["username"] == "carol"
    assert "karma" in rd
