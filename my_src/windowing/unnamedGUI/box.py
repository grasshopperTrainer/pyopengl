from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
from ..callback_repository import Callback_repository
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
import weakref
from collections import namedtuple



class Box:
    def __init__(self, posx, posy, width, height, window=None, viewport=None):

        self._posx = posx
        self._posy = posy
        self._width = width
        self._height = height

        self._abs_posx = None
        self._abs_posy = None
        self._abs_width = None
        self._abs_height = None

        self._reference = None

        if window != None:
            self._window = weakref.ref(window)
            self._reference = window
        else:
            self._window = None #type:Window

        if viewport != None:
            self._viewport = weakref.ref(viewport)
            self._reference = viewport
        else:
            self._viewport = None

        self._children = []
        self._flag_draw = True

    def draw(self):
        pass

    @property
    def size(self):
        i = namedtuple('original_size', ['posx','posy','width','height'])
        return i(self._posx, self._posy, self._width, self._height)
    @property
    def pixel_size(self):
        i = namedtuple('pixel_size', ['posx','posy','width','height'])
        return i(self.pixel_posx, self.pixel_posy,self.pixel_width, self.pixel_height)

    def vertex(self, *index):
        vertex_list = []

        if len(index) == 0:
            index = 0,1,2,3

        width = self.pixel_width
        height = self.pixel_height

        if 0 in index:
            vertex_list.append((self.pixel_posx, self.pixel_posy))
        if 1 in index:
            vertex_list.append((self.pixel_posx + width, self.pixel_posy))
        if 2 in index:
            vertex_list.append((self.pixel_posx + width, self.pixel_posy + height))
        if 3 in index:
            vertex_list.append((self.pixel_posx, self.pixel_posy + height))

        if len(index) == 1:
            return vertex_list[0]
        return vertex_list

    @property
    def pixel_posx(self):
        result = None
        if isinstance(self._posx, float):
            result =  self._posx*self._reference.pixel_width
        elif callable(self._posx):
            result = self._posx(self._reference.pixel_width)
        else:
            result = self._posx

        if isinstance(self._reference, Box):
            return result + self._reference.pixel_posx

        return result

    @property
    def pixel_posy(self):
        result = None
        if isinstance(self._posy, float):
            result = self._posy*self._reference.pixel_height
        elif callable(self._posy):
            result = self._posy(self._reference.pixel_height)
        else:
            result = self._posy
        if isinstance(self._reference, Box):
            return result + self._reference.pixel_posy
        return result

    @property
    def pixel_width(self):
        if isinstance(self._width, float):
            return self._width*self._reference.pixel_width
        elif callable(self._width):
            return self._width(self._reference.pixel_width)
        else:
            return self._width


    @property
    def pixel_height(self):
        if isinstance(self._height, float):
            return self._height*self._reference.pixel_height
        elif callable(self._height):
            return self._height(self._reference.pixel_height)
        else:
            return self._height


    @property
    def window(self):
        if self._window == None:
            return None
        else:
            if self._window() == None:
                return None
            else:
                return self._window()

    @property
    def viewport(self):
        if self._viewport == None:
            return None
        else:
            if self._viewport() == None:
                return None
            else:
                return self._viewport()

    def set_window(self, window):
        self._window = weakref.ref(window)
        pass

    def set_viewport(self, viewport):
        self._viewport = weakref.ref(viewport)

    def set_reference(self, ref):
        self._reference = ref

        if ref.window != None:
            self.set_window(ref.window)
        if ref.viewport != None:
            self.set_viewport(ref.viewport)

        ref._children.append(self)

    def set_children(self, *ref):
        for box in ref:
            if self._window != None:
                box.set_window(self.window)
            if self._viewport != None:
                box.set_viewport(self.viewport)

            self._children.append(box)
            box._reference = self

    def copy(self):
        """
        copy for new position and size
        :return:
        """
        pass

    def disable_draw(self):
        self._flag_draw = False
        for box in self._children:
            box.disable_draw()
    def enable_draw(self):
        self._flag_draw = True
        for box in self._children:
            box.enable_draw()
    def switch_draw_state(self):
        self._flag_draw = not self._flag_draw


