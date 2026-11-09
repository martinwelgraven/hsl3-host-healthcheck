from dataclasses import dataclass, field
from typing import List

@dataclass
class ConfigTranslation:
    category: str
    language: str
    name: str
    index: int = field(init=False)
    translation_inputs: List[str]
    translation_outputs: List[str]
    _next_id: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        self.index = ConfigTranslation._next_id
        ConfigTranslation._next_id += 1