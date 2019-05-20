import OpenGL.GL as gl
from .components.framebuffer import Framebuffer
from .components.renderbuffer import Renderbuffer
from .components.texture import Texture_new
from patterns.update_check_descriptor import UCD
from ..current_framebuffer import Current_framebuffer

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
        Current_framebuffer.set_current(self)
        self._framebuffer.bind()
        # gl.glClearColor(0,1,1,1)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def end(self):
        self._framebuffer.unbind()
        pass

    def crop_from_to(self):
        pass

    @property
    def texture(self):
        return self._texture

    @property
    def size(self):
        return self._size