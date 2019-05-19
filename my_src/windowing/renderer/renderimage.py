import OpenGL.GL as gl
from .components.framebuffer import Framebuffer
from .components.renderbuffer import Renderbuffer
from .components.texture import Texture_new


class Renderimage:

    def __init__(self, width, height):
        self._size = [width, height]

        self._framebuffer = Framebuffer(True)
        self._renderbuffer = Renderbuffer(size=self._size)
        self._texture = Texture_new(*self._size)

        self.build()

    def build(self):
        # self.bind()
        self._renderbuffer.build()
        self._texture.build()
        self._framebuffer.build(self._texture, self._renderbuffer)

    def begin(self):
        self._framebuffer.bind()
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def end(self):
        self._framebuffer.unbind()
        pass


