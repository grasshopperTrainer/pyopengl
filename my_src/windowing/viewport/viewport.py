from patterns.update_check_descriptor import UCD
from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from .Camera import _Camera
from collections import namedtuple
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..windows import Windows

class Viewport:
    _current = None
    DEF_CLEAR_COLOR = 0, 0, 0, 0

    posx = UCD()
    posy = UCD()
    width = UCD()
    height = UCD()

    abs_posx = UCD()
    abs_posy = UCD()
    abs_width = UCD()
    abs_height = UCD()

    def __init__(self, x, y, width, height, fbl=None, name= None):

        self._bound_fbl = fbl
        self._name = name

        self.posx = x
        self.posy = y
        self.width = width
        self.height = height

        self.abs_posx.set_pre_get_callback(self.cal_abs_posx)
        self.abs_posy.set_pre_get_callback(self.cal_abs_posy)
        self.abs_width.set_pre_get_callback(self.cal_abs_width)
        self.abs_height.set_pre_get_callback(self.cal_abs_height)

        self.abs_posx = self.cal_abs_posx()
        self.abs_posy = self.cal_abs_posy()
        self.abs_width = self.cal_abs_width()
        self.abs_height = self.cal_abs_height()

        self._camera = _Camera(self)

        gl.glClearColor(*self.DEF_CLEAR_COLOR)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self._flag_clear = None
        self._clear_color = None

        self.set_current(self)

        self._iter_count = 0

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
            gl.glClear(gl.GL_STENCIL_BUFFER_BIT)

            # clear just once
            # only allowed again if self.clear() is called again
            self._flag_clear = False

    def open(self, do_clip = True):
        # if self._bound_fbl is not None:
        #     FBL.set_current(self._bound_fbl)
        self.set_current(self)

        with Windows.get_current():
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

            gl.glViewport(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)
            if do_clip:
                gl.glScissor(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)

        return self

    @property
    def absolute_values(self):
        n = namedtuple('pixel_coordinates',['posx','posy','width','height'])
        return n(self.abs_posx,self.abs_posy,self.abs_width,self.abs_height)

    def close(self):
        if self._flag_clear:
            self.fillbackground()

    def cal_abs_posx(self):
        h = Windows.get_current().width if self._bound_fbl is None else self._bound_fbl.width
        if isinstance(self.posx, float):
            self.abs_posx = int(self.posx * h)
        elif callable(self.posx):
            self.abs_posx = int(self.posx(h))
        else:
            self.abs_posx = self.posx


    def cal_abs_posy(self):
        h = Windows.get_current().height if self._bound_fbl is None else self._bound_fbl.height
        if isinstance(self.posy, float):
            self.abs_posy = int(self.posy * h)
        elif callable(self.posy):
            self.abs_posy = int(self.posy(h))
        else:
            self.abs_posy = self.posy


    def cal_abs_width(self):
        h = Windows.get_current().width if self._bound_fbl is None else self._bound_fbl.width
        if isinstance(self.width, float):
            self.abs_width = int(self.width * h)
        elif callable(self.width):
            self.abs_width = int(self.width(h))
        else:
            self.abs_width = self.width


    def cal_abs_height(self):
        h = Windows.get_current().height if self._bound_fbl is None else self._bound_fbl.height
        if isinstance(self.height, float):
            self.abs_height = int(self.height * h)

        elif callable(self.height):
            self.abs_height = int(self.height(h))

        else:
            self.abs_height = self.height

    def get_vertex_from_window(self, index):
        """
        Returns coordinate relative to window coordinate.
        Index goes anti-clockwise begining from top left.

        0-------3
        ｜     ｜
        ｜     ｜
        1-------2

        :param vertex: index of a vertex 0,1,2,3
        :return: tuple(x,y)
        """
        if index == 0:
            return self.abs_posx, self.abs_posy
        elif index == 1:
            return self.abs_posx, self.abs_posy + self.abs_height
        elif index == 2:
            return self.abs_posx+self.abs_width, self.abs_posy + self.abs_height
        elif index == 3:
            return self.abs_posx+self.abs_width, self.abs_posy
        else:
            raise

    def get_vertex_from_screen(self, index):
        raise
        pass

    def set_min(self):
        pass

    def set_max(self):
        pass

    @property
    def camera(self):
        return self._camera

    @property
    def name(self):
        return self._name

    @property
    def abs_size(self):
        return [self.abs_width, self.abs_height]

    @classmethod
    def get_current(cls):
        return cls._current
    @classmethod
    def set_current(cls, vp):
        cls._current = vp


