from ..renderer.renderer_template import Renderer_builder
from patterns.update_check_descriptor import UCD
from ..window import Window
# from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker


class Button():
    """
    one renderer should have one shader.
    but this can be called from several plces...
    when initiating ... like first_rect = TestBRO()
    how to make calling free???
    """
    c = Renderer_builder()
    c.use_shader(c.Shader('BRO_rectangle'))
    c.use_triangle_strip_draw()
    c.use_index_buffer(c.Indexbuffer((0,1,3,3,1,2)))

    c.use_render_unit(vao=True, vbo=True)

    renderer = c()

    _posx = UCD()
    _posy = UCD()
    _width = UCD()
    _height = UCD()

    _abs_posx = UCD()
    _abs_posy = UCD()
    _abs_width = UCD()
    _abs_height = UCD()

    def __init__(self,posx, posy, width, height, window:Window, viewport):
        self.unit = self.renderer.new_render_unit()

        self._posx = posx
        self._posy = posy
        self._width = width
        self._height = height

        self._abs_posx = None
        self._abs_posy = None
        self._abs_width = None
        self._abs_height = None

        self._color1 = .1,.1,.1,1
        self._color2 = 0,0,.5,1
        self._draw_color = self._color1

        # self.unit.properties['u_fillcol'] = self._draw_color
        self.unit.shader_attribute.resize(4)

        self.window = window
        self.viewport = viewport

        window.mouse.set_object_selection_callback(
            self.unit,
            window.mouse.set_button_press_callback,
            (viewport.open,self.switch_color))

    def draw(self):
        # self.unit.properties['a_position'][0:4] = self.vertex
        self.unit.shader_attribute.a_position = self.vertex
        self.unit.shader_attribute.u_fillcol = self._draw_color
        # print(self._draw_color)
        # self.unit.properties['u_fillcol'] = self._draw_color
        self.renderer._draw_(self.unit)

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

    @property
    def vertex(self):
        a = self.abs_posx, self.abs_posy
        b = self.abs_posx+self.abs_width, self.abs_posy
        c = self.abs_posx+self.abs_width, self.abs_posy+self.abs_height
        d = self.abs_posx, self.abs_posy+self.abs_height
        return a,b,c,d

    def switch_color(self):
        if self._draw_color == self._color1:
            self._draw_color = self._color2
        else:
            self._draw_color = self._color1
        self.draw()

    @property
    def abs_posx(self):
        if isinstance(self._posx, float):
            self._abs_posx = self._posx*1
            return self._abs_posx
        else:
            self._abs_posx = self._posx
            return self._abs_posx

    @property
    def abs_posy(self):
        if isinstance(self._posy, float):
            self._abs_posy = self._posy*1
            return self._abs_posy
        else:
            self._abs_posy = self._posy
            return self._abs_posy

    @property
    def abs_width(self):
        if isinstance(self._width, float):
            self._abs_width = self._width*1
            return self._abs_width
        else:
            self._abs_width = self._width
            return self._abs_width

    @property
    def abs_height(self):
        if isinstance(self._height, float):
            self._abs_height = self._height*1
            return self._abs_posx
        else:
            self._abs_height = self._height
            return self._height