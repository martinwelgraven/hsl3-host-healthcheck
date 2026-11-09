import os
from dataclasses import dataclass

@dataclass
class ConfigProject:

    root: str
    
    _id: str = ''
    _name: str = ''
    _title: str = ''

    _src_folder: str = ''
    _tests_folder: str = ''
    
    _html_file: str = ''
    _json_file: str = ''
    _python_file: str = ''
    _hsl_file: str = ''
    _test_file: str = ''

    @property 
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value
        self._initialize()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.replace('-', ' ').title()
        self._initialize()

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value    
    
    @property
    def source_path(self) -> str:
        return self._src_folder

    @source_path.setter
    def source_path(self, value: str):
        self._src_folder = value

    @property
    def test_path(self) -> str:
        return self._tests_folder

    @test_path.setter
    def test_path(self, value: str):
        self._tests_folder = value

    @property
    def json_file(self) -> str:
        return self._json_file

    @json_file.setter
    def json_file(self, value: str):
        self._json_file = value

    @property
    def html_file(self) -> str:
        return self._html_file

    @html_file.setter
    def html_file(self, value: str):
        self._html_file = value

    @property
    def python_file(self) -> str:
        return self._python_file

    @python_file.setter
    def python_file(self, value: str):
        self._python_file = value

    @property
    def hsl_file(self) -> str:
        return self._hsl_file

    @hsl_file.setter
    def hsl_file(self, value: str):
        self._hsl_file = value

    @property
    def test_file(self) -> str:
        return self._test_file

    @test_file.setter
    def test_file(self, value: str):
        self._test_file = value

    
    def html_exists(self) -> bool:
        return os.path.exists(os.path.join(self._src_folder, self._html_file))

    def html_path(self) -> str:
        return os.path.join(self._src_folder, self._html_file)
    
    def json_exists(self) -> bool:
        return os.path.exists(os.path.join(self._src_folder, self._json_file))

    def json_path(self) -> str:
        return os.path.join(self._src_folder, self._json_file)

    def python_exists(self) -> bool:
        return os.path.exists(os.path.join(self._src_folder, self._python_file))

    def python_path(self) -> str:
        return os.path.join(self._src_folder, self._python_file)

    def testfile_exists(self) -> bool:
        return os.path.exists(os.path.join(self._tests_folder, self._test_file))
    
    def testfile_path(self) -> str:
        return os.path.join(self._tests_folder, self._test_file)
    
    def hsl_exists(self) -> bool:
        return os.path.exists(os.path.join(self._src_folder, self._hsl_file))
    
    def hsl_path(self) -> str:
        return os.path.join(self._src_folder, self._hsl_file)

    def __post_init__(self):
        if self.root is None:
           print('Root directory could not be retrieved.')
           exit()
     
        if not os.path.exists(self.root):
            print(f"Root directory '{self.root}' could not be validated.")
            exit()

        self._src_folder = os.path.join(self.root, 'src')
        self._tests_folder = os.path.join(self.root, 'tests')
        self._initialize()
    
    
    def _initialize(self):
        if self.id == '' or self.name == '':
            return
        
        self._title = f"{self._id} - {self._name.replace('-', ' ').title()}" 
        
        self._json_file = f"config_{self._name.replace(' ','-').lower()}.json"
        self._html_file = f"log{str(self._id)}.html"
        self._python_file = f"hsl3_{self._id}_{self._name.replace(' ','_').replace('-','_').lower()}.py"
        self._hsl_file = f"{self._id}_{self._name.replace(' ','_').lower()}.hsl"
        self._test_file = f"test_{self._id}_{self._name.replace(' ','_').lower()}.py"
            
        if not os.path.exists(self._src_folder):
            os.mkdir(self._src_folder)
       
        if not os.path.exists(self._tests_folder):
            os.mkdir(self._tests_folder)
       