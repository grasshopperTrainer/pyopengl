from numbers import Number
import ctypes
import glfw
import numpy as np
import weakref
# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

from .component_bp import RenderComponent

class Framebuffer(RenderComponent):
    def __init__(self):
        self._color_attachments = weakref.WeakValueDictionary()

        self._depth_attachment = None
        self._stencil_attachment = None


        self._context = None
        self._glindex = None

    def build(self, context):
        if context is None:
            self._context = Unique_glfw_context.get_current()
        else:
            self._context = context

        with self._context as gl:
            self._glindex = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)

            gl.glEnable(gl.GL_SCISSOR_TEST)

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def bind_color_attachment(self, color_attachment, pos):
        # bind color_attachments
        with self._context as gl:
            attachment = eval(f'gl.GL_COLOR_ATTACHMENT{pos}')
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)
            gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,
                                    attachment,
                                    color_attachment._glindex,
                                    0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self._color_attachments[attachment] = color_attachment

    def bind_depth_attachment(self, depth_attachment):
        with self._context as gl:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)
            gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,
                                         gl.GL_DEPTH_ATTACHMENT,
                                         gl.GL_RENDERBUFFER,
                                         depth_attachment._glindex)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self._depth_attachment = weakref.ref(depth_attachment)

    def bind_stencil_attachment(self, stencil_attachment):
        # stencil
        with self._context as gl:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)
            gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,
                                         gl.GL_STENCIL_ATTACHMENT,
                                         gl.GL_RENDERBUFFER,
                                         stencil_attachment._glindex)
            gl.glEnable(gl.GL_STENCIL_TEST)
            gl.glClear(gl.GL_STENCIL_BUFFER_BIT)

        self._stencil_attachment = weakref.ref(stencil_attachment)

    def check_status(self):
        s = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if s != gl.GL_FRAMEBUFFER_COMPLETE:
            raise Exception('building frame buffer failed')

    def bind(self):
        with self._context as gl:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)

    def unbind(self):
        with self._context as gl:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def delete(self):
        if self._glindex != None:
            with self._context as gl:
                gl.glDeleteFramebuffers(1, self._glindex)
            self._glindex = None
            self._context = None

    def __del__(self):
        if self._glindex != None:
            self.delete()