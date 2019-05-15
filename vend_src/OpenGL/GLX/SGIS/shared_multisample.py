'''OpenGL extension SGIS.shared_multisample

This module customises the behaviour of the 
OpenGL.raw.GLX.SGIS.shared_multisample to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIS/shared_multisample.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLX import _types, _glgets
from OpenGL.raw.GLX.SGIS.shared_multisample import *
from OpenGL.raw.GLX.SGIS.shared_multisample import _EXTENSION_NAME

def glInitSharedMultisampleSGIS():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION