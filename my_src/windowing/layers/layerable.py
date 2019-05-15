from patterns.strict_method_implant import SMI
from ..window import Window

class Layerable(SMI):

    def __new__(cls, *args, **kwargs):
        # automatically save object into the layer
        w = Window.get_current_window()
        self = super().__new__(cls)
        w.layer[0].add(self)
        return self

    def _stop_(self):
        pass

    def _hide_(self):
        pass

    def _draw_(self):
        pass
