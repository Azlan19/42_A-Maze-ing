# A-Maze-ing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Python 3.10+ maze generator that reads a config file, generates a maze with DFS, embeds a "42" pattern, writes hex output, renders in the terminal, and ships the core as a pip package.

**Architecture:** Approach B — clean 4-module split. `mazegen/` is the pip-installable library (generator + solver). `config.py`, `output.py`, `display.py`, and `a_maze_ing.py` are the application layer. Person 1 owns `mazegen/`; Person 2 owns the application layer and can stub Person 1's interface from day one.

**Tech Stack:** Python 3.10+, pytest, flake8, mypy, setuptools/wheel (build), ANSI escape codes (display)

---

## File Map

| File | Responsibility |
|------|---------------|
| `mazegen/generator.py` | `MazeGenerator` class — DFS, "42" embed, wall constants |
| `mazegen/solver.py` | `solve()` — BFS shortest path, pure function |
| `mazegen/__init__.py` | Exports `MazeGenerator` and `solve` |
| `config.py` | `MazeConfig` dataclass + `parse_config()` |
| `output.py` | `write_output()` — hex file writer |
| `display.py` | `render()` — ASCII terminal renderer + ANSI colors |
| `a_maze_ing.py` | Main entry point + interactive menu loop |
| `pyproject.toml` | Package build config for `mazegen-1.0.0.whl` |
| `Makefile` | install / run / debug / clean / lint targets |
| `config.txt` | Default configuration file |
| `tests/test_config.py` | Config parser tests |
| `tests/test_generator.py` | DFS generation, wall coherence, connectivity |
| `tests/test_solver.py` | BFS path tests |
| `tests/test_output.py` | Output file format tests |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `requirements.txt`
- Create: `config.txt`
- Create: `tests/__init__.py`
- Modify: `mazegen/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "mazegen"
version = "1.0.0"
requires-python = ">=3.10"
description = "Reusable maze generator (DFS) with BFS solver"

[tool.setuptools.packages.find]
include = ["mazegen*"]
```

- [ ] **Step 2: Create `Makefile`**

```makefile
.PHONY: install run debug clean lint lint-strict

install:
	pip install -r requirements.txt

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	       --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
```

- [ ] **Step 3: Create `requirements.txt`**

```
flake8>=6.0
mypy>=1.0
pytest>=7.0
build>=0.10
```

- [ ] **Step 4: Create default `config.txt`**

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

- [ ] **Step 5: Create `tests/__init__.py`** (empty file)

- [ ] **Step 6: Update `mazegen/__init__.py`**

```python
from mazegen.generator import MazeGenerator
from mazegen.solver import solve

__all__ = ["MazeGenerator", "solve"]
```

- [ ] **Step 7: Install dependencies and verify**

```bash
pip install -r requirements.txt
python3 -c "from mazegen import MazeGenerator; print('OK')"
```
Expected: `OK`

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml Makefile requirements.txt config.txt tests/__init__.py mazegen/__init__.py
git commit -m "chore: project scaffolding, Makefile, pyproject.toml"
```

---

## Task 2: Config Parser

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_config.py`:

```python
import pytest
from config import parse_config, MazeConfig


def test_valid_config(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=10\nHEIGHT=8\nENTRY=0,0\nEXIT=9,7\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=True\nSEED=42\n"
    )
    cfg = parse_config(str(cfg_file))
    assert cfg.width == 10
    assert cfg.height == 8
    assert cfg.entry == (0, 0)
    assert cfg.exit == (9, 7)
    assert cfg.output_file == "maze.txt"
    assert cfg.perfect is True
    assert cfg.seed == 42


def test_comments_ignored(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "# This is a comment\nWIDTH=5\nHEIGHT=5\n"
        "ENTRY=0,0\nEXIT=4,4\nOUTPUT_FILE=out.txt\nPERFECT=False\n"
    )
    cfg = parse_config(str(cfg_file))
    assert cfg.width == 5
    assert cfg.seed is None


def test_missing_key_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text("WIDTH=5\nHEIGHT=5\nENTRY=0,0\nEXIT=4,4\nPERFECT=True\n")
    with pytest.raises(ValueError, match="OUTPUT_FILE"):
        parse_config(str(cfg_file))


def test_entry_out_of_bounds_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=5\nHEIGHT=5\nENTRY=0,99\nEXIT=4,4\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    )
    with pytest.raises(ValueError, match="ENTRY"):
        parse_config(str(cfg_file))


def test_entry_equals_exit_raises(tmp_path):
    cfg_file = tmp_path / "config.txt"
    cfg_file.write_text(
        "WIDTH=5\nHEIGHT=5\nENTRY=2,2\nEXIT=2,2\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    )
    with pytest.raises(ValueError, match="different"):
        parse_config(str(cfg_file))


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        parse_config("nonexistent.txt")
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_config.py -v
```
Expected: `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Implement `config.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


@dataclass
class MazeConfig:
    """Validated maze generation configuration."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int]


def parse_config(path: str) -> MazeConfig:
    """Parse and validate a KEY=VALUE config file.

    Args:
        path: Path to the config file.

    Returns:
        A validated MazeConfig instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If any required key is missing or has an invalid value.
    """
    raw: dict[str, str] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid config line: {line!r}")
            key, _, value = line.partition("=")
            raw[key.strip()] = value.strip()

    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        key = next(iter(sorted(missing)))
        raise ValueError(f"Missing required key '{key}'")

    try:
        width = int(raw["WIDTH"])
        height = int(raw["HEIGHT"])
    except ValueError:
        raise ValueError("WIDTH and HEIGHT must be integers")
    if width < 1 or height < 1:
        raise ValueError("WIDTH and HEIGHT must be positive integers")

    entry = _parse_coord(raw["ENTRY"], "ENTRY", width, height)
    exit_ = _parse_coord(raw["EXIT"], "EXIT", width, height)
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different cells")

    perfect_str = raw["PERFECT"].lower()
    if perfect_str not in ("true", "false"):
        raise ValueError("PERFECT must be 'True' or 'False'")
    perfect = perfect_str == "true"

    seed: Optional[int] = None
    if "SEED" in raw:
        try:
            seed = int(raw["SEED"])
        except ValueError:
            raise ValueError("SEED must be an integer")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=raw["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
    )


def _parse_coord(
    value: str, key: str, width: int, height: int
) -> tuple[int, int]:
    """Parse and bounds-check a 'x,y' coordinate string."""
    try:
        parts = value.split(",")
        x, y = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise ValueError(f"{key} must be in 'x,y' format")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"{key} ({x},{y}) is outside maze bounds {width}x{height}"
        )
    return (x, y)
```

- [ ] **Step 4: Run tests — all must pass**

```bash
pytest tests/test_config.py -v
```
Expected: 6 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: config parser with full validation"
```

---

## Task 3: Complete MazeGenerator Interface

**Files:**
- Modify: `mazegen/generator.py`
- Create: `tests/test_generator.py`

- [ ] **Step 1: Write failing tests for the generator interface**

Create `tests/test_generator.py`:

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_generator.py -v
```
Expected: FAILED — `MazeGenerator.__init__` doesn't accept `entry`/`exit` yet

- [ ] **Step 3: Update `MazeGenerator.__init__` in `mazegen/generator.py`**

Replace the entire file with:

```python
"""Maze generation using iterative Recursive Backtracker (DFS)."""
from __future__ import annotations
import random
from typing import Optional

# Wall bit flags — each wall is one bit in the cell's integer value
NORTH: int = 1   # bit 0 — 0001
EAST:  int = 2   # bit 1 — 0010
SOUTH: int = 4   # bit 2 — 0100
WEST:  int = 8   # bit 3 — 1000

# When moving in a direction, the opposite wall on the neighbour
OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

# Moving in a direction changes coordinates by (dx, dy)
DIRECTION_DELTA: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),   # up → smaller row index
    EAST:  (1,  0),
    SOUTH: (0,  1),   # down → larger row index
    WEST:  (-1, 0),
}

# "4" pixel bitmap (5 wide × 5 tall), 1=solid wall cell
_FOUR: list[list[int]] = [
    [1, 0, 1, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
]

# "2" pixel bitmap (5 wide × 5 tall), 1=solid wall cell
_TWO: list[list[int]] = [
    [1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1],
]

_SCALE = 2           # cells per bitmap pixel
_DIGIT_W = 5 * _SCALE   # 10 cells wide per digit
_DIGIT_H = 5 * _SCALE   # 10 cells tall per digit
_GAP = 4                # cells between "4" and "2"
_PATTERN_W = _DIGIT_W * 2 + _GAP   # 24 cells wide total
_PATTERN_H = _DIGIT_H               # 10 cells tall
_MIN_W = _PATTERN_W + 4             # 28 minimum maze width
_MIN_H = _PATTERN_H + 4             # 14 minimum maze height


class MazeGenerator:
    """Generates a 2D maze using iterative Recursive Backtracker (DFS).

    Args:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        seed: Optional integer seed for reproducibility.
        perfect: If True, generate a perfect maze (unique path between any two cells).
        entry: (x, y) start cell. Defaults to (0, 0).
        exit: (x, y) end cell. Defaults to (width-1, height-1).
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
        perfect: bool = True,
        entry: tuple[int, int] = (0, 0),
        exit: Optional[tuple[int, int]] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect
        self.seed = seed
        self.entry = entry
        self.exit = exit if exit is not None else (width - 1, height - 1)
        self.pattern_cells: set[tuple[int, int]] = set()

        # grid[row][col]; 0xF = all walls closed
        self.grid: list[list[int]] = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]

    def print_grid_raw(self) -> None:
        """Print raw hex values for debugging."""
        for row in self.grid:
            print(" ".join(f"{cell:X}" for cell in row))

    def generate(self) -> None:
        """Generate the maze. Populates self.grid and self.pattern_cells."""
        pass  # implemented in Task 4
