from dataclasses import dataclass


@dataclass
class Building:
    name: str
    level: int = 1
