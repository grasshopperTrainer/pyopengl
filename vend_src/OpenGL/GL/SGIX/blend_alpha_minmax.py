'''OpenGL extension SGIX.blend_alpha_minmax

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.blend_alpha_minmax to provide a more 
Python-friendly API

Overview (from the spec)
	
	Two additional blending equations are specified using the interface
	defined by EXT_blend_minmax.  These equations are similar to the
	MIN_EXT and MAX_EXT blending equations, but the outcome for all four
	color parts is determined by a comparison of just the alpha
	component's source and destination values.  These equations are useful
	in image processing and advanced shading algorithms.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/blend_alpha_minmax.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.SGIX.blend_alpha_minmax import *
from OpenGL.raw.GL.SGIX.blend_alpha_minmax import _EXTENSION_NAME

def glInitBlendAlphaMinmaxSGIX():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION