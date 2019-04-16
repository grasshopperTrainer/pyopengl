import threading
import weakref
from collections import OrderedDict
from time import sleep
from time import time

import OpenGL.GL as gl
import glfw as glfw
import glfw.GLFW as GLFW

from error_handler import *
from renderers.renderUnit.renderunit import RenderUnit
from virtual_scope import Virtual_scope


class _Mouse:

    def __init__(self, window):
        self._window = window

        self._button_pressed = []
        self._scroll_offset = []
        self._flag_cursor_onscreen = False

        def empty(*args, **kwargs):
            pass

        self._event_move = empty
        self._event_enter = empty
        self._event_exit = empty
        self._event_click = empty
        self._event_scroll = empty

        glfw.set_cursor_pos_callback(self._window.glfw_window, self._callback_mouse_move)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self._callback_mouse_enter)
        glfw.set_mouse_button_callback(self._window.glfw_window, self._callback_mouse_button)
        glfw.set_scroll_callback(self._window.glfw_window, self._callback_mouse_scroll)

    def __call__(self, func):
        source = inspect.getsource(func).splitlines()[2:]
        source = [line[4:] for line in source]

        functions = {}
        add = False

        for i, line in enumerate(source):
            if line.find('def') == 0:
                end = line.find('(')
                name = line[3:end].strip()
                functions[name] = line + '\n'
            elif line[:4] == '    ':
                functions[name] += line + '\n'
        signs = ['move', 'enter', 'exit', 'click', 'scroll']
        for func_name in functions:
            if func_name in signs:
                func = functions[func_name]
                exec(f'self._event_{func_name} = func')

    def _callback_mouse_move(self, context, xpos, ypos):
        self._window._context_scope.run(self._event_move)

    def _callback_mouse_enter(self, context, entered):
        if entered:
            self._window._context_scope.run(self._event_enter)
            self._flag_cursor_onscreen = True
        else:
            self._window._context_scope.run(self._event_exit)
            self._flag_cursor_onscreen = False

    def _callback_mouse_button(self, context, button, action, mods):
        if action is 1:
            self._button_pressed.append(button)
        if action is 0:
            self._button_pressed.remove(button)

        self._window._context_scope.run(self._event_click)

    def _callback_mouse_scroll(self, context, xoffset, yoffset):
        self._scroll_offset = xoffset, yoffset
        self._window._context_scope.run(self._event_scroll)

    @property
    def cursor_onscreen(self):
        return self._flag_cursor_onscreen

    @property
    def mouse_position(self):
        try:
            x, y = glfw.get_cursor_pos(self._glfw_window)
        except:
            x, y = -1, -1
        return x, y

    @property
    def scroll_offset(self):
        return self._scroll_offset

    @property
    def button_pressed(self):
        return self._button_pressed


class _Keyboard:

    def __init__(self, window):
        self._window = window

        self._pressed_keys = []
        self._event_keyboard = 'pass'

        glfw.set_key_callback(self._window._glfw_window, self._callback_keyboard)

    def press(self, func):
        self._event_keyboard = self._window._snatch_decorated(func)

    def _callback_keyboard(self,instance, key,scancode,action,mods):
        if action is 1:
            self.pressed_keys.append(key)
        if action is 0:
            self.pressed_keys.remove(key)

        self._window.execute(self._window,self._event_keyboard)

    @property
    def pressed_keys(self):
        return self._pressed_keys

    def key_pressed(self, *keys):
        pressed = True
        for key in keys:
            pressed = pressed and key in self.pressed_keys

        return pressed









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
        import OpenGL.GL as gl
        import numpy as np
        from renderers.TestRenderer import Renderer

    _init_global = _global_init
    _windows = _Windows()
    _current_window = None

    _framecount = 0
    _framerate_target = 60
    _print_framerate = False

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
                if 'Window' in code_context and '=' in code_context:
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

        self._preset_window_default()
        if self._mother_window is not None:
            share = mother_window.glfw_window
        else:
            share = None
        self._glfw_window = glfw.create_window(width, height, name, monitor, share)
        if not self._glfw_window:
            glfw.terminate()

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
        self._keyboard = _Keyboard(self)
        self._mouse = _Mouse(self)

        #window to follow when close
        # TODO maybe it has to be reversed? like...
        #   not a window that has to follow other windows closing
        #   stores that window object, but window that closes other windows
        #   contain windows that it has to close.
        self._follow_close = []

        # drawing layers
        self._layers = []

    @property
    def mother_window(self):
        return self._mother_window

    @property
    def renderers(self):
        return self._context_scope.search_value_bytype(RenderUnit)

    def _preset_window_default(self):
        # default setting
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)

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

    # def __getattr__(self, item):
    #     # print(item)
    #     if item in Renderer.get_instances():
    #         renderer = Renderer.get_instances()[item]
    #         name = renderer.name
    #         # print(f'self.{name} = renderer')
    #         self.__setattr__(name,renderer)
    #         return renderer
    #     else:
    #         print_message("can't find attribute")
    #         raise AttributeError



    def preset_window(self,func = None):
        """
        Decorator. set attribute for this single window.
        Use glfw.window_hint() to specify window attribute.

        :param func: function wrapped for decorator
        :return: None
        """
        func()
        # del self.window
        # i = self._init_info
        # self.window = glfw.create_window(i['width'],i['height'],
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
            Window._init_global = self
        # for window instance init
        else:
            self._init_func = func

    def draw(self, func):
        self._draw_func = func


    # def thread_run(self):
    #     # if glfw.get_current_context() is not self.glfw_window:
    #     glfw.make_context_current(self.glfw_window)
    #     # glfw.swap_interval(1)
    #     exec(self.init_source)
    #
    #     timer = Timer(self.framerate, self.name)
    #     timer.set_init_position()
    #     timer.print_framerate()
    #     while True:
    #         timer.set_routine_start()
    #         # print(self)
    #         if self._terminate_flag:
    #             # will mulfunction if not detached before thread is over
    #             glfw.make_context_current(None)
    #             break
    #         # print(self.draw_source)
    #         for line in self.draw_source:
    #             exec(line)
    #         glfw.swap_buffers(self.glfw_window)
    #         # print(self, self.draw_source)
    #
    #         self._framerendered_flag = True
    #
    #         timer.set_routine_end()

    def initiation_gl_setting(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

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
            window.initiation_gl_setting()

            # if Window has global init
            func = window.__class__._init_global
            window._context_scope.append_scope_byfunc(func)

            # if window has mother window
            if window._mother_window is not None:
                if window.mother_window.init_func is not None:
                    window._context_scope.append_scope_byscope(window.mother_window._context_scope)

                renderers = window.mother_window.renderers

                for renderer in renderers:
                    renderer[1].rebind()

            if window.init_func is not None:
                window._context_scope.append_scope_byfunc(window.init_func)

            # assigned var names
            # TODO maybe need more assigned variables?
            window._context_scope.append_scope_byitems(('window', 'windows', 'self'), (window, window.windows, window))




        timer = Timer(cls._framerate_target,'single thread')
        timer.set_init_position()
        # timer.print_framerate()
        # timer.print_framerate_drawing()
        while True:
            timer.set_routine_start()
            if cls._display_window():
                # to give access to other windows through keyword 'windows'
                windows = cls._windows
                for window in cls._windows:
                    #drawing
                    # try:
                    # glfw.make_context_current(None)
                    # glfw.make_context_current(window.glfw_window)
                    window.make_window_current()

                    window._context_scope.run(window.draw_func)

                    # except Exception as e:
                    #     print(e, window.instance_name, len(cls._windows))
                    #     break
                    glfw.swap_buffers(window.glfw_window)

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

    def close_window_concequently(self):
        for window in self._windows:
            if window.mother_window == self or self in window._follow_close:
                window.close_window_concequently()
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
                    window.close_window_concequently()
                    pass

                elif window.option_close is 1:
                    glfw.hide_window(window.glfw_window)

                elif window.option_close is 2:
                    glfw.destroy_window(window.glfw_window)

        for window in cls._windows:
            if glfw.get_window_attrib(window.glfw_window,GLFW.GLFW_VISIBLE):
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
        What does it mean when window_sould_close is raised by glfw?

        :param option:
        0 or 'c' - remove window from application
        1 or 'h' - hide window (running but not being displayed)
        2 or 's' - save (class)Window property while removing glfw context
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
        RenderUnit.push_current_window(self)
        glfw.make_context_current(None)
        glfw.make_context_current(self.glfw_window)

    @classmethod
    def get_current_window(cls):
        return cls._current_window


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
        #     self._glfwtime = glfw.get_time()

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

