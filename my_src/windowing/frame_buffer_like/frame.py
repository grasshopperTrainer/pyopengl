from windowing.renderer.components import *
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
from .render_object_registry import Render_object_registry
from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from ..viewport.viewport import Viewport
from numbers import Number
import numpy as np


class Frame(FBL):
    def __init__(self, width, height):
        #typecheck
        if not isinstance(width, Number):
            raise TypeError
        if not isinstance(height, Number):
            raise TypeError

        # is_window_type = any([c.__name__ == 'Window' for c in window_binding.__class__.__mro__])
        # if not is_window_type:
        #     if window_binding != None:
        #         raise TypeError

        self._size = width, height
        # self._window_binding = window_binding

        self._frame_buffer = Framebuffer()
        self._color_attachments = []
        self._depth_attachment = None
        self._stencil_attachment = None

        self._flag_color_use = False
        self._flag_depth_use = False
        self._flag_stencil_use = False

        self._flag_built = False
        self._flag_something_rendered = False

        self._render_unit_registry = Render_object_registry(self)

    def __del__(self):
        print(f'gc, Frame {self}')

    def delete(self):
        print('deleting frame')
        self._stencil_attachment.delete()
        self._depth_attachment.delete()
        for i in self._color_attachments:
            i.delete()
        self._frame_buffer.delete()

    def build(self):
        if not (len(self._color_attachments) != 0 or self._depth_attachment != None or self._stencil_attachment != None):
            raise

        if self._depth_attachment != None:
            self._depth_attachment.build()
        if self._stencil_attachment != None:
            self._stencil_attachment.build()
        for i in self._color_attachments:
            i.build()

        self._frame_buffer.build(self._color_attachments, self._depth_attachment, self._stencil_attachment)

        self._flag_built = True

    def rebuild(self, width, height):
        self._size = width, height
        for i in self._color_attachments:
            i.rebuild(width, height)
        if self._depth_attachment != None:
            self._depth_attachment.rebuild(width, height)
        if self._stencil_attachment != None:
            self._stencil_attachment.rebuild(width, height)

        self.build()

    def __enter__(self):
        # FBL.set_current(self)
        if not self._flag_built:
            raise
        self._frame_buffer.bind()
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        # if clear is set
        if Viewport.get_current()._flag_clear:
            vp = Viewport.get_current()
            # clear id color to black
            gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT1)
            gl.glClearColor(0,0,0,0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            # clear ambient color
            gl.glClearColor(*vp.clear_color)
            gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)
            vp.fillbackground()
            # reset draw buffer for comming drawing
            self.bindDrawBuffer()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flag_something_rendered = True

    def bindDrawBuffer(self):
        at = [gl.GL_COLOR_ATTACHMENT0 + i for i in range(len(self._color_attachments))]
        at + [gl.GL_DEPTH_ATTACHMENT, gl.GL_STENCIL_ATTACHMENT]
        gl.glDrawBuffers(len(self._color_attachments), at)

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
        return self._size[0]
    @property
    def height(self):
        return self._size[1]
    @property
    def size(self):
        return self._size
    @property
    def flag_something_rendered(self):
        return self._flag_something_rendered
    @flag_something_rendered.setter
    def flag_something_rendered(self, v):
        if isinstance(v, bool):
            self._flag_something_rendered = v
        else:
            raise
    @property
    def render_unit_registry(self):
        return self._render_unit_registry

    def use_color_attachment(self, slot):
        texture = Texture_new(self._size[0],self._size[1],slot)
        self._color_attachments.append(texture)
        return texture

    def use_depth_attachment(self,bitdepth):
        if bitdepth not in [16,24,32,'32F']:
            raise ValueError('bit depth can be 16,24,32 or 32F')

        internalformat = f'Renderbuffer.GL_DEPTH_COMPONENT{bitdepth}'

        render = Renderbuffer(self._size[0],self._size[1], eval(internalformat))
        self._depth_attachment = render
        return render

    def use_stencil_attachment(self, bitdepth):
        if bitdepth not in [1,4,8,16]:
            raise ValueError('bit depth can be 1,4,8 or 16')

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
