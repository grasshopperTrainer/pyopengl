from ..renderer_builder import Renderer_builder
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
from ..components import *

class Render_unit:
    def __init__(self):

        self._vao = Vertexarray()
        self._vbo = Vertexbuffer()
        self._flag_built = False

    def _build_(self):
        if not self._flag_built:
            self.vao.build()
            self.vao.bind()

            self.vbo.build()

            self.vao.unbind()

            self._flag_built = True


    @property
    def vao(self):
        return self._vao

    @property
    def vbo(self):
        return self._vbo

class TestBRO():
    """
    one renderer should have one shader.
    but this can be called from several plces...
    when initiating ... like first_rect = TestBRO()
    how to make calling free???
    """
    shader = None
    indexbuffer = None
    render_unit = []


    def __init__(self):
        # if not registered
        fbl = FBL.get_current()
        if self.__class__ not in fbl.registered_shaders:
            fbl.register_shader(self.__class__)
            self._shader = Shader('BRO_rectangle', 'test_renderer_builder')
            self._indexbuffer = Indexbuffer()
            self._render_units = []

            self._shader.build()
            self._indexbuffer.build()
        else:
            self._render_unit.apeend(Render_unit())

    def draw(self):
        fbl = FBL.get_current()
        print(fbl.registered_shaders)
        if self in fbl.registered_shaders:
            print('this renderer is registered insied the window')
            print(self)
        else:
            print(f'mother window:{fbl.mother_window}')
            print(f'children window:{fbl.children_window}')

        pass