from numbers import Number

import numpy as np
from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl

from .component_bp import RenderComponent


class Indexbuffer(RenderComponent):
    def __init__(self, data=None, glusage=gl.GL_DYNAMIC_DRAW, dtype=None):
        self._data = None
        self._dtype = None
        self._glusage = None

        if data is None:
            self._data = np.array([])
        else:
            self.data = data

        if glusage is None:
            glusage = gl.GL_DYNAMIC_DRAW
        self._glusage = glusage

        # save dtype for glDrawElement()
        if dtype is None:
            # if not given will consider it automate mode
            self._dtype = None
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
        else:
            raise TypeError

        # object index(?or just referring as just object is correct?) from OpenGL
        self._glindex = None

    def build(self):
        # if self._flag_firstbuild:
        self._glindex = gl.glGenBuffers(1)
            # self._flag_firstbuild = False

        datasize = self.data.size * self.data.itemsize
        self.bind()
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, datasize, self.data, self._glusage)

        self.unbind()
        # print('-index buffer built')

    def bind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._glindex)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

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

    @property
    def ibo(self):
        return self._glindex

    @property
    def count(self):
        return len(self.data)

    @property
    def gldtype(self):
        npdtype = self._data.dtype
        if npdtype == np.uint8:
            return gl.GL_UNSIGNED_BYTE
        elif np.dtype == np.uint16:
            return gl.GL_UNSIGNED_SHORT
        elif np.dtype == np.uint32:
            return gl.GL_UNSIGNED_INT
