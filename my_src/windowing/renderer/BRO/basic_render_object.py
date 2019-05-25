from windowing.layers.layerable import Layerable
from windowing.renderer.renderer_builder import Renderer_builder


class BasicRenderObject(Layerable, Renderer_builder):
    DEF_FILL_COLOR = 1, 1, 1, 1
    DEF_EDGE_COLOR = 0, 0, 0, 1
    DEF_EDGE_WEIGHT = 2




