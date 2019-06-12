import threading
import weakref
import traceback
from collections import OrderedDict
from time import sleep
from time import time

from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker

import glfw as glfw
# import glfw.GLFW as GLFW

from error_handler import *
# from renderers.renderer.renderunit import RenderUnit
from virtual_scope import *

from .IO_device import *
from .layers import *
from .viewport import *

from patterns.update_check_descriptor import UCD
from .frame_buffer_like.frame_buffer_like_bp import FBL

from windowing.frame_buffer_like.renderable_image import Renderable_image
from windowing.frame_buffer_like.frame import Frame
from .windows import Windows

class Test:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Window:
    """
    Main class for window creation.


    """
    """
    Load packages for internal use.
    MEMO
    import numpy as np
    from windowing.renderer import BRO
    from windowing.renderable_image import Renderable_image
    from windowing.unnamedGUI import mygui
    from windowing.viewport.viewport import Viewport
    import OpenGL.GL as gl
    import glfw as glfw
    """
    def _global_init():
        import numpy as np
        from windowing.renderer import BRO
        from windowing.frame_buffer_like.renderable_image import Renderable_image
        from windowing.unnamedGUI import mygui
        from windowing.viewport.viewport import Viewport
        import OpenGL.GL as gl
        import glfw as glfw
        pass

    _init_global = _global_init
    _windows = Windows()

    _default_framerate_target = 60
    _print_framerate = False

    _flag_resized = UCD()
    _flag_something_rendered = UCD()
    _size = UCD()
    # ^are UCD still valid?

    @classmethod
    def glfw_init(cls):
        """
        Init GLFW and GL.
        Singular caller for main file.
        :return: None
        """
        glfw.init()
        gl.context_specification_check() # check additional specification
    def __enter__(self):
        return self
    def __enter__(self):
        print('this is enter')
        return self.myframe
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __new__(cls,*args,**kwargs):
        self = super().__new__(cls)

        # cls._windows + self
        return self # return proxy of generated object

    def __init__(self, width, height, name, monitor = None, mother_window = None):

        self._size = width, height
        self._name = name
        self._monitor = monitor

        # add this window to a group
        # but if window is set to be singular
        # evade window creation
        self.windows + self

        Windows.set_current(self) # for init process may be needing which window is current
        # stores object name as an instance name
        # f = inspect.currentframe().f_back
        # self._instance_name = ''
        # try:
        #     while True:
        #         code_context = inspect.getframeinfo(f).code_context[0]
        #         if ' Window(' in code_context and '=' in code_context:
        #             self._instance_name = code_context.split('=')[0].strip()
        #             break
        #         else:
        #             f = f.f_back
        # except:
        #     print_message("can't grasp instance name", "error")
        #     self._instance_name = 'unknown'

        # 1. generate contex first.
        # Do not mix order 1 and 2. There is automated vertex array operation during 2.
        if mother_window is not None:
            self._glfw_window = glfw.create_window(width, height, name, monitor, mother_window._glfw_window)
        else:
            self._glfw_window = glfw.create_window(width, height, name, monitor, None)
        # glfw window creation error check
        if not self._glfw_window:
            glfw.terminate()
            raise Exception("can't create glfw context")
        # set it current for farther settings
        glfw.make_context_current(self.glfw_window)

        # 2. store relationship between mother and children
        self._children_windows = []
        self._mother_window = mother_window  # type: Window
        if mother_window is not None:
            mother_window._children_windows.append(weakref.proxy(self))
            # if window is shared share unique context too
            self._unique_glfw_context = mother_window.unique_glfw_context.give_tracker_to(self)
        else:
            # this is a unique context wrapper and is a context identifier
            self._unique_glfw_context = GLFW_GL_tracker(self)


        # customizable frame
        m = glfw.get_primary_monitor()
        _,_,max_width,max_height = glfw.get_monitor_workarea(m)
        extra = 500 # this is to cover Windows content area. May be needed for full screen draw
        self._myframe = Frame(max_width+extra, max_height+ extra)  # type: Renderable_image
        # glsl: layout(location = 0), this is default output
        # this is ambient color output
        self._myframe.use_color_attachment(0)
        # this is id_color: please output color for distinguishing drawn objects
        self._myframe.use_color_attachment(1)
        # use basig depth and stencil
        self._myframe.use_depth_attachment(bitdepth=32)
        self._myframe.use_stencil_attachment(bitdepth=16)
        self._myframe.build()
        print('window my frame buffer=',self.myframe._frame_buffer._glindex)


        # some info for resetting
        # look at preset_window() for further usage
        self._init_info = OrderedDict({
            'width': width,
            'height': height,
            'name': name,
            'monitor': monitor,
            'share': mother_window
        })

        # option of window closing event
        # tells what to do when window is set to close
        # options are: remove, hide, save
        # look at close_option() setter for furthr usage
        self._close_option = 0

        # frame operation
        self._framerate_target = 60
        self._framecount = 0

        # function to execute in each state
        self._init_func = None
        self._draw_func = None

        # set virtual scoper for executing init and draw functions
        # TODO think this won't work generally
        path = inspect.getfile(inspect.currentframe().f_back.f_back)
        self._context_scope = Virtual_scope(executing_filepath=path)

        # enable inputs
        self._keyboard = Keyboard(self)
        self._mouse = Mouse(self)

        # follow closing of following windows
        # set by follows_closing()

        # drawing layers
        # TODO integrate
        self._layers = Layers(self)

        # flags for frame drawing and swapping
        self._flag_resized = True

        # viewport collection
        self._viewports = Viewports(self)

        self.initiation_post_glfw_setting()
        self.initiation_gl_setting()
        self.initiation_window_setting()

        self._flag_singular = False


        self._flag_movable = True

        self._callbacks = {
            'pre_draw':[],
            'post_draw':[],
            'window_resize':[],
            'window_close':[],
            'window_pos':[],
            'window_refresh':[],
            'window_focused':[],
            'window_maximized':[],
            'window_iconify':[],
            'window_content_scale':[]
                           }

        self._z_position = 0

    @property
    def mother_window(self):
        return self._mother_window
    @property
    def children_windows(self):
        return self._children_windows
    @property
    def draw_func(self):
        return self._draw_func
    @property
    def init_func(self):
        return self._init_func

    # @property
    # def framerate(self):
    #     return self._default_framerate_target
    # @framerate.setter
    # def framerate(self, value):
    #     self._default_framerate_target = value
    def _callback_exec(func):
        def wrapper(*args, **kwargs):
            name = func.__name__.split('_callback')[0]
            for f,a,k,_ in args[0]._callbacks[name]:
                f(*a,**k)
            func(*args, **kwargs)
        return wrapper

    @_callback_exec
    def window_resize_callback(self, window, width, height):
        if any(a < b for a,b in zip(self.myframe.size, self.size)):
            self.myframe.rebuild(self.size)
        self._flag_resized = True

    @_callback_exec
    def window_refresh_callback(self,a):
        pass
    @_callback_exec
    def pre_draw_callback(self):
        pass
    @_callback_exec
    def post_draw_callback(self):
        pass
    @_callback_exec
    def window_pos_callback(self, window, x, y):
        pass
    @_callback_exec
    def window_close_callback(self,window):
        pass
    @_callback_exec
    def window_focused_callback(self,window,focused):
        print('ddd')
        pass
    @_callback_exec
    def window_iconify_callback(self, window, iconified):
        pass
    @_callback_exec
    def window_content_scale_callback(self, xscale, yscale):
        pass
    @_callback_exec
    def window_maximized_callback(self,window, maximized):
        pass

    def _callback_setter(func):
        def wrapper(self, function, args: tuple = (), kwargs: dict = {}, name:str = 'unknown'):
            if not callable(function):
                raise TypeError
            if not isinstance(args, tuple):
                raise TypeError
            if not isinstance(kwargs, dict):
                raise TypeError
            callback_name = func.__name__.split('set_')[1].split('_callback')[0]
            self._callbacks[callback_name].append((function,args,kwargs,name))
        return wrapper

    @_callback_setter
    def set_pre_draw_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown'):
        pass
    @_callback_setter
    def set_post_draw_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown'):
        pass
    @_callback_setter
    def set_window_resize_callback(self, func, args:tuple = (), kwargs:dict={}, name:str='unknown'):
        pass
    @_callback_setter
    def set_window_close_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown'):
        pass
    @_callback_setter
    def set_window_pos_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown'):
        pass
    @_callback_setter
    def set_window_iconify_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown'):
        pass

    def _follow(func):
        def wrapper(self, *windows):
            if not all([isinstance(w, Window) for w in windows]):
                raise TypeError
        return wrapper

    @_follow
    def follow_window_iconify(self, *windows):
        for w in windows:
            w.set_window_iconify_callback(self.config_iconified, (True,))
    @_follow
    def follows_window_close(self, *windows):
        for w in windows:
            w.set_window_close_callback(self.close)

    # def (self, window):
    #     if not isinstance(window,Window):
    #         raise TypeError
    #     self.set_window_iconify_callback(window.config_iconified, (True,))

    def set_window_z_position(self, z:int):
        self.windows.set_window_z_position(self,z)
    def test(self):
        glfw.request_window_attention(self.glfw_window)
    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard
    @property
    def instance_name(self):
        return self._instance_name
    @property
    def windows(self):
        return self.__class__._windows

    def _set_config(func):
        def wrapper(self, set:bool):
            if set:
                set = glfw.TRUE
            else:
                set = glfw.FALSE

            hint = 'glfw.' + func.__name__.split('config_')[1].upper()
            if hasattr(self, 'glfw_window'):
                try:
                    glfw.set_window_attrib(self.glfw_window, eval(hint), set)
                except:
                    print(f"hint {hint} can't be set after glfw context creation")
            else:
                glfw.window_hint(eval(hint), set)

        return wrapper


    @_set_config
    def config_decorated(self, set:bool):
        pass
    @_set_config
    def config_resizable(self, set:bool):
        pass


    def config_movable(self, set:bool):
        self._flag_movable = set

    def config_iconified(self, set: bool):
        if set:
            set = glfw.TRUE
        else:
            set = glfw.FALSE

        if hasattr(self, 'glfw_window'):
            if set:
                glfw.iconify_window(self.glfw_window)
            else:
                pass
        else:
            glfw.window_hint(glfw.ICONIFIED, set)

    def config_focused(self, set:bool):
        if set:
            set = glfw.TRUE
        else:
            set = glfw.FALSE

        if hasattr(self, 'glfw_window'):
            if set:
                glfw.focus_window(self.glfw_window)
            else:
                pass
        else:
            glfw.window_hint(glfw.FOCUSED, set)

    def config_visible(self, set:bool):
        if set:
            set = glfw.TRUE
        else:
            set = glfw.FALSE

        if hasattr(self, 'glfw_window'):
            if set:
                glfw.show_window(self.glfw_window)
            else:
                glfw.hide_window(self.glfw_window)
        else:
            glfw.window_hint(glfw.VISIBLE, set)
    # def show(self):
    #     glfw.show_window(self.glfw_window)
    # def hide(self):
    #     glfw.hide_window(self.glfw_window)

    def _get_config(func):
        @property
        def wrapper(self):
            hint = 'glfw.' + func.__name__.split('is_')[1].upper()
            return bool(glfw.get_window_attrib(self.glfw_window,eval(hint)))
        return wrapper

    @_get_config
    def is_visible(self):
        pass

    @_get_config
    def is_resizable(self):
        pass
    @_get_config
    def is_focused(self):
        pass




    def initiation_post_glfw_setting(self):
        # default setting
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.set_framebuffer_size_callback(self.glfw_window, self.window_resize_callback)
        glfw.set_window_refresh_callback(self.glfw_window, self.window_refresh_callback)
        glfw.set_window_pos_callback(self.glfw_window,self.window_pos_callback)
        glfw.set_window_focus_callback(self.glfw_window,self.window_focused_callback)
        glfw.set_window_iconify_callback(self.glfw_window,self.window_iconify_callback)
        glfw.set_window_close_callback(self.glfw_window,self.window_close_callback)
        glfw.set_window_content_scale_callback(self.glfw_window,self.window_content_scale_callback)
        glfw.set_window_maximize_callback(self.glfw_window,self.window_maximized_callback)
        # g.swap_interval(60)

    def initiation_gl_setting(self):
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_STENCIL_TEST)
        a = gl.glGetIntegerv(gl.GL_SCISSOR_TEST)
        b = gl.glGetIntegerv(gl.GL_DEPTH_TEST)
        c = gl.glGetIntegerv(gl.GL_STENCIL_TEST)
        if a.value + b.value + c.value != 3:
            raise Exception('enabling test problem')

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    def initiation_window_setting(self):
        # self._viewports.new(0, 0, 1.0, 1.0, 'default')
        pass

    # def clear(self, *color):
    #     if len(color) == 0:
    #         color = (1, 1, 1, 1)
    #     GL.glClearColor(*color)
    #     GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    #     GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
    #     self._flag_need_swap = True
    def _draw_(self):
        pass

    @classmethod
    def run_single_thread(cls, framecount = None):
        """
        runs all windows in single thread.
        works very fine.
        :return:
        """

        timer = Timer(cls._default_framerate_target, 'single thread')
        timer.set_init_position()
        # timer.print_framerate()
        # timer.print_framerate_drawing()
        while True:
            timer.set_routine_start()
            if cls._display_window():
                # to give access to other windows through keyword 'windows'
                for window in cls._windows: #type: Window

                    #drawing
                    window.make_window_current()
                    # window.viewports[0].open()
                    window.pre_draw_callback()
                    window._draw_()
                    window.post_draw_callback()

                    if window.myframe.flag_something_rendered:
                        # copy from custom myframebuffer and draw it on window
                        window.make_window_current()
                        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER,window.myframe._frame_buffer._glindex)
                        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0) # set source

                        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER,0)
                        gl.glBlitFramebuffer(0,0,window.width,window.height,
                                             0,0,window.width,window.height,
                                             gl.GL_COLOR_BUFFER_BIT,
                                             gl.GL_LINEAR)

                        glfw.swap_buffers(window.glfw_window)


                    window.myframe.flag_something_rendered = False
                    window._flag_resized = False

                    # viewports = window.viewports._viewports
                    #
                    # # UCD.reset_instance_descriptors_update(window)
                    # UCD.reset_instance_descriptors_update(*viewports.values())
                    # UCD.reset_instance_descriptors_update(*[v.camera for v in viewports.values()])
                    window.mouse.reset()

                glfw.poll_events()

            else:
                break

            timer.set_routine_end()
            if timer.framecount == framecount:
                break

        # TODO fix ↓
        # Shader.deleteProgram()
        glfw.terminate()

    @classmethod
    def run_multi_thread(cls):
        raise DeprecationWarning('multi threading for windwing deprecated')
        for window in cls._windows:
            t = threading.Thread(target= window.thread_run)
            window.thread = t
            window.thread.start()

        timer = Timer(cls._framerate_target,'event')
        timer.set_init_position()
        while cls._display_window(True):
            timer.set_routine_start()
            if cls._display_window(True):

                if all([window._framerendered_flag for window in cls._windows]):
                    glfw.poll_events()
                    for window in cls._windows:
                        window._framerendered_flag = False
            else:
                break
            timer.set_routine_end()

        glfw.terminate()
        pass

    @classmethod
    def print_framerate(cls, state: bool = True):
        cls._print_framerate = state

    def close(self):
        """
        Closes window concequently.

        To close itself, closes all the child windows beforehand

        :return: None
        """
        for window in self._windows:
            if self in window.children_windows:
                window.children_windows.remove(self)


        glfw.make_context_current(None)
        glfw.destroy_window(self.glfw_window)
        GLFW_GL_tracker.remove(self)
        self._windows - self


    @classmethod
    def _display_window(cls, multi_thread = False):
        """
        checks in every draw_all iteration whether a window
        sould be desplayed.
        If there is no window to display or all are invisible
        returns False thus drawing application terminates.
        :return: bool
        """
        # close operation
        for i,window in enumerate(cls._windows):
            if glfw.window_should_close(window.glfw_window):
                glfw.make_context_current(None)

                if multi_thread:
                    window._terminate_flag = True
                    window.thread.join()
                else:
                    pass

                if window.close_option is 0:
                    window.close()
                    pass

                elif window.close_option is 1:
                    glfw.hide_window(window.glfw_window)

                elif window.close_option is 2:
                    glfw.destroy_window(window.glfw_window)

        for window in cls._windows:
            if glfw.get_window_attrib(window.glfw_window, glfw.VISIBLE):
                return True
            else:
                continue

        print('TERMINATING GLFW')
        print('first possible cause is : all windows closed')
        print('second possible cause is : all windows hidden')
        return False

    @property
    def glfw_window(self):
        return self._glfw_window

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f"window: '{self.name}'"

    @property
    def close_option(self):
        return self._close_option



    @close_option.setter
    def close_option(self, option: (int, str)):
        """
        Set window attribute for closing operation.
        What does it mean when window_sould_close is raised by g?

        :param option:
        0 or 'c' - remove window from application
        1 or 'h' - hide window (running but not being displayed)
        2 or 's' - save (class)Window property while removing g context
        :return: None
        """
        if isinstance(option, str):
            if option is 'c':
                option = 0
            elif option is 'h':
                option = 1
            elif option is 's':
                option = 2
            else:
                raise ValueError

        if isinstance(option, int):
            self._close_option = option

        else:
            print_message('Type error. Maintain attribute.')

    def make_window_current(self):
        # if self.windows.get_current() != self:
        self.windows.set_current(self)

        glfw.make_context_current(None)
        glfw.make_context_current(self.glfw_window)

        GLFW_GL_tracker.set_current(self.unique_glfw_context)
        FBL.set_current(self._myframe)


    # @classmethod
    # def get_current_window(cls):
    #     return cls.windows.get_current()

    @property
    def layers(self):
        return self._layers

    @property
    def viewports(self):
        return self._viewports #type:Viewports

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def size(self):
        self._size = glfw.get_framebuffer_size(self.glfw_window)
        return self._size

    @property
    def is_resized(self):
        return self._flag_resized

    @property
    def master_window(self):
        master = None
        if self.mother_window is None:
            return self
        else:
            master = self.mother_window.master_window
        return master

    @property
    def offspring_windows(self, _count=0):
        children = []
        if len(self.children_windows) != 0:
            children += self.children_windows
            for c in self.children_windows:
                children += c.offspring_windows
        return children

    @property
    def shared_windows(self):
        m = self.master_window
        o = m.offspring_windows
        o.insert(0,weakref.proxy(m))
        o.remove(self)
        return o

    @property
    def unique_glfw_context(self):
        return self._unique_glfw_context
    @property
    def myframe(self):
        return self._myframe

    def gen_child(self,width, height, name, monitor):
        w = Window(width, height, name, monitor, self)
        self.make_window_current()
        return w

    def get_vertex(self, vertex = 0):
        """
        Returns coordinate of window vertex.
        Index goes anti-clockwise begining from top left.

        0-------3
        ｜     ｜
        ｜     ｜
        1-------2

        :param vertex: index of a vertex 0,1,2,3
        :return: tuple(x,y)
        """
        top_left = glfw.get_window_pos(self._glfw_window)
        if vertex == 0:
            return top_left
        elif vertex == 1:
            return top_left[0],top_left[1] + self.height
        elif vertex == 2:
            return top_left[0]+ self.width,top_left[1]+self.height
        elif vertex == 3:
            return top_left[0]+self.width,top_left[1]
        else:
            raise KeyError

    def move_to(self, target_screen_coord, reference_window_coord):
        x,y = int(target_screen_coord[0] - reference_window_coord[0]), int(target_screen_coord[1] - reference_window_coord[1])
        self.position = (x,y)

    @property
    def position(self):
        return glfw.get_window_pos(self.glfw_window)

    @position.setter
    def position(self, pos):
        if self._flag_movable:
            glfw.set_window_pos(self.glfw_window, int(pos[0]), int(pos[1]))

    def set_fix_position(self, target_screen_pos, reference_window_pos):
        self.move_to(target_screen_pos,reference_window_pos)
        self._flag_movable = False

    def set_size_limit(self):
        pass

    @property
    def is_singular(self):
        return self._flag_singular

    # def follow_cursor(self):
    #     print(self.mouse.window_position)
