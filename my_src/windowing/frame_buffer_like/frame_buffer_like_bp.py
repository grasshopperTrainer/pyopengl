from patterns.strict_method_implant import SMI
import weakref
class FBL(SMI):
    """
    this if mother of frame buffer-like class
    such as glfw.Window itself and Frame buffer object
    from OpenGL
    """
    _current = None
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        FBL._current = weakref.ref(self)
        return self

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
        if cls._current is None:
            return None
        else:
            if cls._current() is None:
                cls._current = None
                return None
            else:
                return cls._current()
    @classmethod
    def set_current(cls, fbl):
        try:
            cls._current = weakref.ref(fbl)
        except:
            cls._current = None

        # else:
        #     raise