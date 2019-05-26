'''OpenGL extension NV.fence

This module customises the behaviour of the 
OpenGL.raw.GL.NV.fence to provide a more
Python-friendly API

Overview (from the spec)
	
	The goal of this extension is provide a finer granularity of
	synchronizing GL command completion than offered by standard OpenGL,
	which offers only two mechanisms for synchronization: Flush and Finish.
	Since Flush merely assures the user that the commands complete in a
	finite (though undetermined) amount of time, it is, thus, of only
	modest utility.  Finish, on the other hand, stalls CPU execution
	until all pending GL commands have completed.  This extension offers
	a middle ground - the ability to "finish" a subset of the command
	stream, and the ability to determine whether a given command has
	completed or not.
	
	This extension introduces the concept of a "fence" to the OpenGL
	command stream.  Once the fence is inserted into the command stream, it
	can be queried for a given condition - typically, its completion.
	Moreover, the application may also request a partial Finish -- that is,
	all commands prior to the fence will be forced to complete until control
	is returned to the calling process.  These new mechanisms allow for
	synchronization between the host CPU and the GPU, which may be accessing
	the same resources (typically memory).
	
	This extension is useful in conjunction with NV_vertex_array_range
	to determine when vertex information has been pulled from the
	vertex array range.  Once a fence has been tested TRUE or finished,
	all vertex indices issued before the fence must have been pulled.
	This ensures that the vertex data memory corresponding to the issued
	vertex indices can be safely modified (assuming no other outstanding
	vertex indices are issued subsequent to the fence).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/fence.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.NV.fence import *
from OpenGL.raw.GL.NV.fence import _EXTENSION_NAME

def glInitFenceNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDeleteFencesNV.fences size not checked against n
glDeleteFencesNV= wrapper.wrapper(glDeleteFencesNV).setInputArraySize(
    'fences', None
)
glGenFencesNV= wrapper.wrapper(glGenFencesNV).setOutput(
    'fences',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetFenceivNV= wrapper.wrapper(glGetFenceivNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION