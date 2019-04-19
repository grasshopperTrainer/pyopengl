from OpenGL.GL import *
from .component_bp import _Component_bp


class Vertexarray(_Component_bp):

    def __init__(self, init_sign):
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
