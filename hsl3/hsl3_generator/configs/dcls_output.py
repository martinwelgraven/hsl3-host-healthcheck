from dataclasses import dataclass, field
from typing import Optional, Union
from enum import Enum


class OutputType(Enum):
    NUMBER = 1
    STRING = 2  # always bytes

    def upper(self):
        return self.name

@dataclass
class ConfigOutput:
    label: str
    init_value: Union[bytes, float]
    type: OutputType
    
    index: int = field(init=False)
    identifier: Optional[str] = ''
    sbc: bool = False
    description: str = ''
    _next_id: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        try:
            self.index = ConfigOutput._next_id
            ConfigOutput._next_id += 1
            self.type = OutputType[self.type.upper()]
        except KeyError:
            print(f"Invalid output defined: '{self.label}' with type '{self.type}'\r\n")
            exit()