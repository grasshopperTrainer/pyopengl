'''OpenGL extension SGIX.texture_add_env

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.texture_add_env to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/texture_add_env.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.SGIX.texture_add_env import *
from OpenGL.raw.GL.SGIX.texture_add_env import _EXTENSION_NAME

def glInitTextureAddEnvSGIX():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION