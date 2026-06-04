import random

# Wall bit flags — each wall is one bit in the cell's integer value
NORTH: int = 1   # bit 0 — 0001
EAST:  int = 2   # bit 1 — 0010
SOUTH: int = 4   # bit 2 — 0100
WEST:  int = 8   # bit 3 — 1000


# When moving in a direction, what's the opposite wall on the neighbour?
# If I go East into a neighbour, that neighbour's West wall is what I crossed.
OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

# Moving in a direction changes your coordinates by (dx, dy)
DIRECTION_DELTA: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),   # North = up = y decreases
    EAST:  (1,  0),   # East  = right = x increases
    SOUTH: (0,  1),   # South = down = y increases
    WEST:  (-1, 0),   # West  = left = x decreases
}
# Why NORTH = (0, -1) and not (0, 1)? Because in a 2D list, grid[0] is the top row.
# Moving North means going to a smaller row index. This trips up almost everyone — just lock it in now.


class MazeGenerator:
    """Generates a 2D maze using a configurable algorithm.

    Args:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        seed: Optional integer seed for reproducibility.
        perfect: If True, generate a perfect maze (one path between any two cells).
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect
        self.seed = seed

        # This is the maze. A 2D list of integers.
        # grid[row][col] — grid[0][0] is top-left.
        # Every cell starts with ALL FOUR walls closed (value 0xF = 15).
        self.grid: list[list[int]] = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]

        # We'll store the solution path here after generation.
        self.solution: list[str] = []

        # Seed the random number generator for reproducibility.
        # If seed is None, random.seed(None) uses system time — still works.
        random.seed(self.seed)

    def print_grid_raw(self) -> None:
        """Print the raw hex values of the grid. For debugging only."""
        for row in self.grid:
            print(" ".join(f"{cell:X}" for cell in row))
