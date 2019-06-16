import weakref
import inspect
import numpy as np
import ctypes
from collections import namedtuple


import glfw.GLFW as glfw
import OpenGL.GL as gl
# import OpenGL.
# from windowing.windows import Windows

class Object:
    def __init__(self, id, objects):
        self.id = id
        self.objects = objects
        self.attributes = {}

    def set_attribute(self, pname, value):
        self.attributes[pname] = value

    @property
    def bound_targets(self):
        targets = []
        for n,t in self.objects.targets.items():
            if t.object == self:
                targets.append(t)
        return targets

class Objects:
    _debug = True
    def __init__(self, name):
        self.name = name
        self.collection = {}
        self.collection[0] = Object(0, self)
        self.targets = {}
        self.slots = {}
        self.active = None

    def generate(self, id):
        try:
            id = int(id)
            self.collection[id] = Object(id, self)
            self.dprint(f'gl, {self.name} {id} created')
        except:
            ids = list(id)
            for id in ids:
                id = int(id)
                self.collection[id] = Object(id,self)
                self.dprint(f'gl, {self.name} {id} created')

    def binding(self, target):
        return self.targets[target].binding

    def bind(self, id, target = None):
        if target not in self.targets:
            self.targets[target] = Target(target)
        self.targets[target].bind(self.collection[id])

        if self.active is not None:
            self.targets[self.active].bind(self.collection[id])

    def activate_slot(self, slot):
        if slot not in self.targets:
            self.targets[slot] = Target(slot)
        self.active = slot

    def remove(self, id):
        id = int(id)
        # print(self.name, id, type(id), type(list(self.collection.keys())[0]), self.collection)
        # print(self.collection[id])
        try:
            del self.collection[id]
            self.dprint(f'gl, {self.name} {id} deleted')
        except Exception as e:
            self.dprint(f'gl, {self.name} {id} delete error')
            raise
    @classmethod
    def dprint(cls, str):
        if cls._debug:
            print(str)

class Target:
    def __init__(self, name):
        self.name = name
        self.object = None

    def bind(self, object):
        if isinstance(object, Object):
            self.object = object
        else:
            raise

    @property
    def binding(self):
        return self.object

    def __str__(self):
        return f'<target object of {self.name}>'

class GLFW_GL_tracker:
    """
    Stores opengl binding state.

    Please store the object withint glfw.contex wrapping class object
    as a representation of unique glfw.context.

    There are two main purpose of the class.
    1. To store gl info such as generated buffers and currently bound
    buffers and other info good to be logged.

    2. This object represents a unique glfw context, meaning shared
    glfw contexts will contain one GL_tracker object. The characteristics
    of uniqueness is built for the reasons:
        1) Couldn't find a way to extract unique glfw object(with unique id,
           ex) glfw.get_current_context() doesn't return glfw context object
           generated by glfw.create_window()).
        2) Think glfw.context doesn't store its other shared contexts.

    """
    # instance dict of the trackers bound with FBL(Window) object
    _windows = weakref.WeakKeyDictionary()
    # _windows = {}
    _current = None

    def __init__(self, bound_object):
        # store instance
        self.__class__._windows[bound_object] = self

        self._render_buffers = Objects('render_buffers')
        self._textures = Objects('textures')
        self._frame_buffers = Objects('frame_buffers')
        self._programs = Objects('programs')
        self._shaders = Objects('shaders')
        self._buffers = Objects('buffers')
        self._vertex_arrays = Objects('vertes_arrays')

        # # self._bound_object =
        # # use dict to store generated's additional state information
        # self._programs = Object('program')
        # self._buffers = Object('buffer')
        # self._vertex_arrays = Object('vertex_array')
        # self._shaders = Object('shader')
        # self._textures = Object('texture')
        # self._render_buffers = Object('render_buffer')
        # self._frame_buffers = Object('frame_buffers')
        # self.objet_list = [
        #     self._programs,
        #     self._buffers,
        #     self._vertex_arrays,
        #     self._shaders,
        #     self._textures,
        #     self._render_buffers,
        #     self._frame_buffers]
        # # self._frame_buffers.set_slots('GL_FRAMEBUFFER')
        #
        # self._textures_active = {}
        # self._drawbuffer = {}

    def give_tracker_to(self, window):
        """
        Stores new Window object and returns self.
        Different windows sharing one tracker means
        their glfw.context is shared.

        :param window: fbl.window object to give to
        :return: object of tracker
        """
        self._windows[window] = self
        # after some vao have been created make them for new window
        # think this is a duck taping
        # ex) what if there is a deleted vao like 1,2,-,-,5,6
        vao_n = len(self._vertex_arrays.collection)-1
        gl.glGenVertexArrays(vao_n)
        return self

    def print_full_info(self):
        # print()
        # windows = []
        # for w,c in self.__class__._windows.items():
        #     if c is self:
        #         windows.append(w)
        # print(f"OpenGL CONTEXT INFO of {'window' if len(windows) == 1 else 'windows'}:")
        # windows = str([i.name for i in windows])
        # print(f'{windows: >{len(windows)+4}}')
        # print()
        #
        # for i in self.objet_list:
        #     for ii in i.format_generated():
        #         print(ii)
        #     print(i.collection)
        #     print()
        pass

    @classmethod
    def remove(cls, window):
        del cls._windows[window]

    @classmethod
    def set_current(cls, object):
        cls._current = weakref.proxy(object)

    @classmethod
    def get_current(cls):
        if cls._current is None:
            raise
        return cls._current



