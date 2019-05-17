'''OpenGL extension EXT.texture_snorm

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.texture_snorm to provide a more 
Python-friendly API

Overview (from the spec)
	
	Fixed-point textures in unextended OpenGL have integer parts,
	but those values are taken to represent floating-point values in
	the range [0.0,1.0]. These integer parts are considered
	"unsigned normalized" integers. When such a texture is accessed by
	a shader or by fixed-function fragment processing, floating-point
	values are returned in the range [0.0,1.0].
	
	This extension provides a set of new "signed normalized" integer
	texture formats. These are taken to represent a floating-point
	value in the range [-1.0,1.0] with an exact 0.0.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/texture_snorm.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.texture_snorm import *
from OpenGL.raw.GL.EXT.texture_snorm import _EXTENSION_NAME

def glInitTextureSnormEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION