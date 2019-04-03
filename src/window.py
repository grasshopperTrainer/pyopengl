import glfw as glfw
import glfw.GLFW as GLFW
from OpenGL.GL import *

from time import sleep
from time import time

import threading
import inspect
import weakref
import numpy as np
from collections import OrderedDict

from buffers import Buffer
from renderer import Renderer
from shader import Shader
from error_handler import *
from gltracker import GLtracker
from gloverride import *
from input_dictionary import _Input_dicts


class _Context_scope:

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        pass

class Switch:
    def __init__(self):
        self.draw_window = True
        self.display_window = True

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
        self.__class__.windows[other.instance_name] = other

    def __iter__(self):
        return self
    def __next__(self):
        if self.iter_count < len(self.windows):
            self.iter_count +=1
            return self.windows[list(self.windows.keys())[self.iter_count-1]]
        else:
            self.iter_count = 0
            raise StopIteration

class Window:
    _windows = _Windows()

    _framecount = 0
    _framerate_target = 60
    _print_framerate = False
    @classmethod
    def glfw_init(cls):
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

        self.draw_source = 'glClear(GL_COLOR_BUFFER_BIT)'
        self.init_source = 'pass' #type: str

        self._framerate_target = 60
        self._framecount = 0
        self._framerendered_flag = False
        self._terminate_flag = False

        self.thread = None

        self._renderers = [] # type: List[Renderer]
        self._context_scope = _Context_scope()

        self._enable_event()
        self._keys_pressed = []
        self._event_function = None

    @property
    def mother_window(self):
        return self._mother_window

    @property
    def renderers(self):
        return self._renderers

    def _preset_window_default(self):
        # default setting
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)

    def _enable_event(self):
        # glfw.set_input_mode(self.glfw_window, GLFW.GLFW_STICKY_KEYS, GL_TRUE)
        glfw.set_key_callback(self.glfw_window, self._callback_keyboard)
        pass

    def event(self,func):
        self._event_function = self._snatch_decorated(func)

    def _callback_keyboard(self,instance, key,scancode,action,mods):
        # print()
        # print(self,instance,key,scancode,action,mods)
        if action is 1:
            self.keys_pressed.append(key)
        if action is 0:
            self.keys_pressed.remove(key)

        if self._event_function is not None:
            # will use 'window' for referencing self
            window = self
            exec(self._event_function)

    def close_window(self):
        glfw.set_window_should_close(self.glfw_window,True)

    @property
    def keys_pressed(self):
        return self._keys_pressed

    def key_pressed(self, key):
        return key in self.keys_pressed

    @property
    def framerate(self):
        return self._framerate_target

    @framerate.setter
    def framerate(self, value):
        self._framerate_target = value

    def __getattr__(self, item):
        # print(item)
        if item in Renderer.get_instances():
            renderer = Renderer.get_instances()[item]
            name = renderer.name
            # print(f'self.{name} = renderer')
            self.__setattr__(name,renderer)
            return renderer
        else:
            print_message("can't find attribute")
            raise AttributeError



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



    def init(self, func):
        self.init_source = self._snatch_decorated(func)

    def draw(self, func):
        self.draw_source = self._snatch_decorated(func)


    def thread_run(self):
        # if glfw.get_current_context() is not self.glfw_window:
        glfw.make_context_current(self.glfw_window)
        # glfw.swap_interval(1)
        exec(self.init_source)

        timer = Timer(self.framerate, self.name)
        timer.set_init_position()
        timer.print_framerate()
        while True:
            timer.set_routine_start()
            # print(self)
            if self._terminate_flag:
                # will mulfunction if not detached before thread is over
                glfw.make_context_current(None)
                break
            # print(self.draw_source)
            for line in self.draw_source:
                exec(line)
            glfw.swap_buffers(self.glfw_window)
            # print(self, self.draw_source)

            self._framerendered_flag = True

            timer.set_routine_end()



    @classmethod
    def run_single_thread(cls):
        """
        runs all windows in single thread.
        works very fine.
        :return:
        """
        # TODO is it good to have this long initiation here?
        #initiation
        for window in cls._windows:
            glfw.make_context_current(window.glfw_window)

            # if window has mother window
            condition1 = window._mother_window is not None
            profile = glfw.get_window_attrib(window.glfw_window,GLFW.GLFW_OPENGL_PROFILE)
            condition2 = profile == GLFW.GLFW_OPENGL_CORE_PROFILE

            if condition1 and condition2:
                renderers = window.mother_window.renderers
                for _renderer in renderers:
                    _renderer.rebind()
                pass
            # first execute and save names, values in current namespace
            exec(window.init_source)

            # translate into scope
            lines = window.init_source.splitlines()
            att_names = []

            for i,line in enumerate(lines):
                #scratch Renderer objects
                if 'Renderer(' in line:
                    att_name = line.split('=')[0].strip()
                    exec(f'window.renderers.append({att_name})')
                #scratch attributes
                if '=' in line:
                    name_value = [i.strip() for i in line.split('=')]
                    att_names.append(name_value[0])
                    # exec(f'window._hollow_window.{name_value[0]} = {name_value[1]}')
                    lines[i] = f'window._context_scope.{name_value[0]} = {name_value[1]}'

            #execute again to save attributes to scope
            merged = ''
            for line in lines:
                merged += line + '\n'
            exec(merged)

            #erase all attribute names from exec() namespace
            attributes = list(window._context_scope.__dict__.keys())
            for name in attributes:
                exec(f'del {name}')

            #reformat draw_source so it could only reference given scope
            lines = window.draw_source.splitlines()
            merged = ''
            attributes = dict(zip(attributes,('window._context_scope',)*len(attributes)))

            #incase context is shared make it excessible
            if window.mother_window is not None:
                mother_attributes = list(window.mother_window._context_scope.__dict__.keys())
                mother_attributes = dict(zip(mother_attributes, ('window.mother_window._context_scope',)*len(mother_attributes)))
                #override
                mother_attributes.update(attributes)
                attributes = mother_attributes

            for line in lines:
                for name in attributes:
                    if name in line:
                        #check if word represents attribute
                        #TODO still translation is not perfect
                        #   for example in case name of attribute is
                        #   inside a string 'ddd (attribute name) ddd'
                        #   translation below wouldn't catch it.
                        #   So fix it
                        position = line.index(name)
                        left_condition = True
                        right_condition = True
                        if position is not 0:
                            left = line[position - 1]
                            if left.isalpha() or left.isnumeric():
                                left_condition = True
                        if position + len(name) is not len(line):
                            right = line[position + len(name)]
                            if right.isalpha() or right.isnumeric():
                                right_condition = False
                        #if a word is a name of attribute
                        if left_condition and right_condition:
                            line = line.replace(name,f'{attributes[name]}.{name}')
                merged += line + '\n'
            window.draw_source = merged


        timer = Timer(cls._framerate_target,'single thread')
        timer.set_init_position()
        # timer.print_framerate()
        # timer.print_framerate_drawing()
        while True:
            timer.set_routine_start()
            if cls._display_window():

                windows = cls._windows
                for window in cls._windows:
                    #drawing

                    if glfw.get_current_context() is not window.glfw_window:
                        glfw.make_context_current(window.glfw_window)
                    # print(glfw.get_window_attrib(window.glfw_window,GLFW.GLFW_DECORATED))
                    lines = window.draw_source.splitlines()

                    exec(window.draw_source)
                    glfw.swap_buffers(window.glfw_window)

                glfw.poll_events()

            else:
                break
            timer.set_routine_end()
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
                if multi_thread:
                    window._terminate_flag = True
                    window.thread.join()
                else:
                    pass
                if window.option_close is 0:
                    glfw.make_context_current(None)
                    glfw.destroy_window(window.glfw_window)
                    # print_message(f'{window} destryed')
                    cls._windows.remove(window)

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
        self._framecount += 1
        # measure sleep
        if self._framecount % self._frametarget is 0:
            per_second_rendering_time = time() - self._saved_time_second
            self._current_framerate = self._frametarget / per_second_rendering_time
            self._saved_time_second = time()
            if self._print_framerate:
                print()
                print(f'{self._name}: framerate: {round(self._current_framerate)}')

        target = 1/self._frametarget
        rendering_time = glfw.get_time()

        if self._print_framerate_drawing:
            if self._framecount % self._frametarget is 0:
                try:
                    fps = 1/rendering_time
                except:
                    fps = 0
                print(f'drawing_framerate: {fps}')
            self._glfwtime = glfw.get_time()

        #sleep
        waiting_time = target - rendering_time - self._frame_compensation
        if waiting_time >= 0:
            sleep(waiting_time)
        else:
            pass
    @property
    def current_framerate(self):
        return self._current_framerate

