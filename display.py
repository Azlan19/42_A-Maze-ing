from mazegen.generator import NORTH, EAST, SOUTH, WEST, DIRECTION_DELTA

# Ansi color code
# Every color must be followed by RESET to stop color -
# bleeding into next character
RESET = "\033[0m"
MAGENTA = "\033[35m"
RED = "\033[31m"
CYAN = "\033[36m"
DARK_GREY = "\033[90m"

# The list a_maze_ing.py cycles through when the user chooses an option
WALL_COLOURS: list[str] = [
    "\033[37m",  # white
    "\033[33m",  # yellow
    "\033[32m",  # green
    "\033[34m",  # blue
]

# Convert path letters back to direction name
_CHAR_TO_DIRECTION: dict[str, int] = {
    "N": NORTH,
    "E": EAST,
    "S": SOUTH,
    "W": WEST,
}


def _path_cells(
    entry: tuple[int, int],
    path: list[str]
) -> set[tuple[int, int]]:
    """Convert direction letters into the
    set of cells the path passes through"""
    cells: set[tuple[int, int]] = {entry}
    x, y = entry
    for letter in path:
        dx, dy = DIRECTION_DELTA[_CHAR_TO_DIRECTION[letter]]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def _cell_char(
    x: int,
    y: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_cells: set[tuple[int, int]],
    pattern_cells: set[tuple[int, int]],
) -> str:
    """Return the 2-character wide interior string for a cell"""
    if (x, y) == entry:
        return MAGENTA + " E" + RESET
    if (x, y) == exit:
        return RED + " X" + RESET
    if (x, y) in pattern_cells:
        return DARK_GREY + "██" + RESET
    if (x, y) in path_cells:
        return CYAN + " ." + RESET
    return "  "


def _top_border(
    grid: list[list[int]],
    width: int,
    row: int,
    wall_colour: str
) -> str:
    """Build the horizontal border line above a given row"""
    output = wall_colour + "█" + RESET
    for col in range(width):
        # row == 0 always writes the wall,
        # grid[row][col] & NORTH writes if NORTH is a wall
        if row == 0 or grid[row][col] & NORTH:
            output += wall_colour + "███" + RESET
        else:
            output += "  " + wall_colour + "█" + RESET
    return output


def _bottom_border(
    width: int,
    wall_colour: str
) -> str:
    """Build the horizontal bottom border line"""
    output = wall_colour + "█" + RESET
    for _ in range(width):
        output += wall_colour + "███" + RESET
    return output


def _cell_line(
    grid: list[list[int]],
    width: int,
    row: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_cells: set[tuple[int, int]],
    pattern_cells: set[tuple[int, int]],
    wall_colour: str
) -> str:
    """Build the interior line between cells for the given row"""
    output = ""
    for col in range(width):
        if col == 0 or grid[row][col] & WEST:
            output += wall_colour + "█" + RESET
        else:
            output += " "
        output += _cell_char(col, row, entry, exit, path_cells, pattern_cells)
    output += wall_colour + "█" + RESET
    return output


def render(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    show_path: bool,
    wall_colour: str,
    pattern_cells: set[tuple[int, int]]
) -> None:
    """Print the maze to stdout with ANSI colours"""
    if show_path and path:
        path_cells = _path_cells(entry, path)
    else:
        path_cells = set()

    lines: list[str] = []

    for row in range(height):
        lines.append(_top_border(grid, width, row, wall_colour))
        lines.append(_cell_line(grid, width, row, entry, exit,
                     path_cells, pattern_cells, wall_colour))

    lines.append(_bottom_border(width, wall_colour))
    print("\n".join(lines))


# from mazegen.generator import MazeGenerator
# from mazegen.solver import solve

# mg = MazeGenerator(19, 19, seed=100)
# mg.generate()
# path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
# render(mg.grid, mg.width, mg.height, mg.entry, mg.exit,
#        path, True, WALL_COLOURS[1], mg.pattern_cells)
