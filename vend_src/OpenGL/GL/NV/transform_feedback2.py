'''OpenGL extension NV.transform_feedback2

This module customises the behaviour of the 
OpenGL.raw.GL.NV.transform_feedback2 to provide a more 
Python-friendly API

Overview (from the spec)
	
	The NV_transform_feedback and EXT_transform_feedback extensions allow
	applications to capture primitives to one or more buffer objects when
	transformed by the GL.  This extension provides a few additional
	capabilities to these extensions, making transform feedback mode
	more useful.
	
	First, it provides transform feedback objects encapsulating transform
	feedback-related state, allowing applications to replace the entire
	transform feedback configuration in a single bind call.  Second, it
	provides the ability to pause and resume transform feedback operations.
	When transform feedback is paused, applications may render without
	transform feedback or may use transform feedback with different state and
	a different transform feedback object.  When transform feedback is
	resumed, additional primitives are captured and appended to previously
	captured primitives for the object.
	
	Additionally, this extension provides the ability to draw primitives
	captured in transform feedback mode without querying the captured
	primitive count.  The command DrawTransformFeedbackNV() is equivalent to
	glDrawArrays(<mode>, 0, <count>), where <count> is the number of vertices
	captured to buffer objects during the last transform feedback capture
	operation on the transform feedback object used.  This draw operation only
	provides a vertex count -- it does not automatically set up vertex array
	state or vertex buffer object bindings, which must be done separately by
	the application.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/transform_feedback2.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.NV.transform_feedback2 import *
from OpenGL.raw.GL.NV.transform_feedback2 import _EXTENSION_NAME

def glInitTransformFeedback2NV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDeleteTransformFeedbacksNV.ids size not checked against n
glDeleteTransformFeedbacksNV= wrapper.wrapper(glDeleteTransformFeedbacksNV).setInputArraySize(
    'ids', None
)
glGenTransformFeedbacksNV= wrapper.wrapper(glGenTransformFeedbacksNV).setOutput(
    'ids',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
### END AUTOGENERATED SECTION