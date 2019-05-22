from numbers import Number
from .viewport import Viewport

class Viewports:
    _current_viewport = None

    def __init__(self, fbl):
        self._fbl = fbl
        self._viewports = {}

        # make new default viewport
        # which is whole window 2D space between 0 to width&height

        self.new(0, 0, 1.0, 1.0, 'default')
        self._viewports['default'].camera.mode = 2
        self._viewports['default'].camera.move(1, 0, 0, 1)

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        new_vp = Viewport(x, y, width, height, self._fbl, name)
        self._viewports[name] = new_vp
        # gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)

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
            return list(self._viewports.items())[item][1]

    @property
    def window(self):
        return self._fbl

    @property
    def current_viewport(self):
        if self.__class__._current_viewport is None:
            return self._viewports['default']

        return self.__class__._current_viewport

