from .renderer.components import *
from .frame_buffer_like.frame_buffer_like_bp import FBL
from .my_openGL.glfw_gl_tracker import Trackable_openGL as gl
import numpy as np
class Frame(FBL):
    def __init__(self, width, height):
        self._size = width, height
        self._frame_buffer = Framebuffer()
        self._color_attachments = []
        self._depth_attachment = None
        self._stencil_attachment = None

        self._flag_color_use = False
        self._flag_depth_use = False
        self._flag_stencil_use = False

        self._flag_built = False

    def build(self):
        if not (self._flag_color_use or self._flag_depth_use or self._flag_stencil_use):
            raise

        self._stencil_attachment.build()
        self._depth_attachment.build()
        for i in self._color_attachments:
            i.build()

        self._frame_buffer.build(self._color_attachments, self._depth_attachment, self._stencil_attachment)

        self._flag_built = True

    def rebuild(self):
        pass

    def bind(self):
        pass

    def unbind(self):
        pass

    def begin(self):
        # FBL.set_current(self)
        if not self._flag_built:
            raise

        self._frame_buffer.bind()


    def end(self):
        self._frame_buffer.unbind()

    @property
    def width(self):
        return self._size[1]
    @property
    def height(self):
        return self._size[0]
    @property
    def size(self):
        return self._size

    def use_color_attachment(self, slot):
        self._flag_color_use = True
        texture = Texture_new(self._size[0],self._size[1],slot)
        self._color_attachments.append(texture)
        return texture

    def use_depth_attachment(self,bitdepth):
        if bitdepth not in [16,24,32,'32F']:
            raise ValueError('bit depth can be 16,24,32 or 32F')

        self._flag_depth_use = True
        internalformat = f'Renderbuffer.GL_DEPTH_COMPONENT{bitdepth}'

        render = Renderbuffer(self._size[0],self._size[1], eval(internalformat))
        self._depth_attachment = render
        return render

    def use_stencil_attachment(self, bitdepth):
        if bitdepth not in [1,4,8,16]:
            raise ValueError('bit depth can be 1,4,8 or 16')
        self._flag_stencil_use = True

        internalformat = f'Renderbuffer.GL_STENCIL_INDEX{bitdepth}'
        render = Renderbuffer(self._size[0],self._size[1],eval(internalformat))
        self._stencil_attachment = render
        return render

    @property
    def color_attachment(self):
        return self._color_attachments
    @property
    def depth_attachment(self):
        return self._depth_attachment
    @property
    def stencil_attachment(self):
        return self._stencil_attachment
