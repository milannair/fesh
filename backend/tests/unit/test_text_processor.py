"""Tests for app.services.text_processor.TextProcessor"""

import pytest
from app.services.text_processor import TextProcessor


def test_imports():
    """TextProcessor can be imported and has expected methods."""
    assert callable(TextProcessor.extract_from_files)
    assert callable(TextProcessor.split_text)
    assert callable(TextProcessor.preprocess_text)
    assert callable(TextProcessor.get_text_stats)


def test_split_text_delegates():
    chunks = TextProcessor.split_text("Short text.", chunk_size=500)
    assert chunks == ["Short text."]


def test_preprocess_text_normalizes_whitespace():
    raw = "  line1  \r\n\r\n\r\n  line2  \r\n  line3  "
    result = TextProcessor.preprocess_text(raw)
    # Consecutive blank lines collapsed to at most one blank line
    assert "\n\n\n" not in result
    assert "line1" in result
    assert "line2" in result
    assert "line3" in result


def test_preprocess_text_strips_lines():
    raw = "  hello  \n  world  "
    result = TextProcessor.preprocess_text(raw)
    assert result == "hello\nworld"


def test_get_text_stats():
    text = "Hello world\nSecond line"
    stats = TextProcessor.get_text_stats(text)
    assert stats["total_chars"] == len(text)
    assert stats["total_lines"] == 2
    assert stats["total_words"] == 4


def test_extract_from_files(tmp_text_file, tmp_md_file):
    text = TextProcessor.extract_from_files([tmp_text_file, tmp_md_file])
    assert "Document 1" in text
    assert "Hello world" in text
