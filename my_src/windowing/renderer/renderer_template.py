# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.windows import Windows
from ..my_openGL.unique_glfw_context import Unique_glfw_context
from ..renderer import components as comp

from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..viewport.viewports import Viewport

import numpy as np
import weakref
import copy

# class VBO_layout:
#     def __init__(self, ident):
#         self.ident = ident
#
# class Layout_container:
#     MULTI_VBO = VBO_layout(0)
#     SINGLE_VBO = VBO_layout(1)
class Render_unit:
    pass

class Render_unit_builder:
    reg_count = 0
    def __new__(cls, *args, **kwargs):
        new_cls = type(f'Render_unit{cls.reg_count}', (Render_unit, Render_unit_temp, ), {})
        cls.reg_count += 1
        return new_cls


class Render_unit_temp:

    _init_list = []

    _context = None
    _shader = None
    _vertex_array = None
    _vertex_buffer = None
    _index_buffer = None
    _texture = None
    _hollow_comp = comp.RenderComponent()

    @classmethod
    def set_context(cls, context):
        cls._context = context

    @classmethod
    def use_shader(cls, shader=None):
        if shader is None:
            cls._shader = comp.Shader()
        else:
            cls._shader = shader
    @classmethod
    def use_vertex_array(cls,vao=None):
        if vao is None:
            cls._vertex_array = comp.Vertexarray
        else:
            cls._vertex_array = vao

    @classmethod
    def use_vertex_buffer(cls,vbo=None):
        if vbo is None:
            cls._vertex_buffer = comp.Vertexbuffer
        else:
            cls._vertex_buffer = vbo

    @classmethod
    def use_index_buffer(cls,ibo=None):
        if ibo is None:
            cls._index_buffer = comp.Indexbuffer
        else:
            cls._index_buffer = ibo

    @classmethod
    def use_texture(cls,texture=None):
        if texture is None:
            cls._texture = comp.Texture
        else:
            cls._texture = texture

    @property
    def shader(self):
        if self._shader is None:
            return self.__class__._hollow_comp
        else:
            return self._shader

    @property
    def vertex_array(self):
        if self._vertex_array is None:
            return self.__class__._hollow_comp
        else:
            return self._vertex_array

    @property
    def vertex_buffer(self):
        if self._vertex_buffer is None:
            return self.__class__._hollow_comp
        else:
            return self._vertex_buffer

    @property
    def index_buffer(self):
        if self._index_buffer is None:
            return self.__class__._hollow_comp
        else:
            return self._index_buffer

    @property
    def texture(self):
        if self._texture is None:
            return self.__class__._hollow_comp
        else:
            return self._texture

    def __init__(self):
        shader = self.__class__._shader
        # generate instance
        # components can have three state 1. as a type 2. as a None 3. as a exterior object or
        cls = self.__class__
        context = shader._context

        self._use_my_vertex_array = False
        if isinstance(cls._vertex_array, type):
            vertex_array = cls._vertex_array()
            vertex_array.build(context)
            self._use_my_vertex_array = True
        elif cls._vertex_array is None:
            vertex_array = self._hollow_comp
        else:
            vertex_array = self._vertex_array

        self._use_my_vertex_buffer = False
        if isinstance(cls._vertex_buffer, type):
            vertex_buffer = cls._vertex_buffer()
            vertex_buffer.build(context)
            self._use_my_vertex_buffer = True
        elif cls._vertex_buffer is None:
            vertex_buffer = self._hollow_comp
        else:
            vertex_buffer = self._vertex_buffer
        # bind shader and vao_vbo_pair
        shader_attribute = self._shader.input_type(vertex_array, vertex_buffer, shader)

        self._use_my_index_buffer= False
        if isinstance(cls._index_buffer, type):
            index_buffer = cls._index_buffer()
            index_buffer.build(context)
            self._use_my_index_buffer= True
        elif cls._index_buffer is None:
            index_buffer = self._hollow_comp
        else:
            index_buffer = self._index_buffer

        self._use_my_texture= False
        if isinstance(cls._texture, type):
            texture = cls._texture()
            texture.build(context)
            self._use_my_texture= True
        elif cls._texture is None:
            texture = self._hollow_comp
        else:
            texture = self._texture
        # print(self._vertex_array._glindex)
        # print(self._vertex_buffer._glindex)
        # print(self._index_buffer._glindex)
        #
        # exit()
        self._context_dict = weakref.WeakKeyDictionary()
        self._context_dict[Unique_glfw_context.get_current()] = [shader, vertex_array, vertex_buffer, index_buffer, texture, shader_attribute]

    def __del__(self):
        for shader, vao, vbo, ibo, tex, att in self._context_dict.values():
            if self._use_my_index_buffer:
                ibo.delete()
            if self._use_my_texture:
                tex.delete()
            if self._use_my_vertex_array:
                vao.delete()
            if self._use_my_vertex_buffer:
                vbo.delete()

    # def build(self):
        # # build rest of
        #
        # with self._context as context:
        #     if not self.shader.is_built:
        #         self.shader.build(context)
        #
        #     self.vertex_array.build(context)
        #     self.vertex_array.bind()
        #
        #     self.index_buffer.build(context)
        #     self.vertex_buffer.build(context)
        #
        #     self.vertex_array.unbind()
        #
        #     self.texture.build(context)

    # def _build_(self):
    #     # if not self.shader.is_built:
    #     #     self.shader.build()
    #
    #     self.vertex_array.build()
    #     self.vertex_array.bind()
    #
    #     self.index_buffer.build()
    #     self.vertex_buffer.build()
    #
    #     self.vertex_array.unbind()
    #
    #     self.texture.build()


    def bind(self):
        context = Unique_glfw_context.get_current()
        if context not in self._context_dict:
            self.rebuild(context)

        shader, vao, vbo, ibo, tex, att = self._context_dict[context]
        # if not self._flag_built:
        #     # self._build_()
        #     self._flag_built = True
        with context as gl:
            shader.bind()

            if isinstance(vao, comp.Vertexarray):
                vao.bind()
                if not gl.vao_stores_ibo:
                    ibo.bind()
            else:
                vbo.bind()
                ibo.bind()

            tex.bind()

    def rebuild(self, new_context):
        shader, vertex_array, vertex_buffer, index_buffer, texture, shader_attribute = list(self._context_dict.values())[0]
        new_shader = copy.copy(shader)
        new_vertex_array = copy.copy(vertex_array)
        new_vertex_buffer= copy.copy(vertex_buffer)
        new_index_buffer= copy.copy(index_buffer)
        new_texture = copy.copy(texture)

        new_shader.build(new_context)
        new_vertex_array.build(new_context)
        new_vertex_buffer.build(new_context)
        new_index_buffer.build(new_context)
        new_texture.build(new_context)

        new_shader_attribute = shader_attribute.copy(new_vertex_array, new_vertex_buffer, new_shader)
        self._context_dict[new_context] = [new_shader, new_vertex_array, new_vertex_buffer, new_index_buffer, new_texture, new_shader_attribute]
        # print('-------------')
        # with new_context as gl:
        #     print(new_context)
        #     print(gl.original_gl.glGenBuffers(1))
        #
        #
        # print(self._shader, id(self._shader))
        # print(self._vertex_array)
        # print(self._vertex_buffer)
        # print(self._index_buffer)
        # print(self._texture)
        # print('-------------')
        # print(new_context)
        # print(Windows.get_current())
        # raise
        # raise
    @property
    def shader_attribute(self):
        current_c = Unique_glfw_context.get_current()
        if current_c not in self._context_dict:
            # print(Unique_glfw_context.get_current())
            self.rebuild(current_c)

        return self._context_dict[current_c][-1]

    def report_to_stack(self):
        current_c = Unique_glfw_context.get_current()
        if current_c not in self._context_dict:
            self.rebuild(current_c)
        # print(Windows.get_current(), current_c, self, FBL.get_current(), Viewport.get_current())
        current_c.stack_render_unit((self, FBL.get_current(), Viewport.get_current(), 0))


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

    class Shader:
        pass

    class VertexBuffer:
        pass

    class Indexbuffer:
        pass

    class Texture:
        pass

    Shader = comp.Shader
    Vertexbuffer = comp.Vertexbuffer
    Indexbuffer = comp.Indexbuffer
    Texture = comp.Texture
    # layout = Layout_container
    _vertex_array = None
    _vertex_buffer = None
    _index_buffer = None
    _texture = None

    @classmethod
    def use_shader(cls, shader):
        if isinstance(shader, comp.Shader):
            cls._shader = shader
        else:
            raise TypeError

    @classmethod
    def use_index_buffer(cls, index_buffer):
        if isinstance(index_buffer, comp.Indexbuffer):
            cls._index_buffer = index_buffer
        else:
            raise TypeError

    @classmethod
    def use_texture(cls):
        cls._texture = comp.Texture()

    @classmethod
    def use_render_unit(cls, vao=True, vbo=True, index=False, texture=False):
        cls._use_render_unit_vao = vao
        cls._use_render_unit_vbo = vbo
        cls._use_render_unit_index = index
        cls._use_render_unit_texture = texture

        # ru = Render_unit_builder()
        #
        # ru.use_shader(cls._shader)
        # ru.use_vertex_array() if vao else ru.use_vertex_array(cls._vertex_array)
        # ru.use_vertex_buffer() if vbo else ru.use_vertex_buffer(cls._vertex_buffer)
        # ru.use_index_buffer() if index else ru.use_index_buffer(cls._index_buffer)
        # ru.use_texture() if texture else ru.use_texture(cls._texture)
        #
        # cls._render_unit_class = ru

    @classmethod
    def use_triangle_strip_draw(cls):
        cls._drawmode = Unique_glfw_context.GL_TRIANGLE_STRIP


    def new_render_unit(self):
        # check for context first call
        glfw_context = Unique_glfw_context.get_current()
        reg = self._context_register
        # print(list(glfw_context._windows.items()))

        if glfw_context not in reg:
            render_unit_class = Render_unit_builder(glfw_context)

            shader = copy.copy(self._shader)
            shader.build(glfw_context)
            render_unit_class.use_shader(shader)

            if self._use_render_unit_index:
                reunder_unit_class.use_index_buffer()
            else:
                if self._index_buffer != None:
                    new_index_buffer = copy.deepcopy(self._index_buffer)
                    new_index_buffer.build(glfw_context)
                    render_unit_class.use_index_buffer(new_index_buffer)

            if self._use_render_unit_texture:
                render_unit_class.use_texture()
            else:
                if self._texture != None:
                    new_texture = copy.deepcopy(self._index_buffer)
                    new_texture.build(glfw_context)
                    render_unit_class.use_texture(new_texture)

            if self._use_render_unit_vao:
                render_unit_class.use_vertex_array()
            else:
                if self._vertex_array != None:
                    new_vertex_array = copy.deepcopy(self._vertex_array)
                    new_vertex_array.build(glfw_context)
                    render_unit_class.use_vertex_array(new_vertex_array)

            if self._use_render_unit_vbo:
                render_unit_class.use_vertex_buffer()
            else:
                if self._vertex_buffer != None:
                    new_vertex_buffer = copy.deepcopy(self._vertex_buffer)
                    new_vertex_buffer.build(glfw_context)
                    render_unit_class.use_vertex_buffer(new_vertex_buffer)

            reg[glfw_context] = render_unit_class
        ru = reg[glfw_context]()
        # exit()
        return ru

    def __init__(self, name: str = None):
        # check shader-context-existence
        if not (hasattr(self, '_shader') and hasattr(self, '_drawmode')):
            raise Exception('Not enough comp fed.')

        # self._render_units = {}
        self._context_register = weakref.WeakKeyDictionary()

        self._MM = np.eye(4)

        self._flag_draw = True
        self._flag_run = True

        # default layer setting
        # self.current_window.layer[0].add(self)

    # def set_layout(self, const):
    #     if isinstance(const,VBO_layout):
    #         self._vbo_layout = const
    #     else:
    #         raise TypeError("should use instance's.const.(CORRECT_TYPE_CONST)")

    @property
    def shader(self):
        return self.__class__._shader
    @property
    def vertex_array(self):
        if hasattr(self,'_vertex_array'):
            return self._vertex_array
        else:
            return comp.RenderComponent

    @property
    def vertex_buffer(self):
        if hasattr(self, '_vertex_buffer'):
            return self._vertex_buffer
        else:
            return comp.RenderComponent

    @property
    def index_buffer(self):
        if hasattr(self, '_index_buffer'):
            return self._index_buffer
        else:
            return comp.RenderComponent

    @property
    def texture(self):
        if hasattr(self, '_texture'):
            return self._texture
        else:
            return comp.RenderComponent

    # def _check_shader_build(self):
    #     # check for context first call
    #     glfw_context = Unique_glfw_context.get_current()
    #     reg = self._context_register
    #
    #     if glfw_context not in reg:
    #         # generate class_singular gl components for the first call
    #         self._shader.build()
    #         if hasattr(self, '_index_buffer'):
    #             self._index_buffer.build()
    #         if hasattr(self, '_texture'):
    #             self._texture.build()
    #         reg.append(glfw_context)

    def _draw_(self, render_unit:Render_unit_temp, fbl = None):
        # self._check_shader_build()

        # actual draw
        # FBL.get_current().render_unit_registry.register(render_unit)
        # render_unit.bind()

        if self.flag_draw:
            # Automated condition can't be set
            # for example) if first draw is ignored and second draw is run
            # to have similar frame to swap, ignored first has to be drawn before second
            # which is nonsence.
            # To avoid this window drawn on has to check every renderer before any draw call is made
            # and if any draw call is evaluated to be called all other draw call on window has to be called

            # TODO BUT if viewport is consistent window could just copy from front buffer partially and paste it
            #      on the current drawing(back) buffer. This won't effect another viewport beeing refreshed.
            #      If this makes thing faster this is worth a strategy.
            #      Implement this.
            if True:
                ibo = render_unit.index_buffer
                if ibo.count != 0:  # draw a thing

                    render_unit.report_to_stack()
                            # print(render_unit._context)
                            # exit()
                            #
                            # render_unit.shader_attribute.PM = Viewport.get_current().camera.PM
                            # render_unit.shader_attribute.VM = Viewport.get_current().camera.VM
                            # # get id color
                            # if hasattr(render_unit.shader_attribute,'u_id_color'):
                            #     color_id = fbo.render_unit_registry.id_color(render_unit) + [1,]
                            #     render_unit.shader_attribute.u_id_color = color_id # push color
                            # gl.glDrawElements(self.drawmode, ibo.count, ibo.gldtype, None)
                    # fbo.end()

            # TODO is this unnecessary processing? checking?
            # self._unbind_global()

    def _unbind_global(self):
        self.shader.unbind()
        self.vertex_array.unbind()
        self.vertex_buffer.unbind()
        self.index_buffer.unbind()
        self.texture.unbind()

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
