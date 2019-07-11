from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
from ..callback_repository import Callback_repository
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
import weakref
from collections import namedtuple
from ..mcs import MCS

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
            self._unit.draw()
        else:
            print(f'{self} is deactivated drawing is ignored')

class Block(Filled_box):
    # TODO maybe need do-not-color
    def __init__(self, posx, posy, width, height, window=None):
        super().__init__(posx,posy,width,height, window)

    def draw(self):
        super().draw()
        for child in self._children:
            child.draw()

    def set_vertical(self, *boxes):
        pass

    def set_state_change(self):
        pass