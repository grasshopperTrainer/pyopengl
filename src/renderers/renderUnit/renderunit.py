from numbers import Number

import glfw
from OpenGL.GL import *

from .components import *


class RenderUnit:
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

        self._flag_firstbuild = True

        if name is None:
            name = f'unmarked{len(self.__class__._renderers)}'
        self._name = name
        self.__class__._renderers[name] = self

        self.variables_to_update = {}
        self.context = glfw.get_current_context()
        self._mode = GL_TRIANGLES

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

    def bind_vertexbuffer(self, data, glusage=None):
        self._vertexbuffer = Vertexbuffer(data, glusage)

    def bind_indexbuffer(self, data, glusage=None):
        self._indexbuffer = Indexbuffer(data, glusage)

    def bind_texture(self, file, slot=None):
        self._texture = Texture(file, slot)

    def firstbuild(self):
        # stop condition
        min_req = all(self._shader is not None, self._vertexbuffer is not None)
        if not min_req:
            raise ArgumentError('minimum required components(shader and vertexbuffer) not provided')
            # TODO or should i just ignore or provide default value?

        # if minimum requirement met, continue
        self._shader

        pass

    def draw(self, func=None):
        # first call
        if self._flag_firstbuild:
            self.build()
            self._flag_firstbuild = False

        # real draw
        if func is None:
            # load opengl states
            self.shader.bind()
            self.vertexarray.bind()
            # self.vertexbuffer.bind()
            self.indexbuffer.bind()
            self.texture.bind()

            # update all variables of shader
            # self.update_variables()
            glDrawElements(self.mode, self.indexbuffer.count, GL_UNSIGNED_INT, None)

        # for decorater
        else:
            func()

    def build(self):
        if self.shader is not None:
            self.shader.build()

        if self.vertexbuffer is not None:
            self.vertexarray = Vertexarray()
            self.vertexarray.build()
            self.vertexarray.bind()

            self.vertexbuffer.build()

            self.vertexarray.unbind()

        if self.indexbuffer is not None:
            self.indexbuffer.build()

        if self.texture is not None:
            self.texture.build()

    def rebind(self):
        self.vertexarray.build()
        self.vertexarray.bind()

        self.vertexbuffer.build()

        self.vertexarray.unbind()

    @property
    def name(self):
        return self._name

    # @classmethod
    # def get_instances(cls):
    #     return cls._renderers
    #
    # @classmethod
    # def drawall(cls):
    #     for renderer in cls._renderers:
    #         renderer.draw()
    #     pass

    def update_variables(self):
        dic = self.variables_to_update
        try:
            for n in dic:
                self._shader.set_variable(n, dic[n])
                self._shader.update_variable()
        except:
            raise Exception("can't update variable to shader")

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

    # port for retriving current info
    @classmethod
    def push_current_window(cls, window):
        cls._current_window = window

    @property
    def current_window(self):
        return self.__class__._current_window
