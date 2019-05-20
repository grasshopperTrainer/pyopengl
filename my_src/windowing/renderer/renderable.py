import glfw
import OpenGL.GL as gl

from .components import *
from patterns.update_check_descriptor import UCD
# from windowing.layers.layerable import Layerable
from ..window import Window

class RenderUnit():
    """
    Pattern sould be determined:
    1. Renderer instance contain only one shader
    Problem is the renderers. Should Renderer contain one renderers for each kinds
    or could it contain multiple renderers and switch between them while rendering?

    For now leave all be single: sinble shader, single vao,vbo,vio.

    """
    _renderers = {}
    _current_window = None
    GL_DYNAMIC_DRAW = gl.GL_DYNAMIC_DRAW

    def __init__(self, name: str = None):
        self._shader = Shader()

        self._vertexarray = {}
        self._vertexbuffer = Vertexbuffer()
        self._indexbuffer = Indexbuffer()
        self._texture = Texture()


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

    @property
    def shader(self):
        return self._shader

    @shader.setter
    def shader(self, shader: Shader):
        if isinstance(shader, Shader):
            self._shader = shader

    @property
    def vertexarray(self):
        if self.current_window in self._vertexarray:
            return self._vertexarray[self.current_window]
        else:
            self._vertexarray[self.current_window] = Vertexarray()
            return self._vertexarray[self.current_window]

    @vertexarray.setter
    def vertexarray(self, vertexarray: Vertexarray):
        if isinstance(vertexarray, Vertexarray):
            self._vertexarray[self.current_window] = vertexarray

    @property
    def vertexbuffer(self):
        return self._vertexbuffer

    @vertexbuffer.setter
    def vertexbuffer(self, vertexbuffer: Vertexbuffer):
        if isinstance(vertexbuffer, Vertexbuffer):
            self._vertexbuffer = vertexbuffer

    @property
    def indexbuffer(self):
        return self._indexbuffer

    @indexbuffer.setter
    def indexbuffer(self, indexbuffer: Indexbuffer):
        if isinstance(indexbuffer, Indexbuffer):
            self._indexbuffer = indexbuffer

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, texture: Texture):
        if isinstance(texture, Texture):
            self._texture = texture

    def bind_shader(self, file_name, name=None):
        self._shader = Shader(file_name, name)

    def bind_vertexbuffer(self, glusage=None):
        self._vertexbuffer = Vertexbuffer(glusage)

    def bind_indexbuffer(self, glusage=None):
        self._indexbuffer = Indexbuffer(glusage)

    def bind_texture(self, file, slot=None):
        if file is not None:
            self._texture = Texture_load(file, slot)
        self.property['useTexture'] = True

    # def bind_framebuffer(self):
    #     self._framebuffer = Framebuffer(None)

    def draw(self):
        self._draw_()

    def _draw_(self, func=None):
        # real draw
        if func is None:

            # if vertexarray for current context is not built
            if not isinstance(self.vertexarray, Vertexarray):
                self._build_()

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

            # TODO is unbinding every time necessary?
        # for decorater
        else:
            func()

    def draw_element(self):
        window = self.current_window
        viewport = window.viewports.current_viewport

        if UCD.is_any_descriptor_updated(viewport, viewport.camera) or self.shader.properties.is_any_update:
            window._flag_something_rendered = True
            # before make any change erase background
            viewport.fillbackground()
            # draw a thing
            if self.indexbuffer.count != 0:
                gl.glDrawElements(self.mode, self.indexbuffer.count, self.indexbuffer.gldtype, None)
            # tell window change has been made on framebuffer
            # and should swap it

        # update have been handled so reset update flag
        # self.shader.properties.reset_update()
        # UCD.reset_instance_updates(viewport, viewport.camera)
        # self.current_window.viewports.current_viewport.reset_update()

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
    def current_window(self):
        return Window.get_current_window()

    def _build_(self):
        print('building render unit')
        if len(self._vertexarray) == 1:
            if self.shader is not None:
                self.shader.build()

            if isinstance(self.vertexbuffer, RenderComponent):
                self.vertexarray = Vertexarray(1)
                self.vertexarray.build()
                self.vertexarray.bind()

                self.vertexbuffer.build()

                self.vertexarray.unbind()

            if self.indexbuffer is not None:
                self.indexbuffer.build()

            # if isinstance(self.texture, RenderComponent):
            self.texture.build()
        # for a call from another shared g context
        # just build VertexArray and put buffer info into it
        else:
            self.vertexarray = Vertexarray(1)
            self.vertexarray.build()
            self.vertexarray.bind()

            self.vertexbuffer.build()

            self.vertexarray.unbind()

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

        # for assigned uniforms
        vp = self.current_window.viewports.current_viewport
        vm = self.shader.properties['VM']
        matrix = vp.camera.VM
        gl.glUniformMatrix4fv(vm.location, 1, True, matrix)
        pm = self.shader.properties['PM']
        matrix = vp.camera.PM
        gl.glUniformMatrix4fv(pm.location, 1, True, matrix)


    def _unbindall(self):
        self.shader.unbind()
        self.vertexarray.unbind()
        self.vertexbuffer.unbind()
        self.indexbuffer.unbind()
        self.texture.unbind()

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
    def property(self):
        return self.shader.properties
