# from .basic_render_object import *
from ..components.texture import Texture_new, Texture_load, Texture
import OpenGL.GL as gl

import numpy as np
from ...renderer.components import *
from patterns.store_instances_dict import SID
from ...viewport.viewport import Viewport
from ..render_unit import RenderUnit

class TestBRO():

    def __init__(self):
        # Render_unit_builder.load_shader(path_or_name='BRO_rectangle')
        self.a = RenderUnit()
        self.a.use_shader(self.a.components.Shader('BRO_rectangle', 'a TestBRO'))
        self.a.use_vertexbuffer()
        self.a.use_indexbuffer()
        self.a.use_texture()


    def draw(self):
        self.a.property['a_position'][0:4] = [0,0],[100,0],[100,100],[0,100]
        self.a.property['u_fillcol'] = [1,0,1,1]

        self.a.property['useTexture'] = False
        self.a.property['texSlot'] = 0

        # print(self.a._vertexbuffer._data)
        # exit()
        self.a._draw_()

# class Render_unit_builder(SID):
#
#     def __init__(self, path_or_name):
#         self._glsl_path = path_or_name
#         self._loaded_shader = Shader(path_or_name)

# class Storage:
#
#     def __init__(self, path, shader):
#         pass
#
