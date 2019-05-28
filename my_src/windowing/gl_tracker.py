import weakref
import inspect
import numpy as np
import ctypes

import glfw.GLFW as glfw
import OpenGL.GL as gl
from .frame_buffer_like.frame_buffer_like_bp import FBL

class GL_tracker:
    """
    Stores opengl binding state.

    ex) what shaders, represented as gl object index and custom names, does window have?
    ex) what buffers, represented as gl object index and custom names, does window have?
    How to make it ass automatic? should it be very strict?
    What if this class is an intermediate between Window_glfw_context and gl calls?
    So class methods are for general gl_calls.
    """
    _FBLs = weakref.WeakKeyDictionary()

    def __init__(self, context):
        self._context = context

        # use dict to store additional state information
        self._programs = {}
        self._buffers = {}
        self._vertex_arrays = {}
        self._shaders = {}
        self._textures = {}

        # stores current binding
        self._bound_program = int
        self._bound_vertex_array = int
        self._bound_buffer = {
            'GL_ARRAY_BUFFER': None,
            'GL_ELEMENT_ARRAY_BUFFER': None
        }

        # texture
        self._bound_texture = {
            'GL_TEXTURE_2D' : None
        }
        self._active_texture = str
        self._param_texture = {
            'GL_TEXTURE_2D' : {}
        }

        # store instance
        self.__class__._FBLs[context] = self


    def follow(self, window):
        self._FBLs[window] = self
        return self

class context_check:
    """
    Pre function execution operator.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # checks whether current fbl has tracker within it
        if FBL.get_current() not in GL_tracker._FBLs:
            raise Exception('Frame_buffer_like object not bound with trackable_GL')

        if isinstance(self.func, vao_related):
            return self.func
        else:
            return lambda *args,**kwargs: self.func(Trackable_openGL, *args, **kwargs)

class vao_related:
    """
    Decorator for vao_related functions.
    if glfw context doesn't support vertex array sharing this function will triger
    to make all shared windows have same vertex array shape, operations.
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if not Trackable_openGL._gen_vertex_array_shared:
            fbl = FBL.get_current()
            windows = fbl.shared_windows + [fbl, ]
            for win in windows:
                win.make_window_current()
                return_v = self.func(Trackable_openGL,*args, **kwargs)
            return return_v

        else:
            return self.func(*args, **kwargs)


class Trackable_openGL:
    """
    Collection of openGL functinons and constants.

    Loads GL_tracker and stores value such as gl_index when needed.
    """

    GL_COLOR_BUFFER_BIT = gl.GL_COLOR_BUFFER_BIT
    GL_DEPTH_BUFFER_BIT = gl.GL_DEPTH_BUFFER_BIT

    GL_SCISSOR_TEST = gl.GL_SCISSOR_TEST
    GL_DEPTH_TEST = gl.GL_DEPTH_TEST

    GL_BLEND = gl.GL_BLEND
    GL_SRC_ALPHA = gl.GL_SRC_ALPHA
    GL_ONE_MINUS_SRC_ALPHA = gl.GL_ONE_MINUS_SRC_ALPHA

    GL_DYNAMIC_DRAW = gl.GL_DYNAMIC_DRAW

    GL_TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP

    # value types
    GL_TRUE = gl.GL_TRUE
    GL_FALSE = gl.GL_FALSE

    GL_UNSIGNED_BYTE = gl.GL_UNSIGNED_BYTE
    GL_UNSIGNED_SHORT = gl.GL_UNSIGNED_SHORT
    GL_UNSIGNED_INT = gl.GL_UNSIGNED_INT
    GL_INT = gl.GL_INT

    GL_FLOAT = gl.GL_FLOAT

    # shader
    GL_VERTEX_SHADER = gl.GL_VERTEX_SHADER
    GL_FRAGMENT_SHADER = gl.GL_FRAGMENT_SHADER
    GL_COMPILE_STATUS = gl.GL_COMPILE_STATUS

    # array buffer
    GL_ARRAY_BUFFER = gl.GL_ARRAY_BUFFER
    GL_ELEMENT_ARRAY_BUFFER = gl.GL_ELEMENT_ARRAY_BUFFER

    GL_TEXTURE_2D = gl.GL_TEXTURE_2D
    GL_TEXTURE_MIN_FILTER = gl.GL_TEXTURE_MIN_FILTER
    GL_TEXTURE_MAG_FILTER = gl.GL_TEXTURE_MAG_FILTER
    GL_TEXTURE_WRAP_S = gl.GL_TEXTURE_WRAP_S
    GL_TEXTURE_WRAP_T = gl.GL_TEXTURE_WRAP_T
    GL_TEXTURE_WRAP_R = gl.GL_TEXTURE_WRAP_R
    GL_LINEAR = gl.GL_LINEAR
    GL_REPEAT = gl.GL_REPEAT
    for i in range(32):
        exec(f'GL_TEXTURE{i} = gl.GL_TEXTURE{i}')

    @classmethod
    def context_sharing_check(cls):
        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, glfw.GLFW_FALSE)
        first_win = glfw.glfwCreateWindow(10, 10, 'first', None, None)
        second_win = glfw.glfwCreateWindow(10, 10, 'second', None, first_win)
        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, glfw.GLFW_TRUE)

        glfw.glfwMakeContextCurrent(first_win)

        first_bo = gl.glGenBuffers(1)
        first_vao = gl.glGenVertexArrays(1)
        first_program = gl.glCreateProgram()
        first_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        first_texture = gl.glGenTextures(1)
        # first_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, first_bo)
        gl.glBindVertexArray(first_vao)
        first_bound_vao = ctypes.c_int()
        gl.glGetIntegerv(gl.GL_VERTEX_ARRAY_BINDING, first_bound_vao)
        first_bound_bo = ctypes.c_int()
        gl.glGetIntegerv(gl.GL_ARRAY_BUFFER_BINDING, first_bound_bo)

        glfw.glfwMakeContextCurrent(second_win)

        second_bound_vao = ctypes.c_int()
        gl.glGetIntegerv(gl.GL_VERTEX_ARRAY_BINDING, second_bound_vao)
        second_bound_bo = ctypes.c_int()
        gl.glGetIntegerv(gl.GL_ARRAY_BUFFER_BINDING, second_bound_bo)

        second_buffer = gl.glGenBuffers(1)
        second_vertexarray = gl.glGenVertexArrays(1)
        second_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        second_program = gl.glCreateProgram()
        second_texture = gl.glGenTextures(1)
        # comparison

        cls._gen_buffer_shared = True if first_bo != second_buffer else False
        cls._gen_vertex_array_shared = True if first_vao != second_vertexarray else False
        cls._gen_shader_shared = True if first_shader != second_shader else False
        cls._gen_program_shared = True if first_program != second_program else False
        cls._gen_texture_shared = True if first_texture != second_texture else False

        print(cls._gen_buffer_shared)
        print(cls._gen_vertex_array_shared)
        print(cls._gen_shader_shared)
        print(cls._gen_program_shared)
        print(cls._gen_texture_shared)

        glfw.glfwDestroyWindow(first_win)
        glfw.glfwDestroyWindow(second_win)


    @context_check
    def glGenBuffers(cls,n,buffers=None):
        index = gl.glGenBuffers(n, buffers)
        cls.ins()._buffers[index] = {}
        return index

    @context_check
    @vao_related
    def glBindBuffer(cls, target, buffer):
        buffer_d = cls.ins()._bound_buffer
        if target == cls.GL_ARRAY_BUFFER:
            buffer_d['GL_ARRAY_BUFFER'] = buffer
        elif target == cls.GL_ELEMENT_ARRAY_BUFFER:
            buffer_d['GL_ELEMENT_ARRAY_BUFFER'] = buffer
        else:
            raise
        gl.glBindBuffer(target, buffer)

    @context_check
    def glBufferData(cls, target, size, data, usage):
        # TODO is automated size calculation good?
        gl.glBufferData(target, size, data, usage)

    @context_check
    def glCreateProgram(cls):
        index = gl.glCreateProgram()
        cls.ins()._programs[index] = {'linked': False}
        return index

    @context_check
    def glUseProgram(cls, program):
        cls.ins()._bound_program = program
        gl.glUseProgram(program)

    @context_check
    def glCreateShader(cls, type):
        index = gl.glCreateShader(type)
        cls.ins()._shaders[index] = {}

        return index

    @context_check
    def glClearColor(cls,r,g,b,a):
        gl.glClearColor(r,g,b,a)

    @context_check
    def glClear(cls, mask):
        gl.glClear(mask)

    @context_check
    def glEnable(cls, cap):
        gl.glEnable(cap)

    @context_check
    def glBlendFunc(cls, sfactor,dfactor):
        gl.glBlendFunc(sfactor,dfactor)

    @context_check
    def glViewport(cls,x,y,width,height):
        gl.glViewport(x,y,width,height)

    @context_check
    def glScissor(cls,x,y,width,height):
        gl.glScissor(x,y,width,height)

    @context_check
    def glShaderSource(cls, shader, count, string=None, length=None):
        gl.glShaderSource(shader, count, string, length)

    @context_check
    def glCompileShader(cls, shader):
        gl.glCompileShader(shader)

    @context_check
    def glGetShaderiv(cls, shader, pname, param=None):
        return gl.glGetShaderiv(shader,pname)

    @context_check
    def glAttachShader(cls, program, shader):
        gl.glAttachShader(program, shader)

    @context_check
    def glLinkProgram(cls, program):
        cls.ins()._programs[program]['linked'] = True
        gl.glLinkProgram(program)

    @context_check
    def glValidateProgram(cls, program):
        gl.glValidateProgram(program)

    @context_check
    def glDeleteShader(cls, shader):
        gl.glDeleteShader(shader)
        del cls.ins()._shaders[shader]

    @context_check
    def glBindAttribLocation(cls, program, index, name):
        gl.glBindAttribLocation(program, index, name)

    @context_check
    def glGetUniformLocation(cls, program, name):
        index = gl.glGetUniformLocation(program, name)
        return index


    @context_check
    @vao_related
    def glGenVertexArrays(cls, n, arrays=None):
        """
        Generate vertex arrays.
        Additional procedure to generate arrays in each shared glfw context.
        This procedure is as even if glfw context is shared with another,
        it doesn't share vertex array.

        :param n: number of vertex arrays to generate
        :param arrays: ignored
        :return:
        """
        index = gl.glGenVertexArrays(n, arrays)
        cls.ins()._vertex_arrays[index] = {}

        return index

    @context_check
    @vao_related
    def glBindVertexArray(cls, array):
        gl.glBindVertexArray(array)

    @context_check
    def glGenTextures(cls, n, textures=None):
        index = gl.glGenTextures(n, textures)
        cls.ins()._textures[index] = {}
        return index

    @context_check
    def glTexParameter(cls, target, pname, parameter):
        gl.glTexParameter(target, pname, parameter)
        if target == gl.GL_TEXTURE_2D:
            tname = 'GL_TEXTURE_2D'

        if pname == gl.GL_TEXTURE_MIN_FILTER:
            name = 'GL_TEXTURE_MIN_FILTER'
        elif pname == gl.GL_TEXTURE_MAG_FILTER:
            name = 'GL_TEXTURE_MAG_FILTER'
        elif pname == gl.GL_TEXTURE_WRAP_S:
            name = 'GL_TEXTURE_WRAP_S'
        elif pname == gl.GL_TEXTURE_WRAP_R:
            name = 'GL_TEXTURE_WRAP_R'
        elif pname == gl.GL_TEXTURE_WRAP_T:
            name = 'GL_TEXTURE_WRAP_T'

        if parameter == gl.GL_LINEAR:
            value = 'GL_LINEAR'
        elif parameter == gl.GL_REPEAT:
            value = 'GL_VALUE'


        cls.ins()._param_texture[tname][name] = value

    @context_check
    def glActiveTexture(cls, texture):
        gl.glActiveTexture(texture)
        base = gl.GL_TEXTURE0
        n = texture - base
        cls.ins()._active_texture = f'GL_TEXTURE{n}'

    @context_check
    def glBindTexture(cls, target, texture):
        gl.glBindTexture(target, texture)

        if target == gl.GL_TEXTURE_2D:
            name = 'GL_TEXTURE_2D'

        cls.ins()._bound_texture[name] = texture

    @context_check
    def glBufferSubData(cls,target,offset,size,data):
        gl.glBufferSubData(target,offset,size,data)

    @context_check
    def glUniformMatrix4fv(cls, location, count, transpose, value):
        gl.glUniformMatrix4fv(location, count, transpose, value)
    @context_check
    def glUniform4fv(cls, location, count, value):
        gl.glUniform4fv(location, count, value)
    @context_check
    def glUniform1i(cls, location, v0):
        gl.glUniform1i(location, v0)

    @context_check
    @vao_related
    def glEnableVertexAttribArray(cls, index):
        gl.glEnableVertexAttribArray(index)

    @context_check
    @vao_related
    def glVertexAttribPointer(cls,index, type, size, normalized, stride, pointer):
        gl.glVertexAttribPointer(index, type, size, normalized, stride, pointer)

    @context_check
    def glDrawElements(cls,mode,count,type,indices):
        gl.glDrawElements(mode,count,type,indices)

    @classmethod
    def fbl(cls):
        return FBL.get_current()

    @classmethod
    def ins(cls):
        return GL_tracker._FBLs[FBL.get_current()]

    def follow(self, window):
        self._FBLs[window] = self
        return self

