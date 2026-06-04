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

