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
# Why NORTH = (0, -1) and not (0, 1)? In a 2D list, grid[0] is the top row,
# so moving North means going to a SMALLER row index. Lock this in now --
# it trips up almost everyone.


# --- "42" pattern bitmaps ---------------------------------------------------
# Each digit is a 5x5 pixel drawing. 1 = solid block, 0 = empty.
# You can read the shapes straight out of the 1s.

# "4"
_FOUR: list[list[int]] = [
    [1, 0, 1, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
]

# "2"
_TWO: list[list[int]] = [
    [1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1],
]

# Each bitmap pixel is scaled into a _SCALE x _SCALE block of maze cells so the
# "42" is big enough to read in the rendered maze.
_SCALE = 2                          # cells per bitmap pixel
_DIGIT_W = 5 * _SCALE               # 10 cells wide per digit
_DIGIT_H = 5 * _SCALE               # 10 cells tall per digit
_GAP = 4                            # blank cells between "4" and "2"
_PATTERN_W = _DIGIT_W * 2 + _GAP    # 24 cells wide for the whole "42"
_PATTERN_H = _DIGIT_H               # 10 cells tall
_MIN_W = _PATTERN_W + 4             # 28 = min maze width to fit "42" + margin
_MIN_H = _PATTERN_H + 4             # 14 = min maze height to fit "42" + margin


class MazeGenerator:
    """Generates a 2D maze using a configurable algorithm.

    Args:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        seed: Optional integer seed for reproducibility.
        perfect: If True, one path between any two cells (no loops).
        entry: (x, y) start cell. Defaults to (0, 0) — the top-left corner.
        exit: (x, y) end cell. Defaults to (width-1, height-1) — bottom-right.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect
        self.seed = seed

        # Where the maze starts and ends.
        # exit defaults to None in the signature, so resolve it here:
        # the bottom-right corner is (width-1, height-1).
        self.entry = entry
        self.exit = exit if exit is not None else (width - 1, height - 1)

        # Cells occupied by the "42" drawing. Filled during generate().
        self.pattern_cells: set[tuple[int, int]] = set()

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

    def generate(self) -> None:
        """Generate the maze. Populates self.grid and self.pattern_cells."""
        # Start fresh: every cell sealed (all four walls up).
        self.grid = [
            [0xF for _ in range(self.width)]
            for _ in range(self.height)
        ]
        # Seed the RNG here so each generate() call is reproducible.
        random.seed(self.seed)

        # Mark the "42" cells as obstacles before carving.
        self._embed_pattern()

        # Carve passages with depth-first search (tunnels around the "42").
        self._carve_dfs()

        # Safety pass: force every pattern cell back to fully sealed, in case
        # a neighbour carved a wall that touches it.
        for px, py in self.pattern_cells:
            self.grid[py][px] = 0xF

        # For an imperfect maze, knock down extra walls to create loops.
        if not self.perfect:
            self._add_loops()

    def _carve_dfs(self) -> None:
        """Carve a perfect maze with an iterative depth-first search.

        Walks from the entry cell, knocking down walls into unvisited
        neighbours, and backtracking (popping the stack) at dead ends.
        """
        visited: set[tuple[int, int]] = set()
        # Treat any "42" pattern cells as already visited so DFS never
        # carves into them. (Empty until _embed_pattern is implemented.)
        visited.update(self.pattern_cells)

        # The stack holds the path from entry to the current cell.
        stack: list[tuple[int, int]] = [self.entry]
        visited.add(self.entry)

        directions = list(DIRECTION_DELTA.keys())

        while stack:
            x, y = stack[-1]            # current cell = top of the stack
            random.shuffle(directions)  # try the four directions randomly

            moved = False
            for direction in directions:
                dx, dy = DIRECTION_DELTA[direction]
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                ):
                    # Knock down the shared wall on BOTH cells.
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~OPPOSITE[direction]
                    visited.add((nx, ny))
                    stack.append((nx, ny))  # step forward
                    moved = True
                    break

            if not moved:
                stack.pop()                 # dead end -> back up

    def _embed_pattern(self) -> None:
        """Mark cells that draw '42' as obstacles. Fills self.pattern_cells.

        Skips silently if the maze is too small to fit the pattern + margin.
        """
        self.pattern_cells = set()
        if self.width < _MIN_W or self.height < _MIN_H:
            print("Warning: maze too small for '42' pattern, skipping.")
            return

        # Centre the whole "42" block inside the maze.
        offset_x = (self.width - _PATTERN_W) // 2
        offset_y = (self.height - _PATTERN_H) // 2

        # Stamp each digit. The "2" starts one digit-width + gap to the right.
        for bitmap, digit_offset_x in [(_FOUR, 0), (_TWO, _DIGIT_W + _GAP)]:
            for row in range(5):
                for col in range(5):
                    if not bitmap[row][col]:
                        continue
                    # Scale this 1 pixel up into a _SCALE x _SCALE block.
                    for sr in range(_SCALE):
                        for sc in range(_SCALE):
                            cx = offset_x + digit_offset_x + col * _SCALE + sc
                            cy = offset_y + row * _SCALE + sr
                            self.pattern_cells.add((cx, cy))

    def _add_loops(self) -> None:
        """Knock down extra walls to turn a perfect maze into a looped one.

        Targets ~10% of the cell count in extra passages, but refuses any
        wall removal that would open up a 3x3 fully-open area (keeps it
        looking like a maze, not a room).
        """
        # Gather every still-closed wall between two non-obstacle cells.
        candidates: list[tuple[int, int, int]] = []  # (x, y, direction)
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if (x + 1 < self.width
                        and (x + 1, y) not in self.pattern_cells
                        and self.grid[y][x] & EAST):
                    candidates.append((x, y, EAST))
                if (y + 1 < self.height
                        and (x, y + 1) not in self.pattern_cells
                        and self.grid[y][x] & SOUTH):
                    candidates.append((x, y, SOUTH))

        random.shuffle(candidates)
        target = max(1, (self.width * self.height) // 10)
        removed = 0

        for x, y, direction in candidates:
            if removed >= target:
                break
            dx, dy = DIRECTION_DELTA[direction]
            nx, ny = x + dx, y + dy
            if self._would_create_open_area(x, y, nx, ny, direction):
                continue
            self.grid[y][x] &= ~direction
            self.grid[ny][nx] &= ~OPPOSITE[direction]
            removed += 1

    def _would_create_open_area(
        self, x: int, y: int, nx: int, ny: int, direction: int
    ) -> bool:
        """True if removing this wall would create a 3x3 fully-open area."""
        # Tentatively remove the wall, test, then restore it.
        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

        found = False
        for cx, cy in [(x, y), (nx, ny)]:
            for top in range(cy - 2, cy + 1):
                for left in range(cx - 2, cx + 1):
                    if self._is_open_3x3(left, top):
                        found = True
                        break
                if found:
                    break
            if found:
                break

        self.grid[y][x] |= direction
        self.grid[ny][nx] |= OPPOSITE[direction]
        return found

    def _is_open_3x3(self, left: int, top: int) -> bool:
        """True if the 3x3 block at (left, top) has no internal walls."""
        right = left + 2
        bottom = top + 2
        if left < 0 or top < 0 or right >= self.width or bottom >= self.height:
            return False

        # No East walls between horizontally-adjacent cells in the block.
        for row in range(top, bottom + 1):
            for col in range(left, right):
                if self.grid[row][col] & EAST:
                    return False
        # No South walls between vertically-adjacent cells in the block.
        for row in range(top, bottom):
            for col in range(left, right + 1):
                if self.grid[row][col] & SOUTH:
                    return False
        return True
