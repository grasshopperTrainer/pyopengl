# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from ..my_openGL.unique_glfw_context import Unique_glfw_context
from ..renderer import components as comp
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
    _drawmode = None

    _context_registry = None

    @classmethod
    def use_shader(cls, shader):
        if not isinstance(shader, comp.Shader):
            raise TypeError
        elif shader._context != None:
            raise
        cls._shader = shader

    @classmethod
    def use_index_buffer(cls, index_buffer):
        if not isinstance(index_buffer, comp.Indexbuffer):
            raise
        elif index_buffer._context != None:
            raise

        cls._index_buffer = index_buffer

    @classmethod
    def use_vertex_array(cls, vertex_array):
        if not isinstance(vertex_array, comp.Vertexarray):
            raise TypeError
        elif vertex_array._context != None:
            raise

        cls._vertex_array = vertex_array

    @classmethod
    def use_vertex_buffer(cls, vertex_buffer):
        if not isinstance(vertex_buffer, comp.Vertexbuffer):
            raise TypeError
        elif vertex_buffer._context != None:
            raise

        cls._vertex_buffer = vertex_buffer

    @classmethod
    def use_texture(cls):
        cls._texture = comp.Texture()

    @classmethod
    def use_render_unit(cls, vao_vbo=True, index=False, new_texture=False, loaded_texture=False):
        if vao_vbo:
            cls._vertex_array = cls.Vertexarray
            cls._vertex_buffer = cls.Vertexbuffer

        cls._index_buffer = cls.Indexbuffer if index else cls._index_buffer

        if all((new_texture, loaded_texture)):
            raise
        if new_texture:
            cls._texture = comp.Texture_new
        elif loaded_texture:
            cls._texture = comp.Texture_load

    @classmethod
    def use_drawmode_triangle_strip(cls):
        cls._drawmode = Unique_glfw_context.GL_TRIANGLE_STRIP


    def new_render_unit(self):
        return self._render_unit_class()

    def __init__(self, name: str = None, **kwargs):
        # check shader-context-existence
        if self._shader == None:
            raise SyntaxError('Shader not fed')
        if self._drawmode == None:
            raise SyntaxError('Drawmode not fed')

        # build a registry per newly build class
        # -not referenced class Render_template itself
        if self.__class__._context_registry is None:
            self.__class__._context_registry = weakref.WeakKeyDictionary()

        # self._render_units = {}
        self._MM = np.eye(4)

        self._flag_draw = True
        self._flag_run = True

        # check context and register
        cls = self.__class__
        context = Unique_glfw_context.get_current()
        if context is None:
            raise
        self._context = weakref.ref(context)
        # store template components
        if context not in cls._context_registry:
            form = namedtuple('renderer_component',
                              ['shader',
                               'vertex_array',
                               'vertex_buffer',
                               'index_buffer',
                               'texture',
                               'shader_io'])
            renderer_components = [cls._shader, cls._vertex_array, cls._vertex_buffer, cls._index_buffer, cls._texture, None]
            for i, comp in enumerate(renderer_components):
                if comp != None and not isinstance(comp, type):
                    renderer_components[i] = copy.deepcopy(comp)
                    renderer_components[i].build(context)
            cls._context_registry[context] = form(*renderer_components)

        # build a unit set, save it in instance
        base_components = cls._context_registry[context]

        for n,v in zip(base_components._fields, base_components):
            if v is None:
                exec(f'self._{n} = None')
            elif isinstance(v, type):
                # decoder for **kwargs
                args_to_feed = {}
                for args_name, value in kwargs.items():
                    if f'{n}_' in args_name:
                        args_to_feed[args_name.replace(f'{n}_','')] = value

                exec(f'self._{n} = v(**args_to_feed)')
                exec(f'self._{n}.build(context)')
            else:
                exec(f'self._{n} = v')
                if eval(f'self._{n}._glindex is None'):
                    raise

        if not all(i != None for i in (self._vertex_array, self._vertex_buffer)):
            # TODO handle condition no vertex array or vertex buffer
            #   can it be that way?
            raise
        # this always need to be seperate
        self._shader_io = self._shader.io_type(self._shader, self._vertex_array, self._vertex_buffer)
        # if vao_vbo is global
        # if isinstance(cls._vertex_array, self.Vertexarray):
        #     cls.shader_io = self._shader_io

        self._draw_scissor = []

    @property
    def context(self):
        if self._context() is None:
            raise
        return self._context()

    @property
    def shader_io(self):
        return self._shader_io

    def draw(self, comment=''):

        if self.flag_draw:
            if Unique_glfw_context.get_current() != self.context:
                raise
            self.shader_io.capture_push_value()
            self.context.render_unit_add(self,comment)

    def _draw_(self, context, frame, viewport):
        # binding
        if self.context != context:
            raise

        self._shader.bind()
        if self._vertex_array != None:
            self._vertex_array.bind()
            if not context._spec_vao_stores_ibo:
                if self._index_buffer != None:
                    self._index_buffer.bind()
        else:
            if self._vertex_buffer != None:
                self._vertex_buffer.bind()
            if self._index_buffer != None:
                self._index_buffer.bind()
        if self._texture != None:
            self._texture.bind()

        if hasattr(self.shader_io, 'PM'):
            self.shader_io.PM = viewport.camera.PM
        if hasattr(self.shader_io, 'VM'):
            self.shader_io.VM = viewport.camera.VM
        if hasattr(self.shader_io, 'u_id_color'):
            color_id = frame.render_unit_registry.register(self)
            self.shader_io.u_id_color = color_id  # push color

        self.shader_io.push_all(context)

        if self._draw_scissor:
            context.glScissor(*self._draw_scissor)
        # TODO how to store drawing conditing inside unit?
        context.glDrawElements(context.GL_TRIANGLE_STRIP, self._index_buffer.count, self._index_buffer.gldtype, None)

    def draw_scissor(self, posx=None, posy=None, width=None, height=None):
        if any(i is None for i in (posx, posy, width, height)):
            self._draw_scissor = []
        else:
            self._draw_scissor = posx, posy, width, height

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
    # @property
    # def vertex_buffer(self):
    #     return self._context_registry[Unique_glfw_context.get_current()]
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
    def __new__(cls, *args, **kwargs) -> Renderer_template:
        if cls is Renderer_builder:
            new_cls = type(f'Renderer_builder{cls.reg}', (Renderer_template,), {})
            cls.reg += 1
            return new_cls
