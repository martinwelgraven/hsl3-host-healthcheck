"""
This class represents a slot in the HSL3 framework.
The data_type property is not part of the official documentation.
"""

class Hsl3Slot:
    def __init__(self) -> None:
        self._value = None
        self._changed = False
        self._data_type = None

    @property
    def changed(self):
        has_changed = self._changed
        self._changed = False
            
        return has_changed

    @property
    def data_type(self):
        pass
    
    @data_type.setter
    def data_type(self, data_type):
        self._data_type = data_type

    @property
    def value(self):
        self._changed = False
        return self._value

    @value.setter
    def value(self, new_value):
        self._changed = True
        self._value = new_value
