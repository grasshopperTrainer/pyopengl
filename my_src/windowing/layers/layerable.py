from patterns.strict_method_implant import SMI
from ..window import Window
from ..frame_buffer_like import FBL

class Layerable(SMI):

    def __new__(cls, *args, **kwargs):
        # automatically save object into the layer
        fb = FBL._current
        self = super().__new__(cls)
        fb.layer[0].add(self)
        return self

    def _stop_(self):
        pass

    def _hide_(self):
        pass

    def _draw_(self):
        pass
