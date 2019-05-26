'''OpenGL extension WIN.phong_shading

This module customises the behaviour of the 
OpenGL.raw.GL.WIN.phong_shading to provide a more
Python-friendly API

Overview (from the spec)
	
	WIN_phong_shading enables rendering Phong shaded primitives using OpenGL.
	Phong shading is a well known shading technique documented 
	in most graphics texts. 
	
	As opposed to Gouraud (or smooth) shading, which simply calculates the 
	normals at the vertices and then interpolates the colors of the pixels, 
	Phong shading involves interpolating an individual normal for every pixel,
	and then applying the shading model to each pixel based on its normal 
	component. 
	
	While Phong shading requires substantially more computation than does 
	Gouraud shading, the resulting images are more realistic, especially if the
	primitives are large. 

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/WIN/phong_shading.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.WIN.phong_shading import *
from OpenGL.raw.GL.WIN.phong_shading import _EXTENSION_NAME

def glInitPhongShadingWIN():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION