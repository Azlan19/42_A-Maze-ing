*This project has been created as part of the 42 curriculum by **oazlan** and **dzhukov**.*

## Description

**a-maze-ing** is a CLI tool that generates, solves and renders mazes in the
terminal. It reads a config file, builds a maze (with a "42" hidden in its
walls), finds the shortest path from entry to exit, displays it in colour, and
writes it to a file — all from an interactive menu (regenerate, toggle path,
cycle colours).

## Instructions

```bash
make install   # pip install -r requirements.txt
make run       # python3 a_maze_ing.py config.txt
make lint      # flake8 + mypy
pytest         # run the test suite
```

`python3 a_maze_ing.py <config_file>` also works directly with any config file.

## Configuration file

Plain-text `KEY=VALUE` lines (`#` for comments), e.g. `config.txt`:

```
WIDTH=11
HEIGHT=9
ENTRY=0,0
EXIT=10,8
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

| Key | Meaning |
|-----|---------|
| `WIDTH`, `HEIGHT` | maze size in cells |
| `ENTRY`, `EXIT` | start/end cells as `x,y` |
| `OUTPUT_FILE` | where the maze is written |
| `PERFECT` | `True` = exactly one path between cells, `False` = adds loops |
| `SEED` | optional, makes generation reproducible |

`parse_config()` validates all of this and raises `ValueError` on bad input.

The output file (`output.py`) lists, per row, one hex digit per cell encoding
its walls (`NORTH=1, EAST=2, SOUTH=4, WEST=8`), then a blank line, the entry
and exit coordinates, and the solution as a string of `N`/`E`/`S`/`W` letters.

## Maze generation algorithm

We use an **iterative depth-first search / recursive backtracker**
(`MazeGenerator._carve_dfs`): from the entry, randomly visit an unvisited
neighbour and knock down the wall to it, backtracking via a stack when stuck.
The "42" pattern cells are pre-marked so the carving tunnels around them. When
`PERFECT=False`, an extra pass removes a few more walls to add loops.

**Why:** it's simple to implement iteratively (no recursion-depth issues),
guarantees a fully-connected "perfect" maze with no extra connectivity checks,
produces long winding corridors that look good in a terminal, is trivially
seedable for reproducible output, and naturally supports carving around
pre-marked obstacle cells like our "42".

## Reusable code

`mazegen/` is a self-contained, pip-installable library with no dependency on
config/display/output:
- `MazeGenerator` builds a maze from just `width`, `height`, `seed`,
  `perfect`, `entry`, `exit` — usable in any project that needs a maze.
- `solve()` is a pure BFS function: grid + entry/exit in, shortest path out.
- Shared wall constants (`NORTH/EAST/SOUTH/WEST`, `DIRECTION_DELTA`) give any
  consumer (renderer, solver, I/O) a common way to read the grid.

The application layer (`config.py`, `output.py`, `display.py`) is similarly
decoupled: each only needs a grid plus entry/exit/path data, so it can work
with mazes from any source.

## Team and project management

**Roles**
- **oazlan** — Parsing the config file and algorithm 
- **dzhukov** — Generating the maze and displaying it

**Planning:** Although we set "roles" for this project, a lot of it was completed together on 1 machine. This way
we were able to understand every aspect of the project without having to relearn

**What worked / could improve:** We decided early on on what we wanted to achieve and in what format, so there was
no time wasted discussing and planning. Maybe we could work more individually to learn the whole process with branching
in git since the group projects rely on this.

**Tools:** Git/GitHub, pytest, flake8, mypy, and Claude Code (see Resources).

## Resources


- TUM Data Science I (Data Structures) Course for the BFS and DFS algorithm  
- 42 A-Maze-ing subject  
- Asking a lot of other 42 students  

**AI usage:** Claude - To understand packages, dsiplaying the maze in the terminal, and structure of the project