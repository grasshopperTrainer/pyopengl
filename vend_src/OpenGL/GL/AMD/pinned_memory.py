'''OpenGL extension AMD.pinned_memory

This module customises the behaviour of the 
OpenGL.raw.GL.AMD.pinned_memory to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension defines an interface that allows improved control
	of the physical memory used by the graphics device.
	
	It allows an existing page of system memory allocated by the application
	to be used as memory directly accessible to the graphics processor. One
	example application of this functionality would be to be able to avoid an
	explicit synchronous copy with sub-system of the application; for instance
	it is possible to directly draw from a system memory copy of a video
	image.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/AMD/pinned_memory.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.AMD.pinned_memory import *
from OpenGL.raw.GL.AMD.pinned_memory import _EXTENSION_NAME

def glInitPinnedMemoryAMD():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION