from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ConfigTimer:
    index: int = field(init=False)
    identifier: Optional[str] = ''
    description: str = ''
    _next_id: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        self.index = ConfigTimer._next_id
        ConfigTimer._next_id += 1