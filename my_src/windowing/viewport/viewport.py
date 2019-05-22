from patterns.update_check_descriptor import UCD
import OpenGL.GL as gl
from .Camera import _Camera
from collections import namedtuple
from ..frame_buffer_like import FBL

class Viewport:
    _current = None
    DEF_CLEAR_COLOR = 0, 0, 0, 0

    posx = UCD()
    posy = UCD()
    width = UCD()
    height = UCD()

    def __init__(self, x, y, width, height, fbl=None, name= None):

        self._bound_fbl = fbl
        self._name = name

        self.posx = x
        self.posy = y
        self.width = width
        self.height = height

        self._camera = _Camera(self)

        gl.glClearColor(*self.DEF_CLEAR_COLOR)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self._flag_clear = None
        self._clear_color = None

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

    def open(self, do_clip = True):
        if self._bound_fbl is not None:
            FBL.set_current_fbl(self._bound_fbl)
        self.set_current_viewport(self)

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

    @property
    def abs_posx(self):
        if isinstance(self.posx, float):
            if self._bound_fbl is None:
                return int(self.posx * FBL.get_current_fbl().width)
            else:
                return int(self.posx * self._bound_fbl.width)
        else:
            return self.posx

    @property
    def abs_posy(self):
        if isinstance(self.posy, float):
            if self._bound_fbl is None:
                return int(self.posy * FBL.get_current_fbl().height)
            else:
                return int(self.posy * self._bound_fbl.height)
        else:
            return self.posy

    @property
    def abs_width(self):
        if isinstance(self.width, float):
            if self._bound_fbl is None:
                return int(self.width * FBL.get_current_fbl().width)
            else:
                return int(self.width * self._bound_fbl.width)
        else:
            return self.width

    @property
    def abs_height(self):
        if isinstance(self.height, float):

            if self._bound_fbl is None:
                return int(self.height * FBL.get_current_fbl().height)
            else:
                return int(self.height * self._bound_fbl.height)
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

    @classmethod
    def get_current_viewport(cls):
        return cls._current

    @classmethod
    def set_current_viewport(cls, vp):
        cls._current = vp