from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from .Camera import _Camera
from collections import namedtuple
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..windows import Windows

class Viewport:
    _current = None
    DEF_CLEAR_COLOR = 0, 0, 0, 0
    def __init__(self, x, y, width, height, window=None, name= None):

        self._window = window
        self._name = name

        self._posx = x
        self._posy = y
        self._width = width
        self._height = height

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

    def clear_instant(self, *color):
        if len(color) == 0:
            if self._clear_color is None:
               color = self.DEF_CLEAR_COLOR
            else:
                color = self._clear_color
        # clear window frame's
        # with self._bound_fbl.myframe:
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

            gl.glClearColor(*color)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
            gl.glClear(gl.GL_STENCIL_BUFFER_BIT)

            # clear just once
            # only allowed again if self.clear() is called again
            self._flag_clear = False

    def open(self, do_clip = True):
        if Windows.get_current() != self._window:
            self._window.make_window_current()
        self.set_current(self)

        with self._window.myframe:
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

            gl.glViewport(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)
            if do_clip:
                gl.glScissor(self.abs_posx, self.abs_posy, self.abs_width, self.abs_height)

        return self

    @property
    def absolute_gl_values(self):
        n = namedtuple('pixel_coordinates',['posx','posy','width','height'])
        return n(self.abs_posx,self.abs_posy,self.abs_width,self.abs_height)

    def close(self):
        if self._flag_clear:
            self.fillbackground()
    @property
    def abs_posx(self):
        h = Windows.get_current().width if self._window is None else self._window.width
        if isinstance(self._posx, float):
            return int(self._posx * h)
        elif callable(self._posx):
            return int(self._posx(h))
        else:
            return self._posx

    @property
    def abs_posy(self):
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
        if isinstance(self._posy, float):
            return int((1-self._posy) * h - self.abs_height)
        elif callable(self._posy):
            return int(h-self._posy(h) - self.abs_height)
        else:
            return int(h-self._posy - self.abs_height)

    @property
    def abs_width(self):
        h = Windows.get_current().width if self._window is None else self._window.width
        if isinstance(self._width, float):
            return int(self._width * h)
        elif callable(self._width):
            return int(self._width(h))
        else:
            return self._width

    @property
    def abs_height(self):
        h = Windows.get_current().height if self._window is None else self._window.height
        if isinstance(self._height, float):
            return int(self._height * h)
        elif callable(self._height):
            return int(self._height(h))
        else:
            return self._height

    @property
    def abs_glfw_posx(self):
        return self.abs_posx

    @property
    def abs_glfw_posy(self):
        h = Windows.get_current().height if self._window is None else self._window.height
        if isinstance(self._posy, float):
            return int(self._posy * h)
        elif callable(self._posy):
            return int(self._posy(h))
        else:
            return int(self._posy)

    @property
    def abs_glfw_width(self):
        return self.abs_width
    @property
    def abs_glfw_height(self):
        return self.abs_height

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
                result.append((self.abs_glfw_posx, self.abs_glfw_posy))
            elif i == 1:
                result.append((self.abs_glfw_posx, self.abs_glfw_posy + self.abs_glfw_height))
            elif i == 2:
                result.append((self.abs_glfw_posx+self.abs_glfw_width, self.abs_glfw_posy + self.abs_glfw_height))
            elif i == 3:
                result.append((self.abs_glfw_posx+self.abs_glfw_width, self.abs_glfw_posy))
            else:
                raise
        if len(result) == 1:
            return result[0]
        else:
            return result

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

    def delete(self):
        self._window = None
