import OpenGL.GL as gl
from windowing.renderer.components.framebuffer import Framebuffer
from windowing.renderer.components.renderbuffer import Renderbuffer
from windowing.renderer.components.texture import Texture_new
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
from windowing.viewport.viewport import Viewport

class Renderable_image(FBL):
    def __init__(self, width, height):
        self._size = [width, height]

        self._framebuffer = Framebuffer()
        self._renderbuffer = Renderbuffer(width, height,Renderbuffer.GL_DEPTH_COMPONENT)
        self._texture = Texture_new(*self._size, slot=1)

        self._default_viewport = Viewport(0,0,width,height)

        self._build()

    def _build(self):
        # self.bind()
        self._renderbuffer.build()
        self._texture.build()
        self._framebuffer.build(self._texture, self._renderbuffer)

    def rebuild(self,width, height):
        self._texture.delete()
        self._framebuffer.delete()
        self._renderbuffer.delete()

        self._framebuffer = Framebuffer()
        self._renderbuffer = Renderbuffer(width, height)
        self._texture = Texture_new(width, height, slot=1)

        self._build()

    def begin(self):
        # FBL.set_current(self)

        self._framebuffer.bind()

        self._default_viewport.open()

        # gl.glClearColor(0,1,1,1)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_STENCIL_BUFFER_BIT)

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