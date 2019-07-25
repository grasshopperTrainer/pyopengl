import weakref
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
# from windowing.frame_buffer_like.frame import Frame

class Layer:
    def __enter__(self):
        if self._collection.get_current() != self:
            self._previous_layer = self._collection.get_current()
        self._collection.set_current(self)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._previous_layer != None:
            self._collection.set_current(self._previous_layer)
            self._previous_layer = None
        # self._collection.set_current(self._collection[0])
        pass

    def __init__(self, collection, id, name):
        self._previous_layer = None
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

    def __str__(self):
        return f'<Layer> name:{self._name} id:{self._id}'
    def __repr__(self):
        return self.__str__()

