'''OpenGL extension NV.texture_expand_normal

This module customises the behaviour of the 
OpenGL.raw.GL.NV.texture_expand_normal to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension provides a remapping mode where unsigned texture
	parts (in the range [0,1]) can be treated as though they
	contained signed data (in the range [-1,+1]).  This allows
	applications to easily encode signed data into unsigned texture
	formats.
	
	The functionality of this extension is nearly identical to the
	EXPAND_NORMAL_NV remapping mode provided in the NV_register_combiners
	extension, although it applies even if register combiners are used.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/texture_expand_normal.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.texture_expand_normal import *
from OpenGL.raw.GL.NV.texture_expand_normal import _EXTENSION_NAME

def glInitTextureExpandNormalNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION