import glfw
import OpenGL.GL as gl
from OpenGL.error import Error

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
    def __init__(self, bound_builder):
        self._bound_builder = bound_builder
        self._vao = comp.Vertexarray()
        self._Vbo = comp.Vertexbuffer()
        self._flag_built = False

    def _build_(self):
        if not self._flag_built:
            self.vao.build()
            self.vao.bind()

            self.vbo.build()

            self.vao.unbind()

            self._flag_built = True


    @property
    def vao(self):
        return self._vao

    @property
    def vbo(self):
        return self._vbo


class Renderer_builder:
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
    _renderers = {}
    _current_window = None
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


    def __init__(self, name: str = None):
        self._context = FBL.get_current()

        self._shader = comp.RenderComponent()

        self._indexbuffer = comp.RenderComponent()
        self._texture = comp.RenderComponent()

        self._vbo_layout = Layout_container.MULTI_VBO
        # multiple...pairs... what for shared glfw...
        # if called in a shared glfw... should it be handled here or outside?
        # if called from shared glfw just rebind vao-vbo
        # if called from unshared glfw if will have different vbo and crash or work strangely
        # is there a way to check if a window is shared?
        self._vertexunit = {}

        self._MM = np.eye(4)

        if name is None:
            name = f'unmarked{len(self.__class__._renderers)}'
        self._name = name
        self.__class__._renderers[name] = self

        self.context = glfw.get_current_context()
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

    def add_new_unit(self):
        """
        single multi multi single....
        if i divide vertex array + vertex buffer under the name of 'unit'
        if single VAO + single VBO pair is a single 'unit'
        this Renderer_builder will contain a list of multiple units and
        function for appending new, deleting, copying etc - list control functions.

        :return:
        """

        # there can be three types of fbl
        # 1. original glfw window
        # 2. child of original glfw window - meaning shared glfw context
        # 3. frame buffer like Renderable_image
        # #1 stores original - only one
        # #2 has to have newly build Vertexarray but vbo will be the same - can be multiple
        # #3 has same copy of #1 has - can be multiple
        # how to form data structure?

        # know from where it is called
        fbl = FBL.get_current()

        # if its a glfw window
        # TODO Window and Renderable_image better be inside fbl

        ru = Render_unit(fbl)

        if isinstance(fbl, Window):
            if not fbl in self._vertexunit:
                self._vertexunit[fbl] = []

            self._vertexunit[fbl].append(ru)

        elif isinstance(fbl, Renderable_image):
            pass
        # need to return something...
        return ru

    @property
    def shader(self):
        return self._shader

    @shader.setter
    def shader(self, shader: comp.Shader):
        if isinstance(shader, comp.Shader):
            self._shader = shader

    @property
    def vertexarray(self):
        win = FBL.get_current()
        if win is None:
            raise Error("can't find frame_buffer_like object")

        if win in self._vertexarray:
            return self._vertexarray[win]
        else:
            self._vertexarray[win] = None
            return self._vertexarray[win]

    @vertexarray.setter
    def vertexarray(self, vertexarray: comp.Vertexarray):
        if isinstance(vertexarray, comp.Vertexarray):
            self._vertexarray[FBL.get_current()] = vertexarray

    @property
    def vertexbuffer(self):
        return self._vertexbuffer

    @vertexbuffer.setter
    def vertexbuffer(self, vertexbuffer: comp.Vertexbuffer):
        if isinstance(vertexbuffer, comp.Vertexbuffer):
            self._vertexbuffer = vertexbuffer

    @property
    def indexbuffer(self):
        return self._indexbuffer

    @indexbuffer.setter
    def indexbuffer(self, indexbuffer: comp.Indexbuffer):
        if isinstance(indexbuffer, comp.Indexbuffer):
            self._indexbuffer = indexbuffer

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, texture: comp.Texture):
        if isinstance(texture, comp.Texture):
            self._texture = texture

    # temp names
    def set_shader(self, shader=None):
        if shader is None:
            # TODO if not given use dynamic shader
            pass
        else:
            if isinstance(shader, comp.Shader):
                self._shader = shader
            else:
                raise TypeError


    def use_indexbuffer(self, indexbuffer=None):
        if indexbuffer is None:
            self._indexbuffer = comp.Indexbuffer(gl.GL_STATIC_DRAW)
        else:
            self._indexbuffer = comp.Indexbuffer


    def use_texture(self, texture=None):
        if texture is None:
            self._texture = comp.Texture()
        else:
            self._texture = texture


    # def bind_framebuffer(self):
    #     self._framebuffer = Framebuffer(None)

    def _check_shader_existence(self):
        # check minimum comp needed
        if self._shader != None:
            pass
        else:
            raise Error('Not enough comp fed.')

    def _build_(self, render_unit):

        self.shader.build()

        render_unit._build_()

        if self.indexbuffer is not None:
            self.indexbuffer.build()
        if self.texture is not None:
            self.texture.build()

        # for a call from another shared glfw context
        # just build VertexArray and put buffer info into it
        elif self.vertexarray is None:
            self.vertexarray = comp.Vertexarray()
            self.vertexarray.build()
            self.vertexarray.bind()

            self.vertexbuffer.build()

            self.vertexarray.unbind()

    def _draw_(self, render_unit):
        self._check_shader_existence()
        # real draw
        # if vertexarray for current context is not built
        self._build_(render_unit)

        if self.flag_run:

            # load opengl states
            self.shader.bind()
            self.vertexarray.bind()
            # self.vertexbuffer.bind()
            self.indexbuffer.bind()
            self.texture.bind()

            # update all variables of shader
            self.update_variables()

            self.draw_element()
            # TODO is this unnecessary processing? checking?
            self._unbindall()

        else:
            if self.flag_draw:
                # load opengl states
                self.shader.bind()
                self.vertexarray.bind()
                # self.vertexbuffer.bind()
                self.indexbuffer.bind()
                self.texture.bind()

                self.draw_element()

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

    def update_variables(self):
        # bind buffer and vertexattribpointer with gl if form of buffer has changed
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
