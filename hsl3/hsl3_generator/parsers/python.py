from hsl3.hsl3_generator.configs.dcls_module import ConfigModule

class PythonfileParser:
    """ Class for handling the generation of Python code for a logic module. """
    
    def write_first_python(self, python_file: str, config: ConfigModule):

        python_content = f'# Auto-generated Python file\r\n'
        python_content += f'# Logic Node: {config.title}\r\n'
        python_content += f'# Author:\r\n'  
        python_content += f'# Description: \r\n'
        python_content += f'# INFO: \r\n'
        python_content += f'# DISCLAIMER: \r\n\r\n'
        
        nl = '\n'
        nt = '\t\t\t'
        python_content = "class LogicModule:\n\n"
        python_content += "\tdef __init__(self, hsl3):\n"
        python_content += "\t\tself.fw = hsl3\n"
        python_content += "\t\tself.debug = self.fw.create_debug_section()\n\n"
        
        python_content += "\t\t# For local reuse of output values\n"
        
        output_content = ""
        for output in config.outputs:
            output_content += f"\n\t\t\t\'{output.identifier}': " + "{ "
            output_content += f"'value': " + (f"'{output.init_value}'" if output.type.name == 'STRING' else str(output.init_value)) + ", "
            output_content += f"'sbc': '{output.sbc}', "
            output_content += f"'index': {output.index} "
            output_content += "}"
            output_content += "," if len(config.outputs) > output.index else ""
            
        python_content += "\t\tself.outputs = {"
        python_content += f"\t\t\t{output_content} \n\t\t}}\n\n"
        python_content += "\tdef on_init(self, inputs, store):\n"
        python_content += "\t\t\"\"\"\n"
        python_content += "\t\tInitialize the module with input connections and store information\n"
        python_content += "\t\tArgs:\n"
        python_content += "\t\t\tinputs: Hsl3Slots object containing input slot definitions\n"
        python_content += "\t\t\tstore: Hsl3Slots object containing the storage object for maintaining state (for this node unused)\n"
        python_content += "\t\t\"\"\"\n\n"
        python_content += "\t\tfor key in inputs.keys():\n"
        python_content += "\t\t\t# .keys() returns both indexes and keynames\n"

        input_identifiers = [f"{input.identifier}" for input in config.inputs]
        python_content += f"\t\t\tif key in {input_identifiers}:\n"
        python_content += "\t\t\t\tpass\n\n"
        python_content += "\tdef on_calc(self, inputs):\n"
        python_content += "\t\t\"\"\"\n"
        python_content += "\t\tCalculate called if any new input is received by the logic node.\n\n"
        python_content += "\t\tArgs:\n"
        python_content += "\t\t\tinputs:  Hsl3Slots object containing input slot definition\n"
        python_content += "\t\t\"\"\"\n\n"
        python_content += "\t\tif inputs.changed('IN01'):  \n"
        python_content += "\t\t\tpass\n\n"
        python_content += "\tdef on_timer(self, timer):\n"
        python_content += "\t\t\"\"\" Timers \"\"\"\n"
        python_content += "\t\tpass\n\n"

        python_content += "\tdef set_output(self, key, value):\n"
        python_content += "\t\t\"\"\" Set output value taking into account 'send by change' settings \"\"\"\n\n"
        python_content += "\t\tif key in self.outputs.keys():\n"
        python_content += "\t\t\tif self.outputs[key]['value'] != value or self.outputs[key]['sbc'] == 's':\n"
        python_content += "\t\t\t\tself.outputs[key]['value'] = value\n"
        python_content += "\t\t\t\tself.fw.set_output(key, value)\n"
        python_content += "\n"

        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
