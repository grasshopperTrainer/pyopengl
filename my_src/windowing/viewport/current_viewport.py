


class Current_viewport:

    _current = None

    @classmethod
    def set_current(cls, viewport):
        cls._current = viewport
    @classmethod
    def get_current(cls):
        return cls._current