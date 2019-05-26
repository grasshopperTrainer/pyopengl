import glfw
from ..gl_tracker import GL_tracker as gl

from ..renderer import components as comp

from patterns.update_check_descriptor import UCD
from ..window import Window
from ..renderable_image import Renderable_image
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..viewport.viewports import Viewport
from collections import namedtuple
import numpy as np
import weakref

class VBO_layout:
    def __init__(self, ident):
        self.ident = ident

class Layout_container:
    MULTI_VBO = VBO_layout(0)
    SINGLE_VBO = VBO_layout(1)

class Render_unit:
    reg_count = 0
    def __new__(cls, *args, **kwargs):
        new_cls = type(f'Render_unit{cls.reg_count}', (Render_unit_temp, ), {})
        cls.reg_count += 1
        return new_cls


class Render_unit_temp:
    _vao = comp.RenderComponent
    _vbo = comp.RenderComponent
    _ibo = comp.RenderComponent
    _tex = comp.RenderComponent

    @classmethod
    def use_vao(cls):
        cls._vao = comp.Vertexarray

    @classmethod
    def use_vbo(cls):
        cls._vbo = comp.Vertexbuffer

    @classmethod
    def use_index(cls):
        cls._ibo = comp.Indexbuffer

    @classmethod
    def use_texture(cls):
        cls._tex = comp.Texture

    @property
    def vao(self):
        if hasattr(self, '_vao'):
            return self._vao
        else:
            return comp.RenderComponent

    @property
    def vbo(self):
        if hasattr(self, '_vbo'):
            return self._vbo
        else:
            return comp.RenderComponent

    @property
    def ibo(self):
        if hasattr(self, '_ibo'):
            return self._ibo
        else:
            return comp.RenderComponent

    @property
    def tex(self):
        if hasattr(self, '_tex'):
            return self._tex
        else:
            return comp.RenderComponent

    def __init__(self):
        cls = self.__class__
        self._vao = cls._vao()
        self._vbo = cls._vbo()
        self._ibo = cls._ibo()
        self._tex = cls._tex()

    def _build_(self):
            self.vao.build()
            self.vao.bind()

            self.vbo.build()

            self.vao.unbind()

            self.ibo.build()

            self.tex.build()

    def _update_variables_(self):
        pass

