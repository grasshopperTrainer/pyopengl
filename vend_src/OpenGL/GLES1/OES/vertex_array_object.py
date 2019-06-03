'''OpenGL extension OES.vertex_array_object

This module customises the behaviour of the 
OpenGL.raw.GLES1.OES.vertex_array_object to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/OES/vertex_array_object.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES1 import _types, _glgets
from OpenGL.raw.GLES1.OES.vertex_array_object import *
from OpenGL.raw.GLES1.OES.vertex_array_object import _EXTENSION_NAME

def glInitVertexArrayObjectOES():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDeleteVertexArraysOES.arrays size not checked against n
glDeleteVertexArraysOES=wrapper.wrapper(glDeleteVertexArraysOES).setInputArraySize(
    'arrays', None
)
# INPUT glGenVertexArraysOES.arrays size not checked against n
glGenVertexArraysOES=wrapper.wrapper(glGenVertexArraysOES).setInputArraySize(
    'arrays', None
)
### END AUTOGENERATED SECTION