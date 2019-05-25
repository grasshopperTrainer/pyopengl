from .vertexarray import Vertexarray
from .vertexbuffer import Vertexbuffer


class Vertex_unit:
    """
    component class of renderer_builder

    contains pair of 'vertex array' and 'vertex buffer'
    """
    def __init__(self, vbo_usage = None, vbo_dtype = None):
        """

        :param vbo_usage:
        :param vbo_dtype:
        """
        self._VAO = Vertexarray()
        self._VBO = Vertexbuffer(vbo_usage, vbo_dtype)

    def _build_(self):
        pass

    def _bind_(self):
        self._VBO.unbint()

    def _unbind_(self):
        self._VAO.unbind()