class Filled_box(Box):
    """
            one renderer should have one shader.
            but this can be called from several plces...
            when initiating ... like first_rect = TestBRO()
            how to make calling free???
            """
    c = Renderer_builder()
    c.use_shader(c.Shader('basic_gui_box'))
    c.use_triangle_strip_draw()
    c.use_index_buffer(c.Indexbuffer((0, 1, 3, 3, 1, 2)))

    c.use_render_unit(vao=True, vbo=True)

    renderer = c()

    def __init__(self,posx, posy, width, height, window=None, viewport=None):
        super().__init__(posx, posy, width, height, window, viewport)

        self._unit = self.renderer.new_render_unit()
        self._unit.shader_attribute.resize(4)

        self._fill_color = 1,1,1,1

    @property
    def fill_color(self):
        return self._fill_color
    @fill_color.setter
    def fill_color(self, color):
        self._fill_color = color
    @property
    def unit(self):
        return self._unit

    def set_fill_color(self, *rgba):
        self._fill_color = rgba

    def draw(self):
        if self._flag_draw:
            if self.viewport != None:
                self.viewport.open()
            self._unit.shader_attribute.a_position = self.vertex()
            self._unit.shader_attribute.u_fillcol = self._fill_color

            self.renderer._draw_(self._unit)

class Block(Filled_box):
    def __init__(self, posx, posy, width, height, window=None, viewport=None):
        super().__init__(posx,posy,width,height, window, viewport)

        callbacks = ['state_change']
        self._callback_repo = Callback_repository(window, callbacks)

    # def append_horizontal(self, *boxes, row = 0):
    #     """
    #     :param boxes:
    #     :param absolute_pos:
    #     :return:
    #     """
    #     if len(self._children) < row + 1:
    #         for i in range(row + 1 - len(self._children)):
    #             self._children.append([])
    #
    #     row = self._children[row]
    #     print(self._children,row)
    #     for box in boxes:
    #         if isinstance(box, Box):
    #             if self._window != None:
    #                 box.set_window(self.window)
    #             if self._viewport != None:
    #                 box.set_viewport(self.viewport)
    #             box.set_reference(self)
    #
    #             # row.append(box)
    #         else:
    #             raise
    #     print(row)
    #     print(self._children)
    #     exit()

    def draw(self):
        super().draw()
        print('drawing block')
        print(self._children)
        print(id(self._children))
        for child in self._children:
            child.draw()
        # else:
        #     for child in self._children:
        #         print('child draw', child)
        #         child.draw()

    def set_vertical(self, *boxes):
        pass

    def set_state_change(self):
        pass

    def align_horrizontal(self, *objects, bottom_top=0):

        if len(objects) == 0:
            objects = self._children
        # print(objects)
        # exit()
        # reference vertice for alignment
        if bottom_top == 0:
            ref_pos = [a-b for a,b in zip(objects[0].vertex(1), self.vertex(0))]
        else:
            ref_pos = [a-b for a,b in zip(objects[0].vertex(2), self.vertex(0))]

        for child in objects[1:]:
            if bottom_top == 0:
                child._posx, child._posy = ref_pos
                ref_pos = [a-b for a,b in zip(child.vertex(1), self.vertex(0))]
            else:
                dist = [a-b for a,b in zip(ref_pos, child.vertex(3))]
                child._posx, child._posy = [int(a+b) for a,b in zip(dist, child.vertex(0))]
                ref_pos = [a-b for a,b in zip(child.vertex(2), self.vertex(0))]

    def align_vertical(self, *objects_to_align, left_right = 0, offset = (0,0)):
        print('aligning vertical')
        print(self.vertex())
        print(self.pixel_posx, self.pixel_posy, self.pixel_width,self.pixel_height)
        print()
        ref_pos = [a+b for a,b in zip(self.vertex(0), offset)]
        for object in objects_to_align:
            object.set_reference(self)
            # print(object._posx, object._posy)
            # print(object.vertex())
            # object._posx, object._posy = ref_pos
            # print(object._posx, object._posy)
            # print(object.vertex())
            # if left_right == 0:
            #     ref_pos = object.pixel_width, object.pixel_height
            #
            # elif left_right == 1:
            #     # ref_pos = object.vertex(2)
            #     pass

class Block_expandable(Block):

    pass


