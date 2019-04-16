import numpy as np
from OpenGL.GL import *


# class Buffer:
#     def __init__(self, vb_data: np.ndarray, ib_data: np.ndarray,
#                  vb_glusage = GL_STATIC_DRAW, ib_glusage = GL_STATIC_DRAW):
#
#         self._vao = glGenVertexArrays(1)
#         glBindVertexArray(self._vao)
#         self._vb_data = vb_data
#         self._vb_glusage = vb_glusage
#         self._ib_glusage = ib_glusage
#         self._ib_data = ib_data
#
#         self._vbo = glGenBuffers(1)
#         _Vertexbuffer(vb_data, GL_ARRAY_BUFFER, vb_glusage,self._vbo)
#         self._ibo = glGenBuffers(1)
#         _Indexbuffer(ib_data, GL_ELEMENT_ARRAY_BUFFER, ib_glusage,self._ibo)
#
#         # unbind
#         self.unbind()
#
#     def unbind(self):
#         glBindBuffer(GL_ARRAY_BUFFER,0)
#         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
#         glBindVertexArray(0)
#
# def rebuild_vertexarray(self):
#     """
#     in glfw context sharing, vertex array is not shared.
#     This fact is crucial especially for CORE_PROFILE because
#     giving vertex array is must.
#     This method is to rebuild vertex array according to the vertex buffer
#     stored here.
#     :return: None
#     """
#     vao = glGenVertexArrays(1)
#     glBindVertexArray(vao)
#
#     _Vertexbuffer(self._vb_data,GL_ARRAY_BUFFER,self._vb_glusage,self._vbo)
#
#     self.unbind()
#
#     @property
#     def array(self):
#         return self._vao
#
#     @property
#     def indexbuffer(self):
#         return self._ibo
#
#     @property
#     def vertexbuffer(self):
#         return self._vbo

class _Buffer:
    def __new__(cls, *args, **kwargs):
        if len(args) + len(kwargs) == 0:
            ins = super().__new__(_Buffer)
            # ins.__init__()
            return ins
        else:
            ins = super().__new__(cls)
            ins.__init__(*args, **kwargs)
            return ins

    # def __init__(self, data, gltarget, glusage):
    #
    #     # typecheck
    #     a = isinstance(data, np.ndarray)
    #     b = isinstance(gltarget, (opc.IntConstant, int))
    #     c = isinstance(glusage, (opc.IntConstant, int))
    #
    #     if not (a and b and c):
    #         print(f'[{self.__class__.__name__}]: input types incorrect')
    #         return None
    #     else:
    #         self.gltarget = gltarget
    #         self.glusaget = glusage

    def build(self):
        pass

    def bind(self):
        pass

    def unbind(self):
        pass

    @staticmethod
    def _dtype_to_gltype(dtype: np.dtype):
        # name_dtype = dtype.name
        # name_gltype = 'GL_'
        # if name_dtype[0] is 'u':
        #     name_gltype += 'UNSIGNED_'
        # if 'int' in name_dtype:
        #     name_gltype += INT
        # print(name)
        # typeof = type
        if dtype.subdtype is None:
            typeof = dtype.type
        else:
            typeof = dtype.subdtype[0].type

        if typeof is np.float32:
            return GL_FLOAT
        elif typeof is np.uint8:
            return GL_UNSIGNED_BYTE
        elif typeof is np.uint16:
            return GL_UNSIGNED_SHORT
        elif typeof is np.uint32:
            return GL_UNSIGNED_INT

        elif None:
            # TODO add more conversion if needed
            pass
        else:
            # TODO type error for no supported GL data type
            pass
        pass
