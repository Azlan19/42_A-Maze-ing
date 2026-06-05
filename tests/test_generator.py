from mazegen.generator import (
    MazeGenerator,
    NORTH,
    EAST,
    SOUTH,
    WEST,
    DIRECTION_DELTA,
)


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


def test_wall_coherence():
    mg = MazeGenerator(6, 5, seed=7)
    mg.generate()
    for y in range(mg.height):
        for x in range(mg.width):
            if x + 1 < mg.width:
                east = bool(mg.grid[y][x] & EAST)
                west = bool(mg.grid[y][x + 1] & WEST)
                assert east == west, (
                    f"Mismatch at ({x},{y}) East={east} "
                    f"vs ({x+1},{y}) West={west}"
                )
            if y + 1 < mg.height:
                south = bool(mg.grid[y][x] & SOUTH)
                north = bool(mg.grid[y + 1][x] & NORTH)
                assert south == north, (
                    f"Mismatch at ({x},{y}) South={south} "
                    f"vs ({x},{y+1}) North={north}"
                )


def test_perfect_maze_full_connectivity():
    """All non-pattern cells must be reachable from entry by BFS."""
    from collections import deque
    mg = MazeGenerator(6, 5, seed=7)
    mg.generate()

    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque([mg.entry])
    visited.add(mg.entry)
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy) in DIRECTION_DELTA.items():
            if not (mg.grid[y][x] & direction):
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    all_cells = {
        (x, y) for y in range(mg.height) for x in range(mg.width)
    }
    reachable = all_cells - mg.pattern_cells
    assert visited == reachable


def test_pattern_embedded_on_large_maze():
    """A maze >=28x14 gets the '42' stamped as sealed obstacles."""
    from collections import deque
    mg = MazeGenerator(30, 16, seed=5)
    mg.generate()

    # The "42" occupies some cells.
    assert len(mg.pattern_cells) > 0
    # Those cells stay fully sealed -- they are walls, not corridors.
    for (px, py) in mg.pattern_cells:
        assert mg.grid[py][px] == 0xF

    # Every non-pattern cell is still reachable: DFS carved around the "42".
    visited: set[tuple[int, int]] = {mg.entry}
    queue: deque[tuple[int, int]] = deque([mg.entry])
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy) in DIRECTION_DELTA.items():
            if not (mg.grid[y][x] & direction):
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    all_cells = {(x, y) for y in range(mg.height) for x in range(mg.width)}
    assert visited == all_cells - mg.pattern_cells


def _count_passages(mg: MazeGenerator) -> int:
    """Count open internal walls (each open wall = one passage)."""
    count = 0
    for y in range(mg.height):
        for x in range(mg.width):
            if x + 1 < mg.width and not (mg.grid[y][x] & EAST):
                count += 1
            if y + 1 < mg.height and not (mg.grid[y][x] & SOUTH):
                count += 1
    return count


def test_imperfect_maze_has_more_passages():
    """PERFECT=False adds extra passages (loops) beyond the spanning tree."""
    perfect = MazeGenerator(10, 10, seed=4, perfect=True)
    perfect.generate()
    imperfect = MazeGenerator(10, 10, seed=4, perfect=False)
    imperfect.generate()
    assert _count_passages(imperfect) > _count_passages(perfect)


def test_external_borders_intact():
    """Border walls must remain closed."""
    mg = MazeGenerator(5, 5, seed=3)
    mg.generate()
    for x in range(mg.width):
        assert mg.grid[0][x] & NORTH, f"Top border open at ({x}, 0)"
    for x in range(mg.width):
        assert mg.grid[mg.height - 1][x] & SOUTH, \
            f"Bottom border open at ({x},{mg.height-1})"
    for y in range(mg.height):
        assert mg.grid[y][0] & WEST, f"Left border open at (0,{y})"
    for y in range(mg.height):
        assert mg.grid[y][mg.width - 1] & EAST, \
            f"Right border open at ({mg.width-1},{y})"