```

- [ ] **Step 4: Run tests — all must pass**

```bash
pytest tests/test_generator.py -v
```
Expected: 3 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add mazegen/generator.py tests/test_generator.py
git commit -m "feat: MazeGenerator interface with entry/exit params and pattern constants"
```

---

## Task 4: DFS Maze Generation (Perfect Maze)

**Files:**
- Modify: `mazegen/generator.py` — implement `generate()` and `_carve_dfs()`

- [ ] **Step 1: Add wall coherence test to `tests/test_generator.py`**

```python
def test_wall_coherence():
    mg = MazeGenerator(6, 5, seed=7)
    mg.generate()
    for y in range(mg.height):
        for x in range(mg.width):
            if x + 1 < mg.width:
                east = bool(mg.grid[y][x] & EAST)
                west = bool(mg.grid[y][x + 1] & WEST)
                assert east == west, (
                    f"Mismatch at ({x},{y}) East={east} vs ({x+1},{y}) West={west}"
                )
            if y + 1 < mg.height:
                south = bool(mg.grid[y][x] & SOUTH)
                north = bool(mg.grid[y + 1][x] & NORTH)
                assert south == north, (
                    f"Mismatch at ({x},{y}) South={south} vs ({x},{y+1}) North={north}"
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


def test_external_borders_intact():
    """Border walls must remain closed (except entry/exit cells which are internal)."""
    mg = MazeGenerator(5, 5, seed=3)
    mg.generate()
    # Top row: North walls closed
    for x in range(mg.width):
        assert mg.grid[0][x] & NORTH, f"Top border open at ({x}, 0)"
    # Bottom row: South walls closed
    for x in range(mg.width):
        assert mg.grid[mg.height - 1][x] & SOUTH, f"Bottom border open at ({x},{mg.height-1})"
    # Left column: West walls closed
    for y in range(mg.height):
        assert mg.grid[y][0] & WEST, f"Left border open at (0,{y})"
    # Right column: East walls closed
    for y in range(mg.height):
        assert mg.grid[y][mg.width - 1] & EAST, f"Right border open at ({mg.width-1},{y})"
```

- [ ] **Step 2: Run tests — confirm new tests fail**

```bash
pytest tests/test_generator.py::test_wall_coherence tests/test_generator.py::test_perfect_maze_full_connectivity -v
```
Expected: FAILED — `generate()` is a no-op

- [ ] **Step 3: Implement `generate()` and `_carve_dfs()` in `mazegen/generator.py`**

Replace the `generate` method stub and add `_carve_dfs`:

