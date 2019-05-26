'''OpenGL extension EXT.create_context_es2_profile

This module customises the behaviour of the 
OpenGL.raw.WGL.EXT.create_context_es2_profile to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/create_context_es2_profile.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.WGL import _types, _glgets
from OpenGL.raw.WGL.EXT.create_context_es2_profile import *
from OpenGL.raw.WGL.EXT.create_context_es2_profile import _EXTENSION_NAME

def glInitCreateContextEs2ProfileEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION