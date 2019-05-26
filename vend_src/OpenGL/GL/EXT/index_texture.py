'''OpenGL extension EXT.index_texture

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.index_texture to provide a more
Python-friendly API

Overview (from the spec)
	
	This extends the definition of texturing so that it is supported
	in color index mode.  This extension builds on the notion of
	texture images which have color index internal formats which was
	introduced in EXT_paletted_texture.
	
	This extension also introduces a new texture environment function
	ADD which is useful for combining lighting and texturing in
	color index mode.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/index_texture.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.index_texture import *
from OpenGL.raw.GL.EXT.index_texture import _EXTENSION_NAME

def glInitIndexTextureEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION