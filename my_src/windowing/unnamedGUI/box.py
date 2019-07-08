from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
from ..callback_repository import Callback_repository
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
import weakref
from collections import namedtuple
from ..matryoshka_coordinate_system import Matryoshka_coordinate_system

class Box(Matryoshka_coordinate_system):

    def __init__(self, posx, posy, width, height, window=None, viewport=None):
        super().__init__(posx,posy,width,height)

        if window != None:
            self._window = weakref.ref(window)
        else:
            self._window = None

        if viewport != None:
            self._viewport = weakref.ref(viewport)
        else:
            self._viewport = None

        if viewport == None:
            if window != None:
                self.is_child_of(window)
        else:
            self.is_child_of(viewport)

        self._flag_draw = True
        self._flag_state = 0


    def draw(self):
        pass

    def is_mother_of(self, *objects):
        super().is_mother_of(*objects)
        for child in objects:
            child.set_window(self.window)
            child.set_viewport(self.viewport)

    # def set_window(self, window):
    #     if window != None:
    #         self._window = weakref.ref(window)

    def set_viewport(self, viewport):
        if viewport != None:
            self._viewport = weakref.ref(viewport)

    def copy(self):
        """
        copy for new position and size
        :return:
        """
        pass

    def reset_state(self):
        self._flag_state = 0

    def reset_all_state(self):
        self._flag_state = 0
        for box in self._children:
            box.reset_all_state()

    def disable_all_draw(self):
        self._flag_draw = False
        for box in self._children:
            box.disable_all_draw()

    def enable_all_draw(self):
        self._flag_draw = True
        for box in self._children:
            box.enable_all_draw()

    def switch_all_draw(self):
        self._flag_draw = not self._flag_draw
        for box in self._children:
            box.switch_all_draw()

    @property
    def viewport(self):
        if self._viewport != None:
            return self._viewport()
        return None

    @property
    def window(self):
        if self._window != None:
            return self._window()
        return None

class Filled_box(Box):
    """
            one renderer should have one shader.
            but this can be called from several plces...
            when initiating ... like first_rect = TestBRO()
            how to make calling free???
            """
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('basic_gui_box'))
    renderer.use_triangle_strip_draw()
    renderer.use_index_buffer(renderer.Indexbuffer((0, 1, 3, 3, 1, 2)))

    renderer.use_render_unit(vao=True, vbo=True)

    def __init__(self,posx, posy, width, height, window=None, viewport=None):
        super().__init__(posx, posy, width, height, window, viewport)

        self._unit = self.renderer()
        self._unit.shader_io.resize(4)

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
        if len(rgba) != 4:
            raise
        elif not all([isinstance(c, (int, float)) for c in rgba]):
            raise

        self._fill_color = rgba

    def draw(self):
        if self._flag_draw:
            if self.viewport != None:
                with self.viewport:
                    self._unit.shader_io.a_position = self.vertex()
                    self._unit.shader_io.u_fillcol = self._fill_color

                    self._unit._draw_()

class Block(Filled_box):
    # TODO maybe need do-not-color
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

    # def align_horrizontal(self, *objects, bottom_top=0):
    #
    #     if len(objects) == 0:
    #         objects = self._children
    #     # print(objects)
    #     # exit()
    #     # reference vertice for alignment
    #     if bottom_top == 0:
    #         ref_pos = [a-b for a,b in zip(objects[0].vertex(1), self.vertex(0))]
    #     else:
    #         ref_pos = [a-b for a,b in zip(objects[0].vertex(2), self.vertex(0))]
    #
    #     for child in objects[1:]:
    #         if bottom_top == 0:
    #             child.posx, child.posy = [a/b for a,b in zip(ref_pos, self.pixel_size)]
    #             # print(self.vertex())
    #             # print(ref_pos)
    #             # exit()
    #             ref_pos = [a-b for a,b in zip(child.vertex(1), self.vertex(0))]
    #         else:
    #             dist = [a-b for a,b in zip(ref_pos, child.vertex(3))]
    #             child.posx, child.posy = [int(a+b) for a,b in zip(dist, child.vertex(0))]
    #             ref_pos = [a-b for a,b in zip(child.vertex(2), self.vertex(0))]
    #
    # def align_vertical(self, *objects_to_align, left_right = 0, offset = (0,0)):
    #     # print('aligning vertical')
    #     # print(self.vertex())
    #     # print(self.pixel_posx, self.pixel_posy, self.pixel_width,self.pixel_height)
    #     # print()
    #     ref_pos = [a+b for a,b in zip(self.vertex(0), offset)]
    #     for object in objects_to_align:
    #         object.set_reference(self)
    #         # print(object._posx, object._posy)
    #         # print(object.vertex())
    #         # object._posx, object._posy = ref_pos
    #         # print(object._posx, object._posy)
    #         # print(object.vertex())
    #         # if left_right == 0:
    #         #     ref_pos = object.pixel_width, object.pixel_height
    #         #
    #         # elif left_right == 1:
    #         #     # ref_pos = object.vertex(2)
    #         #     pass

class Block_expandable(Block):

    pass


