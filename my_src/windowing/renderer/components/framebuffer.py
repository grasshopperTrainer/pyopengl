from numbers import Number

import numpy as np
import OpenGL.GL as gl

from .component_bp import RenderComponent

class Framebufer(RenderComponent):
    def __init__(self,init_sign):
        self._glindex = None
        print('INIT FRAME BUFFER')
        self.build()

    def build(self):
        self._glindex = gl.glGenFramebuffers(1)
        print(self._glindex)

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glindex)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)