'''OpenGL extension ARB.instanced_arrays

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.instanced_arrays to provide a more
Python-friendly API

Overview (from the spec)
	
	A common use case in GL for some applications is to be able to
	draw the same object, or groups of similar objects that share
	vertex data, primitive count and type, multiple times.  This 
	extension provides a means of accelerating such use cases while 
	restricting the number of API calls, and keeping the amount of 
	duplicate data to a minimum.
	
	In particular, this extension specifies an alternative to the 
	read-only shader variable introduced by ARB_draw_instanced.  It
	uses the same draw calls introduced by that extension, but 
	redefines them so that a vertex shader can instead use vertex 
	array attributes as a source of instance data.
	
	This extension introduces an array "divisor" for generic
	vertex array attributes, which when non-zero specifies that the
	attribute is "instanced."  An instanced attribute does not
	advance per-vertex as usual, but rather after every <divisor>
	conceptual draw calls.
	
	(Attributes which aren't instanced are repeated in their entirety
	for every conceptual draw call.)
	
	By specifying transform data in an instanced attribute or series
	of instanced attributes, vertex shaders can, in concert with the 
	instancing draw calls, draw multiple instances of an object with 
	one draw call.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/instanced_arrays.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.instanced_arrays import *
from OpenGL.raw.GL.ARB.instanced_arrays import _EXTENSION_NAME

def glInitInstancedArraysARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION