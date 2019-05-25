from .basic_render_object import *
from ..components.texture import Texture_new, Texture_load, Texture
import OpenGL.GL as gl

import numpy as np

class Rectangle(BasicRenderObject):

    def __init__(self, pos = [0,0], size = [100,100], fillcol = None, edgecol = None, edgeweight = None):
        self._pos = np.array(pos)
        self._size = np.array(size)
        self._fillcol = fillcol
        self._edgecol = edgecol
        self._edgeweight = edgeweight

        r = Renderer_builder()
        self._renderer = r
        self._renderer.move(self._pos[0], self._pos[1], 0)

        r.set_shader(r.components.Shader('BRO_rectangle_with_edge', 'a Rectangle object'))
        r.use_vertexbuffer()
        r.use_indexbuffer()
        r.property['a_texCoord'][0:4] = [0, 0], [1, 0], [1, 1], [0, 1]
        r.property['texSlot'] = 0

    def draw(self):
        self._draw_()

    def _draw_(self):
        self._renderer.property['u_size'] = self._size
        self._renderer.property['a_position'][0:4] = self.vertex
        self._renderer.property['u_edgeweight'] = self.edgeweight
        self._renderer.property['u_fillcol'] = self.fillcol
        self._renderer.property['u_edgecol'] = self.edgecol
        # global updates

        self._renderer._draw_()

    def _hide_(self):
        pass

    def _stop_(self):
        pass

    @property
    def vertex(self):
        off = self.edgeweight / 2

        a = np.array((-off, -off))
        b = np.array((self._size[0] + off, -off))
        c = self._size + off
        d = np.array((-off, self._size[1] + off))
        return a,b,c,d

    @property
    def fillcol(self):
        if self._fillcol is None:
            return super().DEF_FILL_COLOR
        return self._fillcol

    @property
    def edgecol(self):
        if self._edgecol is None:
            return super().DEF_EDGE_COLOR
        return self._edgecol
    @property
    def edgeweight(self):
        if self._edgeweight is None:
            return super().DEF_EDGE_WEIGHT
        return self._edgeweight

    def render_texture(self, texture):
        if isinstance(texture, str):
            self._renderer.bind_texture(texture)

        elif isinstance(texture, Texture):
            self._renderer.texture = texture
            self._renderer.property['useTexture'] = True

        else:
            raise TypeError