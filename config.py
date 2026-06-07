from dataclasses import dataclass

REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
                 "OUTPUT_FILE", "PERFECT"}


@dataclass
class MazeConfig:
    """Validate maze configuration"""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


# Parse through config file
def parse_config(path: str) -> MazeConfig:
    raw: dict[str, str] = {}
    with open(path) as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            raw[key] = value

    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ValueError(f"Missing required key: {next(iter(missing))}")

    try:
        width = int(raw["WIDTH"])
        height = int(raw["HEIGHT"])
    except ValueError:
        raise ValueError("WIDTH and HEIGHT must be integers")
    if width < 1 or height < 1:
        raise ValueError("WIDTH and HEIGHT must be positive")

    entry = _parse_coordinates(raw["ENTRY"], "ENTRY", width, height)
    exit_ = _parse_coordinates(raw["EXIT"], "EXIT", width, height)
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different")

    if raw["PERFECT"] not in ("True", "False"):
        raise ValueError("PERFECT must be True or False")
    perfect = raw["PERFECT"] == "True"

    seed = None
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
        seed=seed)


# Helper function to parse through coordinates
def _parse_coordinates(value: str, key: str, width: int, height: int) -> tuple[int, int]:
    try:
        x, y = value.split(",")
        x, y = int(x), int(y)
    except ValueError:
        raise ValueError(f"{key} must be in x,y format")
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"{key} ({x},{y}) are out of bounds for ({width},{height})")
    return (x, y)
