from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from hsl3.hsl3_generator.configs.dcls_output import ConfigOutput
from hsl3.hsl3_generator.configs.dcls_input import ConfigInput
from hsl3.hsl3_generator.configs.dcls_store import ConfigStore
from hsl3.hsl3_generator.configs.dcls_timer import ConfigTimer
from hsl3.hsl3_generator.configs.dcls_script import ConfigScript
from hsl3.hsl3_generator.configs.dcls_translation import ConfigTranslation

@dataclass
class ConfigModule:

    id: str
    name: str
    title: str = ''
    version: str = "0.1.0"
    version_date: Optional[str] = datetime.now().strftime('%Y-%m-%d')
    category: str = 'IOT Device Data'
    context: str = ''

    description: str = ''
    note: str = ''
    warning: str = ''

    inputs: List[ConfigInput]= field(default_factory=list)
    outputs: List[ConfigOutput]= field(default_factory=list)
    scripts: List[ConfigScript]= field(default_factory=list)
    stores: List[ConfigStore] = field(default_factory=list)
    timers: List[ConfigTimer] = field(default_factory=list)
    translations: List[ConfigTranslation] = field(default_factory=list)
    
    hsl_filename: Optional[str] = ''

    def __post_init__(self):
        if self.title == '':
            self.title = f"{self.id} - {self.name.replace('-', ' ').title()}"

        if self.context == '':
            self.context = self.name.replace('-', '_').lower()

        if self.hsl_filename == '':
            if len(str(self.hsl_filename)) == 0:
                self.hsl_filename = f'{self.id}_{self.name}.hsl'