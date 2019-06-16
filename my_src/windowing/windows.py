from collections import OrderedDict
import weakref
from .my_openGL.glfw_gl_tracker import GLFW_GL_tracker
from .frame_buffer_like.frame_buffer_like_bp import FBL
import glfw
class Windows:
    """
    Collector of Window objects.
    Stores real objects and return proxy of object.
    ^is this necessary?
    """
    windows = OrderedDict()
    # windows_z = dict()
    iter_count = 0
    _current_window = None

    def __init__(self):
        self.windows = self.__class__.windows # just a redirector
        self.iter_count = self.__class__.iter_count # just a redirector

    def __get__(self, instance, owner):
        return Windows()

    def __getattr__(self, item):
        if item is 'remove':
            return self.__delattr__
        return self.windows[item]

    # removes from dict
    def __delattr__(self, item):
        self.windows.pop(item.name)

    def __sub__(self, dwindow):

        # clean relationship
        for w in self.windows.values():
            if dwindow == w._mother_window:
                w._mother_window = None
            if dwindow in w._children_windows:
                w._children_windows.remove(dwindow)


        # remove if global
        if self.get_current() == dwindow:
            self.set_current(None)
        if FBL.get_current() == dwindow.myframe:
            FBL.set_current(None)

        # destroy sub components that has dwindow reference
        dwindow._mouse.delete()
        dwindow._keyboard.delete()

        dwindow._viewports.delete()
        # del dwindow._mouse

        del self.windows[dwindow.name]


    # append to dict
    def __add__(self, other):
        # check name unique
        if other.name in self.windows.keys():
            count = 1
            keys = self.windows.keys()
            while True:
                key = other.name+str(count)
                if key in keys:
                    count += 1
                else:
                    break
        else:
            key = other.name

        other._name = key
        self.windows[key] = other
        # self._current_window = other
        # self.set_window_z_position(other, 0)

    # iteration, return window object
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

    @classmethod
    def set_current(cls, window):
        try:
            cls._current_window = weakref.proxy(window)
        except:
            cls._current_window = window
    @classmethod
    def get_current(cls):
        return cls._current_window

    @classmethod
    def has_window_named(cls, name):
        if name in cls.windows:
            return True
        else:
            return False

    # @classmethod
    # def set_window_z_position(cls, window, z):
    #     for l in cls.windows_z.values():
    #         if window in l:
    #             l.remove(window)
    #             break
    #
    #     z = int(z)
    #     if z not in cls.windows_z:
    #         cls.windows_z[z] = []
    #
    #     cls.windows_z[z].append(window)
    #
    # @classmethod
    # def get_window_z_position(cls):
    #     return cls.windows_z