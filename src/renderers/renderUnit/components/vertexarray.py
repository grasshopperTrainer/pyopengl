from OpenGL.GL import *


class Vertexarray():

    def __init__(self):
        self._glindex = None

    def build(self):
        self._glindex = glGenVertexArrays(1)

    def bind(self):
        glBindVertexArray(self._glindex)

    def unbind(self):
        glBindVertexArray(0)

    @property
    def vao(self):
        return self._glindex
