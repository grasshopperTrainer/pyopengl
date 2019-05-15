'''OpenGL extension SUN.vertex

This module customises the behaviour of the 
OpenGL.raw.GL.SUN.vertex to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides new GL commands to specify vertex data such as 
	color and normal along with the vertex in one single GL command in order to
	minimize the overhead in making GL commands for each set of vertex data.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SUN/vertex.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.SUN.vertex import *
from OpenGL.raw.GL.SUN.vertex import _EXTENSION_NAME

def glInitVertexSUN():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glColor4ubVertex2fvSUN= wrapper.wrapper(glColor4ubVertex2fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 2
)
glColor4ubVertex3fvSUN= wrapper.wrapper(glColor4ubVertex3fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 3
)
glColor3fVertex3fvSUN= wrapper.wrapper(glColor3fVertex3fvSUN).setInputArraySize(
    'c', 3
).setInputArraySize(
    'v', 3
)
glNormal3fVertex3fvSUN= wrapper.wrapper(glNormal3fVertex3fvSUN).setInputArraySize(
    'v', 3
).setInputArraySize(
    'n', 3
)
glColor4fNormal3fVertex3fvSUN= wrapper.wrapper(glColor4fNormal3fVertex3fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'n', 3
)
glTexCoord2fVertex3fvSUN= wrapper.wrapper(glTexCoord2fVertex3fvSUN).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'v', 3
)
glTexCoord4fVertex4fvSUN= wrapper.wrapper(glTexCoord4fVertex4fvSUN).setInputArraySize(
    'tc', 4
).setInputArraySize(
    'v', 4
)
glTexCoord2fColor4ubVertex3fvSUN= wrapper.wrapper(glTexCoord2fColor4ubVertex3fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'v', 3
)
glTexCoord2fColor3fVertex3fvSUN= wrapper.wrapper(glTexCoord2fColor3fVertex3fvSUN).setInputArraySize(
    'c', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'v', 3
)
glTexCoord2fNormal3fVertex3fvSUN= wrapper.wrapper(glTexCoord2fNormal3fVertex3fvSUN).setInputArraySize(
    'v', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'n', 3
)
glTexCoord2fColor4fNormal3fVertex3fvSUN= wrapper.wrapper(glTexCoord2fColor4fNormal3fVertex3fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'n', 3
)
glTexCoord4fColor4fNormal3fVertex4fvSUN= wrapper.wrapper(glTexCoord4fColor4fNormal3fVertex4fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 4
).setInputArraySize(
    'tc', 4
).setInputArraySize(
    'n', 3
)
glReplacementCodeuiVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiVertex3fvSUN).setInputArraySize(
    'v', 3
).setInputArraySize(
    'rc', 1
)
glReplacementCodeuiColor4ubVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiColor4ubVertex3fvSUN).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'rc', 1
)
glReplacementCodeuiColor3fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiColor3fVertex3fvSUN).setInputArraySize(
    'c', 3
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'rc', 1
)
glReplacementCodeuiNormal3fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiNormal3fVertex3fvSUN).setInputArraySize(
    'n', 3
).setInputArraySize(
    'rc', 1
).setInputArraySize(
    'v', 3
)
glReplacementCodeuiColor4fNormal3fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiColor4fNormal3fVertex3fvSUN).setInputArraySize(
    'n', 3
).setInputArraySize(
    'c', 4
).setInputArraySize(
    'rc', 1
).setInputArraySize(
    'v', 3
)
glReplacementCodeuiTexCoord2fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiTexCoord2fVertex3fvSUN).setInputArraySize(
    'v', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'rc', 1
)
glReplacementCodeuiTexCoord2fNormal3fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiTexCoord2fNormal3fVertex3fvSUN).setInputArraySize(
    'n', 3
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'rc', 1
)
glReplacementCodeuiTexCoord2fColor4fNormal3fVertex3fvSUN= wrapper.wrapper(glReplacementCodeuiTexCoord2fColor4fNormal3fVertex3fvSUN).setInputArraySize(
    'n', 3
).setInputArraySize(
    'c', 4
).setInputArraySize(
    'v', 3
).setInputArraySize(
    'tc', 2
).setInputArraySize(
    'rc', 1
)
### END AUTOGENERATED SECTION