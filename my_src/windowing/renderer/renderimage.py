import OpenGL.GL as gl
from .components.framebuffer import Framebuffer
from .components.renderbuffer import Renderbuffer
from .components.texture import Texture_new
from ..frame_buffer_like import FBL
from ..viewport.viewport import Viewport
from patterns.update_check_descriptor import UCD

class Renderimage(FBL):
    _size = UCD()
    def __init__(self, width, height):
        self._size = [width, height]

        self._framebuffer = Framebuffer(True)
        self._renderbuffer = Renderbuffer(size=self._size)
        self._texture = Texture_new(*self._size)

        self._default_viewport = Viewport(0,0,width,height)

        self.build()

    def build(self):
        # self.bind()
        self._renderbuffer.build()
        self._texture.build()
        self._framebuffer.build(self._texture, self._renderbuffer)

    def begin(self):
        FBL.set_current(self)

        self._framebuffer.bind()

        self._default_viewport.open()

        # gl.glClearColor(0,1,1,1)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def end(self):
        self._framebuffer.unbind()
        pass

    @property
    def texture(self):
        return self._texture

    @property
    def width(self):
        return self._size[0]
    @property
    def height(self):
        return self._size[1]
    @property
    def size(self):
        return self._size