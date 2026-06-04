import pytest
from mazegen.generator import MazeGenerator, NORTH, EAST, SOUTH, WEST


def test_init_default_exit():
    mg = MazeGenerator(5, 4, seed=1)
    assert mg.width == 5
    assert mg.height == 4
    assert mg.entry == (0, 0)
    assert mg.exit == (4, 3)


def test_init_custom_entry_exit():
    mg = MazeGenerator(10, 8, seed=1, entry=(1, 0), exit=(8, 7))
    assert mg.entry == (1, 0)
    assert mg.exit == (8, 7)


def test_grid_shape_before_generate():
    mg = MazeGenerator(5, 4, seed=1)
    assert len(mg.grid) == 4
    assert all(len(row) == 5 for row in mg.grid)
    assert mg.grid[0][0] == 0xF
