import numpy as np
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context as gl
import weakref

class RenderComponent:
    # def __new__(cls, *args, **kwargs):
    #     if len(args) + len(kwargs) == 0:
    #         ins = super().__new__(RenderComponent)
    #         # ins.__init__()
    #         return ins
    #     else:
    #         ins = super().__new__(cls)
    #         return ins
    _context = None
    def build(self, context):
        self._context = weakref.ref(context)

    @property
    def context(self):
        return self._context()

    def __del__(self):
        if self._context != None:
            if self._context() != None:
                if self._glindex != None:
                    self.delete()
    @classmethod
    def bind(cls):
        pass
    @classmethod
    def unbind(cls):
        pass

    @property
    def is_built(self):
        if self._glindex is None:
            return False
        return True

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


    def __str__(self):
        return f'<{self.__class__.__name__} object with opengl index: {self._glindex}>'