'''OpenGL extension EXT.draw_instanced

This module customises the behaviour of the 
OpenGL.raw.GLES2.EXT.draw_instanced to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/draw_instanced.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.EXT.draw_instanced import *
from OpenGL.raw.GLES2.EXT.draw_instanced import _EXTENSION_NAME

def glInitDrawInstancedEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawElementsInstancedEXT.indices size not checked against 'count,type'
glDrawElementsInstancedEXT=wrapper.wrapper(glDrawElementsInstancedEXT).setInputArraySize(
    'indices', None
)
### END AUTOGENERATED SECTION