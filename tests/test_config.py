import pytest
from config import parse_config, MazeConfig


def test_valid_config(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=10\nHEIGHT=8\nENTRY=0,0\nEXIT=9,7\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=True\nSEED=42\n"
    )
    cfg = parse_config(str(cfg_file))
    assert cfg.width == 10
    assert cfg.height == 8
    assert cfg.entry == (0, 0)
    assert cfg.exit == (9, 7)
    assert cfg.output_file == "maze.txt"
    assert cfg.perfect is True
    assert cfg.seed == 42


def test_comments_ignored(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "# This is a comment\nWIDTH=5\nHEIGHT=5\n"
        "ENTRY=0,0\nEXIT=4,4\nOUTPUT_FILE=out.txt\nPERFECT=False\n"
    )
    cfg = parse_config(str(cfg_file))
    assert cfg.width == 5
    assert cfg.seed is None


def test_missing_key_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text("WIDTH=5\nHEIGHT=5\nENTRY=0,0\nEXIT=4,4\nPERFECT=True\n")
    with pytest.raises(ValueError, match="OUTPUT_FILE"):
        parse_config(str(cfg_file))


def test_entry_out_of_bounds_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=5\nHEIGHT=5\nENTRY=0,99\nEXIT=4,4\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    )
    with pytest.raises(ValueError, match="ENTRY"):
        parse_config(str(cfg_file))


def test_entry_equals_exit_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=5\nHEIGHT=5\nENTRY=2,2\nEXIT=2,2\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    )
    with pytest.raises(ValueError, match="different"):
        parse_config(str(cfg_file))


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        parse_config("nonexistent.txt")