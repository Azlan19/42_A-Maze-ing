import os
# import pytest
from output import write_output


def test_output_format(tmp_path):
    # 2x2 grid, hand-crafted
    grid = [[0xF, 0x6], [0x9, 0xF]]
    fname = str(tmp_path / "maze.txt")
    write_output(grid, (0, 0), (1, 1), ["E", "S"], fname)

    with open(fname) as f:
        lines = f.read().split("\n")

    assert lines[0] == "F6"
    assert lines[1] == "9F"
    assert lines[2] == ""
    assert lines[3] == "0,0"
    assert lines[4] == "1,1"
    assert lines[5] == "ES"


def test_empty_path(tmp_path):
    grid = [[0xF]]
    fname = str(tmp_path / "maze.txt")
    write_output(grid, (0, 0), (0, 0), [], fname)
    with open(fname) as f:
        lines = f.read().split("\n")
    assert lines[5] == ""


def test_output_file_created(tmp_path):
    fname = str(tmp_path / "output.txt")
    write_output([[0xA]], (0, 0), (0, 0), [], fname)
    assert os.path.exists(fname)
