import glfw
from ..gl_tracker import Trackable_openGL as gl

from ..renderer import components as comp
import ctypes

from patterns.update_check_descriptor import UCD
from ..window import Window
from ..renderable_image import Renderable_image
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..viewport.viewports import Viewport
from .components.glsl_property_container import Glsl_property_container

from collections import namedtuple
import numpy as np
import weakref

# class VBO_layout:
#     def __init__(self, ident):
#         self.ident = ident
#
# class Layout_container:
#     MULTI_VBO = VBO_layout(0)
#     SINGLE_VBO = VBO_layout(1)

class Render_unit_builder:
    reg_count = 0
    def __new__(cls, *args, **kwargs):
        new_cls = type(f'Render_unit{cls.reg_count}', (Render_unit_temp, ), {})
        cls.reg_count += 1
        return new_cls


class Render_unit_temp:

    _init_list = []

    _shader = None
    _vertex_array = None
    _vertex_buffer = None
    _index_buffer = None
    _texture = None
    _hollow_comp = comp.RenderComponent()

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
        self._shader = self.__class__._shader
        self._properties = self._shader.properties.copy_with_location()

        cls = self.__class__
        if isinstance(cls._vertex_array, type):
            self._vertex_array = cls._vertex_array()
        if isinstance(cls._vertex_buffer, type):
            self._vertex_buffer = cls._vertex_buffer()
        if isinstance(cls._index_buffer, type):
            self._index_buffer = cls._index_buffer()
        if isinstance(cls._texture, type):
            self._texture = cls._texture()

        self._flag_built = False

    def _build_(self):
        if not self.shader.is_built:
            self.shader.build()

        self.vertex_array.build()
        self.vertex_array.bind()

        self.index_buffer.build()
        self.vertex_buffer.build()

        self.vertex_array.unbind()

        self.texture.build()

    def update_variables(self):
        # for attribute
        # bind buffer and vertex_attrib_pointer with gl if form of buffer has changed
        if self.properties.attribute.is_buffer_formchange:
            self.vertex_buffer.bind()
            buffer = self.properties.attribute.buffer
            self.vertex_buffer.set_attribpointer(buffer)
            self.vertex_buffer.unbind()

        # for vertex buffer
        # update buffer if change has been made
        # change whole if all buffer is changed
        changed_blocks = self.properties.attribute.updated
        if len(changed_blocks) != 0:
            self.vertex_buffer.bind()

            if len(changed_blocks) == len(self.properties.attribute.names):
                buffer = self.properties.attribute.buffer
                self.vertex_buffer.set_attribpointer(buffer)
                # size = buffer.itemsize * buffer.size
                # gl.glBufferData(gl.GL_ARRAY_BUFFER, size, buffer, self.vertex_buffer._glusage)

            else:
                # update part only
                for block in changed_blocks:

                    buffer = self.properties.attribute.buffer
                    start_pos = self.properties.attribute.posof_block(block.name)

                    # finde starting offset
                    start_off = 0
                    for i in range(start_pos):
                        dtype = buffer.dtype[i]
                        bytesize = dtype.itemsize
                        start_off += bytesize

                    data = block.data
                    for i in range(buffer.size):
                        off = start_off + buffer.itemsize * i
                        element = data[i]
                        size = element.itemsize * element.size
                        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, off, size, element)

            self.vertex_buffer.unbind()

            # if isinstance(self.index_buffer, comp.Indexbuffer):
            #     # automated index setting
            #     # if size changed
            #     if self._drawmode == gl.GL_TRIANGLE_STRIP:
            #         num_tri = buffer.size - 2
            #         if num_tri != self.index_buffer.data.size:
            #             indicies = []
            #             for i in range(num_tri):
            #                 if i == 0:
            #                     indicies += [0, 1, 2]
            #                 elif i == 1:
            #                     indicies += [2, 0, 3]
            #                 else:
            #                     indicies += [i, i - 1, i + 1]
            #             if len(indicies) != 0:
            #                 self.index_buffer.data = indicies
            #                 self.index_buffer.build()
            #                 self.index_buffer.bind()
            #             else:
            #                 pass
            #     else:
            #         raise Exception(f"please define handler of other draw mode '{self.mode}'")

        # for uniforms
        changed_blocks = self.properties.uniform.updated
        if len(changed_blocks) != 0:
            # update part only
            for block in changed_blocks:
                n = block.data[0].size
                t = block.data.dtype
                if 'vec' in block.glsltype:
                    n = block.glsltype.split('vec')[1]
                    c = 1
                    t = 'f'
                    exec(f'gl.glUniform{n}{t}v({block.location},{c},block.data[{c - 1}])')
                elif 'mat' in block.glsltype:
                    n = block.glsltype.split('mat')[1]
                    c = 1
                    t = 'f'
                    exec(f'gl.glUniformMatrix{n}{t}v({block.location},{c},True,block.data[{c - 1}])')
                elif block.glsltype == 'int':
                    gl.glUniform1i(block.location, block.data[0])
                elif block.glsltype == 'float':
                    gl.glUniform1f(block.location, block.data[0])
                elif block.glsltype == 'bool':
                    gl.glUniform1i(block.location, int(block.data[0]))
                elif block.glsltype == 'sampler2D':
                    gl.glUniform1i(block.location, block.data[0])
                else:
                    raise TypeError(f"parsing for '{block.glsltype}' undefined")

        # update assigned matrix from global object
        # mm = self.properties['MM']
        # matrix = self.MM
        # gl.glUniformMatrix4fv(mm.location, 1, True, matrix)

        vp = Viewport.get_current()
        vm = self.properties['VM']
        matrix = vp.camera.VM
        gl.glUniformMatrix4fv(vm.location, 1, True, matrix)

        pm = self.properties['PM']
        matrix = vp.camera.PM
        gl.glUniformMatrix4fv(pm.location, 1, True, matrix)

    def bind(self):
        if not self._flag_built:
            self._build_()
            self._flag_built = True

        self.shader.bind()

        if isinstance(self.vertex_array, comp.Vertexarray):
            self.vertex_array.bind()
            if not gl.vao_stores_ibo:
                self.index_buffer.bind()
        else:
            self.vertex_buffer.bind()
            self.index_buffer.bind()

        self.texture.bind()

    @property
    def properties(self):
        return self._properties

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
    GL_DYNAMIC_DRAW = gl.GL_DYNAMIC_DRAW

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
    _vertex_array = comp.RenderComponent()
    _vertex_buffer = comp.RenderComponent()
    _index_buffer = comp.RenderComponent()
    _texture = comp.RenderComponent()

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

        ru = Render_unit_builder()

        ru.use_shader(cls._shader)
        ru.use_vertex_array() if vao else ru.use_vertex_array(cls._vertex_array)
        ru.use_vertex_buffer() if vbo else ru.use_vertex_buffer(cls._vertex_buffer)
        ru.use_index_buffer() if index else ru.use_index_buffer(cls._index_buffer)
        ru.use_texture() if texture else ru.use_texture(cls._texture)

        cls._render_unit_class = ru

    @classmethod
    def use_triangle_strip_draw(cls):
        cls._drawmode = gl.GL_TRIANGLE_STRIP

    @classmethod
    def new_render_unit(cls):
        fbl = FBL.get_current()
        reg = cls._fbl_register
        glfw_context = fbl.unique_glfw_context
        if glfw_context not in reg:
            # generate class_singular gl components for the first call
            cls._shader.build()
            if hasattr(cls, '_index_buffer'):
                cls._index_buffer.build()
            if hasattr(cls, '_texture'):
                cls._texture.build()
            reg.append(fbl.unique_glfw_context)

        # make new unit
        ru = cls._render_unit_class()
        if glfw_context not in cls._render_units:
            cls._render_units[glfw_context] = []
        cls._render_units[glfw_context].append(ru)
        return ru

    _render_units = {}
    _fbl_register= []

    def __init__(self, name: str = None):
        # check shader-context-existence
        if not (hasattr(self, '_shader') and hasattr(self, '_drawmode')):
            raise Exception('Not enough comp fed.')


        # self._vbo_layout = Layout_container.MULTI_VBO
        # multiple...pairs... what for shared glfw...
        # if called in a shared glfw... should it be handled here or outside?
        # if called from shared glfw just rebind vao-vbo
        # if called from unshared glfw if will have different vbo and crash or work strangely
        # is there a way to check if a window is shared?
        self._vertexunit = {}

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

    def _draw_(self, render_unit, fbl = None):
        # check initiated context
        context = FBL.get_current().unique_glfw_context
        if render_unit not in self._render_units[context]:
            raise

        if self.flag_draw or self.flag_run:
            # load opengl states
            render_unit.bind()

            if self.flag_run:
                render_unit.update_variables()

            if self.flag_draw:
                self.draw_element(render_unit.index_buffer)

            # TODO is this unnecessary processing? checking?
            self._unbind_global()

    def _unbind_global(self):
        self.shader.unbind()
        self.vertex_array.unbind()
        self.vertex_buffer.unbind()
        self.index_buffer.unbind()
        self.texture.unbind()

    def draw_element(self, index_buffer):
        window = FBL.get_current()
        viewport = Viewport.get_current()

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
            window._flag_something_rendered = True
            viewport.fillbackground() # before make any change erase background
            if index_buffer.count != 0: # draw a thing

                gl.glDrawElements(self.drawmode, index_buffer.count, index_buffer.gldtype, None)



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

    # def update_global_variables(self):
    #
    #     # bind buffer and vertex_attrib_pointer with gl if form of buffer has changed
    #     if self.shader.properties.attribute.is_buffer_formchange:
    #         self.vertex_buffer.bind()
    #         buffer = self.shader.properties.attribute.buffer
    #         self.vertex_buffer.set_attribpointer(buffer)
    #         self.vertex_buffer.unbind()
    #
    #     # for vertex buffer
    #     # update buffer if change has been made
    #     # change whole if all buffer is changed
    #     changed_blocks = self.shader.properties.attribute.updated
    #     if len(changed_blocks) != 0:
    #         self.vertex_buffer.bind()
    #
    #         if len(changed_blocks) == len(self.shader.properties.attribute.names):
    #             buffer = self.shader.properties.attribute.buffer
    #             size = buffer.itemsize * buffer.size
    #             gl.glBufferData(gl.GL_ARRAY_BUFFER, size, buffer, self.vertex_buffer._glusage)
    #
    #         else:
    #             # update part only
    #             for block in changed_blocks:
    #
    #                 buffer = self.shader.properties.attribute.buffer
    #                 start_pos = self.shader.properties.attribute.posof_block(block.name)
    #
    #                 # finde starting offset
    #                 start_off = 0
    #                 for i in range(start_pos):
    #                     dtype = buffer.dtype[i]
    #                     bytesize = dtype.itemsize
    #                     start_off += bytesize
    #
    #                 data = block.data
    #                 for i in range(buffer.size):
    #                     off = start_off + buffer.itemsize * i
    #                     element = data[i]
    #                     size = element.itemsize * element.size
    #                     # print(off)
    #                     # print(element)
    #                     # print(size)
    #                     gl.glBufferSubData(gl.GL_ARRAY_BUFFER, off, size, element)
    #         self.vertex_buffer.unbind()
    #
    #         # if size changed
    #         if self._drawmode == gl.GL_TRIANGLE_STRIP:
    #             num_tri = buffer.size - 2
    #             if num_tri != self.index_buffer.data.size:
    #                 indicies = []
    #                 for i in range(num_tri):
    #                     if i == 0:
    #                         indicies += [0, 1, 2]
    #                     elif i == 1:
    #                         indicies += [2, 0, 3]
    #                     else:
    #                         indicies += [i, i - 1, i + 1]
    #                 if len(indicies) != 0:
    #                     self.index_buffer.data = indicies
    #                     self.index_buffer.build()
    #                     self.index_buffer.bind()
    #                 else:
    #                     pass
    #         else:
    #             raise Exception(f"please define handler of other draw mode '{self.mode}'")
    #
    #     # for uniforms
    #     changed_blocks = self.shader.properties.uniform.updated
    #     if len(changed_blocks) != 0:
    #         # self.vertexbuffer.bind()
    #
    #         # update part only
    #         for block in changed_blocks:
    #             n = block.data[0].size
    #             t = block.data.dtype
    #             if 'vec' in block.glsltype:
    #                 n = block.glsltype.split('vec')[1]
    #                 c = 1
    #                 t = 'f'
    #                 exec(f'gl.glUniform{n}{t}v({block.location},{c},block.data[{c - 1}])')
    #             elif 'mat' in block.glsltype:
    #                 n = block.glsltype.split('mat')[1]
    #                 c = 1
    #                 t = 'f'
    #                 exec(f'gl.glUniformMatrix{n}{t}v({block.location},{c},True,block.data[{c - 1}])')
    #             elif block.glsltype == 'int':
    #                 gl.glUniform1i(block.location, block.data[0])
    #             elif block.glsltype == 'float':
    #                 gl.glUniform1f(block.location, block.data[0])
    #             elif block.glsltype == 'bool':
    #                 gl.glUniform1i(block.location, int(block.data[0]))
    #             elif block.glsltype == 'sampler2D':
    #                 gl.glUniform1i(block.location, block.data[0])
    #             else:
    #                 raise TypeError(f"parsing for '{block.glsltype}' undefined")
    #
    #     # update assigned matrix
    #     mm = self.shader.properties['MM']
    #     matrix = self.MM
    #     gl.glUniformMatrix4fv(mm.location, 1, True, matrix)
    #     vp = Viewport.get_current()
    #
    #     vm = self.shader.properties['VM']
    #     matrix = vp.camera.VM
    #     gl.glUniformMatrix4fv(vm.location, 1, True, matrix)
    #
    #     pm = self.shader.properties['PM']
    #     matrix = vp.camera.PM
    #     gl.glUniformMatrix4fv(pm.location, 1, True, matrix)


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

