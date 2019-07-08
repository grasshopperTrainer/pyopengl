from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
from .Camera import _Camera
from collections import namedtuple
from ..frame_buffer_like.frame_buffer_like_bp import FBL
from ..windows import Windows
from ..matryoshka_coordinate_system import Matryoshka_coordinate_system
import weakref

class Viewport(Matryoshka_coordinate_system):

    _current = None
    DEF_CLEAR_COLOR = 0, 0, 0, 1
    def __init__(self, x, y, width, height, window=None, name= None):
        super().__init__(x,y,width,height)
        self.is_child_of(window)

        # self._window = window
        self._name = name

        self._camera = _Camera(self)
        with window.glfw_context as gl:
            gl.glClearColor(*self.DEF_CLEAR_COLOR)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        self._flag_clear = None
        self._clear_color = self.DEF_CLEAR_COLOR

        self.set_current(self)

        self._iter_count = 0

    def __enter__(self):
        self.set_current(self)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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

    @property
    def clear_color(self):
        if self._clear_color is None:
            return self.DEF_CLEAR_COLOR
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

    # def open(self, do_clip = True):
    #
    #     with self.mother.glfw_context as gl:
    #         with self.mother.myframe:
    #             gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
    #             if self.get_current() != self or self.mother.is_resized:
    #                 # print(self.pixel_x,self.pixel_y,self.pixel_w,self.pixel_h)
    #                 # print(self.x_changed, self.ref_pixel_w_changed, self._ref_pixel_w, self._ref_pixel_w())
    #                 # print(self.mother)
    #                 gl.glViewport(self.pixel_x, self.pixel_y, self.pixel_w, self.pixel_h)
    #                 if do_clip:
    #                     gl.glScissor(self.pixel_x, self.pixel_y, self.pixel_w, self.pixel_h)
    #
    #                 self.set_current(self)
    #                 self.mother.viewports.set_latest(self)
    #
    #     return self

    # def close(self):
    #     if self._flag_clear:
    #         self.fillbackground()

    @property
    def absolute_gl_values(self):
        n = namedtuple('pixel_coordinates',['posx','posy','width','height'])
        return n(self.pixel_x, self.pixel_y, self.pixel_w, self.pixel_h)


    def get_glfw_vertex(self, *index):
        """
        Returns coordinate relative to window coordinate.
        Index goes anti-clockwise begining from top left.

        0-------1
        ｜     ｜
        ｜     ｜
        3-------2

        :param vertex: index of a vertex 0,1,2,3
        :return: tuple(x,y)
        """
        x = self.pixel_x
        # flippin y axis
        y = self.mother.h - (self.pixel_y + self.pixel_h)
        w = self.pixel_w
        h = self.pixel_h

        result = []
        for i in index:
            if i == 0:
                result.append((x,y))
            elif i == 1:
                result.append((x+w, y))
            elif i == 2:
                result.append((x+w, y+h))
            elif i == 3:
                result.append((x, y+h))
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
        return [self.pixel_w, self.pixel_h]

    @classmethod
    def get_current(cls):
        return cls._current

    @classmethod
    def set_current(cls, vp):
        cls._current = vp

    def delete(self):
        self._window = None