class Renderer_template:
    """
    Pattern sould be determined:
    1. Renderer instance contain only one shader
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
    layout = Layout_container


    @classmethod
    def use_shader(cls, shader):
        cls._shader = shader


    @classmethod
    def use_index_buffer(cls):
        cls._index_buffer = comp.Indexbuffer()

    @classmethod
    def use_texture_buffer(cls):
        cls._texture_buffer = comp.Texture()

    @classmethod
    def use_render_unit(cls, vao=True, vbo=True,index=False,texture=False):
        ru = Render_unit()
        if vao:
            ru.use_vao()
        if vbo:
            ru.use_vbo()
        if index:
            ru.use_index()
        if texture:
            ru.use_texture()

        cls._render_unit_class = ru


    @classmethod
    def new_render_unit(cls):
        ru = cls._render_unit_class()
        cls._render_units.append(ru)
        return ru

    _render_units = []
    _fbl_register= []

    def __init__(self, name: str = None):
        # check shader-context-existence
        if not hasattr(self, '_shader'):
            raise Error('Not enough comp fed.')


        # self._vbo_layout = Layout_container.MULTI_VBO
        # multiple...pairs... what for shared glfw...
        # if called in a shared glfw... should it be handled here or outside?
        # if called from shared glfw just rebind vao-vbo
        # if called from unshared glfw if will have different vbo and crash or work strangely
        # is there a way to check if a window is shared?
        self._vertexunit = {}

        self._MM = np.eye(4)

        self._drawmode = gl.GL_TRIANGLE_STRIP

        self._flag_draw = True
        self._flag_run = True

        # default layer setting
        # self.current_window.layer[0].add(self)

    def set_layout(self, const):
        if isinstance(const,VBO_layout):
            self._vbo_layout = const
        else:
            raise TypeError("should use instance's.const.(CORRECT_TYPE_CONST)")

    @property
    def shader(self):
        if hasattr(self, '_shader'):
            return self._shader
        else:
            return comp.RenderComponent

    @property
    def vertexbuffer(self):
        if hasattr(self, '_vertex_buffer'):
            return self._vertex_buffer
        else:
            return comp.RenderComponent

    @property
    def indexbuffer(self):
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

    def _build_(self):
        fbl = FBL.get_current()
        if fbl not in self.__class__._fbl_register:
            if fbl.mother_window in self.__class__._fbl_register:
                # exception for shared context
                raise
            else:
                # generate class_singular gl components for the first call
                self.shader.build()
                self.indexbuffer.build()
                self.texture.build()




    def _draw_(self, render_unit, fbl = None):
        self._build_()

        if self.flag_draw or self.flag_run:
            # load opengl states
            self.shader.bind()

            self.indexbuffer.bind()
            self.texture.bind()

            # if set to run
            if self.flag_run:
                # update all variables of shader
                self.update_global_variables(render_unit)

            if self.flag_draw:
                self.draw_element()

            # TODO is this unnecessary processing? checking?
            self._unbindall()

    def _unbindall(self):
        self.shader.unbind()
        self.vertexarray.unbind()
        self.vertexbuffer.unbind()
        self.indexbuffer.unbind()
        self.texture.unbind()

    def draw_element(self):
        window = FBL._current
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
            # before make any change erase background
            viewport.fillbackground()
            # draw a thing
            if self.indexbuffer.count != 0:
                gl.glDrawElements(self.mode, self.indexbuffer.count, self.indexbuffer.gldtype, None)

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

    def update_global_variables(self):

        # bind buffer and vertex_attrib_pointer with gl if form of buffer has changed
        if self.shader.properties.attribute.is_buffer_formchange:
            self.vertexbuffer.bind()
            buffer = self.shader.properties.attribute.buffer
            self.vertexbuffer.set_attribpointer(buffer)
            self.vertexbuffer.unbind()

        # for vertex buffer
        # update buffer if change has been made
        # change whole if all buffer is changed
        changed_blocks = self.shader.properties.attribute.updated
        if len(changed_blocks) != 0:
            self.vertexbuffer.bind()

            if len(changed_blocks) == len(self.shader.properties.attribute.names):
                buffer = self.shader.properties.attribute.buffer
                size = buffer.itemsize * buffer.size
                gl.glBufferData(gl.GL_ARRAY_BUFFER, size, buffer, self.vertexbuffer._glusage)

            else:
                # update part only
                for block in changed_blocks:

                    buffer = self.shader.properties.attribute.buffer
                    start_pos = self.shader.properties.attribute.posof_block(block.name)

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
                        # print(off)
                        # print(element)
                        # print(size)
                        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, off, size, element)
            self.vertexbuffer.unbind()

            # if size changed
            if self._drawmode == gl.GL_TRIANGLE_STRIP:
                num_tri = buffer.size - 2
                if num_tri != self.indexbuffer.data.size:
                    indicies = []
                    for i in range(num_tri):
                        if i == 0:
                            indicies += [0, 1, 2]
                        elif i == 1:
                            indicies += [2, 0, 3]
                        else:
                            indicies += [i, i - 1, i + 1]
                    if len(indicies) != 0:
                        self.indexbuffer.data = indicies
                        self.indexbuffer.build()
                        self.indexbuffer.bind()
                    else:
                        pass
            else:
                raise Exception(f"please define handler of other draw mode '{self.mode}'")

        # for uniforms
        changed_blocks = self.shader.properties.uniform.updated
        if len(changed_blocks) != 0:
            # self.vertexbuffer.bind()

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

        # update assigned matrix
        mm = self.shader.properties['MM']
        matrix = self.MM
        gl.glUniformMatrix4fv(mm.location, 1, True, matrix)
        vp = Viewport.get_current()

        vm = self.shader.properties['VM']
        matrix = vp.camera.VM
        gl.glUniformMatrix4fv(vm.location, 1, True, matrix)

        pm = self.shader.properties['PM']
        matrix = vp.camera.PM
        gl.glUniformMatrix4fv(pm.location, 1, True, matrix)


    @property
    def glsl_variables(self):
        return self.shader.variables

    @property
    def mode(self):
        return self._drawmode

    @mode.setter
    def mode(self, value):
        if isinstance(value, int):
            self._drawmode = value

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

