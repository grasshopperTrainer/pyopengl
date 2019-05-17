'''OpenGL extension EXT.pixel_transform

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.pixel_transform to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides support for scaling, rotation, translation and
	shearing of two-dimensional pixel rectangles in the pixel rasterizer.
	The transformation is defined via a 4x4 matrix, where only those entries
	which apply as a 2D affine transformation will be accepted and used.
	These matrices can be manipulated using the same functions as the other 
	OpenGL matrix stacks.
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/pixel_transform.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.EXT.pixel_transform import *
from OpenGL.raw.GL.EXT.pixel_transform import _EXTENSION_NAME

def glInitPixelTransformEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glPixelTransformParameterivEXT= wrapper.wrapper(glPixelTransformParameterivEXT).setInputArraySize(
    'params', 1
)
glPixelTransformParameterfvEXT= wrapper.wrapper(glPixelTransformParameterfvEXT).setInputArraySize(
    'params', 1
)
# INPUT glGetPixelTransformParameterivEXT.params size not checked against 'pname'
glGetPixelTransformParameterivEXT= wrapper.wrapper(glGetPixelTransformParameterivEXT).setInputArraySize(
    'params', None
)
# INPUT glGetPixelTransformParameterfvEXT.params size not checked against 'pname'
glGetPixelTransformParameterfvEXT= wrapper.wrapper(glGetPixelTransformParameterfvEXT).setInputArraySize(
    'params', None
)
### END AUTOGENERATED SECTION