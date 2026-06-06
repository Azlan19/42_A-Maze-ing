import sys

from config import parse_config, MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from output import write_output
from display import render, WALL_COLOURS


def _clear() -> None:
    print("\033[2J\033[H", end="") 
    # \033[2J — ANSI escape code that clears the entire terminal screen.
    # \033[H — moves the cursor back to the top-left corner.
    # end="" — prevents print() from adding an extra newline after the escape codes.

