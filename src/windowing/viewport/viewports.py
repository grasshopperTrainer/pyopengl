from numbers import Number
import OpenGL.GL as gl
import numpy as np
import weakref
from .Camera import _Camera

from .update_check_descriptor import UCD

class _Viewport:
    DEF_CLEAR_COLOR = 0, 0, 0, 0

    posx = UCD()
    posy = UCD()
    width = UCD()
    height = UCD()
    VPM = UCD()

    def __init__(self, mother, name, x, y, width, height):
        self._mother = mother
        self._name = name

        self.posx = x
        self.posy = y
        self.width = width
        self.height = height
        self.VPM.function_when_get(self.build_VPM)
        self.VPM = np.eye(4)

        self._camera = _Camera(self)

        gl.glClearColor(*self.DEF_CLEAR_COLOR)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self._flag_clear = None
        self._clear_color = None

    def build_VPM(self):
        if self._mother.window.is_buffer_swap_required():
            window_size = self._mother.window.size

            move = np.array(
                [[1, 0, 0, -window_size[0] / 2],
                 [0, 1, 0, -window_size[1] / 2],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]]
            )
            scale = np.array(
                [[2 / window_size[0], 0, 0, 0],
                 [0, 2 / window_size[1], 0, 0],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]]
            )
            points = np.array(
                [[self.abs_posx, self.abs_posx + self.abs_width],
                 [self.abs_posy, self.abs_posy + self.abs_height],
                 [0, 0],
                 [1, 1]]
            )
            trans = scale.dot(move)
            normalized_vp = trans.dot(points)
            l = normalized_vp[0][0]
            r = normalized_vp[0][1]
            b = normalized_vp[1][0]
            t = normalized_vp[1][1]
            move = np.array(
                [[1, 0, 0, (r + l) / 2],
                 [0, 1, 0, (t + b) / 2],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]]
            )
            scale = np.array(
                [[(r - l) / 2, 0, 0, 0],
                 [0, (t - b) / 2, 0, 0],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]]
            )
            trans = scale.dot(move)
            # print(points)
            # print(trans)

            self.VPM = trans

    def clear(self, *color):
        # if clear is called, save clear color
        if len(color) == 4:
            self._clear_color = color
        # not going to clear right now because it may be meaningless
        # if nothing is drawn on viewport
        self._flag_clear = True

    def fillbackground(self):
        # clear window by being called from (class)RenderUnit.draw_element()
        if self._flag_clear:
            if self._clear_color is None:
                color = self.DEF_CLEAR_COLOR
            else:
                color = self._clear_color

            gl.glClearColor(*color)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

            # clear just once
            # only allowed again if self.clear() is called again
            self._flag_clear = False

    def open(self):
        self._mother.make_viewport_current(self)
        # gl.glViewport(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)
        gl.glScissor(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)

    @property
    def abs_posx(self):
        if isinstance(self.posx, float):
            return int(self.posx * self._mother.window.width)
        else:
            return self.posx

    @property
    def abs_posy(self):
        if isinstance(self.posy, float):
            return int(self.posy * self._mother.window.height)
        else:
            return self.posy

    @property
    def abs_width(self):
        if isinstance(self.width, float):
            return int(self.width * self._mother.window.width)
        else:
            return self.width

    @property
    def abs_height(self):
        if isinstance(self.height, float):

            return int(self.height * self._mother.window.height)
        else:
            return self.height

    @property
    def camera(self):
        return self._camera

    @property
    def name(self):
        return self._name

    @property
    def abs_size(self):
        return [self.abs_width, self.abs_height]


class Viewports:
    _current_viewport = None

    def __init__(self, window):
        self._window = window
        self._viewports = {}

        # make new default viewport
        # which is whole window 2D space between 0 to width&height

        self.new(0, 0, 1.0, 1.0, 'default')
        self._viewports['default'].camera.mode = 2
        self._viewports['default'].camera.move(1, 0, 0, 1)

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        new_vp = _Viewport(self, name, x, y, width, height)
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
        return self._window

    @property
    def current_viewport(self):
        if self.__class__._current_viewport is None:
            return self._viewports['default']

        return self.__class__._current_viewport