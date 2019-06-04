import weakref
from collections import namedtuple
from windowing.renderer.renderer_template import Render_unit

class Render_object_registry:

    def __init__(self, fbl):
        self._window = fbl
        self._collections = weakref.WeakKeyDictionary()
        self._candidate = []
        self._structure = namedtuple('registered',['id','used'])
        # RGB 8bit each, A will be always 1
        self._counter = 0x000001
        self._counter_max = 0xffffff
        # set mode
        # removes uncalled in every
        self._mode = 0

    def register(self, object):
        if self._counter ^ self._counter_max == 0  and len(self._candidate) == 0:
            raise IndexError('register is fully filled')

        if isinstance(object, Render_unit):
            if object not in self._collections:
                if len(self._candidate) == 0:
                    id = self._counter
                    self._counter += 0x1
                else:
                    id = self._candidate.pop(0)
                self._collections[object] = self._structure(id, False)

        else:
            raise TypeError

    def id(self, object):
        return self._collections[object].id

    def id_color(self, object):
        inte = self._collections[object].id
        inte = format(inte,'06x')
        color= [int(f'0x{inte[i*2:i*2+2]}',16)/255 for i in range(3)]
        return color

    def color_id(self, color):
        hex = bytearray(color).hex()
        inte = int(hex, 16)
        return inte