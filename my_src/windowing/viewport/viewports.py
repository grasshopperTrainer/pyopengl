from numbers import Number
from .viewport import Viewport

class Viewports:
    _current_viewport = None

    def __init__(self, window):
        self._window = window
        self._viewports = {}

        # make new default viewport
        # which is whole window 2D space between 0 to width&height

        self.new(0, 0, 1.0, 1.0, 'default')
        self._viewports['default'].camera.mode = 2
        self._viewports['default'].camera.move(0, 0, 1)
        # have it as base
        self._viewports['default'].open()

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        new_vp = Viewport(x, y, width, height, self._window, name)
        self._viewports[name] = new_vp
        # gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)
        return new_vp

    def make_viewport_current(self, viewport):
        self.__class__._current_viewport = viewport

    def close(self):
        vp = self._viewports['default']
        self.make_viewport_current(vp)
        vp.open()

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._viewports[item]
        elif isinstance(item, int):
            return list(self._viewports.items())[item][1] #type:Viewport

    @property
    def current_viewport(self):
        if self.__class__._current_viewport is None:
            return self._viewports['default']

        return self.__class__._current_viewport

