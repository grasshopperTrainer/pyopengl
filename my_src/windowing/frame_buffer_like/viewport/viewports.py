import weakref
from numbers import Number
from .viewport import Viewport

class Viewports:

    def __init__(self, window):
        self._window = window
        self._viewports = {}
        self._current = None
        # make new default viewport
        # which is whole window 2D space between 0 to width&height

        default = self.new(0, 0, 1.0, 1.0, 'default')
        default.camera.mode = 2
        default.camera.move(0, 0, 1)
        # have it as base
        # self._viewports['default'].open()
        self.set_current(default)

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) or callable(i) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        new_vp = Viewport(x, y, width, height, self._window, self, name)
        self._viewports[name] = new_vp
        # gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)
        return new_vp

    def delete(self):
        for vp in self._viewports.values():
            vp.delete()
        self._window = None
        self._current = None

    def __del__(self):
        print(f'gc, Viewports {self}')

    def __getitem__(self, item) -> Viewport:
        if isinstance(item, str):
            return self._viewports[item]
        elif isinstance(item, int):
            return list(self._viewports.items())[item][1]
    @property
    def default(self):
        return self[0]

    def set_current(self, viewport):
        self._current = weakref.ref(viewport)

    def get_current(self):
        return self._current()