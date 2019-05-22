from patterns.strict_method_implant import SMI
from .layers.layers import Layers
class FBL(SMI):
    """
    this if mother of frame buffer-like class
    such as glfw.Window itself and Frame buffer object
    from OpenGL
    """
    _current = None
    def __new__(cls, *args, **kwargs):
        ins = super().__new__(cls)

        ins.__setattr__('layers',Layers(ins))

        return ins

    @SMI.must_func
    @property
    def width(self):
        pass

    @SMI.must_func
    @property
    def height(self):
        pass

    @SMI.must_func
    @property
    def size(self):
        pass

    @classmethod
    def get_current_fbl(cls):
        return cls._current
    @classmethod
    def set_current_fbl(cls, fbl):
        cls._current = fbl