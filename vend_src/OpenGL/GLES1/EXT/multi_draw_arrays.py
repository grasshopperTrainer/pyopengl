'''OpenGL extension EXT.multi_draw_arrays

This module customises the behaviour of the 
OpenGL.raw.GLES1.EXT.multi_draw_arrays to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/multi_draw_arrays.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES1 import _types, _glgets
from OpenGL.raw.GLES1.EXT.multi_draw_arrays import *
from OpenGL.raw.GLES1.EXT.multi_draw_arrays import _EXTENSION_NAME

def glInitMultiDrawArraysEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glMultiDrawArraysEXT.count size not checked against 'primcount'
# INPUT glMultiDrawArraysEXT.first size not checked against 'primcount'
glMultiDrawArraysEXT=wrapper.wrapper(glMultiDrawArraysEXT).setInputArraySize(
    'count', None
).setInputArraySize(
    'first', None
)
# INPUT glMultiDrawElementsEXT.count size not checked against 'primcount'
# INPUT glMultiDrawElementsEXT.indices size not checked against 'primcount'
glMultiDrawElementsEXT=wrapper.wrapper(glMultiDrawElementsEXT).setInputArraySize(
    'count', None
).setInputArraySize(
    'indices', None
)
### END AUTOGENERATED SECTION