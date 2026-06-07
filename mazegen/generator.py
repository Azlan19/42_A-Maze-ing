import random

NORTH: int = 1   # bit 0 0001
EAST:  int = 2   # bit 1 0010
SOUTH: int = 4   # bit 2 0100
WEST:  int = 8   # bit 3 1000

# opposite wall on the neighbour
OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

# coordinate change per direction
DIRECTION_DELTA: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),   # up y decreases
    EAST:  (1,  0),   # right x increases
    SOUTH: (0,  1),   # down y increases
    WEST:  (-1, 0),   # left x decreases
}


# 42 pattern bitmaps
_FOUR: list[list[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

_TWO: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]


_DIGIT_W = 3
_DIGIT_H = 5
_GAP = 1                            # gap between 4 and 2
_PATTERN_W = _DIGIT_W * 2 + _GAP   # total width of 42
_PATTERN_H = _DIGIT_H               # total height of 42
_MIN_W = _PATTERN_W + 4             # min maze width
_MIN_H = _PATTERN_H + 4             # min maze height


class MazeGenerator:
    """Generates a 2D maze using a configurable algorithm.

    Args:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        seed: Optional integer seed for reproducibility.
        perfect: If True, one path between any two cells (no loops).
        entry: (x, y) start cell. Defaults to (0, 0) the top-left corner.
        exit: (x, y) end cell. Defaults to (width-1, height-1) bottom-right.
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
        self.entry = entry
        if exit is not None:
            self.exit = exit
        else:
            self.exit = (width - 1, height - 1)

        self.pattern_cells: set[tuple[int, int]] = set()
        self.grid: list[list[int]] = self._fresh_grid()
        self.solution: list[str] = []
        random.seed(self.seed)

    def _fresh_grid(self) -> list[list[int]]:
        grid = []
        for _ in range(self.height):
            grid.append([0xF] * self.width)
        return grid

    def generate(self) -> None:
        """Generate the maze. Populates self.grid and self.pattern_cells."""
        self.grid = self._fresh_grid()
        random.seed(self.seed)

        self._embed_pattern()
        self._carve_dfs()

        # re-seal pattern cells in case a neighbour carved into them
        for px, py in self.pattern_cells:
            self.grid[py][px] = 0xF

        if not self.perfect:
            self._add_loops()

    def _carve_dfs(self) -> None:
        """Carve a perfect maze with an iterative depth-first search.

        Walks from the entry cell, knocking down walls into unvisited
        neighbours, and backtracking (popping the stack) at dead ends.
        """
        visited: set[tuple[int, int]] = set()
        visited.update(self.pattern_cells)  # treat 42 cells as already visited

        # stack tracks the current path from entry to where we are now
        stack: list[tuple[int, int]] = [self.entry]
        visited.add(self.entry)

        directions = list(DIRECTION_DELTA.keys())

        while stack:
            x, y = stack[-1]  # current cell is always the top of the stack
            random.shuffle(directions)
            moved = False
            # try each direction until we find an unvisited neighbour
            for direction in directions:
                dx, dy = DIRECTION_DELTA[direction]
                nx, ny = x + dx, y + dy  # coordinates of the neighbour

                if (
                    0 <= nx < self.width    # neighbour is inside the grid
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited  # neighbour not yet carved
                ):
                    # remove wall on both sides
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~OPPOSITE[direction]
                    visited.add((nx, ny))
                    stack.append((nx, ny))  # move into the neighbour
                    moved = True
                    break  # stop trying directions we already moved

            if not moved:
                stack.pop()  # backtrack

    def _embed_pattern(self) -> None:
        """Mark cells that draw '42' as obstacles. Fills self.pattern_cells.

        Skips silently if the maze is too small to fit the pattern + margin.
        """
        self.pattern_cells = set()
        if self.width < _MIN_W or self.height < _MIN_H:
            print("Error: maze too small for '42' pattern, skipping.")
            return

        # centre the 42 block in the maze
        offset_x = (self.width - _PATTERN_W) // 2
        offset_y = (self.height - _PATTERN_H) // 2

        # stamp each digit, 2 is shifted right by one digit width + gap
        for bitmap, digit_offset_x in [(_FOUR, 0), (_TWO, _DIGIT_W + _GAP)]:
            for row in range(5):
                for col in range(3):
                    if not bitmap[row][col]:
                        continue
                    cx = offset_x + digit_offset_x + col
                    cy = offset_y + row
                    self.pattern_cells.add((cx, cy))

    def _add_loops(self) -> None:
        """Knock down extra walls to turn a perfect maze into a looped one.

        Targets ~10% of the cell count in extra passages, but refuses any
        wall removal that would open up a 3x3 fully-open area (keeps it
        looking like a maze, not a room).
        """
        candidates: list[tuple[int, int, int]] = []  # x y direction
        # scan every cell and collect walls we could knock down
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue  # never touch 42 cells
                # only check east and south to avoid adding each wall twice
                if (x + 1 < self.width
                        and (x + 1, y) not in self.pattern_cells
                        and self.grid[y][x] & EAST):
                    candidates.append((x, y, EAST))
                if (y + 1 < self.height
                        and (x, y + 1) not in self.pattern_cells
                        and self.grid[y][x] & SOUTH):
                    candidates.append((x, y, SOUTH))

        random.shuffle(candidates)  # random order
        target = max(1, (self.width * self.height) // 10)  # 10% of total cells
        removed = 0

        # knock down walls until we hit the target
        for x, y, direction in candidates:
            if removed >= target:
                break
            dx, dy = DIRECTION_DELTA[direction]
            nx, ny = x + dx, y + dy
            if self._would_create_open_area(x, y, nx, ny, direction):
                continue  # skip this wall it would make a room
            self.grid[y][x] &= ~direction
            self.grid[ny][nx] &= ~OPPOSITE[direction]
            removed += 1

    def _would_create_open_area(
        self, x: int, y: int, nx: int, ny: int, direction: int
    ) -> bool:
        """True if removing this wall would create a 3x3 fully-open area."""
        # temporarily remove the wall test then restore
        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

        found = False
        # check both cells touching the removed wall
        for cx, cy in [(x, y), (nx, ny)]:
            # slide a 3x3 window up and down around this cell
            for top in range(cy - 2, cy + 1):
                # slide the window left and right
                for left in range(cx - 2, cx + 1):
                    if self._is_open_3x3(left, top):
                        found = True
                        break  # no need to check more positions
                if found:
                    break
            if found:
                break  # no need to check the second cell

        self.grid[y][x] |= direction
        self.grid[ny][nx] |= OPPOSITE[direction]
        return found

    def _is_open_3x3(self, left: int, top: int) -> bool:
        """True if the 3x3 block at (left, top) has no internal walls."""
        right = left + 2
        bottom = top + 2
        if left < 0 or top < 0 or right >= self.width or bottom >= self.height:
            return False

        # check no east walls horizontally
        for row in range(top, bottom + 1):
            for col in range(left, right):
                if self.grid[row][col] & EAST:
                    return False
        # check no south walls vertically
        for row in range(top, bottom):
            for col in range(left, right + 1):
                if self.grid[row][col] & SOUTH:
                    return False
        return True
