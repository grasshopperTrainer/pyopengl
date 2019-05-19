from numbers import Number
import ctypes

import numpy as np
import OpenGL.GL as gl

from .component_bp import RenderComponent

class Framebuffer(RenderComponent):
    def __init__(self,init_sign):
        self._glindex = None
        print('INIT FRAME BUFFER')

    def build(self,texture, renderbuffer):
        self._glindex = gl.glGenFramebuffers(1)

        # texture.bind()
        # renderbuffer.bind()
        # bind texture
        self.bind()
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,
                                  gl.GL_COLOR_ATTACHMENT0,
                                  gl.GL_TEXTURE_2D,
                                  texture._glindex,
                                  0)
        # bind render buffer such as depth buffer
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER,
                                     gl.GL_DEPTH_ATTACHMENT,
                                     gl.GL_RENDERBUFFER,
                                     renderbuffer._glindex)

        s = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if s != gl.GL_FRAMEBUFFER_COMPLETE:
            raise Exception('building frame buffer failed')

        self.unbind()

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)


    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)