import weakref
import inspect
import OpenGL.GL as gl
from .frame_buffer_like.frame_buffer_like_bp import FBL

class myclassmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if FBL.get_current() not in owner._FBLs:
            raise Exception('Frame_buffer_like object not bound with trackable_GL')
        return lambda *args,**kwargs: self.func(owner, *args, **kwargs)

class GL_tracker:
    """
    Stores gl objects to display.
    ex) what shaders, represented as gl object index and custom names, does window have?
    ex) what buffers, represented as gl object index and custom names, does window have?
    How to make it ass automatic? should it be very strict?
    What if this class is an intermediate between Window_glfw_context and gl calls?
    So class methods are for general gl_calls.
    """
    _FBLs = weakref.WeakKeyDictionary()




    GL_COLOR_BUFFER_BIT = gl.GL_COLOR_BUFFER_BIT
    GL_DEPTH_BUFFER_BIT = gl.GL_DEPTH_BUFFER_BIT

    GL_SCISSOR_TEST = gl.GL_SCISSOR_TEST
    GL_DEPTH_TEST = gl.GL_DEPTH_TEST

    GL_BLEND = gl.GL_BLEND
    GL_SRC_ALPHA = gl.GL_SRC_ALPHA
    GL_ONE_MINUS_SRC_ALPHA = gl.GL_ONE_MINUS_SRC_ALPHA

    GL_DYNAMIC_DRAW = gl.GL_DYNAMIC_DRAW

    GL_TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP

    GL_UNSIGNED_BYTE = gl.GL_UNSIGNED_BYTE
    GL_UNSIGNED_SHORT = gl.GL_UNSIGNED_SHORT
    GL_UNSIGNED_INT = gl.GL_UNSIGNED_INT
    GL_INT = gl.GL_INT

    GL_FLOAT = gl.GL_FLOAT

    GL_VERTEX_SHADER = gl.GL_VERTEX_SHADER
    GL_FRAGMENT_SHADER = gl.GL_FRAGMENT_SHADER

    GL_COMPILE_STATUS = gl.GL_COMPILE_STATUS

    GL_ARRAY_BUFFER = gl.GL_ARRAY_BUFFER
    GL_ELEMENT_ARRAY_BUFFER = gl.GL_ELEMENT_ARRAY_BUFFER

    def __init__(self, context):
        self._context = context

        self._programs = {}
        self._buffers = {}
        self._shaders = set()

        self._bound_program = int
        self._bound_buffer = {
            'GL_ARRAY_BUFFER':None,
            'GL_ELEMENT_ARRAY_BUFFER': None
        }


        self.__class__._FBLs[context] = self


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
        cls.ins()._bound_program(program)
        gl.glUseProgram(program)

    @myclassmethod
    def glCreateShader(cls, type):
        index = gl.glCreateShader(type)
        cls.ins()._shaders.add(index)

        return index

    @myclassmethod
    def glClearColor(cls,r,g,b,a):

        print('glClearColor call')
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
        cls.ins()._shaders.remove(shader)

    @myclassmethod
    def glBindAttribLocation(cls, program, index, name):
        gl.glBindAttribLocation(program, index, name)

    @myclassmethod
    def glGetUniformLocation(cls, program, name):
        gl.glGetUniformLocation(program, name)

    @classmethod
    def ins(cls):
        return cls._FBLs[FBL.get_current()]
