
from datetime import datetime

class Hsl3DebugSection:
    """
    An instance of this class is returned when creating a debug section.
    """

    def __init__(self):
        self._fields={}
        self._log=[]

    
    def set(self, name, value):
        """
        Defines a field in the section and sets its value.
        
        Parameters:
         - name - Field name.
         - value - Field value.
        """
        self._fields[name]=value

    def inc(self, name, value=1):
        """
        Increases the field value.
        
        Parameters:
         - name - Field name. If the field does not yet exist, the value is initialised with value.
         - value - Value by which the content of the field (default: 1) is increased. If the value is not a numerical value, an exception is triggered.
        """
        if name not in self._fields:
            self._fields[name] = 0
        if not isinstance(self._fields[name], (int, float)):
            raise TypeError("Field value must be a numerical value.")
        
        self._fields[name] += value
    
    def avg(self, name, value=None):
        """
        Calculates the average of a value.
        Parameters:
         - name - Field name. If the field does not yet exist, the value is initialised with value.
         - value - If the value is a numerical value, the average is calculated. If None is transferred, the field is reset.
         """
        if name not in self._fields:
            self._fields[name] = 0
        if not isinstance(self._fields[name], (int, float)):
            raise TypeError("Field value must be a numerical value.")
        
        self._fields[name] = (self._fields[name] + value) / 2 if value is not None else 0
    
    def timestamp(self, name, value=None):
        """
        Sets a timestamp for the field.
        Parameters:
         - name - Field name. If the field does not yet exist, the value is initialised with value.
         - value - If set, this value is accepted, otherwise current time stamp.
        """
        if name not in self._fields:
            self._fields[name] = 0
        if not isinstance(self._fields[name], (float)):
            raise TypeError("Field value must be a numerical value.")
        
        self._fields[name] = value if value is not None else datetime.now().timestamp()
        
    def log(self, msg):
        """
        Logs a message.
        Parameters:
         - msg - Message to log.
        """
        self._log.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-1]} | {msg}")

    def exception(self, msg):
        """
        Logs an exception message.
        Parameters:
         - msg - Message to log.
        """
        self._log.append(f"EXCEPTION: {msg}")

    def print_log(self):
        for msg in self._log:
            print(msg)