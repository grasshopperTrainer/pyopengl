import glfw as glfw
import glfw.GLFW as GLFW

import inspect
import numpy as np
from collections import OrderedDict

from buffers import Buffer
from renderer import Renderer
from shader import Shader

class Switch:
    def __init__(self):
        self.draw_window = True
        self.display_window = True

class Window:
    _windows = []
    @classmethod
    def glfw_init(cls):
        glfw.init()

    def __init__(self, width, height, name, monitor, share):
        # register window
        self.__class__._windows.append(self)
        self._buffers = []
        self._init_info = OrderedDict({
            'width': width,
            'height': height,
            'name': name,
            'monitor': monitor,
            'share': share
        })
        self._framerate = 30

        self._preset_window_default()
        self.glfw_window = glfw.create_window(width, height, name, monitor, share)
        # check if window is made
        if not self.glfw_window:
            glfw.terminate()
        self._set_framerate()
        self.switches = Switch()

    def _preset_window_default(self):
        # default setting
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)

    def _set_framerate(self):
        #TODO refine framerate operation
        glfw.make_context_current(self.glfw_window)
        glfw.swap_interval(int(60/self.framerate))

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        self._framerate = value

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
        del self.window
        i = self._init_info
        self.window = glfw.create_window(i['width'],i['height'],
                                         i['title'],i['monitor'],
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
        exec(self.init_source)
        while True:
            glfw.make_context_current(self.window)
            exec(self.draw_source)
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        pass

    @classmethod
    def run_all(cls):
        #initiation
        for window in cls._windows:
            glfw.make_context_current(window.glfw_window)
            exec(window.init_source)

        while cls._display_window():
            #for all windows
            to_remove = []
            for i, window in enumerate(cls._windows):

                if not glfw.window_should_close(window.glfw_window):
                    glfw.make_context_current(window.glfw_window)
                    exec(window.draw_source)
                    glfw.swap_buffers(window.glfw_window)

                    # check for window close
                    if glfw.window_should_close(window.glfw_window):
                        window.switches.display_window = False

                else:
                    glfw.destroy_window(window.glfw_window)
                    to_remove.append(i)

            # remove window
            for i in to_remove:
                del cls._windows[i]

            glfw.poll_events()

        # end cleaning
        # TODO fix ↓
        # Shader.deleteProgram()
        glfw.terminate()

    @classmethod
    def _display_window(cls):
        for window in cls._windows:
            if window.switches.display_window:
                return True
            else:
                continue
        return False

    @property
    def name(self):
        return self._init_info['name']

    def __str__(self):
        return f"window: '{self.name}'"