'''OpenGL extension NV.parameter_buffer_object2

This module customises the behaviour of the 
OpenGL.raw.GL.NV.parameter_buffer_object2 to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension builds on the NV_parameter_buffer_object extension to
	provide additional flexibility in sourcing data from buffer objects.  
	
	The original NV_parameter_buffer_object (PaBO) extension provided the
	ability to bind buffer objects to a set of numbered binding points and
	access them in assembly programs as though they were arrays of 32-bit
	scalars (via the BUFFER variable type) or arrays of four-component vectors
	with 32-bit scalar parts (via the BUFFER4 variable type).  However,
	the functionality it provided had some significant limits on flexibility.
	Since any given buffer binding point could be used either as a BUFFER or
	BUFFER4, but not both, programs couldn't do both 32- and 128-bit fetches
	from a single binding point.  Additionally, No support was provided for
	8-, 16-, or 64-bit fetches, though they could be emulated using a larger
	loads, with bitfield operations and/or write masking to put parts in
	the right places.  Indexing was supported, but strides were limited to 4-
	and 16-byte multiples, depending on whether BUFFER or BUFFER4 is used.
	
	This new extension provides the buffer variable declaration type CBUFFER
	to specify a buffer that is treated as an array of bytes, rather than an
	array of words or vectors.  The LDC instruction allows programs to extract
	a vector of data from a CBUFFER variable, using a size and component count
	specified in the opcode modifier.  1-, 2-, and 4-component fetches are
	supported.  The LDC instruction supports byte offsets using normal array
	indexing mechanisms; both run-time and immediate offsets are supported.
	Offsets used for a buffer object fetch are required to be aligned to the
	size of the fetch (1, 2, 4, 8, or 16 bytes).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/parameter_buffer_object2.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.parameter_buffer_object2 import *
from OpenGL.raw.GL.NV.parameter_buffer_object2 import _EXTENSION_NAME

def glInitParameterBufferObject2NV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION