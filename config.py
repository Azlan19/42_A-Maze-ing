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
    with open(path, "r") as file:
        for line in file:
            if line.startswith("#") or not line.strip():
                continue
            raw: dict[str, str] = {}
            key,_,value = line.partition("=")
            raw[key] = value

