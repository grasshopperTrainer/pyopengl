from OpenGL.GL import *

class Vertex_array:
    def __init__(self, n = 1):
        self._vbo = glGenVertexArrays(n)

    def bind(self):
        glBindVertexArray(self._vbo)

    def unbinde(self):
        glBindVertexArray(0)

    @property
    def array(self):
        return self._vbo