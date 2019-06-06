from patterns.strict_method_implant import SMI

class FBL(SMI):
    """
    this if mother of frame buffer-like class
    such as glfw.Window itself and Frame buffer object
    from OpenGL
    """
    _current = None

    @SMI.must_func
    @property
    def flag_something_rendered(self):
        pass

    @SMI.must_func
    @property
    def render_unit_registry(self):
        pass

    @SMI.must_func
    @property
    def width(self):
        pass

    @SMI.must_func
    @property
    def height(self):
        pass

    @SMI.must_func
    @property
    def size(self):
        pass

    @SMI.must_func
    def begin(self):
        pass
    @SMI.must_func
    def end(self):
        pass


    @classmethod
    def get_current(cls):
        return cls._current
    @classmethod
    def set_current(cls, fbl):
        if isinstance(fbl, FBL):
            cls._current = fbl
        else:
            raise