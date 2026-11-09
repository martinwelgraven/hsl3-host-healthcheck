from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ConfigScript:
    index: int = field(init=False)
    filename: Optional[str] = ''
    folder: Optional[str] = ''
    _next_id: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        self.index = ConfigScript._next_id
        ConfigScript._next_id += 1