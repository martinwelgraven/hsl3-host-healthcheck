from dataclasses import dataclass, field
from typing import Optional, Union
from enum import Enum


class InputType(Enum):
    NUMBER = 1
    STRING = 2 # always bytes
    BASE_PATH = 3
    DESTINATION_PORT = 4

    def upper(self):
        return self.name
        
@dataclass
class ConfigInput:
    label: str
    init_value: Union[bytes, float]
    type: InputType
    index: int = field(init=False)
    identifier: Optional[str] = ''
    description: str = ''
    _next_id: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        try:
            self.index = ConfigInput._next_id
            ConfigInput._next_id += 1
            self.type = InputType[self.type.upper()]
        except KeyError:
            print(f"Invalid input defined: '{self.label}' with type '{self.type}'\r\n")
            exit()

    def to_dict(self) -> dict:
        return {
            'type': self.type.name.lower(),
            'identifier': self.identifier,
            'init_value': self.init_value,
            'label': self.label
        }