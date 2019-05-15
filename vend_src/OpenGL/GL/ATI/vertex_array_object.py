'''OpenGL extension ATI.vertex_array_object

This module customises the behaviour of the 
OpenGL.raw.GL.ATI.vertex_array_object to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension defines an interface that allows multiple sets of
	vertex array data to be cached in persistent server-side memory.
	It is intended to allow client data to be stored in memory that
	can be directly accessed by graphics hardware.
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ATI/vertex_array_object.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.ATI.vertex_array_object import *
from OpenGL.raw.GL.ATI.vertex_array_object import _EXTENSION_NAME

def glInitVertexArrayObjectATI():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glNewObjectBufferATI.pointer size not checked against size
glNewObjectBufferATI= wrapper.wrapper(glNewObjectBufferATI).setInputArraySize(
    'pointer', None
)
# INPUT glUpdateObjectBufferATI.pointer size not checked against size
glUpdateObjectBufferATI= wrapper.wrapper(glUpdateObjectBufferATI).setInputArraySize(
    'pointer', None
)
glGetObjectBufferfvATI= wrapper.wrapper(glGetObjectBufferfvATI).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetObjectBufferivATI= wrapper.wrapper(glGetObjectBufferivATI).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetArrayObjectfvATI= wrapper.wrapper(glGetArrayObjectfvATI).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetArrayObjectivATI= wrapper.wrapper(glGetArrayObjectivATI).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVariantArrayObjectfvATI= wrapper.wrapper(glGetVariantArrayObjectfvATI).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVariantArrayObjectivATI= wrapper.wrapper(glGetVariantArrayObjectivATI).setOutput(
    'params',size=(1,),orPassIn=True
)
### END AUTOGENERATED SECTION