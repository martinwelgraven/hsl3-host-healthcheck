import os
import ast
import base64
import gzip

from hsl3.hsl3_generator.configs.dcls_module import ConfigModule
from hsl3.hsl3_generator.configs.dcls_store import StoreType
from hsl3.hsl3_generator.configs.dcls_input import InputType
from hsl3.hsl3_generator.configs.dcls_output import OutputType


class ModuleParser:
    """ Class for parsing the JSON configuration to for a logic module. """

    def __init__(self, base_path):
        self.module_code = []
        self.slot_base_path = 0
        self.slot_destination_port = 0

        self.base_path = base_path

        self.inputs_str = ''
        self.outputs_str = ''

    def get_module_file_content(self, module_config: ConfigModule):
        
        self.set_inputs_str(module_config.inputs)
        self.set_outputs_str(module_config.outputs)

        self.set_expert_info(module_config)
        self.set_translations(module_config.translations)
        self.set_module_definition(module_config)

        self.set_module_inputs(module_config.inputs)
        self.set_module_stores(module_config.stores)
        self.set_module_outputs(module_config.outputs)

        self.set_module_input_names(module_config.inputs)
        self.set_module_store_names(module_config.stores)
        self.set_module_timer_names(module_config.timers)
        self.set_module_output_names(module_config.outputs)

        self.set_module_scripts(module_config)

        return '\n'.join(self.module_code)

    
    def set_expert_info(self, module_config: ConfigModule):
        #Information for the HS/FS experts to easily identify the module and its structure in the HSL3 code
        expert_info = f'5000'                                                   # record type                               
        expert_info += f'|\"{module_config.category}\\{module_config.name}\"'   # Designation: Name of the block in the HS/FS Expert.
        expert_info += f'|{int(len(module_config.stores) > 0)}'                 # Remanent:	If this module is defined as remanent:
        expert_info += f'|{len(module_config.inputs)}'                          # Number of inputs
        expert_info += f'|{self.inputs_str}'                                    # Input label names
        expert_info += f'|{len(module_config.outputs)}'                         # Number of outputs
        expert_info += f'|{self.outputs_str}'                                   # Output label names
        expert_info += f'|\"{module_config.version}\"'                          # Version
        expert_info += f'|{self.slot_destination_port}'                         # No. of an input or 0 | Input used to specify the destination port for port forwarding.
        expert_info += f'|{self.slot_base_path}'                                # No. of an input or 0 | Input used to specify the base path for port forwarding.

        self.module_code.append(expert_info)

    def set_inputs_str(self, inputs):
        for input in inputs:
            if input.type == InputType.BASE_PATH:
                self.slot_base_path = input.index
            if input.type == InputType.DESTINATION_PORT:
                self.slot_destination_port = input.index
        
        self.inputs_str = '|'.join(map(lambda input: f'\"{input.label}\"', inputs))

    def set_outputs_str(self, outputs):
        self.outputs_str = '|'.join(map(lambda output: f'\"{output.label}\"', outputs))

    def set_translations(self, translations):
        for translation in translations:
            inputs_str = '|'.join(map(lambda input: f'\"{input}\"', translation.translation_inputs))
            outputs_str = '|'.join(map(lambda output: f'\"{output}\"', translation.translation_outputs))

            translation_definition = f'4999'                                                # record type
            translation_definition += f'|\"{translation.language}\"'                        # Language abbreviation	Text 2-digit language abbreviation of the respective language.
            translation_definition += f'|\"{translation.category}\\{translation.name}\"'    # Designation: Name of the block in the above mentioned language in the HS/FS Expert.
            translation_definition += f'|{inputs_str}'                                      # Translation of the input labels in the above mentioned language. The order corresponds to the order of the inputs defined in the module definition (5001).        
            translation_definition += f'|{outputs_str}'                                     # Translation of the output labels in the above mentioned language. The order corresponds to the order of the outputs defined in the module definition (5001).  

            self.module_code.append(translation_definition)

    def set_module_definition(self, module_config: ConfigModule):
        module_definition =  f'5001'                          # record type
        module_definition += f'|{len(module_config.inputs)}'   # Number of inputs
        module_definition += f'|{len(module_config.outputs)}'  # Number of outputs
        module_definition += f'|{len(module_config.timers)}'   # Number of timers
        module_definition += f'|{len(module_config.stores)}'   # Number of stores
        module_definition += f'|1'                             # Calculation at initialisation
        module_definition += f'|0'                             # Coded formula block | Indicates whether the block contains coded lines of type 5012.       
        module_definition += f'|\"HSL3.main.{module_config.context}\"' # A reference to the context of the module !!NEW IN HSL3!!
        
        self.module_code.append(module_definition)

    def set_module_inputs(self, inputs):
        for input in inputs:
            initial_value = f'\"{input.init_value}\"' if input.type == InputType.STRING else input.init_value
            input_definition = f'5002'                  # record type
            input_definition += f'|{input.index}'       # Input index
            input_definition += f'|{initial_value}'     # Initial value of the input. The type depends on the input type (e.g. number, string, boolean).
            input_definition += f'|{1 if input.type == InputType.STRING else 0}'  # Is string: 1 if the input is of type string, otherwise 0.
            
            self.module_code.append(input_definition)

    def set_module_stores(self, stores):
        for store in stores:
            initial_value = f'\"{store.init_value}\"' if store.type == StoreType.STRING else store.init_value
            store_definition = f'5003'                  # record type
            store_definition += f'|{store.index}'       # Store index
            store_definition += f'|{initial_value}'     # Initial value of the store. The type depends on the store type (e.g. number, string, boolean).
            store_definition += f'|1'                   # Remanent 1.
            
            self.module_code.append(store_definition)
    
    def set_module_outputs(self, outputs):
        for output in outputs:
            initial_value = f'\"{output.init_value}\"' if output.type == OutputType.STRING else output.init_value
            output_definition = f'5004'                  # record type
            output_definition += f'|{output.index}'      # Output index
            output_definition += f'|{initial_value}'     # Initial value of the output. The type depends on the output type (e.g. number, string, boolean).
            output_definition += f'|0'                   # Rounding to binary.
            output_definition += f'|1'                   # Calculation at initialisation (1: Send / 2: Send by Change)
            output_definition += f'|{1 if output.type == OutputType.STRING else 0}'  # Is string: 1 if the output is of type string, otherwise 0.
            
            self.module_code.append(output_definition)
    
    def set_module_input_names(self, inputs):
        for input in inputs:
            input_name = f"\'{input.identifier}\'" if len(input.identifier) > 0 else f"\'{input.label}\'"

            input_definition = f'5012'                          # record type
            input_definition += f'|0'                           # End after execution
            input_definition += f'|\"\"'                        # Condition
            input_definition += f'|\"HSL3.set_input_name({input.index}, { input_name })\"'  # Action
            input_definition += f'|\"\"'                        # Time formula
            input_definition += f'|0'                           # Pin - Output
            input_definition += f'|0'                           # Pin - Time memory
            input_definition += f'|0'                           # Pin - memory variable
            input_definition += f'|0'                           # Pin - Negated output

            self.module_code.append(input_definition)
    
    def set_module_store_names(self, stores):
        for store in stores:
            store_name = f"\'{store.identifier}\'" if len(store.identifier) > 0 else f"\'{store.label}\'"

            store_definition = f'5012'                          # record type
            store_definition += f'|0'                           # End after execution
            store_definition += f'|\"\"'                        # Condition
            store_definition += f'|\"HSL3.set_store_name({store.index}, {store_name})\"'  # Action
            store_definition += f'|\"\"'                        # Time formula
            store_definition += f'|0'                           # Pin - Output
            store_definition += f'|0'                           # Pin - Time memory
            store_definition += f'|0'                           # Pin - memory variable
            store_definition += f'|0'                           # Pin - Negated output)
            
            self.module_code.append(store_definition)
    
    def set_module_timer_names(self, timers):
        for timer in timers:
            timer_name = f"\'{timer.identifier}\'" if len(str(timer.identifier)) > 0 else f"\'{timer.label}\'"
            timer_definition = f'5012'                          # record type
            timer_definition += f'|0'                           # End after execution
            timer_definition += f'|\"\"'                        # Condition
            timer_definition += f'|\"HSL3.set_timer_name({timer.index}, {timer_name})\"'  # Action
            timer_definition += f'|\"\"'                        # Time formula
            timer_definition += f'|0'                           # Pin - Output
            timer_definition += f'|0'                           # Pin - Time memory
            timer_definition += f'|0'                           # Pin - memory variable
            timer_definition += f'|0'                           # Pin - Negated output

            self.module_code.append(timer_definition)

    def set_module_output_names(self, outputs):
        for output in outputs:
            output_name = f"\'{output.identifier}\'" if len(str(output.identifier)) > 0 else f"\'{output.label}\'"
            output_definition = f'5012'                          # record type
            output_definition += f'|0'                           # End after execution
            output_definition += f'|\"\"'                        # Condition
            output_definition += f'|\"HSL3.set_output_name({output.index}, {output_name})\"'  # Action
            output_definition += f'|\"\"'                        # Time formula
            output_definition += f'|0'                           # Pin - Output
            output_definition += f'|0'                           # Pin - Time memory
            output_definition += f'|0'                           # Pin - memory variable
            output_definition += f'|0'                           # Pin - Negated output
            
            self.module_code.append(output_definition)
    
    def extract_imports_ast(self, file_content):
        imports = []
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            else:
                if isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
        return imports

    def topological_sort(self, dependencies):
        visited = set()
        temp_mark = set()
        result = []
        def visit(node):
            if node in temp_mark:
                raise ValueError('Circular dependency found!')
            else:
                if node not in visited:
                    temp_mark.add(node)
                    for dep in dependencies[node]:
                        visit(dep)
                    temp_mark.remove(node)
                    visited.add(node)
                    result.append(node)
        for node in dependencies:
            if node not in visited:
                visit(node)
        return result

    def set_module_scripts(self, module_config: ConfigModule):
        script_files = []
        dependencies = {}
        script_prefix = f'hsl3_{module_config.id}'
        
        for script in module_config.scripts:
            print(f'Processing script file: {script}')
            if hasattr(script, 'folder') and len(str(script.folder)) > 0:
                for filename in os.listdir(os.path.join(str(self.base_path), str(script.folder))):
                    if filename.startswith(script_prefix) and filename.endswith('.py'):
                            script_files.append(filename)
            if hasattr(script, 'filename') and len(str(script.filename)) > 0 and str(script.filename).startswith(script_prefix):
                script_files.append(os.path.join(str(self.base_path), str(script.filename)))
        
        if len(script_files) == 0:
            raise Exception(f'No file with prefix {script_prefix} was found.')
        
        else:
            for script_file in script_files:
                dependencies[script_file] = []
                with open(script_file, 'r') as f:
                    content = f.read()
                    imports = self.extract_imports_ast(content)
        
                    for imp in imports:
                        imp_file = imp.replace('.', '/') + '.py'
                        if imp_file in script_files:
                            dependencies[script_file].append(imp_file)
        
        sorted_files = self.topological_sort(dependencies)

        for script_file in sorted_files:
            with open(script_file, 'r', encoding='utf-8') as script_src:
                src = script_src.read()
               
                data = gzip.compress(src.encode(), mtime=0)
                data = data[:9] + b'\xff' + data[10:]
                encoded_src = base64.b64encode(data)
                # Definition of a formula block that loads the script content into the module. The script content is compressed and encoded in base64 to ensure it can be safely included in the HSL3 code.
                script_definition = f'5012'     # record type
                script_definition += f'|0'      # End after execution
                script_definition += f'|\"\"'   # Condition
                script_definition += f'|\"HSL3.load(\'{os.path.splitext(os.path.split(script_file)[(-1)])[0]}\', \'{encoded_src.decode()}\')\"'  # Formula
                script_definition += f'|\"\"'   # Time formula
                script_definition += f'|0'      # Pin - Output
                script_definition += f'|0'      # Pin - Time memory
                script_definition += f'|0'      # Pin - memory variable
                script_definition += f'|0'      # Pin - Negated output    
                self.module_code.append(script_definition)
