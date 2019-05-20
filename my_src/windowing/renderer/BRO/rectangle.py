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

        self._rect = RenderUnit()

        self._build_()

    def _build_(self):
        self._rect.bind_shader(file_name='BRO_rectangle')
        self._rect.bind_indexbuffer(glusage=self._rect.GL_DYNAMIC_DRAW)
        self._rect.bind_vertexbuffer(glusage=self._rect.GL_DYNAMIC_DRAW)
        self._rect.property['a_texCoord'][0:4] = [0,0],[1,0],[1,1],[0,1]
        self._rect.property['texSlot'] = 0

    def _draw_(self):
        self._rect.property['u_size'] = self._size
        self._rect.property['a_position'][0:4] = self.vertex
        self._rect.property['u_edgeweight'] = self.edgeweight
        self._rect.property['u_fillcol'] = self.fillcol
        self._rect.property['u_edgecol'] = self.edgecol
        # global updates

        self._rect.draw()

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

    def draw_texture(self, texture):
        if isinstance(texture, str):
            self._rect.bind_texture(texture)

        elif isinstance(texture, Texture):
            self._rect.texture = texture
            self._rect.property['useTexture'] = True

        else:
            raise TypeError
