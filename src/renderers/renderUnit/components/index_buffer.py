import numpy as np
from OpenGL.GL import *

from .buffer import _Buffer


class Indexbuffer(_Buffer):
    # def __new__(cls, *args, **kwargs):
    #     if len(args) + len(kwargs) == 0:
    #         ins = super().__new__(cls)
    #         ins.__init__(*args, **kwargs)
    #         return ins
    #     else:
    #         return _Buffer

    def __init__(self, data: np.ndarray, glusage=GL_DYNAMIC_DRAW):
        # input type checker
        # super().__init__(data, GL_ELEMENT_ARRAY_BUFFER, glusage)

        self._data = data
        if glusage is None:
            glusage = GL_DYNAMIC_DRAW
        self._glusage = glusage

        self._glindex = None

    def build(self):
        self._glindex = glGenBuffers(1)
        datasize = self.data.size * self.data.itemsize

        self.bind()
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, datasize, self.data, self._glusage)
        self.unbind()

    def bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._glindex)

    def unbind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    @property
    def data(self):
        return self._data

    @property
    def ibo(self):
        return self._glindex

    @property
    def count(self):
        return len(self.data)
