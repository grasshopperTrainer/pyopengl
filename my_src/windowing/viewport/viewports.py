from numbers import Number
from .viewport import Viewport

class Viewports:
    _latest_viewport = None

    def __init__(self, window):
        self._window = window
        self._viewports = {}

        # make new default viewport
        # which is whole window 2D space between 0 to width&height

        default = self.new(0, 0, 1.0, 1.0, 'default')

        default.camera.mode = 2
        default.camera.move(0, 0, 1)
        # have it as base
        # self._viewports['default'].open()
        self.__class__._latest_viewport = default
        Viewport.set_current(default)

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) or callable(i) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        new_vp = Viewport(x, y, width, height, self._window, name)
        self._viewports[name] = new_vp
        # gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)
        return new_vp

    def make_viewport_current(self, viewport):
        self.__class__._current_viewport = viewport

    def close(self):
        if self._latest_viewport is None:
            raise

        latest = self.__class__._latest_viewport
        if latest._flag_clear:
            latest.clear_instant()

        self.__class__._latest_viewport = self._viewports['default']
        self.__class__._latest_viewport.open()


    def delete(self):
        for vp in self._viewports.values():
            vp.delete()
        # del self._viewports
        # self._viewports = None
        self._window = None

    def __del__(self):
        print(f'gc, Viewports {self}')

    def __getitem__(self, item) -> Viewport:
        if isinstance(item, str):
            return self._viewports[item]
        elif isinstance(item, int):
            return list(self._viewports.items())[item][1]

    def set_latest(self, vp):
        self.__class__._latest_viewport = vp

    def get_latest(self):
        return self.__class__._latest_viewport