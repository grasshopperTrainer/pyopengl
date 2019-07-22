from .Camera import _Camera
from collections import namedtuple
from windowing.mcs import MCS
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
import weakref

class Viewport(MCS):

    DEF_CLEAR_COLOR = 0, 0, 0, 1
    def __init__(self, x, y, width, height, mother_cs, collection, name= None):
        self._previous_viewport = None
        super().__init__(x,y,width,height)
        # mother coordinate system
        self.is_child_of(mother_cs)

        # self._window = window
        self._name = name

        self._camera = _Camera(self)

        self._flag_clear = None
        self._clear_color = self.DEF_CLEAR_COLOR

        self._iter_count = 0
        self._collection = collection

    def __enter__(self):
        if self._collection.get_current != self:
            self._previous_viewport = self._collection.get_current()
        self._collection.set_current(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._previous_viewport != None:
            self._collection.set_current(self._previous_viewport)
            self._previous_viewport = None
        else:
        #     raise
        #     self._collection.set_current(self._collection[0])
            pass


    def clear(self,*color):
        # TODO need clear option, which color attachment, depth or stencil, id_color
        if len(color) == 4:
            self._clear_color = color
        Unique_glfw_context.get_current().render_unit_add(self, f"cleangin viewport '{self.name}'")

    def _draw_(self, context, frame, viewport, att, uni):
        context.glScissor(*self.pixel_values)
        context.glClearColor(*self.clear_color)
        context.glClear(context.GL_COLOR_BUFFER_BIT)
        context.glClear(context.GL_STENCIL_BUFFER_BIT)

        # automatically clear id color to 0?
        context.glDrawBuffer(context.GL_COLOR_ATTACHMENT1)
        context.glClearColor(0, 0, 0, 0)
        context.glClear(context.GL_COLOR_BUFFER_BIT)

        attachments = [context.GL_COLOR_ATTACHMENT0 + i for i in
                       range(len(frame._color_attachments))]
        context.glDrawBuffers(len(frame._color_attachments), attachments)


    @property
    def clear_color(self):
        if self._clear_color is None:
            return self.DEF_CLEAR_COLOR
        else:
            return self._clear_color

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

    def delete(self):
        self._window = None
