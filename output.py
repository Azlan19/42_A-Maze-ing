def write_output(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    output_file: str,
) -> None:
    """Write the maze to a file in hex format
    """

    with open(output_file, "w") as file:
        for row in grid:
            for cell in row:
                file.write("".join(f"{cell:X}"))
            file.write("\n")
        file.write("\n")
        file.write(f"{entry[0]}, {entry[1]}\n")
        file.write(f"{exit[0]}, {exit[1]}\n")
        file.write("".join(path) + "\n")


# test
# grid = [[14, 0x6], [0x9, 0xC]]
# entry = (0, 0)
# exit = (1, 1)
# path = ['E', 'S']

# write_output(grid, entry, exit, path, 'test_output.txt')