class context_check:
    """
    Decorator for all openGL functions.

    Wanted to hijack everty classmethod calls through magic method
    \but couldn't find one.

    The class does one thing : check if openGL function are called while current
    bound 'glfw.context wrapping object'(ex)Window) has a tracker to log to.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # checks whether current fbl has tracker within it
        # if Windows.get_current() not in GLFW_GL_tracker._windows:
        #     print(list(GLFW_GL_tracker._windows.items()))
        #     raise Exception('Frame_buffer_like object not bound with trackable_GL')
        # modified to insert Trackable_openGL type as cls
        return lambda *args,**kwargs: self.func(Trackable_openGL, *args, **kwargs)

class vao_related:
    """
    Decorator for vao_related functions.
    If glfw context doesn't support vertex array sharing this function will trigger
    to make all shared windows have same vertex array shape, operations by
    calling shared windows through assigned 'shared_windows' argument.

    Built as a type to postpone calling? - if not problem with
    feeding type(Trackabl_openGL) as an argument.
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if not Trackable_openGL._spec_vertex_array_shared:

            def func(*args, **kwargs):
                window = Windows.current()
                windows = window.shared_windows + [window, ]
                for win in windows:
                    win.make_window_current()
                    return_v = self.func(*args, **kwargs)
                return return_v

            return func(*args, **kwargs)

        else:
            return self.func(*args, **kwargs)


