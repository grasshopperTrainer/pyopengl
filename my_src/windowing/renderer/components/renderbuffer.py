# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl

from .component_bp import RenderComponent
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Renderbuffer(RenderComponent):
    GL_DEPTH_COMPONENT = Unique_glfw_context.GL_DEPTH_COMPONENT
    GL_DEPTH_COMPONENT16 = Unique_glfw_context.GL_DEPTH_COMPONENT16
    GL_DEPTH_COMPONENT24 = Unique_glfw_context.GL_DEPTH_COMPONENT24
    GL_DEPTH_COMPONENT32 = Unique_glfw_context.GL_DEPTH_COMPONENT32
    GL_DEPTH_COMPONENT32F = Unique_glfw_context.GL_DEPTH_COMPONENT32F

    GL_STENCIL_COMPONENTS = Unique_glfw_context.GL_STENCIL_COMPONENTS
    GL_DEPTH24_STENCIL8 = Unique_glfw_context.GL_DEPTH24_STENCIL8
    GL_DEPTH32F_STENCIL8 = Unique_glfw_context.GL_DEPTH32F_STENCIL8

    GL_DEPTH_STENCIL = Unique_glfw_context.GL_DEPTH_STENCIL
    GL_STENCIL_INDEX1 = Unique_glfw_context.GL_STENCIL_INDEX1
    GL_STENCIL_INDEX4 = Unique_glfw_context.GL_STENCIL_INDEX4
    GL_STENCIL_INDEX8 = Unique_glfw_context.GL_STENCIL_INDEX8
    GL_STENCIL_INDEX16 = Unique_glfw_context.GL_STENCIL_INDEX16

    def __init__(self, width, height, internalformat):
        self._size = width, height
        self._internal_format = internalformat
        self._context = None
        self._glindex = None

    def build(self, context):
        if context is None:
            self._context = Unique_glfw_context.get_current()
        else:
            self._context = context

        with self._context as gl:
            self._glindex = gl.glGenRenderbuffers(1)

            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._glindex)
            # initial setting
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, self._internal_format, self._size[0], self._size[1])
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def copy(self):
        new = Renderbuffer(*self._size, self._internal_format)
        return new

    def rebuild(self, width, height):
        self._size = width, height
        self.delete()
        self.build()

    def bind(self):
        with self._context as gl:
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._glindex)

    def unbind(self):
        with self._context as gl:
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def delete(self):
        if self._glindex != None:
            with self._context as gl:
                gl.glDeleteRenderbuffers(1, self._glindex)
            self._glindex = None
            self._context = None

    @property
    def bitdepth(self):
        if self._internal_format == self.GL_STENCIL_INDEX8:
            return 255
        else:
            raise

    def __del__(self):
        if self._glindex != None:
            self.delete()
