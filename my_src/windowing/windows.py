from collections import OrderedDict
import weakref

class Windows:
    """
    Collector of Window objects.
    Stores real objects and return proxy of object.
    ^is this necessary?
    """
    windows = OrderedDict()
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
        self.windows.pop(item.instance_name)
    def __sub__(self, other):
        del self.windows[other.instance_name]

    # append to dict
    def __add__(self, other):
        self.windows[other.instance_name] = other

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
        cls._current_window = window
    @classmethod
    def get_current(cls):
        return cls._current_window