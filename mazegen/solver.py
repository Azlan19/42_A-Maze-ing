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

