import numpy as np
from OpenGL.GL import *

from .component_bp import RenderComponent


class Vertexbuffer(RenderComponent):

    def __init__(self, glusage=GL_DYNAMIC_DRAW):

        if glusage is None:
            glusage = GL_DYNAMIC_DRAW
        self._glusage = glusage

        self.flag_firstbuild = True

        self._glindex = None

    def build(self):
        if self.flag_firstbuild:
            self._glindex = glGenBuffers(1)
            self.flag_firstbuild = False

        self.bind()
        glBufferData(GL_ARRAY_BUFFER, 0, None, self._glusage)
        self.unbind()
        print('-vertex buffer built')

    def set_attribpointer(self, buffer):
        datasize = buffer.size * buffer.itemsize

        # TODO glusage resetting needed?

        glBufferData(GL_ARRAY_BUFFER, datasize, buffer, self._glusage)

        # set attribute
        # when not constructed dtype
        if buffer.dtype.fields is None:
            type = self._dtype_to_gltype(buffer.dtype)
            stride = buffer.itemsize
            offset = ctypes.c_void_p(0)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 1, type, GL_FALSE, stride, offset)

        # when using constructed dtype
        else:
            f = buffer.dtype.fields
            num_attributes = len(f)
            dtypes = list(f.values())
            offsets = [i[1] for i in dtypes]
            dtypes = [i[0] for i in dtypes]
            # constant one
            stride = sum([i.itemsize for i in dtypes])

            for i in range(num_attributes):
                d = dtypes[i]
                size = sum(d.shape)
                # if size == 0:
                #     size = 1
                gltype = self._dtype_to_gltype(d)
                offset = ctypes.c_void_p(offsets[i])
                glEnableVertexAttribArray(i)
                # print()
                # print('index:',i)
                # print('size:',size)
                # print('gltype:',gltype)
                # print('stride:',stride)
                glVertexAttribPointer(i, size, gltype, GL_FALSE, stride, offset)
        # m = glGetBufferSubData(GL_ARRAY_BUFFER,0,24)
        # print(m)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self._glindex)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    @property
    def data(self):
        return self._data

    @property
    def vbo(self):
        return self._glindex
