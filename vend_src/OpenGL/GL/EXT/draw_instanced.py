'''OpenGL extension EXT.draw_instanced

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.draw_instanced to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides the means to render multiple instances of
	an object with a single draw call, and an "instance ID" variable
	which can be used by the vertex program to compute per-instance
	values, typically an object's transform.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/draw_instanced.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.EXT.draw_instanced import *
from OpenGL.raw.GL.EXT.draw_instanced import _EXTENSION_NAME

def glInitDrawInstancedEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawElementsInstancedEXT.indices size not checked against 'count,type'
glDrawElementsInstancedEXT= wrapper.wrapper(glDrawElementsInstancedEXT).setInputArraySize(
    'indices', None
)
### END AUTOGENERATED SECTION