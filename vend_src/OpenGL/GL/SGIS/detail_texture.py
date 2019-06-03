'''OpenGL extension SGIS.detail_texture

This module customises the behaviour of the 
OpenGL.raw.GL.SGIS.detail_texture to provide a more
Python-friendly API

Overview (from the spec)
	
	    This extension introduces texture magnification filters that blend
	    between the level 0 image and a separately defined "detail" image.
	    The detail image represents the characteristics of the high frequency
	    subband image above the band-limited level 0 image.  The detail image is
	    typically a rectangular portion of the subband image which is modified
	    so that it can be repeated without discontinuities along its edges.
	    Detail blending can be enabled for all color channels, for the alpha
	    channel only, or for the red, green, and blue channels only.  It is
	    available only for 2D textures.
	
	    WARNING - Silicon Graphics has filed for patent protection for some
		      of the techniques described in this extension document.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIS/detail_texture.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.SGIS.detail_texture import *
from OpenGL.raw.GL.SGIS.detail_texture import _EXTENSION_NAME

def glInitDetailTextureSGIS():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDetailTexFuncSGIS.points size not checked against None
glDetailTexFuncSGIS=wrapper.wrapper(glDetailTexFuncSGIS).setInputArraySize(
    'points', None
)
glGetDetailTexFuncSGIS=wrapper.wrapper(glGetDetailTexFuncSGIS).setOutput(
    'points',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
### END AUTOGENERATED SECTION