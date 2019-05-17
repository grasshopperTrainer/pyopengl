'''OpenGL extension INGR.color_clamp

This module customises the behaviour of the 
OpenGL.raw.GL.INGR.color_clamp to provide a more 
Python-friendly API

Overview (from the spec)
	
	Various RGBA color space conversions require clamping to values
	in a more constrained range than [0, 1].  This extension allows
	the definition of independent color clamp values for each of the
	four color parts as part of the Final Conversion in the pixel
	transfer path for draws, reads, and copies.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/INGR/color_clamp.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.INGR.color_clamp import *
from OpenGL.raw.GL.INGR.color_clamp import _EXTENSION_NAME

def glInitColorClampINGR():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION