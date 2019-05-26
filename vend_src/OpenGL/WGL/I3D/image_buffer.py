'''OpenGL extension I3D.image_buffer

This module customises the behaviour of the 
OpenGL.raw.WGL.I3D.image_buffer to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/I3D/image_buffer.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.WGL import _types, _glgets
from OpenGL.raw.WGL.I3D.image_buffer import *
from OpenGL.raw.WGL.I3D.image_buffer import _EXTENSION_NAME

def glInitImageBufferI3D():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION