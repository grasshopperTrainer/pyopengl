from windowing.layers.layerable import Layerable
from windowing.renderUnit.renderunit import RenderUnit


class RenderObject(Layerable, RenderUnit):
    DEF_FILL_COLOR = 1, 1, 1, 1
    DEF_EDGE_COLOR = 0, 0, 0, 1
    DEF_EDGE_WEIGHT = 2