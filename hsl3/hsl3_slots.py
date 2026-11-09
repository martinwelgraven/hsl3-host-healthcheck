from typing import Union
from hsl3.hsl3_generator.configs.dcls_input import ConfigInput
from hsl3.hsl3_generator.configs.dcls_output import ConfigOutput
from hsl3.hsl3_generator.configs.dcls_store import ConfigStore
from hsl3.hsl3_generator.configs.dcls_timer import ConfigTimer
from hsl3.hsl3_slot import Hsl3Slot

class Hsl3Slots:
    """
    Instances of this class are transferred when the following methods are called:
    - on_init(inputs: Hsl3Slots, store: Hsl3Slots)
        - inputs - Contains all inputs
        - store - Contains all memory variables
    - on_calc(inputs: Hsl3Slots)
        - inputs - Contains all inputs
    - on_timer(timer: Hsl3Slots)
        - timer - Contains all defined timers
    An instance of the Hsl3Slots class can be accessed directly via the index or key of the individual slot.
    """

    def __init__(self, name: str):
        self.name = name
        self._slots_by_key: dict[str, Hsl3Slot] = {}
        self._slots_by_id: list[Union[Hsl3Slot, None]] = [None]    # index 0 unused
        self._meta_by_key: dict[str, object] = {}                  # optional: keep ConfigInput/Output/...


    def hs_set(self, init_slot: Union[ConfigInput, ConfigOutput, ConfigStore, ConfigTimer]):
        """ 
        Sets an object of type Hsl3Slot 
        Method is called by the Wrapper of the HSL3 Framework on initialization.
        This method is not part of the official HSL3 documentation.
        """
        slot = Hsl3Slot()

        idx = int(init_slot.index)  # must be 1..n
        while len(self._slots_by_id) <= idx:
            self._slots_by_id.append(None)
        self._slots_by_id[idx] = slot

        if isinstance(init_slot, (ConfigInput, ConfigOutput, ConfigStore)):
            data_type = init_slot.type.name
            if data_type == "NUMBER":
                if isinstance(init_slot.init_value, bytes) and init_slot.init_value.find(b".")>-1:
                    data_type = "FLOAT"
                else:
                    data_type = "INT"

            slot.data_type = data_type.lower()
            slot.value = init_slot.init_value
        
        if init_slot.identifier:
            self._slots_by_key[str(init_slot.identifier.upper())] = slot
            self._meta_by_key[str(init_slot.identifier.upper())] = init_slot

    def get(self, index_or_key: Union[int, str]) -> Hsl3Slot:
        """
        Parameters
        - index_or_key: The index (int) or key (str) of the slot to retrieve.
        
        Returns an object of type Hsl3Slot or triggers an exception if the index or key does not exist
        """

        if isinstance(index_or_key, int):
            if index_or_key <= 0 or index_or_key >= len(self._slots_by_id):
                raise KeyError(f"Index {index_or_key} not found.")
            
            slot = self._slots_by_id[index_or_key]
            if slot is None:
                raise KeyError(f"Index {index_or_key} not found.")
            return slot
        
        if isinstance(index_or_key, str):
            key = index_or_key.upper()
            try:
                return self._slots_by_key[key]
            except KeyError:
                raise KeyError(f"Key {key} not found.")


    def keys(self):        
        """ Returns a list of all existing keys. """
        out = {}
        for i in range(1, len(self._slots_by_id)):
            if self._slots_by_id[i] is not None:    
                out[i] = self._slots_by_id[i]

        for key in self._slots_by_key.keys():
            out[key] = self._slots_by_key[key]

        return out.keys()
    

    def changed(self, index_or_key) -> bool:
        """
        Returns True or False indicating whether the value of the slot has changed since the last call of the on_calc method. 
        For timers, it indicates whether the timer has been triggered since the last call of the on_timer method.
        
        Parameters:
         - index_or_key
        
        Returns False if the corresponding index or key is not found.
        """
        slot = self.get(index_or_key)
        if slot is not None:
            return slot.changed
        else:
            return False

    def value(self, index_or_key) -> Union[float, int, bytes, None]:
        """
        Returns the value value of the slot. The type of the value is determined by the type of the slot (float, int or bytes). If the value is not set, None is returned.
        
        Parameters:
         - index_or_key
        
        If the corresponding index or key is not found, None is returned.
        """
       
        slot = self.get(index_or_key)
        if slot is not None:
            return slot.value
        else:
            return None
