import glfw
from OpenGL.GL import *
from buffers import Buffer
from shader import Shader
from gloverride import *

class Renderer:
    """
    Pattern sould be determined:
    1. Renderer instance contain only one shader
    Problem is the buffers. Should Renderer contain one buffers for each kinds
    or could it contain multiple buffers and switch between them while rendering?

    For now leave all be single: sinble shader, single vao,vbo,vio.

    """
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
        # print(self._shader.shader,self._buffer.array,self._buffer.indexbuffer)
        glUseProgram(self._shader.shader)
        glBindVertexArray(self._buffer.array)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._buffer.indexbuffer)

        self.update_variables()

        if func is None:
            glDrawElements(self.mode, 6, GL_UNSIGNED_INT, None)
        # for decorater
        else:
            func()

    def rebind(self):
        self._buffer.rebuild_vertexarray()

        pass
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

    def signal(self):
        print(self)