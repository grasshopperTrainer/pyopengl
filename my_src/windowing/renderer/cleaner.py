from .renderer_template import Renderer_builder


class Cleaner:
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('cleaner'))
    renderer.use_drawmode_triangle_strip()
    renderer.use_vertex_array(renderer.Vertexarray())
    renderer.use_vertex_buffer(renderer.Vertexbuffer())
    renderer.use_index_buffer(renderer.Indexbuffer((0, 1, 3, 3, 1, 2)))

    def __init__(self):
        self._unit = self.renderer()
        self._unit.shader_io.resize(4)
        self._unit.shader_io.coordinate = (-1,1),(-1,-1),(1,-1),(1,1)
        self._unit.shader_io.fill_color = 1,1,1,1
        pass

    def clear(self, *rgba):
        if len(rgba) != 0:
            if len(rgba) == 3:
                self._unit.shader_io.fill_color = *rgba,1
            elif len(rgba) == 4:
                self._unit.shader_io.fill_color = rgba
            else:
                raise ValueError

        self._unit.draw()
        # print(self._unit.shader_io.coordinate)