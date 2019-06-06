from numbers import Number
import ctypes

import numpy as np
from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl

from .component_bp import RenderComponent

class Framebuffer(RenderComponent):
    def __init__(self):
        self._glindex = None
        self._color_attachments = []
        self._depth_attachment = None
        self._stencil_attachment = None

        self._bufs = None

    def build(self,color_attachments=None, depth_attachment=None, stencil_attachment=None):
        self._color_attachments = color_attachments
        self._depth_attachment = depth_attachment
        self._stencil_attachment = stencil_attachment

        self._glindex = gl.glGenFramebuffers(1)
        self.bind()
        bufs = []
        # bind color_attachments
        if color_attachments != None:
            if not isinstance(color_attachments, (list, tuple)):
                color_attachments = [color_attachments]
            for i,att in enumerate(color_attachments):
                attachment = eval(f'gl.GL_COLOR_ATTACHMENT{i}')
                bufs.append(attachment)

                gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,
                                        attachment,
                                        att._glindex,
                                        0)

            # fragment output follows attachment number
            gl.glDrawBuffers(len(bufs),bufs)
            self._bufs= bufs
            # print(bufs)
            # exit()

        # bind render buffer such as depth buffer
        if depth_attachment != None:
            gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,
                                         gl.GL_DEPTH_ATTACHMENT,
                                         gl.GL_RENDERBUFFER,
                                         depth_attachment._glindex)
        # stencil
        if stencil_attachment != None:
            gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,
                                         gl.GL_STENCIL_ATTACHMENT,
                                         gl.GL_RENDERBUFFER,
                                         stencil_attachment._glindex)



        s = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if s != gl.GL_FRAMEBUFFER_COMPLETE:
            raise Exception('building frame buffer failed')

        # enableing is per framebuffer
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_STENCIL_TEST)

        # clear, expecially claring depth buffer is important
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.unbind()

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def delete(self):
        gl.glDeleteFramebuffers(1, self._glindex)