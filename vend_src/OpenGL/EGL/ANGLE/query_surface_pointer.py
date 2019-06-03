'''OpenGL extension ANGLE.query_surface_pointer

This module customises the behaviour of the 
OpenGL.raw.EGL.ANGLE.query_surface_pointer to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ANGLE/query_surface_pointer.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.EGL import _types, _glgets
from OpenGL.raw.EGL.ANGLE.query_surface_pointer import *
from OpenGL.raw.EGL.ANGLE.query_surface_pointer import _EXTENSION_NAME

def glInitQuerySurfacePointerANGLE():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION