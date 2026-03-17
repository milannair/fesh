"""Tests for app.services.ontology_generator.OntologyGenerator"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_llm():
    """Create a mock LLMClient instance."""
    with patch("app.services.ontology_generator.LLMClient") as MockCls:
        mock_instance = MagicMock()
        MockCls.return_value = mock_instance
        yield mock_instance


def _valid_ontology():
    """Minimal valid ontology result."""
    return {
        "entity_types": [
            {"name": f"Type{i}", "description": f"Type {i} desc", "attributes": [], "examples": []}
            for i in range(8)
        ] + [
            {"name": "Person", "description": "Fallback person", "attributes": [], "examples": []},
            {"name": "Organization", "description": "Fallback org", "attributes": [], "examples": []},
        ],
        "edge_types": [
            {"name": "WORKS_FOR", "description": "Works for relationship", "source_targets": [], "attributes": []}
        ],
        "analysis_summary": "Test summary",
    }


def test_generate_calls_llm(mock_llm):
    mock_llm.chat_json.return_value = _valid_ontology()

    from app.services.ontology_generator import OntologyGenerator
    gen = OntologyGenerator(llm_client=mock_llm)
    result = gen.generate(
        document_texts=["Some text about a topic."],
        simulation_requirement="Simulate social media reactions",
    )

    mock_llm.chat_json.assert_called_once()
    assert "entity_types" in result
    assert "edge_types" in result


def test_validate_adds_fallback_types(mock_llm):
    from app.services.ontology_generator import OntologyGenerator
    gen = OntologyGenerator(llm_client=mock_llm)

    # Ontology missing Person and Organization
    ontology = {
        "entity_types": [
            {"name": "Student", "description": "A student", "attributes": [], "examples": []},
            {"name": "Professor", "description": "A professor", "attributes": [], "examples": []},
        ],
        "edge_types": [],
    }

    result = gen._validate_and_process(ontology)

    names = [e["name"] for e in result["entity_types"]]
    assert "Person" in names
    assert "Organization" in names


def test_entity_type_limit(mock_llm):
    from app.services.ontology_generator import OntologyGenerator
    gen = OntologyGenerator(llm_client=mock_llm)

    # Ontology with 12 entity types and no fallbacks
    ontology = {
        "entity_types": [
            {"name": f"Type{i}", "description": f"Desc {i}", "attributes": [], "examples": []}
            for i in range(12)
        ],
        "edge_types": [],
    }

    result = gen._validate_and_process(ontology)

    # After adding fallbacks and capping, should not exceed 10
    assert len(result["entity_types"]) <= 10
    names = [e["name"] for e in result["entity_types"]]
    assert "Person" in names
    assert "Organization" in names
