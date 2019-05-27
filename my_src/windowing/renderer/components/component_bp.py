import numpy as np
from ...gl_tracker import Trackable_openGL as gl
class RenderComponent:
    # def __new__(cls, *args, **kwargs):
    #     if len(args) + len(kwargs) == 0:
    #         ins = super().__new__(RenderComponent)
    #         # ins.__init__()
    #         return ins
    #     else:
    #         ins = super().__new__(cls)
    #         return ins

    @classmethod
    def build(cls):
        pass
    @classmethod
    def bind(cls):
        pass
    @classmethod
    def unbind(cls):
        pass

    @staticmethod
    def _dtype_to_gltype(dtype: np.dtype):
        if dtype.subdtype is None:
            typeof = dtype.type
        else:
            typeof = dtype.subdtype[0].type

        if typeof is np.float32:
            return gl.GL_FLOAT
        elif typeof is np.uint8:
            return gl.GL_UNSIGNED_BYTE
        elif typeof is np.uint16:
            return gl.GL_UNSIGNED_SHORT
        elif typeof is np.uint32:
            return gl.GL_UNSIGNED_INT
        elif typeof is np.int32:
            return gl.GL_INT

        elif None:
            # TODO add more conversion if needed
            pass
        else:
            # TODO type error for no supported GL data type
            pass
        pass
