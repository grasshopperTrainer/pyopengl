import glfw as glfw
import glfw.GLFW as GLFW

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


class Switch:
    def __init__(self):
        self.draw_window = True
        self.display_window = True

class Window(threading.Thread):
    _windows = []

    @classmethod
    def glfw_init(cls):
        glfw.init()

    def __init__(self, width, height, name, monitor, share):
        threading.Thread.__init__(self)
        self._buffers = []
        self._init_info = OrderedDict({
            'width': width,
            'height': height,
            'name': name,
            'monitor': monitor,
            'share': share
        })

        self._preset_window_default()
        self._glfw_window = glfw.create_window(width, height, name, monitor, share)
        # glfw.make_context_current(self.glfw_window)
        # check if window is made
        if not self._glfw_window:
            glfw.terminate()
        self._set_framerate()
        self.switches = Switch()
        self._option_close = 0

        self.draw_source = 'pass'
        self.init_source = 'pass'

        self._framerate_target = 30
        self._framecount = 0
        self._framerendered_flag = False
        self._terminate_flag = False

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
        cls._windows.append(self)
        return weakref.proxy(self)

    def _preset_window_default(self):
        # default setting
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)

    def _set_framerate(self):
        # #TODO refine framerate operation
        # glfw.make_context_current(self._glfw_window)
        # glfw.swap_interval(int(60/self.framerate))
        pass

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

    def run(self):
        glfw.make_context_current(self.glfw_window)
        exec(self.init_source)

        saved_time = time()
        while True:
            if self._terminate_flag:
                break

            glfw.set_time(0)

            glfw.make_context_current(self.glfw_window)
            exec(self.draw_source)
            glfw.swap_buffers(self.glfw_window)

            self._framerendered_flag = True



            # control framerate
            # TODO this is single thread single framerate drawing
            #   integrate to multi thread multi framerate operation
            self._framecount += 1
            target = 1 / self._framerate_target
            correction = (time() - saved_time) - target
            saved_time = time()
            waiting_time = target - glfw.get_time() - correction
            if waiting_time > 0:
                sleep(waiting_time)
            else:
                pass


    @classmethod
    def run_all(cls):
        #initiation
        for window in cls._windows:
            glfw.make_context_current(window.glfw_window)
            exec(window.init_source)

        saved_time = time()
        while True:
            glfw.set_time(0)
            # seperated from 'while' to improve time measurement
            if cls._display_window():

                for i, window in enumerate(cls._windows):
                    #drawing

                    if glfw.get_current_context() is not window.glfw_window:
                        glfw.make_context_current(window.glfw_window)
                    # print(glfw.get_window_attrib(window.glfw_window,GLFW.GLFW_DECORATED))
                    exec(window.draw_source)
                    glfw.swap_buffers(window.glfw_window)

                glfw.poll_events()

                #control framerate
                # TODO this is single thread single framerate drawing
                #   integrate to multi thread multi framerate operation
                cls._framecount += 1
                target = 1/cls._framerate_target
                correction = (time()-saved_time) - target
                saved_time = time()
                waiting_time = target - glfw.get_time()-correction
                if waiting_time > 0:
                    sleep(waiting_time)
                else:
                    pass
            else:
                break

        # TODO fix ↓
        # Shader.deleteProgram()
        glfw.terminate()

    @classmethod
    def run_all2(cls):
        for window in cls._windows:
            window.start()

        detection_inevery = 60

        while True:
            if cls._display_window():
                if all([window._framerendered_flag for window in cls._windows]):
                    glfw.poll_events()
                    for window in cls._windows:
                        window._framerendered_flag = False
                sleep(1/detection_inevery)
            else:
                break
        if all([window.is_alive() for window in cls._windows]):
            # glfw.terminate()
            print(cls._windows)
            print_message('glfw terminated')




    @classmethod
    def print_framerate(cls, state: bool = True):
        cls._print_framerate = state


    @classmethod
    def _display_window(cls):
        """
        checks in every draw_all iteration whether a window
        sould be desplayed.
        If there is no window to display or all are invisible
        returns False thus drawing application terminates.
        :return: bool
        """
        for window in cls._windows:
            window._handle_close()
        for window in cls._windows:
            if glfw.get_window_attrib(window.glfw_window,GLFW.GLFW_VISIBLE):
                return True
            else:
                continue
        return False

    def _handle_close(self):
        """
        Manage close operation:
        Refer to option_close for further description
        :return: None
        """
        if glfw.window_should_close(self.glfw_window):
            if self.option_close is 0:
                glfw.destroy_window(self.glfw_window)
                i = self.__class__._windows.index(self)
                n = self.__class__._windows[i].name
                del self.__class__._windows[i]
                self._terminate_flag = True
                print_message(f"window <{n}> closed")

            elif self.option_close is 1:
                glfw.hide_window(self.glfw_window)

            elif self.option_close is 2:
                glfw.destroy_window(self.glfw_window)
        else:
            pass

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