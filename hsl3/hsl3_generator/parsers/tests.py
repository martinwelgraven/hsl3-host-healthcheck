import os

from hsl3.hsl3_generator.configs.dcls_module import ConfigModule


class TestfileParser:

    def __init__(self, test_file: str, json_file: str, config_node: ConfigModule):
        
        self.json_file = json_file
        self.config = config_node
        file_content = self._test_filecontent()

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(file_content)

    
    def _test_filecontent(self) -> str:

        file_content = "# Auto-generated Python file\n"
        file_content += "\n"
        file_content += "import os\n"
        file_content += "import sys\n"
        file_content += "\n"
        file_content += "ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
        file_content += "\n"
        file_content += "if ROOT_DIR not in sys.path:\n"
        file_content += "\tsys.path.insert(0, ROOT_DIR)\n"
        file_content += f"if os.path.join(ROOT_DIR, \"src\") not in sys.path:\n"
        file_content += f"\tsys.path.insert(0, os.path.join(ROOT_DIR, \"src\"))\n"
        file_content += "\n"
        file_content += "from hsl3.hsl3 import Hsl3Framework\n"
        file_content += "from hsl3.hsl3_wrapper import Hsl3WrapperModule\n"
        file_content += f"from src.{str(self.config.scripts[0].filename).replace('.py', '')} import LogicModule\n"
        file_content += "\n"
        file_content += f"json_file = \"{self.json_file}\"\n"
        file_content += "\n"
        file_content += "def main():\n"
        file_content += "\n"
        file_content += "\tif sys.platform == \"win32\":\n"
        file_content += "\t\tos.system('cls')\n"
        file_content += "\telse:\n"
        file_content += "\t\tos.system('clear')\n"
        file_content += "\n"
        file_content += f"\tprint(\" === Starting test for {self.config.title} === \")\n"
        file_content += "\tprint(\"\")\n"
        file_content += "\n"
        file_content += f"\thsl3 = Hsl3Framework(\"{ str(self.config.hsl_filename).replace('.hsl', '') }\")\n"
        file_content += "\tlogic_module = LogicModule(hsl3)\n"
        file_content += f"\twrapper_node = Hsl3WrapperModule(os.path.join(ROOT_DIR, 'src', json_file), logic_module)  # type: ignore\n"
        file_content += "\tif (wrapper_node.config is not None):\n"
        file_content += "\t\thsl3.config = wrapper_node.config\n"
        file_content += "\n"
        file_content += self._set_inputs()
        file_content += "\n"
        file_content += "\tprint(\"\")\n"
        file_content += "\n\tprint(\" === DEBUG LOG ===\")\n"
        file_content += "\tprint(\"\")\n"
        file_content += "\n"
        file_content += "\tlogic_module.debug.print_log()\n"
        file_content += "\n"
        file_content += "\n"
        file_content += "if __name__ == \"__main__\":\n"
        file_content += "\tmain()\n"

        return file_content
    
    def _set_inputs(self) -> str:
        file_content = ""

        for input in self.config.inputs:
            input_value = '\"' + str(input.init_value) + '\"' if input.type.upper() == 'STRING' else input.init_value
            file_content += f"\twrapper_node.set_input_value(\"{input.identifier}\", {input_value})\n"

        return file_content