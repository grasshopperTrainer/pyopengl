'''OpenGL extension ARB.query_buffer_object

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.query_buffer_object to provide a more
Python-friendly API

Overview (from the spec)
	
	Statistics about the operation of the OpenGL pipeline, such as the number
	of samples that passed the depth test, the elapsed time between two events
	or the number of vertices written by transform feedback can be retrieved
	from the GL through query objects. The result of a query object is
	acquired by the application through the OpenGL API into a client provided
	memory location. Should the result returned by the API be required for use
	in a shader, it must be passed back to the GL via a program uniform or
	some other mechanism. This requires a round-trip from the GPU to the CPU
	and back.
	
	This extension introduces a mechanism whereby the result of a query object
	may be retrieved into a buffer object instead of client memory. This allows
	the query rsult to be made available to a shader without a round-trip to
	the CPU for example by subsequently using the buffer object as a uniform
	buffer, texture buffer or other data store visible to the shader. This
	functionality may also be used to place the results of many query objects
	into a single, large buffer and then map or otherwise read back the entire
	buffer at a later point in time, avoiding a per-query object CPU-GPU
	synchronization event.
	
	The extension allows acquiring the result of any query object type
	supported by the GL implementation into a buffer object. The implementation
	will determine the most efficient method of copying the query result to the
	buffer.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/query_buffer_object.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.query_buffer_object import *
from OpenGL.raw.GL.ARB.query_buffer_object import _EXTENSION_NAME

def glInitQueryBufferObjectARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION