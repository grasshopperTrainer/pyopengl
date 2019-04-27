from numbers import Number

import glfw
from OpenGL.GL import *

from .components import *
from windowing.window import Window

import numpy as np

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

        self.variables_to_update = {}
        self.context = glfw.get_current_context()
        self._mode = GL_TRIANGLES

        self._flag_draw = True
        self._flag_run = True

        # default layer setting
        self.current_window.layer[0].add(self)

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

    def bind_indexbuffer(self, data, glusage=None):
        self._indexbuffer = Indexbuffer(data, glusage)

    def bind_texture(self, file, slot=None):
        if file is not None:
            self._texture = Texture(file, slot)

    def draw(self):
        self._draw_()

    def _draw_(self, func=None):
        # real draw
        if func is None:

            if self.flag_run:
                # if vertexarray for current context is not built
                if not isinstance(self.vertexarray, Vertexarray):
                    self._build_()

                # load opengl states
                self.shader.bind()
                self.vertexarray.bind()
                # self.vertexbuffer.bind()
                self.indexbuffer.bind()
                self.texture.bind()

                # update all variables of shader
                self.update_variables()

                if self.flag_draw:
                    glDrawElements(self.mode, self.indexbuffer.count, GL_UNSIGNED_INT, None)

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

                    glDrawElements(self.mode, self.indexbuffer.count, GL_UNSIGNED_INT, None)

                    self._unbindall()

            # TODO is unbinding every time necessary?
        # for decorater
        else:
            func()

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

    def _current_window_(self):
        self._current_window = Window.get_current_window()

    @property
    def current_window(self):
        self._current_window_()
        return self._current_window

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

            if isinstance(self.texture, RenderComponent):
                self.texture.build()
        # for a call from another shared glfw context
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
                glBufferData(GL_ARRAY_BUFFER, size, buffer, self.vertexbuffer._glusage)

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
                        glBufferSubData(GL_ARRAY_BUFFER, off, size, element)
            self.vertexbuffer.unbind()

        # for uniforms
        changed_blocks = self.shader.properties.uniform.updated
        if len(changed_blocks) != 0:
            # self.vertexbuffer.bind()

            # update part only
            for block in changed_blocks:
                print(block)
                n = block.data[0].size
                t = block.data.dtype
                if 'vec' in block.glsltype:
                    n = block.glsltype.split('vec')[1]
                    c = 1
                    t = 'f'
                else:
                    raise TypeError('parsing undefined')
                exec(f'glUniform{n}{t}v({block.location},{c},block.data[{c - 1}])')

    def _unbindall(self):
        self.shader.unbind()
        self.vertexarray.unbind()
        self.vertexbuffer.unbind()
        self.indexbuffer.unbind()
        self.texture.unbind()

    @property
    def glsl_variables(self):
        return self.shader.variables

    def clear(self, *color):
        if len(color) == 0:
            color = (1, 1, 1, 1)
        glClearColor(*color)
        glClear(GL_COLOR_BUFFER_BIT)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if isinstance(value, int):
            self._mode = value

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
