import sys
import os

from config import parse_config, MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from output import write_output
from display import render, WALL_COLOURS


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.flush()
    # os.system("clear")
    # print("\033[2J\033[H", end="") 
    # \033[2J — ANSI escape code that clears the entire terminal screen.
    # \033[H — moves the cursor back to the top-left corner.
    # end="" — prevents print() from adding an extra newline after the escape codes.


def _generate(
    cfg: MazeConfig,
    seed: int
) -> tuple[MazeGenerator, list[str]]:
    mg = MazeGenerator(
        width = cfg.width,
        height = cfg.height,
        seed=seed,
        perfect = cfg.perfect,
        entry = cfg.entry,
        exit = cfg.exit
    )
    mg.generate()
    path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)
    return mg, path
    # Helper function because need to generate the maze twice: at startup and again every rerun


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    cfg = parse_config(sys.argv[1])
    
    if cfg.seed is not None:
        seed = cfg.seed
    else:
        seed = 0
    
    mg, path = _generate(cfg, seed)
    write_output(mg.grid, mg.entry, mg.exit, path, cfg.output_file)
    wall_colour_index = 0
    show_path = True

    while True:
        _clear()
        render(
            mg.grid, mg.width, mg.height,
            mg.entry, mg.exit,
            path, show_path,
            WALL_COLOURS[wall_colour_index],
            mg.pattern_cells
        )

        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colours")
        print("4. Quit")
        choice = input("Choice? (1-4): ").strip()

        if choice == "1":
            seed += 1
            mg, path = _generate(cfg, seed)
            write_output(mg.grid, mg.entry, mg.exit, path, cfg.output_file)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            wall_colour_index = (wall_colour_index + 1) % len(WALL_COLOURS)
        elif choice == "4":
            break


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        pass
