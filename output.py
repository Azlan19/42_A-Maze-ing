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
                file.write(f"{cell:X}")
            file.write("\n")
        file.write("\n")
        file.write(f"{entry[0]},{entry[1]}\n")
        file.write(f"{exit[0]},{exit[1]}\n")
        file.write("".join(path) + "\n")
