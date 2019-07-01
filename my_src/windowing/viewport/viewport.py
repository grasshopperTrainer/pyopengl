from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
from .Camera import _Camera
from collections import namedtuple
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..windows import Windows
from ..matryoshka_coordinate_system import Record_change_value
import weakref

class Viewport:
    posx = Record_change_value()
    posy= Record_change_value()
    width = Record_change_value()
    height = Record_change_value()

    _pixel_width = Record_change_value()
    _pixel_height = Record_change_value()

    _current = None
    DEF_CLEAR_COLOR = 0, 0, 0, 0
    def __init__(self, x, y, width, height, window=None, name= None):

        self._flag_coordinate_updated = True
        self._children = weakref.WeakSet()
        self._vertex = [(),(),(),()]

        self._window = window
        self._name = name

        self.posx = x
        self.posy = y
        self.width = width
        self.height = height

        self._camera = _Camera(self)
        with window.glfw_context as gl:
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

    def clear_instant(self, *color):
        if len(color) == 0:
            if self._clear_color is None:
               color = self.DEF_CLEAR_COLOR
            else:
                color = self._clear_color
        # clear window frame's
        with self._window.glfw_context as gl:
            with FBL.get_current():
                gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self._window.myframe._frame_buffer._glindex)

                gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT1)
                gl.glClearColor(0,0,0,0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

                gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)
                gl.glClearColor(*color)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

                gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
                gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
        self._window.myframe._flag_something_rendered = True
        self._flag_clear = False

    @property
    def clear_color(self):
        if self._clear_color is None:
            return self.DEF_CLEAR_COLOR
        else:
            return self._clear_color

    def fillbackground(self):
        # clear window by being called from (class)RenderUnit.draw_element()
        if self._flag_clear:
            if self._clear_color is None:
                color = self.DEF_CLEAR_COLOR
            else:
                color = self._clear_color

            # with self._window as win:
            with Unique_glfw_context.get_current() as gl:
                gl.glClearColor(*color)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
                gl.glClear(gl.GL_STENCIL_BUFFER_BIT)

            # clear just once
            # only allowed again if self.clear() is called again
            self._flag_clear = False

    def open(self, do_clip = True):

        with self._window.glfw_context as gl:
            with self._window.myframe:
                gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
                if self.get_current() != self or self._window.is_resized:
                    gl.glViewport(self.pixel_posx, self.pixel_posy, self.pixel_width, self.pixel_height)
                    if do_clip:
                        gl.glScissor(self.pixel_posx, self.pixel_posy, self.pixel_width, self.pixel_height)

                    self.set_current(self)
                    self._window.viewports.set_latest(self)

        return self

    @property
    def absolute_gl_values(self):
        n = namedtuple('pixel_coordinates',['posx','posy','width','height'])
        return n(self.pixel_posx, self.pixel_posy, self.pixel_width, self.pixel_height)

    def close(self):
        if self._flag_clear:
            self.fillbackground()
    @property
    def pixel_posx(self):
        h = Windows.get_current().width if self._window is None else self._window.width
        if isinstance(self.posx, float):
            return int(self.posx * h)
        elif callable(self.posx):
            return int(self.posx(h))
        else:
            return self.posx

    @property
    def pixel_posy(self):
        """
        flipin from glfw to gl coordinate
        glfw:
        (0,0)----(w,0)
        |           |
        |           |
        |           |
        |           |
        (0,h)---(w,h)

        gl:
        (0,h)----(w,h)
        |           |
        |           |
        |           |
        |           |
        (0,0)---(w,0)

        :return:
        """
        h = Windows.get_current().height if self._window is None else self._window.height
        if isinstance(self.posy, float):
            return int((1-self.posy) * h - self.pixel_height)
        elif callable(self.posy):
            return int(h - self.posy(h) - self.pixel_height)
        else:
            return int(h - self.posy - self.pixel_height)

    @property
    def pixel_width(self):
        h = Windows.get_current().width if self._window is None else self._window.width
        if isinstance(self.width, float):
            self._pixel_width =  int(self.width * h)
        elif callable(self.width):
            self._pixel_width = int(self.width(h))
        else:
            self._pixel_width = self.width
        return self._pixel_width

    @property
    def pixel_height(self):
        h = Windows.get_current().height if self._window is None else self._window.height
        if isinstance(self.height, float):
            self._pixel_height = int(self.height * h)
        elif callable(self.height):
            self._pixel_height = int(self.height(h))
        else:
            self._pixel_height = self.height
        return self._pixel_height

    @property
    def glfw_posx(self):
        return self.pixel_posx

    @property
    def glfw_posy(self):
        h = Windows.get_current().height if self._window is None else self._window.height
        if isinstance(self.posy, float):
            return int(self.posy * h)
        elif callable(self.posy):
            return int(self.posy(h))
        else:
            return int(self.posy)

    @property
    def glfw_width(self):
        return self.pixel_width
    @property
    def glfw_height(self):
        return self.pixel_height

    def get_vertex_from_window(self, *index):
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

        result = []
        for i in index:
            if i == 0:
                result.append((self.glfw_posx, self.glfw_posy))
            elif i == 1:
                result.append((self.glfw_posx, self.glfw_posy + self.glfw_height))
            elif i == 2:
                result.append((self.glfw_posx + self.glfw_width, self.glfw_posy + self.glfw_height))
            elif i == 3:
                result.append((self.glfw_posx + self.glfw_width, self.glfw_posy))
            else:
                raise
        if len(result) == 1:
            return result[0]
        else:
            return result


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
        return [self.pixel_width, self.pixel_height]

    @classmethod
    def get_current(cls):
        return cls._current

    @classmethod
    def set_current(cls, vp):
        cls._current = vp

    def delete(self):
        self._window = None
