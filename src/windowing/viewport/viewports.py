from numbers import Number
import OpenGL.GL as gl


class Viewports:

    def __init__(self, window):
        self._window = window
        self._viewports = []

    def new(self, x, y, width, height):
        if not all([isinstance(i, Number) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        self._viewports.append([x, y, width, height])
        gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)

    def open(self, index):
        size = self._window.size
        info = self._viewports[index]
        if isinstance(info[0], float):
            x = int(info[0] * size[0])
        else:
            x = info[0]
        if isinstance(info[1], float):
            y = int(info[1] * size[1])
        else:
            y = info[1]
        if isinstance(info[2], float):
            w = int(info[2] * size[0])
        else:
            w = info[2]
        if isinstance(info[3], float):
            h = int(info[3] * size[1])
        else:
            h = info[3]

        gl.glViewport(x, y, w, h)

    def close(self):
        wsize = self._window.size
        gl.glViewport(0, 0, wsize[0], wsize[1])
        pass

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._viewports[item]

    def __call__(self, func):
        print(func)
        func()
# class _Viewport:
#
#     def __init__(self, x, y, width, height):
#         self._x = x
#         self._y = y
#         self._width = width
#         self._height = height
#
#         pass
#
#     def open(self):
#         # gl.glViewportIndexedfv(0)
#         pass
#     def start(self, index):
#         pass
#
#     def end(self, index):
#         pass
#
#     @property
#     def size(self):
#         return self._x,self._y,self._width,self._height
