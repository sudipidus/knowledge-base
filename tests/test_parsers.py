import pytest
from pathlib import Path
from wiki_cli.parsers import detect_parser
from wiki_cli.parsers.text import TextParser
from wiki_cli.parsers.base import ParseResult


def test_text_parser_reads_markdown(tmp_path):
    md_file = tmp_path / "notes.md"
    md_file.write_text("# My Notes\n\nSome content here.")
    parser = TextParser()
    result = parser.parse(str(md_file))
    assert result.content == "# My Notes\n\nSome content here."
    assert result.title == "My Notes"
    assert result.source_type == "text"


def test_text_parser_plain_text(tmp_path):
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("Just plain text.")
    parser = TextParser()
    result = parser.parse(str(txt_file))
    assert result.content == "Just plain text."
    assert result.source_type == "text"


def test_detect_parser_url():
    parser = detect_parser("https://example.com/article")
    assert parser.__class__.__name__ == "WebParser"


def test_detect_parser_pdf(tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    parser = detect_parser(str(pdf))
    assert parser.__class__.__name__ == "PDFParser"


def test_detect_parser_markdown(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# test")
    parser = detect_parser(str(md))
    assert parser.__class__.__name__ == "TextParser"


def test_parse_result_content_hash():
    result = ParseResult(content="hello", title="test", source_type="text")
    assert result.content_hash.startswith("sha256:")
    assert len(result.content_hash) > 10