```python
    def generate(self) -> None:
        """Generate the maze. Populates self.grid and self.pattern_cells."""
        # Reset grid to all walls closed
        self.grid = [[0xF for _ in range(self.width)] for _ in range(self.height)]
        random.seed(self.seed)

        # Embed "42" pattern (sets self.pattern_cells)
        self._embed_pattern()

        # Run DFS
        self._carve_dfs()

        # Force pattern cells back to fully closed (safety pass)
        for px, py in self.pattern_cells:
            self.grid[py][px] = 0xF

        # Add loops for imperfect maze
        if not self.perfect:
            self._add_loops()

    def _carve_dfs(self) -> None:
        """Iterative DFS to carve a spanning tree through non-obstacle cells."""
        visited: set[tuple[int, int]] = set()
        # Pre-mark obstacles so DFS never enters them
        visited.update(self.pattern_cells)

        stack: list[tuple[int, int]] = [self.entry]
        visited.add(self.entry)

        directions = list(DIRECTION_DELTA.keys())

        while stack:
            x, y = stack[-1]
            random.shuffle(directions)

            moved = False
            for direction in directions:
                dx, dy = DIRECTION_DELTA[direction]
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                ):
                    # Carve passage — remove shared wall from both cells
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~OPPOSITE[direction]
                    visited.add((nx, ny))
                    stack.append((nx, ny))
                    moved = True
                    break

            if not moved:
                stack.pop()

    def _embed_pattern(self) -> None:
        """Mark '42' cells as obstacles. Sets self.pattern_cells."""
        self.pattern_cells = set()
        if self.width < _MIN_W or self.height < _MIN_H:
            print("Warning: maze too small for '42' pattern, skipping.")
            return

        offset_x = (self.width - _PATTERN_W) // 2
        offset_y = (self.height - _PATTERN_H) // 2

        for bitmap, digit_offset_x in [(_FOUR, 0), (_TWO, _DIGIT_W + _GAP)]:
            for row in range(5):
                for col in range(5):
                    if bitmap[row][col]:
                        for sr in range(_SCALE):
                            for sc in range(_SCALE):
                                cx = offset_x + digit_offset_x + col * _SCALE + sc
                                cy = offset_y + row * _SCALE + sr
                                self.pattern_cells.add((cx, cy))

    def _add_loops(self) -> None:
        """Add extra passages to create a non-perfect maze with loops."""
        # Collect all closed internal walls between non-obstacle cell pairs
        candidates: list[tuple[int, int, int]] = []  # (x, y, direction)
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if x + 1 < self.width and (x + 1, y) not in self.pattern_cells:
                    if self.grid[y][x] & EAST:
                        candidates.append((x, y, EAST))
                if y + 1 < self.height and (x, y + 1) not in self.pattern_cells:
                    if self.grid[y][x] & SOUTH:
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
        """Return True if removing this wall would create a 3x3 open area."""
        # Temporarily remove the wall
        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

        found = False
        # Check all 3x3 sub-grids that include either cell
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

        # Restore the wall
        self.grid[y][x] |= direction
        self.grid[ny][nx] |= OPPOSITE[direction]
        return found

    def _is_open_3x3(self, left: int, top: int) -> bool:
        """Return True if the 3x3 sub-grid starting at (left, top) is fully open."""
        right = left + 2
        bottom = top + 2
        if left < 0 or top < 0 or right >= self.width or bottom >= self.height:
            return False

        # Check all horizontal adjacencies (no East/West walls)
        for row in range(top, bottom + 1):
            for col in range(left, right):
                if self.grid[row][col] & EAST:
                    return False

        # Check all vertical adjacencies (no South/North walls)
        for row in range(top, bottom):
            for col in range(left, right + 1):
                if self.grid[row][col] & SOUTH:
                    return False

        return True
```

- [ ] **Step 4: Run all generator tests**

```bash
pytest tests/test_generator.py -v
```
Expected: all tests PASSED

- [ ] **Step 5: Commit**

```bash
git add mazegen/generator.py
git commit -m "feat: iterative DFS maze generation with 42 pattern and loop support"
```

---

## Task 5: BFS Solver

**Files:**
- Create: `mazegen/solver.py`
- Create: `tests/test_solver.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_solver.py`:

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_solver.py -v
```
Expected: `ModuleNotFoundError: No module named 'mazegen.solver'`

- [ ] **Step 3: Implement `mazegen/solver.py`**

```python
"""BFS solver for maze shortest path."""
from __future__ import annotations
from collections import deque

