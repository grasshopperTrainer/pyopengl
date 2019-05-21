from patterns.strict_method_implant import SMI

class FBL(SMI):
    """
    this if mother of frame buffer-like class
    such as glfw.Window itself and Frame buffer object
    from OpenGL
    """
    _current = None
    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    @property
    def size(self):
        pass
