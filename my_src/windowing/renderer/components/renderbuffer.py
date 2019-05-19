from numbers import Number

import numpy as np
import OpenGL.GL as gl

from .component_bp import RenderComponent

class Renderbuffer(RenderComponent):
    def __init__(self, size):
        self._glindex = None
        print('INIT RenderBuffer')
        self._size = size

    def build(self):
        self._glindex = gl.glGenRenderbuffers(1)

        self.bind()
        # initial setting
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT, self._size[0],self._size[1])

        self.unbind()

    def bind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self._glindex)

    def unbind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)