class Timer:
    def __init__(self,framerate, name):
        self._framecount = 0
        self._frametarget = framerate
        self._name = name
        self._current_framerate = 0

        self._saved_time_frame_start = None
        self._saved_time_frame_end = None
        self._saved_time_second = None

        self._frame_compensation = 0

        self._start_position_set = False
        self._routine_start_position_set = False
        self._print_framerate = False
        self._print_framerate_drawing = False
        self._glfwtime = 0

    def set_init_position(self):
        self._start_position_set = True
        self._saved_time_frame_start = time()
        self._saved_time_frame_end = glfw.get_time()
        self._saved_time_second = time()
    def print_framerate(self):
        self._print_framerate = True
    def print_framerate_drawing(self):
        self._print_framerate_drawing = True
    def set_routine_start(self):
        glfw.set_time(0)
        if self._start_position_set:
            # for compensation
            target = 1 / self._frametarget
            self._frame_compensation = (time() - self._saved_time_frame_start - target)/2
            self._saved_time_frame_start = time()
            # print(self._frame_compensation)

    def set_routine_end(self):
        # measure sleep
        if self._framecount % self._frametarget is 0:
            per_second_rendering_time = time() - self._saved_time_second
            try:
                self._current_framerate = self._frametarget / per_second_rendering_time
            except:
                pass
            else:
                self._saved_time_second = time()
                # if self._print_framerate:
                #     print()
                #     print(f'{self._name}: framerate: {round(self._current_framerate)}')

        target = 1/self._frametarget
        rendering_time = glfw.get_time()

        # if self._print_framerate_drawing:
        #     if self._framecount % self._frametarget is 0:
        #         try:
        #             fps = 1/rendering_time
        #         except:
        #             fps = 0
        #         print(f'drawing_framerate: {fps}')
        #     self._glfwtime = g.get_time()

        self._framecount += 1
        #sleep
        waiting_time = target - rendering_time - self._frame_compensation
        if waiting_time >= 0:
            sleep(waiting_time)
        else:
            pass
    @property
    def framecount(self):
        return self._framecount


