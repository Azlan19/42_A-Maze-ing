from mazegen.generator import MazeGenerator
from mazegen.solver import solve

__all__ = ["MazeGenerator", "solve"]


# === Used to show how it works in a venv ===
# from mazegen import MazeGenerator, solve

# mg = MazeGenerator(width=11, height=9, seed=42, perfect=True, entry=(0, 0), exit=(10, 8))
# mg.generate()
# path = solve(mg.grid, mg.entry, mg.exit, mg.width, mg.height)

# print("grid:", len(mg.grid), "x", len(mg.grid[0]))
# print("entry/exit:", mg.entry, mg.exit)
# print("solution:", "".join(path))