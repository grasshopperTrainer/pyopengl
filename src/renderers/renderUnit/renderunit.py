from numbers import Number

import glfw
from OpenGL.GL import *

from .components import *
from windowing.window import Window


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

    def bind_vertexbuffer(self, data=None, glusage=None):
        self._vertexbuffer = Vertexbuffer(data, glusage)

    def bind_indexbuffer(self, data, glusage=None):
        self._indexbuffer = Indexbuffer(data, glusage)

    def bind_texture(self, file, slot=None):
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
                self.vertexbuffer.bind()
                self.indexbuffer.bind()
                self.texture.bind()

                # update all variables of shader
                self.update_variables()

            if self.flag_draw:
                glDrawElements(self.mode, self.indexbuffer.count, GL_UNSIGNED_INT, None)

            # TODO is unbinding everytime nessesssary?
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
        if self.shader.properties.is_updated:
            pass

        # dic = self.variables_to_update
        # try:
        #     for n in dic:
        #         self._shader.set_variable(n, dic[n])
        #         self._shader.update_variable()
        # except:
        #     raise Exception("can't update variable to shader")

    def set_variable(self, name: str, values: (list, tuple)) -> None:
        if not isinstance(values, (tuple, list)):
            values = (values,)
            # raise TypeError()

        if isinstance(values[0], Number):
            sign = Number
        else:
            sign = type(values[0])

        if not all([isinstance(v, sign) for v in values]):
            raise TypeError('input types inconsistent')

        self.variables_to_update[name] = values

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
