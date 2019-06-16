from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl

from .component_bp import RenderComponent

class Renderbuffer(RenderComponent):
    GL_DEPTH_COMPONENT = gl.GL_DEPTH_COMPONENT
    GL_DEPTH_COMPONENT16 = gl.GL_DEPTH_COMPONENT16
    GL_DEPTH_COMPONENT24 = gl.GL_DEPTH_COMPONENT24
    GL_DEPTH_COMPONENT32 = gl.GL_DEPTH_COMPONENT32
    GL_DEPTH_COMPONENT32F = gl.GL_DEPTH_COMPONENT32F

    GL_STENCIL_COMPONENTS = gl.GL_STENCIL_COMPONENTS
    GL_DEPTH24_STENCIL8 = gl.GL_DEPTH24_STENCIL8
    GL_DEPTH32F_STENCIL8 = gl.GL_DEPTH32F_STENCIL8

    GL_DEPTH_STENCIL = gl.GL_DEPTH_STENCIL
    GL_STENCIL_INDEX1 = gl.GL_STENCIL_INDEX1
    GL_STENCIL_INDEX4 = gl.GL_STENCIL_INDEX4
    GL_STENCIL_INDEX8 = gl.GL_STENCIL_INDEX8
    GL_STENCIL_INDEX16 = gl.GL_STENCIL_INDEX16

    def __init__(self, width, height, internalformat):
        self._glindex = None
        self._size = width, height
        self._internalformat = internalformat

    def build(self):
        self._glindex = gl.glGenRenderbuffers(1)

        self.bind()
        # initial setting
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, self._internalformat, self._size[0],self._size[1])
        self.unbind()

    def rebuild(self, width, height):
        self._size = width, height
        self.delete()
        self.build()

    def bind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._glindex)

    def unbind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def delete(self):
        gl.glDeleteRenderbuffers(1, self._glindex)
        self._glindex = None

    def __del__(self):
        if self._glindex != None:
            self.delete()
