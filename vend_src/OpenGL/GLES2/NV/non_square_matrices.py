'''OpenGL extension NV.non_square_matrices

This module customises the behaviour of the 
OpenGL.raw.GLES2.NV.non_square_matrices to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/non_square_matrices.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.NV.non_square_matrices import *
from OpenGL.raw.GLES2.NV.non_square_matrices import _EXTENSION_NAME

def glInitNonSquareMatricesNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glUniformMatrix2x3fvNV=wrapper.wrapper(glUniformMatrix2x3fvNV).setInputArraySize(
    'value', 6
)
glUniformMatrix3x2fvNV=wrapper.wrapper(glUniformMatrix3x2fvNV).setInputArraySize(
    'value', 6
)
glUniformMatrix2x4fvNV=wrapper.wrapper(glUniformMatrix2x4fvNV).setInputArraySize(
    'value', 8
)
glUniformMatrix4x2fvNV=wrapper.wrapper(glUniformMatrix4x2fvNV).setInputArraySize(
    'value', 8
)
glUniformMatrix3x4fvNV=wrapper.wrapper(glUniformMatrix3x4fvNV).setInputArraySize(
    'value', 12
)
glUniformMatrix4x3fvNV=wrapper.wrapper(glUniformMatrix4x3fvNV).setInputArraySize(
    'value', 12
)
### END AUTOGENERATED SECTION