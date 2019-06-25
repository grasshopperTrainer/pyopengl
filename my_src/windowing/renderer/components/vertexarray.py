# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from .component_bp import RenderComponent
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Vertexarray(RenderComponent):

    def __init__(self):
        self._glindex = None
        self._context = None

    def build(self, context):
        if context is None:
            self._context = Unique_glfw_context.get_current()
        else:
            self._context = context

        with self._context as gl:
            self._glindex = gl.glGenVertexArrays(1)

    def bind(self):
        with self._context as gl:
            gl.glBindVertexArray(self._glindex)

    def unbind(self):
        with self._context as gl:
            gl.glBindVertexArray(0)

    def delete(self):
        if self._glindex != None:
            with self._context as gl:
                gl.glDeleteVertexArrays(self._glindex)
                print('vertexarray delete done')
            self._glindex = None
            self._context = None

    def __del__(self):
        if self._glindex != None:
            self.delete()


    # @property
    # def vao(self):
    #     return self._glindex

    def __str__(self):
        return f'<Vertex array object with opengl index: {self._glindex}>'