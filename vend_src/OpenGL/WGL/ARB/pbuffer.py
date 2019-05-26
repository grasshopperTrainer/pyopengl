'''OpenGL extension ARB.pbuffer

This module customises the behaviour of the 
OpenGL.raw.WGL.ARB.pbuffer to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/pbuffer.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.WGL import _types, _glgets
from OpenGL.raw.WGL.ARB.pbuffer import *
from OpenGL.raw.WGL.ARB.pbuffer import _EXTENSION_NAME

def glInitPbufferARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION