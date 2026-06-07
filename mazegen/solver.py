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
    """Find shortest path from entry to exit using BFS

    Return: List of direction letters or empty list if no path exists"""
    if entry == exit:
        return []

    # Tracks which cells have been seen
    visited: set[tuple[int, int]] = {entry}
    # Maps each cell to (the cell we came from, the direction we took)
    parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    queue: deque[tuple[int, int]] = deque([entry])  # Start with the entry cell

    while queue:
        x, y = queue.popleft()  # Processes 1 cell at a time from the beginning

        if (x, y) == exit:
            # Return path with helper function
            return _reconstruct_path(parent, entry, exit)

        for direction, (dx, dy) in DIRECTION_DELTA.items():
            if grid[y][x] & direction:  # If wall, continue
                continue
            nx, ny = x + dx, y + dy  # set neighbour coordinates
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = ((x, y), direction)
                    # Added to the back of the queue to be processed
                    queue.append((nx, ny))

    return []


def _reconstruct_path(
    parent: dict[tuple[int, int], tuple[tuple[int, int], int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> list[str]:
    path: list[str] = []
    cell = exit

    while cell != entry:
        prev_cell, direction = parent[cell]
        path.append(_DIRECTION_TO_CHAR[direction])
        cell = prev_cell

    path.reverse()
    return path
