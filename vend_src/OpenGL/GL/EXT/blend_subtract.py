'''OpenGL extension EXT.blend_subtract

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.blend_subtract to provide a more
Python-friendly API

Overview (from the spec)
	
	Two additional blending equations are specified using the interface
	defined by EXT_blend_minmax.  These equations are similar to the
	default blending equation, but produce the difference of its left
	and right hand sides, rather than the sum.  Image differences are
	useful in many image processing applications.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/blend_subtract.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.blend_subtract import *
from OpenGL.raw.GL.EXT.blend_subtract import _EXTENSION_NAME

def glInitBlendSubtractEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION