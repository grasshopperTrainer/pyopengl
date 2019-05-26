'''OpenGL extension ARB.half_float_pixel

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.half_float_pixel to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension introduces a new data type for half-precision (16-bit)
	floating-point quantities.  The floating-point format is very similar
	to the IEEE single-precision floating-point standard, except that it
	has only 5 exponent bits and 10 mantissa bits.  Half-precision floats
	are smaller than full precision floats and provide a larger dynamic
	range than similarly sized normalized scalar data types.
	
	This extension allows applications to use half-precision floating-
	point data when specifying pixel data.  It extends the existing image
	specification commands to accept the new data type.
	
	Floating-point data is clamped to [0, 1] at various places in the
	GL unless clamping is disabled with the ARB_color_buffer_float
	extension.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/half_float_pixel.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.half_float_pixel import *
from OpenGL.raw.GL.ARB.half_float_pixel import _EXTENSION_NAME

def glInitHalfFloatPixelARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION