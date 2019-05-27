import weakref
import inspect
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

class myclassmethod:
    """
    Pre function execution operator.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # checks whether current fbl has tracker within it
        if FBL.get_current() not in GL_tracker._FBLs:
            raise Exception('Frame_buffer_like object not bound with trackable_GL')

        return lambda *args,**kwargs: self.func(owner, *args, **kwargs)

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

    @myclassmethod
    def glGenBuffers(cls,n,buffers=None):
        index = gl.glGenBuffers(n, buffers)
        cls.ins()._buffers[index] = {}
        return index

    @myclassmethod
    def glBindBuffer(cls, target, buffer):
        buffer_d = cls.ins()._bound_buffer
        if target == cls.GL_ARRAY_BUFFER:
            buffer_d['GL_ARRAY_BUFFER'] = buffer
        elif target == cls.GL_ELEMENT_ARRAY_BUFFER:
            buffer_d['GL_ELEMENT_ARRAY_BUFFER'] = buffer
        else:
            raise

        gl.glBindBuffer(target, buffer)

    @myclassmethod
    def glBufferData(cls, target, size, data, usage):
        # TODO is automated size calculation good?
        gl.glBufferData(target, size, data, usage)

    @myclassmethod
    def glCreateProgram(cls):
        index = gl.glCreateProgram()
        cls.ins()._programs[index] = {'linked': False}
        return index

    @myclassmethod
    def glUseProgram(cls, program):
        cls.ins()._bound_program = program
        gl.glUseProgram(program)

    @myclassmethod
    def glCreateShader(cls, type):
        index = gl.glCreateShader(type)
        cls.ins()._shaders[index] = {}

        return index

    @myclassmethod
    def glClearColor(cls,r,g,b,a):
        gl.glClearColor(r,g,b,a)

    @myclassmethod
    def glClear(cls, mask):
        gl.glClear(mask)

    @myclassmethod
    def glEnable(cls, cap):
        gl.glEnable(cap)

    @myclassmethod
    def glBlendFunc(cls, sfactor,dfactor):
        gl.glBlendFunc(sfactor,dfactor)

    @myclassmethod
    def glViewport(cls,x,y,width,height):
        gl.glViewport(x,y,width,height)

    @myclassmethod
    def glScissor(cls,x,y,width,height):
        gl.glScissor(x,y,width,height)

    @myclassmethod
    def glShaderSource(cls, shader, count, string=None, length=None):
        gl.glShaderSource(shader, count, string, length)

    @myclassmethod
    def glCompileShader(cls, shader):
        gl.glCompileShader(shader)

    @myclassmethod
    def glGetShaderiv(cls, shader, pname, param=None):
        return gl.glGetShaderiv(shader,pname)

    @myclassmethod
    def glAttachShader(cls, program, shader):
        gl.glAttachShader(program, shader)

    @myclassmethod
    def glLinkProgram(cls, program):
        cls.ins()._programs[program]['linked'] = True
        gl.glLinkProgram(program)

    @myclassmethod
    def glValidateProgram(cls, program):
        gl.glValidateProgram(program)

    @myclassmethod
    def glDeleteShader(cls, shader):
        gl.glDeleteShader(shader)
        del cls.ins()._shaders[shader]

    @myclassmethod
    def glBindAttribLocation(cls, program, index, name):
        gl.glBindAttribLocation(program, index, name)

    @myclassmethod
    def glGetUniformLocation(cls, program, name):
        index = gl.glGetUniformLocation(program, name)
        return index

    @myclassmethod
    def glGenVertexArrays(cls, n, arrays = None):
        """
        Generate vertex arrays.
        Additional procedure to generate arrays in each shared glfw context.
        This procedure is as even if glfw context is shared with another,
        it doesn't share vertex array.

        :param n: number of vertex arrays to generate
        :param arrays: ignored
        :return:
        """
        windows =  cls.fbl().shared_windows + [cls.fbl(),]
        index = None
        for win in windows:
            win.make_window_current()
            index = gl.glGenVertexArrays(n, arrays)
        cls.ins()._vertex_arrays[index] = {}

        return index

    @myclassmethod
    def glBindVertexArray(cls, array):
        gl.glBindVertexArray(array)
        cls.ins()._bound_vertex_array = array

    @myclassmethod
    def glGenTextures(cls, n, textures=None):
        index = gl.glGenTextures(n, textures)
        cls.ins()._textures[index] = {}
        return index

    @myclassmethod
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

    @myclassmethod
    def glActiveTexture(cls, texture):
        gl.glActiveTexture(texture)
        base = gl.GL_TEXTURE0
        n = texture - base
        cls.ins()._active_texture = f'GL_TEXTURE{n}'

    @myclassmethod
    def glBindTexture(cls, target, texture):
        gl.glBindTexture(target, texture)

        if target == gl.GL_TEXTURE_2D:
            name = 'GL_TEXTURE_2D'

        cls.ins()._bound_texture[name] = texture

    @myclassmethod
    def glBufferSubData(cls,target,offset,size,data):
        gl.glBufferSubData(target,offset,size,data)

    @myclassmethod
    def glUniformMatrix4fv(cls, location, count, transpose, value):
        gl.glUniformMatrix4fv(location, count, transpose, value)
    @myclassmethod
    def glUniform4fv(cls, location, count, value):
        gl.glUniform4fv(location, count, value)
    @myclassmethod
    def glUniform1i(cls, location, v0):
        gl.glUniform1i(location, v0)

    @myclassmethod
    def glEnableVertexAttribArray(cls, index):
        gl.glEnableVertexAttribArray(index)
    @myclassmethod
    def glVertexAttribPointer(cls,index, type, size, normalized, stride, pointer):
        gl.glVertexAttribPointer(index, type, size, normalized, stride, pointer)
    @myclassmethod
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

