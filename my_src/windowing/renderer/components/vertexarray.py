from ...gl_tracker import Trackable_openGL as gl
from .component_bp import RenderComponent


class Vertexarray(RenderComponent):

    def __init__(self):
        self._glindex = None

    def build(self):
        self._glindex = gl.glGenVertexArrays(1)
        print('-vertex array generated')

    def bind(self):
        gl.glBindVertexArray(self._glindex)

    def unbind(self):
        gl.glBindVertexArray(0)

    @property
    def vao(self):
        return self._glindex

    def __str__(self):
        return f'<Vertex array object with opengl index: {self._glindex}>'