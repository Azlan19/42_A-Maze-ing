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