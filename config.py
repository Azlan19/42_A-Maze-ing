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

def parse_config(path: str) -> MazeConfig:
    raw: dict[str, str] = {}
    with open(path) as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key,_,value = line.partition("=")
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
        output_file=["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed)