'''OpenGL extension OES.standard_derivatives

This module customises the behaviour of the 
OpenGL.raw.GLES2.OES.standard_derivatives to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/OES/standard_derivatives.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.OES.standard_derivatives import *
from OpenGL.raw.GLES2.OES.standard_derivatives import _EXTENSION_NAME

def glInitStandardDerivativesOES():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION