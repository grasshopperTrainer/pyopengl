class Current_framebuffer:
    _current = None

    @classmethod
    def set_current(cls, fb_like):
        cls._current = fb_like

    @classmethod
    def get_current(cls):
        return cls._current