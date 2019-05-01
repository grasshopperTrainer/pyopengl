from windowing.layers.layerable import Layerable
from ..renderUnit.renderunit import RenderUnit
from windowing.window import Window

class RenderObject(Layerable, RenderUnit):
    FILL_COLOR = 100, 100, 100, 100
    EDGE_COLOR = 0, 0, 0, 0
