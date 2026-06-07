from mazegen.solver import solve
from mazegen.generator import EAST, WEST, SOUTH, NORTH


def _make_grid(rows: int, cols: int) -> list[list[int]]:
    """All walls closed."""
    return [[0xF] * cols for _ in range(rows)]


def test_adjacent_cells_east():
    grid = _make_grid(1, 2)
    grid[0][0] &= ~EAST
    grid[0][1] &= ~WEST
    path = solve(grid, (0, 0), (1, 0), 2, 1)
    assert path == ["E"]


def test_adjacent_cells_south():
    grid = _make_grid(2, 1)
    grid[0][0] &= ~SOUTH
    grid[1][0] &= ~NORTH
    path = solve(grid, (0, 0), (0, 1), 1, 2)
    assert path == ["S"]


def test_two_step_path():
    # 1x3 corridor going East
    grid = _make_grid(1, 3)
    grid[0][0] &= ~EAST
    grid[0][1] &= ~WEST
    grid[0][1] &= ~EAST
    grid[0][2] &= ~WEST
    path = solve(grid, (0, 0), (2, 0), 3, 1)
    assert path == ["E", "E"]


def test_no_path_returns_empty():
    grid = _make_grid(2, 2)
    # All walls closed — no passage possible
    path = solve(grid, (0, 0), (1, 1), 2, 2)
    assert path == []


def test_same_start_and_end():
    grid = _make_grid(3, 3)
    path = solve(grid, (1, 1), (1, 1), 3, 3)
    assert path == []


def test_path_is_navigable():
    """Walk the returned path and verify we reach exit."""
    from mazegen.generator import MazeGenerator, DIRECTION_DELTA
    mg = MazeGenerator(8, 8, seed=99)
    mg.generate()
    path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)

    CHAR_TO_DIR = {"N": NORTH, "E": EAST, "S": SOUTH, "W": WEST}
    x, y = mg.entry
    for step in path:
        dx, dy = DIRECTION_DELTA[CHAR_TO_DIR[step]]
        x, y = x + dx, y + dy
    assert (x, y) == mg.exit
