# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.windows import Windows
from ..my_openGL.unique_glfw_context import Unique_glfw_context
from ..renderer import components as comp

from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..viewport.viewports import Viewport
from collections import namedtuple

import numpy as np
import weakref
import copy


class Renderer_template:
    """
    Pattern sould be determined:
    1. Renderer instance contain only one shadern
    Problem is the renderers. Should Renderer contain one renderers for each kinds
    or could it contain multiple renderers and switch between them while rendering?

    For now leave all be single: sinble shader, single vao,vbo,vio.

    """
    """
    
    -single shader
    -single vao - single vbo vertex pair
    -multiple vertex pair
    -single index buffer
    -no texture
    
    """
    GL_DYNAMIC_DRAW = Unique_glfw_context.GL_DYNAMIC_DRAW

    # just a shell for IDE
    class Shader:
        pass
    class Vertexarray:
        pass
    class Vertexbuffer:
        pass
    class Indexbuffer:
        pass
    class Texture:
        pass
    # Real component classes
    Shader = comp.Shader
    Vertexarray = comp.Vertexarray
    Vertexbuffer = comp.Vertexbuffer
    Indexbuffer = comp.Indexbuffer
    Texture = comp.Texture

    _shader = None
    _vertex_array = None
    _vertex_buffer = None
    _index_buffer = None
    _texture = None

    _context_registry = weakref.WeakKeyDictionary()

    @classmethod
    def use_shader(cls, shader):
        if isinstance(shader, comp.Shader):
            if shader._context != None:
                raise
            cls._shader = shader
        else:
            raise TypeError

    @classmethod
    def use_index_buffer(cls, index_buffer):
        if isinstance(index_buffer, comp.Indexbuffer):
            if index_buffer._context != None:
                raise

            cls._index_buffer = index_buffer
        else:
            raise TypeError

    @classmethod
    def use_texture(cls):
        cls._texture = comp.Texture()

    @classmethod
    def use_render_unit(cls, vao=True, vbo=True, index=False, texture=False):
        cls._vertex_array = cls.Vertexarray if vao else cls._vertex_array
        cls._vertex_buffer = cls.Vertexbuffer if vbo else cls._vertex_buffer
        cls._index_buffer = cls.Indexbuffer if index else cls._index_buffer
        cls._texture = cls.Texture if texture else cls._texture


    @classmethod
    def use_triangle_strip_draw(cls):
        cls._drawmode = Unique_glfw_context.GL_TRIANGLE_STRIP


    def new_render_unit(self):
        return self._render_unit_class()

    def __init__(self, name: str = None):
        # check shader-context-existence
        if not (hasattr(self, '_shader') and hasattr(self, '_drawmode')):
            raise Exception('Not enough comp fed.')

        # self._render_units = {}
        self._MM = np.eye(4)

        self._flag_draw = True
        self._flag_run = True

        # check context
        cls = self.__class__
        context = Unique_glfw_context.get_current()

        self._context = weakref.ref(context)

        if context not in cls._context_registry:
            form = namedtuple('renderer_component',
                              ['shader',
                               'vertex_array',
                               'vertex_buffer',
                               'index_buffer',
                               'texture', ])
            renderer_components = [cls._shader, cls._vertex_array, cls._vertex_buffer, cls._index_buffer, cls._texture]
            for i, comp in enumerate(renderer_components):
                if comp != None and not isinstance(comp, type):
                    renderer_components[i] = copy.deepcopy(comp)
                    renderer_components[i].build(context)

            cls._context_registry[context] = form(*renderer_components)

        base_components = cls._context_registry[context]

        # build a unit set, save it in instance
        for n,v in zip(base_components._fields, base_components):
            if v is None:
                exec(f'self._{n} = None')
            elif isinstance(v, type):
                exec(f'self._{n} = v()')
                exec(f'self._{n}.build(context)')
            else:
                exec(f'self._{n} = v')

        if not all(i != None for i in (self._vertex_array, self._vertex_buffer)):
            # TODO handle condition no vertex array or vertex buffer
            #   can it be that way?
            raise
        self._shader_io = self._shader.io_type(self._shader, self._vertex_array, self._vertex_buffer)

    @property
    def context(self):
        if self._context() is None:
            raise
        return self._context()

    @property
    def shader_io(self):
        return self._shader_io

    def bind(self):
        if self.context != Unique_glfw_context.get_current():
            raise

        self._shader.bind()
        if self._vertex_array != None:
            self._vertex_array.bind()
            if not Unique_glfw_context._spec_vao_stores_ibo:
                if self._index_buffer != None:
                    self._index_buffer.bind()
        else:
            if self._vertex_buffer != None:
                self._vertex_buffer.bind()
            if self._index_buffer != None:
                self._index_buffer.bind()
        if self._texture != None:
            self._texture.bind()

    def _draw_(self):
        if self.flag_draw:
            if Unique_glfw_context.get_current() != self.context:
                raise

            self.context.stack_render_unit((self, FBL.get_current(), Viewport.get_current(), 0))

    def _hide_(self, set=None):
        if set is None:
            self.flag_run = not self.flag_run
        else:
            self.flag_run = set

    def _stop_(self, set=None):
        if set is None:
            self.flag_draw = not self.flag_draw
        else:
            self.flag_draw = set

    def _reset_(self):
        self.flag_run = True
        self.flag_draw = True

    @property
    def name(self):
        return self._name

    @property
    def glsl_variables(self):
        return self.shader.variables

    @property
    def drawmode(self):
        return self.__class__._drawmode

    @drawmode.setter
    def drawmode(self, value):
        if isinstance(value, int):
            self.__class__._drawmode = value

    def print_va_info(self):
        return self._vertexarray

    @property
    def flag_draw(self):
        return self._flag_draw

    @flag_draw.setter
    def flag_draw(self, value):
        if isinstance(value, bool):
            self._flag_draw = value

    @property
    def flag_run(self):
        return self._flag_run

    @flag_run.setter
    def flag_run(self, value):
        if isinstance(value, bool):
            self._flag_run = value

    @property
    def MM(self):
        return self._MM

    def move(self, x, y, z):
        matrix = np.eye(4)
        matrix[:, 3] = x, y, z, 1

        self._MM = matrix.dot(self._MM)

    @property
    def property(self):
        return self.shader.properties


class Renderer_builder:
    reg = 0
    def __new__(cls, *args, **kwargs):
        if cls is Renderer_builder:
            new_cls = type(f'Renderer_builder{cls.reg}', (Renderer_template,), {})
            cls.reg += 1
            return new_cls
