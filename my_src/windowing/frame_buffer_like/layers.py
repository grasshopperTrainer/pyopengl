import weakref
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL


class Layer:
    def __enter__(self):
        self._collection.set_current(self)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._collection.set_current(self._collection[0])
        pass

    def __init__(self, collection, id, name):
        self._id = id
        self._name = name
        self._collection = collection
        self._objects = []
        self._itercount = 0
        self._state = True

    def turn_on(self):
        self._state = True
    def turn_off(self):
        self._state = False
    def turn_around(self):
        self._state = not self._state

    @property
    def id(self):
        return self._id

    @property
    def is_on(self):
        return self._state

class Layers:
    _current = 0
    def __init__(self):
        self._layers = {}
        self._current = None
        default = self.new('default')
        self.set_current(default)

    def __getitem__(self, item) -> Layer:
        if isinstance(item, str):
            for i in self._layers.values():
                if i._name == item:
                    return i
            raise KeyError(f"no such layer named '{item}'")
        elif isinstance(item, int):
            if item in self._layers:
                return self._layers[item]
            raise KeyError(f"no such layer named '{item}'")
        else:
            raise TypeError(f"key should be str or int")

    def new(self, id=None, name=None):
        if id in self._layers:
            raise
        name = 'unknown' if name is None else None
        layer = Layer(self, id, name)
        self._layers[id] = layer
        return layer

    def set_current(self, layer):
        self._current = weakref.ref(layer)

    @property
    def default(self):
        return self[0]

    def get_current(self):
        return self._current()

    def delete(self):
        self._current = None
        self._layers = None