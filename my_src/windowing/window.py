import threading
import weakref
from collections import OrderedDict
from time import sleep
from time import time

import OpenGL.GL as GL
import glfw as glfw
import glfw.GLFW as GLFW

from error_handler import *
# from renderers.renderer.renderunit import RenderUnit
from virtual_scope import *

from .IO_device import *
from .layers import *
from .viewport import *

from patterns.update_check_descriptor import UCD

class _Windows:
    windows = OrderedDict()
    iter_count = 0
    # def __init__(self):
        # windows = Window.get_windows()
        # for window in windows:
        #     self.__dict__[window.instance_name] = window
    def __init__(self):
        self.windows = self.__class__.windows
        self.iter_count = self.__class__.iter_count

    def __get__(self, instance, owner):
        # return self.__class__.windows
        return _Windows()
    def __getattr__(self, item):
        if item is 'remove':
            return self.__delattr__
        return self.windows[item]

    def __delattr__(self, item):
        self.windows.pop(item.instance_name)

    def __add__(self, other):
        self.windows[other.instance_name] = other
    def __sub__(self, other):
        self.windows.pop(other.instance_name)

    def __iter__(self):
        return self
    def __next__(self):
        if self.iter_count < len(self.windows):
            self.iter_count +=1
            return self.windows[list(self.windows.keys())[self.iter_count-1]] #type: Window
        else:
            self.iter_count = 0
            raise StopIteration

    def __len__(self):
        return len(self.windows)

    def __str__(self):
        return f'collection of {len(self.windows)} window instances'

