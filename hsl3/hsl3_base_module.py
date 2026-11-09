from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_slots import Hsl3Slots


class LogicModule:
    """
    Base class for logic modules.
    Mostly to be used for type hinting and to provide a common interface for all logic modules.
    """

    def __init__(self, hsl3fw: Hsl3Framework) -> None:
        self.fw = hsl3fw

    def on_init(self, inputs: Hsl3Slots, store: Hsl3Slots):
        # Called during logic initialisation. The code is listed in the context of the node.
        pass

    def on_calc(self, inputs: Hsl3Slots):
        # Is called if an input has been written and the node is recalculated
        pass

    def on_timer(self, timer: Hsl3Slots):
        # Called when a timer has been triggered. If no timers are used, this method can be omitted.
        pass