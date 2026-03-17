"""Tests for app.services.simulation_config_generator.SimulationConfigGenerator"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.simulation_config_generator import (
    SimulationConfigGenerator,
    TimeSimulationConfig,
)


@pytest.fixture
def generator():
    """Create a SimulationConfigGenerator with a mocked LLMClient."""
    with patch("app.services.simulation_config_generator.LLMClient") as MockLLM:
        mock_instance = MagicMock()
        mock_instance.model = "test-model"
        MockLLM.return_value = mock_instance
        gen = SimulationConfigGenerator(api_key="fake-key")
        yield gen


# ── _fix_truncated_json ───────────────────────────────────────────

def test_fix_truncated_json_closes_brackets(generator):
    truncated = '{"agents": [{"id": 1}, {"id": 2}'
    fixed = generator._fix_truncated_json(truncated)
    # Should close unclosed brackets
    assert fixed.count('{') == fixed.count('}')
    assert fixed.count('[') == fixed.count(']')
    import json
    parsed = json.loads(fixed)
    assert "agents" in parsed


def test_fix_truncated_json_already_valid(generator):
    valid = '{"key": "value"}'
    fixed = generator._fix_truncated_json(valid)
    import json
    parsed = json.loads(fixed)
    assert parsed == {"key": "value"}


# ── _parse_time_config ────────────────────────────────────────────

def test_parse_time_config_valid(generator):
    raw = {
        "total_simulation_hours": 48,
        "minutes_per_round": 60,
        "agents_per_hour_min": 3,
        "agents_per_hour_max": 15,
        "peak_hours": [20, 21, 22],
        "off_peak_hours": [0, 1, 2, 3],
        "morning_hours": [7, 8],
        "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],
    }
    config = generator._parse_time_config(raw, num_entities=30)
    assert isinstance(config, TimeSimulationConfig)
    assert config.total_simulation_hours == 48
    assert config.agents_per_hour_min == 3
    assert config.agents_per_hour_max == 15


def test_parse_time_config_exceeds_agents(generator):
    raw = {
        "agents_per_hour_min": 100,
        "agents_per_hour_max": 200,
    }
    config = generator._parse_time_config(raw, num_entities=20)
    # Values should be corrected down
    assert config.agents_per_hour_min <= 20
    assert config.agents_per_hour_max <= 20
    assert config.agents_per_hour_min < config.agents_per_hour_max


# ── _get_default_time_config ──────────────────────────────────────

def test_default_time_config(generator):
    result = generator._get_default_time_config(num_entities=30)
    assert result["total_simulation_hours"] == 72
    assert result["minutes_per_round"] == 60
    assert "peak_hours" in result
    assert "off_peak_hours" in result
    assert "morning_hours" in result
    assert "work_hours" in result
    assert result["agents_per_hour_min"] >= 1
    assert result["agents_per_hour_max"] >= result["agents_per_hour_min"]
