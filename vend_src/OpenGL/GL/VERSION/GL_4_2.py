'''OpenGL extension VERSION.GL_4_2

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_4_2 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_4_2.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.VERSION.GL_4_2 import *
from OpenGL.raw.GL.VERSION.GL_4_2 import _EXTENSION_NAME

def glInitGl42VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawElementsInstancedBaseInstance.indices size not checked against count
glDrawElementsInstancedBaseInstance= wrapper.wrapper(glDrawElementsInstancedBaseInstance).setInputArraySize(
    'indices', None
)
# INPUT glDrawElementsInstancedBaseVertexBaseInstance.indices size not checked against count
glDrawElementsInstancedBaseVertexBaseInstance= wrapper.wrapper(glDrawElementsInstancedBaseVertexBaseInstance).setInputArraySize(
    'indices', None
)
glGetInternalformativ= wrapper.wrapper(glGetInternalformativ).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetActiveAtomicCounterBufferiv= wrapper.wrapper(glGetActiveAtomicCounterBufferiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION
