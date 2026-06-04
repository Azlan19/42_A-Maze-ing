from collections import deque

from mazegen.generator import DIRECTION_DELTA, NORTH, EAST, SOUTH, WEST

_DIRECTION_TO_CHAR: dict[int, str] = {
    NORTH: "N",
    EAST:  "E",
    SOUTH: "S",
    WEST:  "W",
}

def solve(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    width: int,
    height: int
) -> list[str]:
    """Find shortest path from entry to exit using BFS"""

    """Return: List of direction letters or empty list if no path exists"""
    if entry == exit:
        return []

    visited: set[tuple[int, int]] = {entry}
    parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    queue: deque[tuple[int, int]] = deque([entry])

    while queue:
        x, y = queue.popleft()

        if (x, y) == exit:
            return [] # Return path with helper function

    
    for direction, (dx, dy) in DIRECTION_DELTA.items():
        if grid[y][x] & direction:
            continue
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
            visited.add((nx, ny))
            parent[(nx, ny)] = ((x, y), direction)
            queue.append((nx, ny))
    
    return []