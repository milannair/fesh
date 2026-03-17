"""Tests for app.utils.file_parser"""

import os
import pytest
from app.utils.file_parser import FileParser, split_text_into_chunks


def test_extract_text_txt(tmp_text_file):
    text = FileParser.extract_text(tmp_text_file)
    assert "Hello world" in text
    assert "test document" in text


def test_extract_text_md(tmp_md_file):
    text = FileParser.extract_text(tmp_md_file)
    assert "# Test" in text
    assert "markdown test document" in text


def test_extract_text_unsupported(tmp_path):
    f = tmp_path / "bad.docx"
    f.write_text("fake docx content")
    with pytest.raises(ValueError, match="Unsupported file format"):
        FileParser.extract_text(str(f))


def test_extract_text_missing_file():
    with pytest.raises(FileNotFoundError):
        FileParser.extract_text("/nonexistent/path/file.txt")


def test_split_text_short():
    text = "Short text."
    chunks = split_text_into_chunks(text, chunk_size=500)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_split_text_long():
    # Build a string of 2000 characters (using sentences to be realistic)
    sentence = "This is a test sentence that is roughly fifty characters. "
    text = sentence * 40  # ~2360 chars
    chunks = split_text_into_chunks(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1
    # Every chunk should be non-empty
    for chunk in chunks:
        assert len(chunk) > 0


def test_split_text_empty():
    chunks = split_text_into_chunks("")
    assert chunks == []


def test_extract_from_multiple(tmp_text_file, tmp_md_file):
    text = FileParser.extract_from_multiple([tmp_text_file, tmp_md_file])
    assert "Document 1" in text
    assert "Document 2" in text
    assert "Hello world" in text
    assert "markdown test document" in text
