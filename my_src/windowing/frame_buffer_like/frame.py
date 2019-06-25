from windowing.renderer.components import *
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
from .render_object_registry import Render_object_registry
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
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
        self._context = None

    def __del__(self):
        print(f'gc, Frame {self}')

    def delete(self):
        print('deleting frame')
        self._stencil_attachment.delete()
        self._depth_attachment.delete()
        for i in self._color_attachments:
            i.delete()
        self._frame_buffer.delete()

    def build(self, context):
        if not (len(self._color_attachments) != 0 or self._depth_attachment != None or self._stencil_attachment != None):
            raise

        self._context = context
        with self._context:

            if self._depth_attachment != None:
                self._depth_attachment.build(context)
            if self._stencil_attachment != None:
                self._stencil_attachment.build(context)
            for i in self._color_attachments:
                i.build(context)

            self._frame_buffer.build(context)
            self._frame_buffer.bind_color_attachment(self._color_attachments[0], 0)
            self._frame_buffer.bind_color_attachment(self._color_attachments[1], 1)
            self._frame_buffer.bind_depth_attachment(self._depth_attachment)
            self._frame_buffer.bind_stencil_attachment(self._stencil_attachment)


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
        if self._context is None:
            raise

        with self._context as gl:
            self._frame_buffer.bind()
            # if clear is set
            if Viewport.get_current()._flag_clear:
                vp = Viewport.get_current()
                # clear all color attachment color
                self.bindDrawBuffer()
                vp.fillbackground()
                # clear id color to black
                gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT1)
                gl.glClearColor(0,0,0,0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                self.bindDrawBuffer()
                # reset draw buffer for comming drawing
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._flag_something_rendered = True

    def bindDrawBuffer(self):
        with self._context as gl:
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
