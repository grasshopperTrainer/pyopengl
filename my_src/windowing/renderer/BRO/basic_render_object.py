from windowing.layers.layerable import Layerable
from windowing.renderer.renderer_template import Renderer_template


class BasicRenderObject(Layerable, Renderer_template):
    DEF_FILL_COLOR = 1, 1, 1, 1
    DEF_EDGE_COLOR = 0, 0, 0, 1
    DEF_EDGE_WEIGHT = 2




