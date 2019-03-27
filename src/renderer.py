import glfw
from OpenGL.GL import *
from buffers import Buffer
from shader import Shader
from gloverride import *

class Renderer:
    _renderers = {}
    def __init__(self, shader: Shader, buffer: Buffer, name: str = None):
        self._shader = shader
        self._buffer = buffer
        if name is None:
            name = f'unmarked{len(self.__class__._renderers)}'
        self._name = name
        self.__class__._renderers[name] = self

        self.variables_to_update = {}
        self.context = glfw.get_current_context()
        self._mode = GL_TRIANGLES


    def draw(self, func = None):
        glUseProgram(self._shader.shader)
        glBindVertexArray(self._buffer.array)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._buffer.indexbuffer)

        self.update_variables()

        if func is None:
            glDrawElements(self.mode, 6, GL_UNSIGNED_INT, None)
        # for decorater
        else:
            func()

    @property
    def name(self):
        return self._name

    @classmethod
    def get_instances(cls):
        return cls._renderers

    @classmethod
    def drawall(cls):
        for renderer in cls._renderers:
            renderer.draw()
        pass

    def update_variables(self):
        dic = self.variables_to_update
        for n in dic:
            self._shader.set_variable(n, dic[n])
            self._shader.update_variable()

    def set_variable(self,name, value):
        self.variables_to_update[name] = value

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if isinstance(value, int):
            self._mode = value