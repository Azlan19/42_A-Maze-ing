from mazegen.generator import NORTH, EAST, SOUTH, WEST, DIRECTION_DELTA

# Ansi color code
RESET = "\033[0m" # Every color must be followed by RESET to stop color bleeding into next character
MAGENTA = "\033[35m"
RED = "\033[31m"
CYAN = "\033[36m"
DARK_GREY = "\033[90m"

# The list a_maze_ing.py cycles through when the user chooses an option
WALL_COLORS: list[str] = [
    "\033[37m",  # white
    "\033[33m",  # yellow
    "\033[32m",  # green
    "\033[34m",  # blue
]

# Convert path letters back to direction name
_CHAR_TO_DIRECTION: dict[int, str] = {
    "N": NORTH,
    "E": EAST,
    "S": SOUTH,
    "W": WEST,
}

