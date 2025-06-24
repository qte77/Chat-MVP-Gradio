"""TODO"""

import os
import pytest
from src.gui.gui_builder.gui_file_utils import generate_html_from_md


def test_basic_html_generation(tmp_path):
    """TODO"""
    session_id = "test001"
    md_list = ["# Hello", "This is a *test*."]

    # expected_output_dir = tmp_path / session_id
    # expected_output_file = expected_output_dir / "preview_output.html"

    output_path = generate_html_from_md(session_id, md_list)

    assert os.path.exists(output_path)
    with open(output_path, encoding="utf-8") as f:
        content = f.read()
    assert "<h1>Hello</h1>" in content
    assert "<em>test</em>" in content


def test_empty_markdown_list(tmp_path):
    """TODO"""
    session_id = "empty"
    md_list = []
    output_path = generate_html_from_md(session_id, md_list)

    assert os.path.exists(output_path)
    with open(output_path) as f:
        content = f.read()
    assert content.strip() == "" or "<body>" in content


def test_multiple_markdown_sections():
    """TODO"""
    session_id = "multi"
    md_list = [
        "# Section 1",
        "Content 1.",
        "# Section 2",
        "Content 2 with **bold** text.",
    ]
    output_path = generate_html_from_md(session_id, md_list)
    with open(output_path) as f:
        content = f.read()
    assert "<h1>Section 1</h1>" in content
    assert "<strong>bold</strong>" in content


def test_invalid_session_id_raises(tmp_path):
    """TODO"""
    with pytest.raises(ValueError):
        generate_html_from_md("", ["# Missing session ID"])
