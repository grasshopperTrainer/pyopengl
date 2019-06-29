from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
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

        if 0 in index:
            vertex_list.append((self.pixel_posx, self.pixel_posy))
        if 1 in index:
            vertex_list.append((self.pixel_posx + self.pixel_width, self.pixel_posy))
        if 2 in index:
            vertex_list.append((self.pixel_posx + self.pixel_width, self.pixel_posy + self.pixel_height))
        if 3 in index:
            vertex_list.append((self.pixel_posx, self.pixel_posy + self.pixel_height))

        if len(index) == 1:
            return vertex_list[0]
        return vertex_list

    @property
    def pixel_posx(self):
        if isinstance(self._posx, float):
            return self._posx*self._reference.pixel_width
        elif callable(self._posx):
            return self._posx(self._reference.pixel_width)
        else:
            if isinstance(self._reference, Box):
                return self._posx + self._reference.pixel_posx
            return self._posx


    @property
    def pixel_posy(self):
        if isinstance(self._posy, float):
            return self._posy*self._reference.pixel_height
        elif callable(self._posy):
            return self._posy(self._reference.pixel_height)
        else:
            if isinstance(self._reference, Box):
                return self._posy + self._reference.pixel_posy
            return self._posy


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
        pass

    def set_viewport(self, viewport):
        self._viewport = weakref.ref(viewport)

    def set_reference(self, ref):
        self._reference = ref

    def copy(self):
        """
        copy for new position and size
        :return:
        """
        pass

class Filled_box(Box):
    """
            one renderer should have one shader.
            but this can be called from several plces...
            when initiating ... like first_rect = TestBRO()
            how to make calling free???
            """
    c = Renderer_builder()
    c.use_shader(c.Shader('BRO_rectangle'))
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
        if self.viewport != None:
            self.viewport.open()
        self._unit.shader_attribute.a_position = self.vertex()
        self._unit.shader_attribute.u_fillcol = self._fill_color

        self.renderer._draw_(self._unit)

class Block(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = []

    def append_horizontal(self, *boxes, row = 0):
        """

        :param boxes:
        :param absolute_pos:
        :return:
        """
        if len(self._children) < row + 1:
            for i in range(row + 1 - len(self._children)):
                self._children.append([])

        row = self._children[row]

        for box in boxes:
            if isinstance(box, Box):
                if self._window != None:
                    box.set_window(self.window)
                if self._viewport != None:
                    box.set_viewport(self.viewport)
                box.set_reference(self)

                row.append(box)
            else:
                raise

    def draw(self):
        print('from block', self._window)
        for row in self._children:
            for child in row:
                child.draw()

    def set_vertical(self, *boxes):
        pass

    def align_horrizontal(self, *objects_to_align, bottom_top=0, rows: (tuple, list) = None):
        if rows == None:
            rows_to_align = self._children
        else:
            rows_to_align = []
            for i in rows:
                rows_to_align.append(self._children[i])
        for row in rows_to_align:

            boxes = []
            if len(objects_to_align) != 0:
                for i in objects_to_align:
                    if i in row:
                        boxes.append(i)
            else:
                boxes = row

            # reference vertice for alignment
            if bottom_top == 0:
                ref_pos = [a-b for a,b in zip(boxes[0].vertex(1), self.vertex(0))]
            else:
                ref_pos = [a-b for a,b in zip(boxes[0].vertex(2), self.vertex(0))]

            for child in boxes[1:]:
                if bottom_top == 0:
                    child._posx, child._posy = ref_pos
                    ref_pos = [a-b for a,b in zip(child.vertex(1), self.vertex(0))]
                else:
                    dist = [a-b for a,b in zip(ref_pos, child.vertex(3))]
                    child._posx, child._posy = [int(a+b) for a,b in zip(dist, child.vertex(0))]
                    ref_pos = [a-b for a,b in zip(child.vertex(2), self.vertex(0))]


# class _Button(Filled_box):
#     """
#         one renderer should have one shader.
#         but this can be called from several plces...
#         when initiating ... like first_rect = TestBRO()
#         how to make calling free???
#         """
#     c = Renderer_builder()
#     c.use_shader(c.Shader('BRO_rectangle'))
#     c.use_triangle_strip_draw()
#     c.use_index_buffer(c.Indexbuffer((0, 1, 3, 3, 1, 2)))
#
#     c.use_render_unit(vao=True, vbo=True)
#
#     renderer = c()


class _Button(Filled_box):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)

        self._color1 = 1, 1, 1, 1
        self._color2 = 0, 0, 0, 1

        self._flag_use_button = True

        self.set_window(window)

    @property
    def color1(self):
        return self._color1

    @color1.setter
    def color1(self, *rgba):
        self._color1 = rgba

    @property
    def color2(self):
        return self._color2

    @color2.setter
    def color2(self, *rgba):
        self._color2 = rgba

    def switch_color(self):
        pass

    def set_window(self, window):
        if window != None:
            # remove callback of previous window
            if self.window != None:
                self.window.mouse.remove_callback(identifier=self)
            # assign new window
            self._window = weakref.ref(window)

            window.set_pre_draw_callback(
                func=self.switch_color,
                identifier=self,
                deleter=self
            )

# few pre_built buttons
class Button_click(_Button):

    def switch_color(self):
        if self.window != None and self.window.is_focused:
            if self.window.mouse.is_in_area(*self.vertex(0,2)):
                if self.window.mouse.is_just_pressed:
                    if self.fill_color == self._color1:
                        self.fill_color = self._color2
                    else:
                        self.fill_color = self._color1
                    self.draw()

class Button_hover(_Button):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)
        self._target_frame_count = 5
        self._accumulate_frame_count = 0

    def switch_color(self):
        if self.window != None and self.window.is_focused:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if self._accumulate_frame_count == self._target_frame_count:
                    if self.fill_color == self.color1:
                        self.fill_color = self.color2
                        self.draw()
                else:
                    self._accumulate_frame_count += 1

            elif self.fill_color == self.color2:
                self._accumulate_frame_count = 0
                self.fill_color = self.color1
                self.draw()
    @property
    def target_frame_count(self):
        return self._target_frame_count
    @target_frame_count.setter
    def target_frame_count(self, count:int):
        count = int(count)
        self._target_frame_count = count


class Button_pressing(_Button):

    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)
        self._buttons_to_respond = [0,]

    def switch_color(self):
        if self.window != None and self.window.is_focused:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if mouse.is_any_pressed:
                    for button in self._buttons_to_respond:
                        if button in mouse.pressed_button:
                            self.fill_color = self.color2
                            self.draw()
                            break

                elif self.fill_color != self.color1:
                    self.fill_color = self.color1
                    self.draw()

            elif self.fill_color != self.color1:
                self.fill_color = self.color1
                self.draw()
        pass

    @property
    def buttons_to_respond(self):
        return self._buttons_to_respond
    @buttons_to_respond.setter
    def buttons_to_respond(self, *buttons:int):
        int_buttons = [int(i) for i in buttons]
        self._buttons_to_respond = int_buttons
