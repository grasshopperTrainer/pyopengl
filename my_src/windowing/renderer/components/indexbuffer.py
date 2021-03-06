from numbers import Number

import numpy as np
# from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl

from .component_bp import RenderComponent
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Indexbuffer(RenderComponent):
    GL_DYNAMIC_DRAW = Unique_glfw_context.GL_DYNAMIC_DRAW
    GL_STATIC_CRAW = Unique_glfw_context.GL_STATIC_DRAW

    def __init__(self, data=None, glusage=None, dtype=None):
        self._data = None
        self._dtype = None
        if glusage is None:
            glusage = self.__class__.GL_DYNAMIC_DRAW
        self._glusage = glusage



        # save dtype for glDrawElement()
        if dtype is None:
            # if not given will consider it automate mode
            self._dtype = np.uint8
        elif isinstance(dtype, int):
            if dtype == 0:
                self._dtype = np.uint8
            elif dtype == 1:
                self._dtype = np.uint16
            else:
                self._dtype = np.uint32
        elif isinstance(dtype, str):
            if 'byte' in dtype or 'BYTE' in dtype:
                self._dtype = np.uint8
            elif 'short' in dtype or 'SHORT' in dtype:
                self._dtype = np.uint16
            elif 'int' in dtype or 'INT' in dtype:
                self._dtype = np.uint32
        elif isinstance(dtype, type(np.dtype)):
            self._dtype = dtype
        else:
            raise TypeError

        if data is None:
            self._data = np.array([])
        elif isinstance(data, np.ndarray):
            self._data = data
        elif isinstance(data, (list, tuple)):
            self._data = np.array(data, dtype=self._dtype)

        # object index(?or just referring as just object is correct?) from OpenGL
        self._context = None
        self._glindex = None

    def build(self, context):
        super().build(context)

        with self.context as gl:
            # if self._flag_firstbuild:
            self._glindex = gl.glGenBuffers(1)
                # self._flag_firstbuild = False
            datasize = self.data.size * self.data.itemsize
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._glindex)
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, datasize, self.data, self._glusage)

            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
            # print('-index buffer built')

    def bind(self):
        with self.context as gl:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._glindex)

    def unbind(self):
        with self.context as gl:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    def delete(self):
        if self._glindex != None:
            with self.context as gl:
                gl.glDeleteBuffers(self._glindex)
            self._glindex = None
            self._context = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, np.ndarray):
            med = value
        elif isinstance(value, (tuple, list)):
            med = np.array(value)
        elif isinstance(value, Number):
            med = np.array([value, ])
        else:
            raise TypeError

        if self._dtype is None:
            max = med.max()
            if max <= 255:
                dtype = np.uint8
            elif max <= 65535:
                dtype = np.uint16
            else:
                dtype = np.uint32
        else:
            dtype = self._dtype

        self._data = med.astype(dtype)

    def copy(self):
        return self.__class__(self._data, self._glusage, self._dtype)

    @property
    def count(self):
        return len(self.data)

    @property
    def gldtype(self):
        npdtype = self._data.dtype
        if npdtype == np.uint8:
            return Unique_glfw_context.GL_UNSIGNED_BYTE
        elif np.dtype == np.uint16:
            return Unique_glfw_context.GL_UNSIGNED_SHORT
        elif np.dtype == np.uint32:
            return Unique_glfw_context.GL_UNSIGNED_INT
