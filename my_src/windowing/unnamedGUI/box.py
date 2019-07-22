from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
from ..callback_repository import Callback_repository
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
import weakref
from collections import namedtuple
from ..mcs import MCS
from .typewriter import Basic_typewriter


class Box(MCS):

    def __init__(self, posx, posy, width, height, window=None):
        super().__init__(posx,posy,width,height)

        if window != None:
            self._window = weakref.ref(window)
            self.is_child_of(window)
        else:
            self._window = None

        # self._flag_draw = True
        self._flag_state = 0
        self._flag_scissor = True

    def scissor(self, b:bool):
        if not isinstance(b, bool):
            raise TypeError
        if b:
            for i in self.family[1:]:
                i._flag_scissor = False

        self._flag_scissor = b

    def draw(self):
        pass

    def set_input_space(self, window):
        self._window = weakref.ref(window)
        pass

    def is_mother_of(self, *objects):
        super().is_mother_of(*objects)

    def is_child_of(self, mother):
        super().is_child_of(mother)
        if isinstance(mother, Window):
            self.set_input_space(mother)
        else:
            self.set_input_space(mother.window)

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
    def window(self):
        if self._window != None:
            return self._window()
        return None

    def is_pressed(self, depth=None):
        print('children pressed?')
        if self.window is None:
            raise

        mouse = self.window.mouse
        mouse.is_in_LCS(self)
        print(mouse.window_position_gl, mouse.is_just_pressed)
        if depth != None:
            if depth == 0:
                return
            else:
                depth -= 1

        print(self.children)
        pass

class Filled_box(Box):
    """
            one renderer should have one shader.
            but this can be called from several plces...
            when initiating ... like first_rect = TestBRO()
            how to make calling free???
            """
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('basic_gui_box'))
    renderer.use_drawmode_triangle_strip()
    renderer.use_index_buffer(renderer.Indexbuffer((0, 1, 3, 3, 1, 2)))

    renderer.use_render_unit(True)

    def __init__(self,posx, posy, width, height, window=None):
        super().__init__(posx, posy, width, height, window)

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
        if self._flag_update:
            self._unit.shader_io.a_position = self.vertex()
            self._unit.shader_io.u_fillcol = self._fill_color
            if self._flag_scissor:
                self._unit.draw_scissor(self.pixel_x,self.pixel_y, self.pixel_w, self.pixel_h)
            self._unit.draw(comment=self.__str__())
            for child in self.children:
                child.draw()
        else:
            # print(f'{self} is deactivated drawing is ignored')
            pass

    # def type_text(self, text, height, position=(0,0)):
    #     self._text = text
    #     self._text_height = height
    #     self._text_position = position
    #
    #     Basic_typewriter.type(self.pixel_x, self.pixel_y, self._string, self._text_height, self.text_fill_color)


class Block(Filled_box):
    # TODO maybe need do-not-color
    def __init__(self, posx, posy, width, height, window=None):
        super().__init__(posx,posy,width,height, window)

    # def draw(self):
    #     super().draw()
    #     for child in self._children:
    #         child.draw()

    def set_vertical(self, *boxes):
        pass

    def set_state_change(self):
        pass


class Textbox(Filled_box):
    def __init__(self,posx, posy, width, height,window, string, text_height):
        super().__init__(posx,posy,width,height,window)
        self.fill_color = 0,0,0,0
        self._text_fill_color = 0,0,0,1
        self._text_height = text_height
        self._string = string

    def draw(self):
        super().draw()
        self.type()

    @property
    def text_fill_color(self):
        return self._text_fill_color
    @text_fill_color.setter
    def text_fill_color(self, rgba):
        if len(rgba) != 4:
            raise
        self._text_fill_color = rgba

    def type(self):
        Basic_typewriter.type(self.pixel_x, self.pixel_y, self._string, self._text_height, self.text_fill_color)

