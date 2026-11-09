import os

from .hsl3_slots import Hsl3Slots
from .hsl3_base_module import LogicModule
from .hsl3_generator.configs.dcls_module import ConfigModule
from .hsl3_generator.parsers.json import JSONfileParser


class Hsl3WrapperModule():
    """ 
    Wrapper class to load the Logic Module and Framework
    This class is not part of the official HSL3 documentation.
    """

    def __init__(self, json_file: str, node: LogicModule) -> None:
        self.node = node
        self.config: ConfigModule = self._open_config(json_file)
     
        self.node.fw.inputs = Hsl3Slots("inputs")
        self.node.fw.outputs = Hsl3Slots("outputs")
        self.node.fw.stores = Hsl3Slots("stores")
        self.node.fw.timers = Hsl3Slots("timers")

        self.node.fw.hs_set_timer_callback(node.on_timer) 
   
        self._set_slots()
        self.node.on_init(self.node.fw.inputs, self.node.fw.stores)
    
    
    def set_input_value(self, key, value):
        """
            Function to mock the call from the HomeServer object to the logic node.
            Sets the input value in the context of the node and triggers the on_calc method of the node.
        """
        self.node.fw.hs_on_input(key, value.encode('iso-8859-15') if isinstance(value, str) else value)
        self.node.on_calc(self.node.fw.inputs) 



    def _open_config(self, source_file) -> ConfigModule:
        """ Helper function to open the config file and parse it into a ConfigModule object. """

        config = JSONfileParser().parse_json(source_file)
        if config == None:
            raise ValueError(f"Could not parse JSON configuration from file: {source_file}")
        
        return config
        
    
    def _set_slots(self):
        """ Loads the slots defined in the config file into the HSL3 framework. """
        for input in self.config.inputs:
            if(isinstance(input.init_value, str)):
                input.init_value = input.init_value.encode("ascii")
            self.node.fw.inputs.hs_set(input)

        for output in self.config.outputs: 
            if(isinstance(output.init_value, str)):
                output.init_value = output.init_value.encode("ascii")
            self.node.fw.outputs.hs_set(output)

        for store in self.config.stores: 
            if(isinstance(store.init_value, str)):
                store.init_value = store.init_value.encode("ascii")
            self.node.fw.stores.hs_set(store)

        for timer in self.config.timers:
            self.node.fw.timers.hs_set(timer)