class Trackable_openGL:
    """
    Collection of openGL functions and constants.
    Will be appended as other functions gets needed.

    *WARNING
    Be conservative modifying openGL functions in any ways.
    This binder class is built primarily to hijack openGL function call and
    log info with glfw context. Some automation can be made but modifying
    name of function, name of parameter, number of parameters is not recommended.
    Can cause confusion to general users referencing issued openGL specification.
    """
    _debug = True

    original_gl = gl
    # clear
    GL_COLOR_BUFFER_BIT = gl.GL_COLOR_BUFFER_BIT
    GL_DEPTH_BUFFER_BIT = gl.GL_DEPTH_BUFFER_BIT
    GL_STENCIL_BUFFER_BIT = gl.GL_STENCIL_BUFFER_BIT

    # test glEnable...
    GL_SCISSOR_TEST = gl.GL_SCISSOR_TEST
    GL_DEPTH_TEST = gl.GL_DEPTH_TEST
    GL_STENCIL_TEST = gl.GL_STENCIL_TEST
    GL_STENCIL_BITS = gl.GL_STENCIL_BITS
    GL_STENCIL_INDEX = gl.GL_STENCIL_INDEX
    GL_STENCIL_INDEX16 = gl.GL_STENCIL_INDEX16
    GL_SCISSOR_BOX = gl.GL_SCISSOR_BOX

    # operation
    GL_KEEP = gl.GL_KEEP
    GL_ZERO = gl.GL_ZERO
    GL_REPLACE = gl.GL_REPLACE
    GL_INCR = gl.GL_INCR
    GL_INCR_WRAP = gl.GL_INCR_WRAP
    GL_DECR = gl.GL_DECR
    GL_DECR_WRAP = gl.GL_DECR_WRAP
    GL_INVERT = gl.GL_INVERT
    # functions ex) stencil
    GL_NEVER = gl.GL_NEVER
    GL_LESS = gl.GL_LESS
    GL_LEQUAL = gl.GL_LEQUAL
    GL_GREATER = gl.GL_GREATER
    GL_GEQUAL = gl.GL_GEQUAL
    GL_EQUAL = gl.GL_EQUAL
    GL_NOTEQUAL = gl.GL_NOTEQUAL
    GL_ALWAYS = gl.GL_ALWAYS

    # color blending
    GL_BLEND = gl.GL_BLEND
    GL_SRC_ALPHA = gl.GL_SRC_ALPHA
    GL_ONE_MINUS_SRC_ALPHA = gl.GL_ONE_MINUS_SRC_ALPHA

    # draw setting
    GL_DYNAMIC_DRAW = gl.GL_DYNAMIC_DRAW
    GL_STATIC_DRAW = gl.GL_STATIC_DRAW

    # element_draw modes
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
    GL_ARRAY_BUFFER_BINDING = gl.GL_ARRAY_BUFFER_BINDING
    GL_ELEMENT_ARRAY_BUFFER = gl.GL_ELEMENT_ARRAY_BUFFER
    GL_ELEMENT_ARRAY_BUFFER_BINDING = gl.GL_ELEMENT_ARRAY_BUFFER_BINDING

    # frame buffer
    GL_FRAMEBUFFER = gl.GL_FRAMEBUFFER
    GL_DRAW_FRAMEBUFFER = gl.GL_DRAW_FRAMEBUFFER
    GL_READ_FRAMEBUFFER = gl.GL_READ_FRAMEBUFFER
    GL_FRAMEBUFFER_COMPLETE = gl.GL_FRAMEBUFFER_COMPLETE
    GL_DEPTH_ATTACHMENT = gl.GL_DEPTH_ATTACHMENT
    GL_STENCIL_ATTACHMENT = gl.GL_STENCIL_ATTACHMENT

    #
    GL_RENDERBUFFER = gl.GL_RENDERBUFFER



    # get_string
    GL_VERSION = gl.GL_VERSION
    GL_VENDOR = gl.GL_VENDOR
    GL_RENDERER = gl.GL_RENDERER

    # texture format
    GL_RGBA = gl.GL_RGBA
    GL_RGB = gl.GL_RGB
    GL_RGBA8 = gl.GL_RGBA8
    GL_R = gl.GL_R

    # depth stencil internal format
    GL_DEPTH_COMPONENT = gl.GL_DEPTH_COMPONENT
    GL_DEPTH_COMPONENT16 = gl.GL_DEPTH_COMPONENT16
    GL_DEPTH_COMPONENT24 = gl.GL_DEPTH_COMPONENT24
    GL_DEPTH_COMPONENT32 = gl.GL_DEPTH_COMPONENT32
    GL_DEPTH_COMPONENT32F = gl.GL_DEPTH_COMPONENT32F

    GL_STENCIL_COMPONENTS = gl.GL_STENCIL_COMPONENTS
    GL_DEPTH24_STENCIL8 = gl.GL_DEPTH24_STENCIL8
    GL_DEPTH32F_STENCIL8 = gl.GL_DEPTH32F_STENCIL8

    GL_DEPTH_STENCIL = gl.GL_DEPTH_STENCIL
    GL_STENCIL_INDEX1 = gl.GL_STENCIL_INDEX1
    GL_STENCIL_INDEX4  = gl.GL_STENCIL_INDEX4
    GL_STENCIL_INDEX8 = gl.GL_STENCIL_INDEX8
    GL_STENCIL_INDEX16 = gl.GL_STENCIL_INDEX16

    #
    GL_BACK = gl.GL_BACK
    GL_FRONT = gl.GL_FRONT
    GL_FRONT_AND_BACK = gl.GL_FRONT_AND_BACK


    # texture setting
    GL_TEXTURE_2D = gl.GL_TEXTURE_2D
    GL_TEXTURE_MIN_FILTER = gl.GL_TEXTURE_MIN_FILTER
    GL_TEXTURE_MAG_FILTER = gl.GL_TEXTURE_MAG_FILTER
    GL_TEXTURE_WRAP_S = gl.GL_TEXTURE_WRAP_S
    GL_TEXTURE_WRAP_T = gl.GL_TEXTURE_WRAP_T
    GL_TEXTURE_WRAP_R = gl.GL_TEXTURE_WRAP_R
    GL_LINEAR = gl.GL_LINEAR
    GL_REPEAT = gl.GL_REPEAT

    GL_MAX_DRAW_BUFFERS = gl.GL_MAX_DRAW_BUFFERS
    # texture slot
    GL_TEXTURE0 = gl.GL_TEXTURE0
    for i in range(1,31):
        exec(f'GL_TEXTURE{i} = gl.GL_TEXTURE{i}')

    GL_COLOR_ATTACHMENT0 = gl.GL_COLOR_ATTACHMENT0
    for i in range(1, 15):
        exec(f'GL_COLOR_ATTACHMENT{i} = gl.GL_COLOR_ATTACHMENT{i}')
    GL_MAX_COLOR_ATTACHMENTS = gl.GL_MAX_COLOR_ATTACHMENTS

    # vertex array parameter
    GL_VERTEX_ARRAY_BUFFER_BINDING = gl.GL_VERTEX_ARRAY_BUFFER_BINDING
    GL_VERTEX_ARRAY_SIZE = gl.GL_VERTEX_ARRAY_SIZE
    GL_VERTEX_ARRAY_BINDING = gl.GL_VERTEX_ARRAY_BINDING

    GL_VERTEX_ARRAY_POINTER = gl.GL_VERTEX_ARRAY_POINTER

    # for IDE hinting
    _spec_buffer_shared = None
    _spec_vertex_array_shared = None
    _spec_shader_shared = None
    _spec_program_shared = None
    _spec_texture_shared = None
    _spec_render_buffer_shared = None
    _spec_frame_buffer_shared = None
    @classmethod
    def context_specification_check(cls):
        """
        Checks glfw, openGL operation and stores some info as class argument.

        *Run once before creating any other glfw contexts.

        :return: None
        """

        # checking shared openGL components under shared glfw contexts


        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, glfw.GLFW_FALSE) # don't show
        first_win = glfw.glfwCreateWindow(10, 10, 'first', None, None) # two test windows
        second_win = glfw.glfwCreateWindow(10, 10, 'second', None, first_win)
        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, glfw.GLFW_TRUE) # invalidate for real operation

        objects = []
        for w in first_win,second_win:
            glfw.glfwMakeContextCurrent(w)
            d = {}
            objects.append(d)
            d['buffer'] = gl.glGenBuffers(1)
            d['vertex_array'] = gl.glGenVertexArrays(1)
            d['program'] = gl.glCreateProgram()
            d['shader'] = gl.glCreateShader(gl.GL_VERTEX_SHADER)
            d['texture'] = gl.glGenTextures(1)
            d['render_buffer'] = gl.glGenRenderbuffers(1)
            d['frame_buffer'] = gl.glGenFramebuffers(1)

        print()
        print('CONTEXT SPECIFICATION RESULT:')
        longest_name_length = 0
        for i in objects[0].keys():
            if len(i)> longest_name_length:
                longest_name_length = len(i)

        # comparison: same value means component not shared between shared context
        for f,s in zip(objects[0].items(),objects[1].items()):
            name = f[0]
            exec(f'cls._spec_{name}_shared = True if f[1] != s[1] else False')
            result = 'SHARED' if f[1] != s[1] else 'NOT_SHARED'
            print(f'    {name}{" "*(longest_name_length - len(name))} is {result}')


        # generate version, renderer info
        cls._spec_version = gl.glGetString(gl.GL_VERSION)
        cls._spec_renderer = gl.glGetString(gl.GL_RENDERER)
        cls._spec_vendor = gl.glGetString(gl.GL_VENDOR)

        # from the bug of intel graphics, need this mark to trigger extra ibo binding
        cls.vao_stores_ibo = False
        # TODO write down test to verify whether GL_ELEMENT_ARRAY_BUFFER can be
        #   bound with VAO. Don't know how yet.

        # remove tester contexts
        glfw.glfwDestroyWindow(first_win)
        glfw.glfwDestroyWindow(second_win)

        cls.byte_attribute_dict = {}
        for key, value in cls.__dict__.items():
            if key[:3] == 'GL_':
                cls.byte_attribute_dict[int(value)] = value

    @context_check
    def glGenBuffers(cls,n,buffers=None):
        index = gl.glGenBuffers(n, buffers)
        cls.current()._buffers.generate(index)
        return index

    # frame buffer
    @context_check
    def glGenFramebuffers(cls, n, framebuffers=None):
        index =  gl.glGenFramebuffers(n,framebuffers)
        cls.current()._frame_buffers.generate(index)
        return index
    @context_check
    def glBindFramebuffer(cls,target, framebuffer):
        """
        Bind frrame buffer.
        GL_FRAMEBUFFER is equivalent to binding to both GL_DRAW_FRAMEBUFFER and GL_READ_FRAMEBUFFER

        :param target: GL_FRAMEBUFFER, GL_DRAW_FRAMEBUFFER, GL_READ_FRAMEBUFFER
        :param framebuffer: gl_object(index-like value)
        :return: None
        """
        if target == gl.GL_FRAMEBUFFER:
            cls.current()._frame_buffers.bind(framebuffer, gl.GL_DRAW_FRAMEBUFFER)
            cls.current()._frame_buffers.bind(framebuffer, gl.GL_READ_FRAMEBUFFER)
            cls.current()._frame_buffers.bind(framebuffer, gl.GL_FRAMEBUFFER)
        else:
            cls.current()._frame_buffers.bind(framebuffer, target)

        gl.glBindFramebuffer(target, framebuffer)
    @context_check
    def glCheckFramebufferStatus(cls, target):
        result = gl.glCheckFramebufferStatus(target)
        cls.current()._frame_buffers.binding(target).set_attribute('status',cls.byte_attribute_dict[result])
        return result
    @context_check
    def glFramebufferRenderbuffer(cls, target, attachment, renderbuffertarget, renderbuffer):
        # log frame buffer
        fbo = cls.current()._frame_buffers
        rbo = cls.current()._render_buffers.collection[renderbuffer]
        # print(rbo.attributes, rbo.id)
        # print(cls.current()._render_buffers.targets)
        # print(rbo.id, renderbuffer)
        # if rbo.id != renderbuffer:
        #     raise
        fbo.binding(target).set_attribute(attachment, rbo)

        gl.glFramebufferRenderbuffer(target, attachment, renderbuffertarget, renderbuffer)
    @context_check
    def glFramebufferTexture(cls, target, attachment, texture, level):
        # log frame buffer
        fbo = cls.current()._frame_buffers
        fbo.binding(target).set_attribute(attachment, {'object':cls.current()._textures.collection[texture], 'level':level})

        gl.glFramebufferTexture(target, attachment, texture, level)
    @context_check
    def glDeleteFramebuffers(cls, n, framebuffers):
        cls.current()._frame_buffers.remove(framebuffers)
        if not isinstance(n, (tuple, list)):
            framebuffers = [framebuffers,]
        gl.glDeleteFramebuffers(n, framebuffers)

    @context_check
    def glGetFramebufferParameteriv(self):
        gl.glGetFramebufferParameteriv()

    # read, draw buffer
    @context_check
    def glDrawBuffer(cls,mode):
        gl.glDrawBuffer(mode)
    @context_check
    def glDrawBuffers(cls, n, bufs):
        gl.glDrawBuffers(n, bufs)
    @context_check
    def glReadBuffer(cls, mode):
        gl.glReadBuffer(mode)


    @context_check
    @vao_related
    def glGenVertexArrays(cls, n, arrays=None):
        index = gl.glGenVertexArrays(n, arrays)
        cls.current()._vertex_arrays.generate(index)
        return index

    @context_check
    @vao_related
    def glBindVertexArray(cls, array):
        cls.current()._vertex_arrays.bind(array)
        gl.glBindVertexArray(array)

    @context_check
    @vao_related
    def glEnableVertexAttribArray(cls, index):
        gl.glEnableVertexAttribArray(index)

    @context_check
    @vao_related
    def glVertexAttribPointer(cls, index, type, size, normalized, stride, pointer):
        gl.glVertexAttribPointer(index, type, size, normalized, stride, pointer)

    @context_check
    @vao_related
    def glBindBuffer(cls, target, buffer):
        cls.current()._buffers.bind(buffer, target)

        gl.glBindBuffer(target, buffer)

    @context_check
    def glBufferData(cls, target, size, data, usage):
        # TODO is automated size calculation good?
        gl.glBufferData(target, size, data, usage)

    @context_check
    def glCreateProgram(cls):
        index = gl.glCreateProgram()
        cls.current()._programs.generate(index)

        return index

    @context_check
    def glUseProgram(cls, program):
        cls.current()._programs.bind(program)
        gl.glUseProgram(program)

    @context_check
    def glCreateShader(cls, type):
        index = gl.glCreateShader(type)
        cls.current()._shaders.generate(index)

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
        cls.current()._programs.collection[program].set_attribute('linked', True)
        gl.glLinkProgram(program)

    @context_check
    def glValidateProgram(cls, program):
        cls.current()._programs.collection[program].set_attribute('validated', True)
        gl.glValidateProgram(program)

    @context_check
    def glDeleteShader(cls, shader):
        gl.glDeleteShader(shader)
        cls.current()._shaders.remove(shader)

    @context_check
    def glBindAttribLocation(cls, program, index, name):
        gl.glBindAttribLocation(program, index, name)

    @context_check
    def glGetUniformLocation(cls, program, name):
        index = gl.glGetUniformLocation(program, name)
        return index




    @context_check
    def glGenTextures(cls, n, textures=None):
        index = gl.glGenTextures(n, textures)
        cls.current()._textures.generate(index)
        return index

    @context_check
    def glTexParameter(cls, target, pname, parameter):
        gl.glTexParameter(target, pname, parameter)
        cls.current()._textures.binding(target).set_attribute(pname, parameter)

    @context_check
    def glTexImage2D(cls, target, level, internalformat, width, height, border, format, type, pixels):
        gl.glTexImage2D(target, level, internalformat,width,height,border,format,type,pixels)

    @context_check
    def glActiveTexture(cls, texture):
        gl.glActiveTexture(texture)
        slot = cls.byte_attribute_dict[texture]
        cls.current()._textures.activate_slot(slot)

    @context_check
    def glBindTexture(cls, target, texture):
        cls.current()._textures.bind(texture, target)
        gl.glBindTexture(target, texture)

    @context_check
    def glDeleteTextures(cls, n, textures):
        cls.current()._textures.remove(textures)
        if not isinstance(textures, (tuple, list)):
            textures = [textures]
        try:
            # don't know why but it throws error
            gl.glDeleteTextures(n, textures)
        except:
            gl.glDeleteTextures(textures)

    @context_check
    def glDeleteRenderbuffers(cls, n, renderbuffers):
        cls.current()._render_buffers.remove(renderbuffers)
        if not isinstance(renderbuffers, (list,tuple)):
            renderbuffers = [renderbuffers,]
        gl.glDeleteRenderbuffers(n, renderbuffers)
    @context_check
    def glBufferSubData(cls,target,offset,size,data):
        gl.glBufferSubData(target,offset,size,data)

    @context_check
    def glUniformMatrix4fv(cls, location, count, transpose, value):
        gl.glUniformMatrix4fv(location, count, transpose, value)

    # uniform input
    @context_check
    def glUniform4fv(cls, location, count, value):
        gl.glUniform4fv(location, count, value)
    @context_check
    def glUniform1i(cls, location, v0):
        gl.glUniform1i(location, v0)
    @context_check
    def glUniform3fv(self,location,count,value):
        gl.glUniform3fv(location,count,value)


    @context_check
    def glDrawElements(cls,mode,count,type,indices):
        gl.glDrawElements(mode,count,type,indices)

    # pixel read blit
    @context_check
    def glReadPixels(cls,x,y,width,height,format,type,pixels=None):
        return gl.glReadPixels(x,y,width,height,format,type,pixels)
    @context_check
    def glBlitFramebuffer(cls,srcX0,srcY0,srcX1,srcY1,dstX0,dstY0,dstX1,dstY1,mask,filter):
        gl.glBlitFramebuffer(srcX0,srcY0,srcX1,srcY1,dstX0,dstY0,dstX1,dstY1,mask,filter)

    @context_check
    def glGetIntegerv(cls,pname,data=None):
        if data is None:
            data = ctypes.c_int()
            gl.glGetIntegerv(pname,data)
            return data
        else:
            gl.glGetIntegerv(pname,data)


    @context_check
    def glGetString(cls, name):
        return gl.glGetString(name)



    @context_check
    def glGetShaderInfoLog(cls, shader):
        return gl.glGetShaderInfoLog(shader)

    # render buffer
    @context_check
    def glGenRenderbuffers(cls,n, renderbuffers=None):
        id = gl.glGenRenderbuffers(n, renderbuffers)
        cls.current()._render_buffers.generate(id)
        return id
    @context_check
    def glBindRenderbuffer(cls, target, renderbuffer):
        """

        :param target: ignore as it's always GL_RENDERBUFFER
        :param renderbuffer: openGL object
        :return:
        """
        cls.current()._render_buffers.bind(renderbuffer, target)
        gl.glBindRenderbuffer(target, renderbuffer)
    @context_check
    def glRenderbufferStorage(self, target, internalformat, width, height):
        # TODO log data info too?
        gl.glRenderbufferStorage(target, internalformat, width, height)

    # texture
    @context_check
    def glGetTexImage(cls, target, level, format, type, array):
        result = gl.glGetTexImage(target, level, format, type, array)
        return result

    # stencil
    @context_check
    def glStencilMask(cls, mask):
        gl.glStencilMask(mask)
    @context_check
    def glStencilFunc(cls,func,ref,mask):
        gl.glStencilFunc(func,ref,mask)
    @context_check
    def glStencilOp(cls,fail,zfail,zpass):
        gl.glStencilOp(fail,zfail,zpass)

    @context_check
    def glIsEnabled(self,cap):
        return gl.glIsEnabled(cap)


    @classmethod
    def window(cls):
        return Windows.current()

    @classmethod
    def current(cls):
        return GLFW_GL_tracker.get_current() #type:GLFW_GL_tracker

    @classmethod
    def test(cls):
        pass