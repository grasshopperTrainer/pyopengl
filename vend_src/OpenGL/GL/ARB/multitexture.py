'''OpenGL extension ARB.multitexture

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.multitexture to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/multitexture.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.ARB.multitexture import *
from OpenGL.raw.GL.ARB.multitexture import _EXTENSION_NAME

def glInitMultitextureARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glMultiTexCoord1dvARB= wrapper.wrapper(glMultiTexCoord1dvARB).setInputArraySize(
    'v', 1
)
glMultiTexCoord1fvARB= wrapper.wrapper(glMultiTexCoord1fvARB).setInputArraySize(
    'v', 1
)
glMultiTexCoord1ivARB= wrapper.wrapper(glMultiTexCoord1ivARB).setInputArraySize(
    'v', 1
)
glMultiTexCoord1svARB= wrapper.wrapper(glMultiTexCoord1svARB).setInputArraySize(
    'v', 1
)
glMultiTexCoord2dvARB= wrapper.wrapper(glMultiTexCoord2dvARB).setInputArraySize(
    'v', 2
)
glMultiTexCoord2fvARB= wrapper.wrapper(glMultiTexCoord2fvARB).setInputArraySize(
    'v', 2
)
glMultiTexCoord2ivARB= wrapper.wrapper(glMultiTexCoord2ivARB).setInputArraySize(
    'v', 2
)
glMultiTexCoord2svARB= wrapper.wrapper(glMultiTexCoord2svARB).setInputArraySize(
    'v', 2
)
glMultiTexCoord3dvARB= wrapper.wrapper(glMultiTexCoord3dvARB).setInputArraySize(
    'v', 3
)
glMultiTexCoord3fvARB= wrapper.wrapper(glMultiTexCoord3fvARB).setInputArraySize(
    'v', 3
)
glMultiTexCoord3ivARB= wrapper.wrapper(glMultiTexCoord3ivARB).setInputArraySize(
    'v', 3
)
glMultiTexCoord3svARB= wrapper.wrapper(glMultiTexCoord3svARB).setInputArraySize(
    'v', 3
)
glMultiTexCoord4dvARB= wrapper.wrapper(glMultiTexCoord4dvARB).setInputArraySize(
    'v', 4
)
glMultiTexCoord4fvARB= wrapper.wrapper(glMultiTexCoord4fvARB).setInputArraySize(
    'v', 4
)
glMultiTexCoord4ivARB= wrapper.wrapper(glMultiTexCoord4ivARB).setInputArraySize(
    'v', 4
)
glMultiTexCoord4svARB= wrapper.wrapper(glMultiTexCoord4svARB).setInputArraySize(
    'v', 4
)
### END AUTOGENERATED SECTION