class Window:
    def _global_init():
        import numpy as np
        from windowing.renderer import BRO
        from windowing.renderer.renderimage import Renderimage
        from windowing.unnamedGUI import mygui
        pass

    _init_global = _global_init
    _windows = _Windows()
    _current_window = None

    _framecount = 0
    _framerate_target = 60
    _print_framerate = False

    _flag_resized = UCD()
    _flag_something_rendered = UCD()
    _size = UCD()

    @classmethod
    def glfw_init(cls,func = None):
        glfw.init()

    def __new__(cls,*args,**kwargs):
        """
         fliped hooking
         from instance → [instances,]
         to [instances,] → instance
         this makes deletion of instance possible before garbage collection
         ex) while inside unfinished loop like 'Window.draw_all()'
         refer to _handle_close for further description
        :param args:
        :param kwargs:
        :return:
        """
        self = super().__new__(cls)
        self.__init__(*args,**kwargs)
        cls._windows + self
        return weakref.proxy(self)

    def __init__(self, width, height, name, monitor = None, mother_window = None):
        self._windows = self.__class__._windows
        # threading.Thread.__init__(self)

        # save name of instance
        f = inspect.currentframe().f_back
        self.instance_name = ''
        try:
            while True:
                code_context = inspect.getframeinfo(f).code_context[0]

                if ' Window(' in code_context and '=' in code_context:
                    self.instance_name = code_context.split('=')[0].strip()
                    break
                else:
                    f = f.f_back
        except:
            print_message("can't grasp instance name","error")
            self.instance_name = 'unknown'

        self._buffers = []
        self._init_info = OrderedDict({
            'width': width,
            'height': height,
            'name': name,
            'monitor': monitor,
            'share': mother_window
        })
        self._mother_window = mother_window #type: Window

        if self._mother_window is not None:
            share = mother_window.glfw_window
        else:
            share = None
        self._glfw_window = glfw.create_window(width, height, name, monitor, share)
        if not self._glfw_window:
            glfw.terminate()
        glfw.make_context_current(self.glfw_window)

        self._option_close = 0

        self._framerate_target = 60
        self._framecount = 0
        self._framerendered_flag = False
        self._terminate_flag = False

        self.thread = None

        self._renderers = []  # type: List[RenderUnit]

        self._draw_func = None
        self._init_func = None
        self._context_scope = Virtual_scope()

        #enable inputs
        self._keyboard = Keyboard(self)
        self._mouse = Mouse(self)

        #window to follow when close
        # TODO maybe it has to be reversed? like...
        #   not a window that has to follow other windows closing
        #   stores that window object, but window that closes other windows
        #   contain windows that it has to close.
        self._follow_close = []

        # drawing layers
        self._layers = Layers(self)

        self._flag_need_swap = True
        self._flag_resized = True
        self._flag_something_rendered = False

        self._size = None
        # viewport
        self._viewports = Viewports(self)


    @property
    def mother_window(self):
        return self._mother_window

    @property
    def renderers(self):
        return self._context_scope.search_value_bytype(RenderUnit)

    @property
    def draw_func(self):
        return self._draw_func
    @property
    def init_func(self):
        return self._init_func

    @property
    def framerate(self):
        return self._framerate_target

    @framerate.setter
    def framerate(self, value):
        self._framerate_target = value

    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard

    @property
    def windows(self):
        return self.__class__._windows

    def preset_window(self,func = None):
        """
        Decorator. set attribute for this single window.
        Use g.window_hint() to specify window attribute.

        :param func: function wrapped for decorator
        :return: None
        """
        func()
        # del self.window
        # i = self._init_info
        # self.window = g.create_window(i['width'],i['height'],
        #                                  i['title'],i['monitor'],
        #                                  i['share'])
        i = self._init_info
        self.init(i['width'], i['height'],
                  i['title'], i['monitor'],
                  i['share'])

    def _snatch_decorated(self, func):
        source = inspect.getsource(func).splitlines()

        indent = 0
        for i in source[0]:
            if i is ' ':
                indent += 1
            else:
                break
        indent += 4

        merged = ''
        for line in source[2:]:
            merged += line[indent:] + '\n'
        return merged

    def init(self = None, func = None):
        # for global init
        if not isinstance(self, Window):
            # Window.glfw_init()
            a = Source_parser.split_func_headbody(Window._init_global, 1, )
            b = Source_parser.split_func_headbody(self, 1)

            Window._init_global = a + b

        # for window instance init
        else:
            self._init_func = func

    def draw(self, func):
        self._draw_func = func

    # def testdraw(self, when):
    #
    #     def wrapper(func_to_execute):
    #         when(func_to_execute)
    #     return wrapper

    def framebuffer_size_callback(self, window, width, height):
        # self.mouse.instant_mouse_onscreen()
        # self.mouse.instant_press_button(button = 0)
        self._flag_resized = True


    def initiation_glfw_setting(self):
        # default setting
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)

        glfw.set_framebuffer_size_callback(self.glfw_window, self.framebuffer_size_callback)
        # g.swap_interval(60)

    def initiation_gl_setting(self):
        GL.glEnable(GL.GL_SCISSOR_TEST)
        GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

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

    @classmethod
    def run_single_thread(cls, framecount = None):
        """
        runs all windows in single thread.
        works very fine.
        :return:
        """
        # TODO is it good to have this long initiation here?
        #initiation
        for window in cls._windows:
            window.make_window_current()

            # init setting
            window.initiation_glfw_setting()
            window.initiation_gl_setting()
            window.initiation_window_setting()

            # assigned var names
            # TODO maybe need more assigned variables?
            window._context_scope.set_assigned(
                {'window': window, 'windows': window.windows, 'self': window, window.instance_name: window})

            # if Window has global init
            func = window.__class__._init_global
            window._context_scope.append_scope(func)

            # if window has mother window
            if window._mother_window is not None:
                if window.mother_window.init_func is not None:
                    window._context_scope.append_scope_byscope(window.mother_window._context_scope)

                # renderers = window.mother_window.renderers
                #
                # for renderer in renderers:
                #     renderer[1].rebind()

            if window.init_func is not None:
                window._context_scope.append_scope(window.init_func)



        timer = Timer(cls._framerate_target,'single thread')
        timer.set_init_position()
        # timer.print_framerate()
        # timer.print_framerate_drawing()
        while True:
            timer.set_routine_start()
            if cls._display_window():
                # to give access to other windows through keyword 'windows'
                for window in cls._windows:

                    #drawing
                    window.make_window_current()
                    window._context_scope.run(window.draw_func)

                    if window._flag_something_rendered:
                        glfw.swap_buffers(window.glfw_window)

                    window._flag_something_rendered = False
                    window._flag_resized = False
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
            if window.mother_window == self or self in window._follow_close:
                window.close()
                break
        glfw.make_context_current(None)
        glfw.destroy_window(self.glfw_window)
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

                if window.option_close is 0:
                    window.close()
                    pass

                elif window.option_close is 1:
                    glfw.hide_window(window.glfw_window)

                elif window.option_close is 2:
                    glfw.destroy_window(window.glfw_window)

        for window in cls._windows:
            if glfw.get_window_attrib(window.glfw_window, GLFW.GLFW_VISIBLE):
                return True
            else:
                continue
        return False

    @property
    def glfw_window(self):
        return self._glfw_window

    @property
    def name(self):
        return self._init_info['name']

    def __str__(self):
        return f"window: '{self.name}'"

    @property
    def option_close(self):
        return self._option_close

    def follows_closing(self, *windows):
        self._follow_close += windows

    @option_close.setter
    def option_close(self, option: (int, str)):
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
            self._option_close = option

        else:
            print_message('Type error. Maintain attribute.')

    def make_window_current(self):
        self.__class__._current_window = self
        # RenderUnit.push_current_window(self)
        glfw.make_context_current(None)
        glfw.make_context_current(self.glfw_window)

    @classmethod
    def get_current_window(cls):
        return cls._current_window

    @property
    def layer(self):
        return self._layers

    @property
    def viewports(self):
        return self._viewports

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
    def current_framerate(self):
        return self._current_framerate
    @property
    def framecount(self):
        return self._framecount