from mazegen.generator import DIRECTION_DELTA, NORTH, EAST, SOUTH, WEST

_DIR_TO_CHAR: dict[int, str] = {
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
    height: int,
) -> list[str]:
    """Find shortest path from entry to exit using BFS.

    Args:
        grid: 2D list of wall bitmasks (grid[row][col]).
        entry: Starting cell (x, y).
        exit: Target cell (x, y).
        width: Grid width in cells.
        height: Grid height in cells.

    Returns:
        List of direction letters ['N','E','S','W',...] or [] if no path.
    """
    if entry == exit:
        return []

    visited: set[tuple[int, int]] = {entry}
    # parent maps cell → (parent_cell, direction_taken)
    parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    queue: deque[tuple[int, int]] = deque([entry])

    while queue:
        x, y = queue.popleft()
        if (x, y) == exit:
            return _reconstruct_path(parent, entry, exit)

        for direction, (dx, dy) in DIRECTION_DELTA.items():
            if grid[y][x] & direction:
                continue  # wall is closed
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = ((x, y), direction)
                queue.append((nx, ny))

    return []


def _reconstruct_path(
    parent: dict[tuple[int, int], tuple[tuple[int, int], int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> list[str]:
    """Walk parent pointers from exit back to entry and reverse."""
    path: list[str] = []
    cell = exit
    while cell != entry:
        prev_cell, direction = parent[cell]
        path.append(_DIR_TO_CHAR[direction])
        cell = prev_cell
    path.reverse()
    return path
```

- [ ] **Step 4: Run all solver tests**

```bash
pytest tests/test_solver.py -v
```
Expected: all tests PASSED

- [ ] **Step 5: Commit**

```bash
git add mazegen/solver.py tests/test_solver.py
git commit -m "feat: BFS solver returning direction letter path"
```

---

## Task 6: Output File Writer

**Files:**
- Create: `output.py`
- Create: `tests/test_output.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_output.py`:

```python
import os
import pytest
from output import write_output


def test_output_format(tmp_path):
    # 2x2 grid, hand-crafted
    grid = [[0xF, 0x6], [0x9, 0xF]]
    fname = str(tmp_path / "maze.txt")
    write_output(grid, (0, 0), (1, 1), ["E", "S"], fname)

    with open(fname) as f:
        lines = f.read().split("\n")

    assert lines[0] == "F6"
    assert lines[1] == "9F"
    assert lines[2] == ""
    assert lines[3] == "0,0"
    assert lines[4] == "1,1"
    assert lines[5] == "ES"


def test_empty_path(tmp_path):
    grid = [[0xF]]
    fname = str(tmp_path / "maze.txt")
    write_output(grid, (0, 0), (0, 0), [], fname)
    with open(fname) as f:
        lines = f.read().split("\n")
    assert lines[5] == ""


def test_output_file_created(tmp_path):
    fname = str(tmp_path / "output.txt")
    write_output([[0xA]], (0, 0), (0, 0), [], fname)
    assert os.path.exists(fname)
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_output.py -v
```
Expected: `ModuleNotFoundError: No module named 'output'`

- [ ] **Step 3: Implement `output.py`**

```python
"""Write maze grid and solution to a hex-encoded output file."""
from __future__ import annotations


def write_output(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    output_file: str,
) -> None:
    """Write the maze to a file in the required hex format.

    Format:
        Row 0 hex digits (no spaces)
        Row 1 hex digits
        ...
        (empty line)
        entry_x,entry_y
        exit_x,exit_y
        PATH_STRING

    Args:
        grid: 2D list of wall bitmasks (grid[row][col]).
        entry: Entry cell (x, y).
        exit: Exit cell (x, y).
        path: Shortest path as direction letters ['N','E','S','W',...].
        output_file: Destination filename.
    """
    with open(output_file, "w") as f:
        for row in grid:
            f.write("".join(f"{cell:X}" for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")
```

- [ ] **Step 4: Run all output tests**

```bash
pytest tests/test_output.py -v
```
Expected: all tests PASSED

- [ ] **Step 5: Commit**

```bash
git add output.py tests/test_output.py
git commit -m "feat: hex output file writer"
```

---

## Task 7: ASCII Display Renderer

**Files:**
- Create: `display.py`

- [ ] **Step 1: Implement `display.py`**

```python
"""ASCII terminal renderer for the maze using ANSI colors."""
from __future__ import annotations

from mazegen.generator import NORTH, EAST, SOUTH, WEST, DIRECTION_DELTA

# ANSI color codes
RESET = "\033[0m"
MAGENTA = "\033[35m"
RED = "\033[31m"
CYAN = "\033[36m"
DARK_GREY = "\033[90m"

WALL_COLORS = ["\033[37m", "\033[33m", "\033[32m", "\033[34m"]  # white, yellow, green, blue

_CHAR_TO_DIR: dict[str, int] = {
    "N": NORTH, "E": EAST, "S": SOUTH, "W": WEST
}


def render(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    show_path: bool,
    wall_color: str,
    pattern_cells: set[tuple[int, int]],
) -> None:
    """Print the maze to stdout with ANSI colors.

    Args:
        grid: 2D wall bitmask grid (grid[row][col]).
        width: Maze width in cells.
        height: Maze height in cells.
        entry: Entry cell (x, y).
        exit: Exit cell (x, y).
        path: Shortest path as direction letters.
        show_path: Whether to highlight the solution path.
        wall_color: ANSI color code string for walls.
        pattern_cells: Set of (x, y) cells occupied by '42' pattern.
    """
    path_cells = _compute_path_cells(entry, path) if show_path and path else set()

    lines: list[str] = []

    for row in range(height):
        # Border line above this row
        border = _build_border_line(grid, width, row, wall_color)
        lines.append(border)
        # Cell line for this row
        cell_line = _build_cell_line(
            grid, width, row, entry, exit, path_cells, pattern_cells, wall_color
        )
        lines.append(cell_line)

    # Bottom border
    lines.append(_build_bottom_border(grid, width, height, wall_color))

    print("\n".join(lines))


def _build_border_line(
    grid: list[list[int]], width: int, row: int, wall_color: str
) -> str:
    """Build the horizontal border line above the given row."""
    out = wall_color + "+" + RESET
    for col in range(width):
        # North wall of this cell (row == 0 → always closed)
        if row == 0 or grid[row][col] & NORTH:
            out += wall_color + "--" + RESET
        else:
            out += "  "
        out += wall_color + "+" + RESET
    return out


def _build_bottom_border(
    grid: list[list[int]], width: int, height: int, wall_color: str
) -> str:
    """Build the bottom border line (always solid)."""
    out = wall_color + "+" + RESET
    for col in range(width):
        out += wall_color + "--+" + RESET
    return out


def _build_cell_line(
    grid: list[list[int]],
    width: int,
    row: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_cells: set[tuple[int, int]],
    pattern_cells: set[tuple[int, int]],
    wall_color: str,
) -> str:
    """Build the cell interior line for the given row."""
    out = ""
    for col in range(width):
        # West wall
        if col == 0 or grid[row][col] & WEST:
            out += wall_color + "|" + RESET
        else:
            out += " "
        # Cell interior
        out += " " + _cell_symbol(col, row, entry, exit, path_cells, pattern_cells) + " "
    # Right border
    out += wall_color + "|" + RESET
    return out


def _cell_symbol(
    x: int,
    y: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_cells: set[tuple[int, int]],
    pattern_cells: set[tuple[int, int]],
) -> str:
    """Return the colored symbol for a cell's interior."""
    if (x, y) == entry:
        return MAGENTA + "E" + RESET
    if (x, y) == exit:
        return RED + "X" + RESET
    if (x, y) in pattern_cells:
        return DARK_GREY + "█" + RESET   # █
    if (x, y) in path_cells:
        return CYAN + "·" + RESET        # ·
    return " "


def _compute_path_cells(
    entry: tuple[int, int], path: list[str]
) -> set[tuple[int, int]]:
    """Convert a direction-letter path into the set of cells it passes through."""
    cells: set[tuple[int, int]] = {entry}
    x, y = entry
    for letter in path:
        dx, dy = DIRECTION_DELTA[_CHAR_TO_DIR[letter]]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells
```

- [ ] **Step 2: Smoke-test visually**

```bash
python3 -c "
from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from display import render, WALL_COLORS

mg = MazeGenerator(10, 8, seed=42)
mg.generate()
path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
render(mg.grid, mg.width, mg.height, mg.entry, mg.exit,
       path, True, WALL_COLORS[0], mg.pattern_cells)
"
```
Expected: maze renders in terminal with E (entry), X (exit), · (path), + and | walls in white

- [ ] **Step 3: Commit**

```bash
git add display.py
git commit -m "feat: ASCII terminal renderer with ANSI colors and path overlay"
```

---

## Task 8: Main Entry Point + Interactive Menu

**Files:**
- Create: `a_maze_ing.py`

- [ ] **Step 1: Implement `a_maze_ing.py`**

```python
"""A-Maze-ing: maze generator entry point."""
from __future__ import annotations
import sys

from config import parse_config, MazeConfig
from display import render, WALL_COLORS
from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from output import write_output


def main() -> None:
    """Parse config, generate maze, write output, run interactive menu."""
    if len(sys.argv) != 2:
        print("Error: usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        cfg = parse_config(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: config file '{sys.argv[1]}' not found")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    seed = cfg.seed if cfg.seed is not None else 0
    show_path = False
    color_index = 0

    mg, path = _generate(cfg, seed)

    try:
        write_output(mg.grid, mg.entry, mg.exit, path, cfg.output_file)
    except OSError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

    while True:
        _clear()
        render(
            mg.grid, mg.width, mg.height,
            mg.entry, mg.exit,
            path, show_path,
            WALL_COLORS[color_index % len(WALL_COLORS)],
            mg.pattern_cells,
        )
        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path")
        print("3. Rotate wall color")
        print("4. Quit")

        try:
            choice = input("Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "1":
            seed += 1
            mg, path = _generate(cfg, seed)
            try:
                write_output(mg.grid, mg.entry, mg.exit, path, cfg.output_file)
            except OSError as e:
                print(f"Error writing output: {e}")
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index += 1
        elif choice == "4":
            break


def _generate(cfg: MazeConfig, seed: int) -> tuple[MazeGenerator, list[str]]:
    """Build and generate a maze, then solve it."""
    mg = MazeGenerator(
        width=cfg.width,
        height=cfg.height,
        seed=seed,
        perfect=cfg.perfect,
        entry=cfg.entry,
        exit=cfg.exit,
    )
    mg.generate()
    path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
    if not path and mg.entry != mg.exit:
        print("Warning: no valid path from entry to exit")
    return mg, path


def _clear() -> None:
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run end-to-end**

```bash
python3 a_maze_ing.py config.txt
```
Expected: maze renders, interactive menu appears, choice prompts work.
- Press 1 → different maze renders
- Press 2 → path appears / disappears
- Press 3 → wall color changes
- Press 4 → exits cleanly

- [ ] **Step 4: Verify output file was created**

```bash
cat maze.txt | head -5
```
Expected: rows of hex digits (A-F0-9), followed by blank line, entry coords, exit coords, path

- [ ] **Step 5: Commit**

```bash
git add a_maze_ing.py
git commit -m "feat: main entry point with interactive menu and full pipeline"
```

---

## Task 9: Package Build

**Files:**
- Verify: `pyproject.toml`
- Build: `dist/mazegen-1.0.0-py3-none-any.whl`

- [ ] **Step 1: Install build tools**

```bash
pip install build
```

- [ ] **Step 2: Build the package**

```bash
python -m build
```
Expected: `Successfully built mazegen-1.0.0.tar.gz` and `mazegen-1.0.0-py3-none-any.whl` in `dist/`

- [ ] **Step 3: Test install from .whl in a fresh venv**

```bash
python3 -m venv /tmp/test_venv
/tmp/test_venv/bin/pip install dist/mazegen-1.0.0-py3-none-any.whl
/tmp/test_venv/bin/python3 -c "
from mazegen import MazeGenerator, solve
mg = MazeGenerator(8, 6, seed=1)
mg.generate()
path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
print('path length:', len(path))
print('pattern cells:', len(mg.pattern_cells))
"
```
Expected: prints path length (>0) and pattern cells (0, since 8×6 < 28×14 minimum)

- [ ] **Step 4: Commit**

```bash
git add dist/ pyproject.toml
git commit -m "build: add mazegen-1.0.0 wheel"
```

---

## Task 10: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md` with all required sections**

```markdown
*This project has been created as part of the 42 curriculum by oazlan.*

# A-Maze-ing

## Description

A maze generator written in Python 3.10+. It reads a configuration file, generates
a maze using the **Recursive Backtracker (DFS)** algorithm, embeds a visible "42"
pattern, writes the maze to a hex-encoded output file, and renders it interactively
in the terminal using ANSI colors.

The core generation logic is packaged as a reusable pip library (`mazegen`).

## Instructions

### Install

```bash
make install
```

### Run

```bash
make run
# or
python3 a_maze_ing.py config.txt
```

### Interactive Controls

| Key | Action |
|-----|--------|
| 1   | Re-generate maze |
| 2   | Show / Hide solution path |
| 3   | Rotate wall color |
| 4   | Quit |

### Config File Format

```
# Lines starting with # are comments
WIDTH=20           # maze width in cells (integer ≥ 1)
HEIGHT=20          # maze height in cells (integer ≥ 1)
ENTRY=0,0          # entry cell x,y (must be inside bounds)
EXIT=19,19         # exit cell x,y (must differ from ENTRY)
OUTPUT_FILE=maze.txt
PERFECT=True       # True = unique path; False = maze has loops
SEED=42            # optional; omit for random
```

### Build Package

```bash
pip install build
python -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

## Maze Generation Algorithm

**Recursive Backtracker (Iterative DFS)**

Start from the entry cell and carve passages to random unvisited neighbours,
backtracking when stuck. Produces a spanning tree (perfect maze). For
`PERFECT=False`, randomly removes extra walls while preventing 3×3 open areas.

Chosen for simplicity, ease of explanation, and natural perfect-maze output.

## Reusable Module (`mazegen`)

```python
from mazegen import MazeGenerator, solve

mg = MazeGenerator(width=20, height=15, seed=42, perfect=True,
                   entry=(0, 0), exit=(19, 14))
mg.generate()

# Access structure
print(mg.grid)          # list[list[int]] — wall bitmasks
print(mg.pattern_cells) # set of (x,y) cells occupied by "42"

# Find shortest path
path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
print(path)  # ['S', 'S', 'E', ...]
```

Wall encoding: `NORTH=1, EAST=2, SOUTH=4, WEST=8`. A set bit means the wall is closed.

## Resources

- Jamis Buck — "Mazes for Programmers" (book)
- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker — weblog.jamisbuck.org](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)

**AI usage:** Claude Code was used to help design the system architecture, generate
test scaffolding, and review type annotations. All code was reviewed, understood,
and adapted by team members before use.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with instructions, config format, and package docs"
```

---

## Task 11: Lint, Types, and Final Polish

- [ ] **Step 1: Run flake8**

```bash
flake8 .
```
Fix any line-length (E501), whitespace (W), or import order (E4xx) violations.

- [ ] **Step 2: Run mypy**

```bash
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
       --disallow-untyped-defs --check-untyped-defs
```
Fix any type errors. Common fixes:
- Add `Optional[X]` where a value could be `None`
- Add return type `-> None` to functions that lack it
- Use `list[int]` not `List[int]` (Python 3.10+ supports lowercase generics)

- [ ] **Step 3: Run full test suite**

```bash
pytest tests/ -v
```
Expected: all tests PASSED

- [ ] **Step 4: Run `make lint` end-to-end**

```bash
make lint
```
Expected: no errors from either flake8 or mypy

- [ ] **Step 5: Final commit**

```bash
git add -u
git commit -m "fix: lint and type annotation cleanup, all checks pass"
```

---

## Verification Checklist (Run After All Tasks)

1. `python3 a_maze_ing.py config.txt` — maze renders, menu works
2. `cat maze.txt` — hex rows, blank line, entry, exit, path string
3. Wall coherence: run `pytest tests/test_generator.py::test_wall_coherence -v` → PASS
4. Connectivity: run `pytest tests/test_generator.py::test_perfect_maze_full_connectivity -v` → PASS
5. Perfect maze with PERFECT=False: change config, regenerate — maze visibly has loops
6. "42" with 20×20 maze: pattern_cells non-empty, pattern visible in render as `█` blocks
7. "42" with 5×5 maze: "Warning: maze too small..." printed, maze still generates
8. Wrong config → clean error message (no traceback)
9. `make lint` → clean
10. Fresh venv + pip install .whl → `from mazegen import MazeGenerator, solve` works
