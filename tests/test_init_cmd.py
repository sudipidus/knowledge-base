import pytest
from pathlib import Path
from wiki_cli.commands.init_cmd import run_init


def test_init_creates_directory_structure(tmp_path):
    run_init(tmp_path)
    assert (tmp_path / "schema/SCHEMA.md").exists()
    assert (tmp_path / "schema/templates/entity.md").exists()
    assert (tmp_path / "schema/templates/concept.md").exists()
    assert (tmp_path / "schema/templates/source-summary.md").exists()
    assert (tmp_path / "schema/templates/comparison.md").exists()
    assert (tmp_path / "sources/raw").is_dir()
    assert (tmp_path / "sources/references").is_dir()
    assert (tmp_path / "sources/inbox").is_dir()
    assert (tmp_path / "wiki/index.md").exists()
    assert (tmp_path / "wiki/log.md").exists()
    assert (tmp_path / "wiki/entities").is_dir()
    assert (tmp_path / "wiki/concepts").is_dir()
    assert (tmp_path / "wiki/topics").is_dir()
    assert (tmp_path / "wiki/syntheses").is_dir()
    assert (tmp_path / "wiki/explorations").is_dir()


def test_init_creates_config_files(tmp_path):
    run_init(tmp_path)
    assert (tmp_path / "wiki.yaml").exists()
    assert (tmp_path / ".env.example").exists()
    assert (tmp_path / ".gitignore").exists()


def test_init_gitignore_contents(tmp_path):
    run_init(tmp_path)
    gitignore = (tmp_path / ".gitignore").read_text()
    assert ".env" in gitignore
    assert "public/" in gitignore
    assert ".obsidian/workspace.json" in gitignore


def test_init_does_not_overwrite_existing(tmp_path):
    (tmp_path / "wiki.yaml").write_text("existing: true")
    run_init(tmp_path)
    assert "existing: true" in (tmp_path / "wiki.yaml").read_text()
