from patterns.strict_method_implant import SMI
from ..window import Window
from ..frame_buffer_like import FBL

class Layerable(SMI):

    def __new__(cls, *args, **kwargs):
        # automatically save object into the layer
        fb = FBL.get_current_fbl()
        self = super().__new__(cls)

        fb.layers[0].add(self)
        return self

    @SMI.must_func
    def _stop_(self):
        pass

    @SMI.must_func
    def _hide_(self):
        pass

    @SMI.must_func
    def _draw_(self):
        pass
