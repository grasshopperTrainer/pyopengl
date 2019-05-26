'''OpenGL extension ARB.texture_mirror_clamp_to_edge

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.texture_mirror_clamp_to_edge to provide a more
Python-friendly API

Overview (from the spec)
	
	ARB_texture_mirror_clamp_to_edge extends the set of texture wrap modes to
	include an additional mode (GL_MIRROR_CLAMP_TO_EDGE) that effectively uses
	a texture map twice as large as the original image in which the additional
	half of the new image is a mirror image of the original image.
	
	This new mode relaxes the need to generate images whose opposite edges
	match by using the original image to generate a matching "mirror image".
	This mode allows the texture to be mirrored only once in the negative
	s, t, and r directions.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/texture_mirror_clamp_to_edge.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.texture_mirror_clamp_to_edge import *
from OpenGL.raw.GL.ARB.texture_mirror_clamp_to_edge import _EXTENSION_NAME

def glInitTextureMirrorClampToEdgeARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION