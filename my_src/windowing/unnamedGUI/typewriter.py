# from ..renderer.typewriter.typewriter import Basic_typewriter
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
from ..renderer.renderer_template import Renderer_builder
import freetype as ft
import numpy as np

# class Typewriter_builder:
#     pass

class Typewriter_builder:
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('char_draw'))
    renderer.use_render_unit(False,False,True,False)
    renderer.use_vertex_array(renderer.Vertexarray())
    renderer.use_vertex_buffer(renderer.Vertexbuffer())
    renderer.use_index_buffer(renderer.Indexbuffer((0,1,3,3,1,2)))
    renderer.use_drawmode_triangle_strip()

    def __init__(self, height):
        self._height = height
        self._characters = {}

    def append_chars(self, font_name_or_path, field):
        # type checking
        if not isinstance(font_name_or_path, str):
            raise TypeError

        if isinstance(field, str):
            if field == 'english':
                fields = [(0x0, 0x7f)]
            elif field == 'korean':
                raise
            else:
                raise Exception('language unknown. manually insert unicode field (int,int)')
        elif isinstance(field, (tuple,list)):
            # list of fields
            # ex (29,294)
            # ex ([20,30],[105,50503],[12002,40],[33,304])
            if len(field) == 2:
                fields = [field]

        # format path
        font_name_or_path = font_name_or_path.strip()
        if '/' not in font_name_or_path:
            # for window fonts
            font_name_or_path = f'C:/Windows/Fonts/{font_name_or_path}.ttf'
        elif font_name_or_path[-4:] != '.ttf':
            raise TypeError

        face = ft.Face(font_name_or_path)
        face.set_pixel_sizes(0, self._height)

        context = Unique_glfw_context.get_current()
        with context as gl:
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

            for field in fields:
                for unicode in range(field[0], field[1]+1):
                    face.load_char(unicode)
                    glyps = face.glyph
                    bitmap = glyps.bitmap
                    buffer = face.glyph.bitmap.buffer

                    render_unit = self.renderer(texture_width = bitmap.width,
                                                texture_height = bitmap.rows,
                                                texture_slot = 0,
                                                texture_data = buffer,
                                                texture_internalformat = 'RED',
                                                texture_format = 'RED')
                    render_unit.shader_io.resize(4)
                    render_unit.shader_io.slot = 0
                    render_unit.shader_io.tex_coord = (0,0),(0,1),(1,1),(1,0)

                    self._characters[chr(unicode)] = (render_unit,
                                                      bitmap.width,
                                                      bitmap.rows,
                                                      glyps.bitmap_left,
                                                      glyps.bitmap_top,
                                                      glyps.advance.x)


    def type(self, originx, originy, string, height ,color):
        # scale factor
        ratio = height/self._height
        for char in string:
            if char not in self._characters:
                raise
            renderer = self._characters[char][0]
            w,h,left_off, bottom_off, advance = np.array(self._characters[char][1:])*ratio # scale

            # position area
            left_top = np.array((originx+left_off, originy+bottom_off))
            vertex = left_top, left_top+np.array((0,-h)),left_top+np.array((w,-h)),left_top+np.array((w,0))

            renderer.shader_io.vertex = vertex
            renderer.shader_io.fill_color = color
            renderer.draw(0, comment=f'typing {char}')

            # move right
            originx += advance/64


class Basic_typewriter:
    typewriter = None
    def __init__(self):
        raise

    def _build_if_non(func):
        @classmethod
        def wrapper(cls,*args, **kwargs):
            if cls.typewriter is None:
                cls.typewriter = Typewriter_builder(100)
                cls.typewriter.append_chars('arial', [0, 128])
            return func(cls, *args, **kwargs)
        return wrapper

    @_build_if_non
    def type(cls, posx, posy, string, height, color):
        cls.typewriter.type(posx, posy, string, height, color)