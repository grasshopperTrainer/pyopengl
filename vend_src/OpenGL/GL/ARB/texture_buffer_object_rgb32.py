'''OpenGL extension ARB.texture_buffer_object_rgb32

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.texture_buffer_object_rgb32 to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension adds three new buffer texture formats - RGB32F, RGB32I, 
	and RGB32UI.  This partially addresses one of the limitations of buffer 
	textures in the original EXT_texture_buffer_object extension and in 
	OpenGL 3.1, which provide no support for three-component formats.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/texture_buffer_object_rgb32.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.texture_buffer_object_rgb32 import *
from OpenGL.raw.GL.ARB.texture_buffer_object_rgb32 import _EXTENSION_NAME

def glInitTextureBufferObjectRgb32ARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION