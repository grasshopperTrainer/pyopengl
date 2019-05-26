'''OpenGL extension APPLE.vertex_program_evaluators

This module customises the behaviour of the 
OpenGL.raw.GL.APPLE.vertex_program_evaluators to provide a more
Python-friendly API

Overview (from the spec)
	
	    This extension allows the one- and two-dimensional evaluators to be used
	    with vertex program attributes.  The operation of this extension is
	    precisely analogous to the operation of the normal evaluators.
	
		Where normal evaluators are enabled with Enable(MAP1_VERTEX_3), for
	    example, attribute evaluators are enabled with
	    EnableVertexAttribAPPLE(index, VERTEX_ATTRIB_MAP1_APPLE).
	
		Where the size (1, 2, 3, or 4) of a normal evaluator is embedded in the
	    token for that evaluator (for example, MAP1_VERTEX_3 has size 3),
	    attribute evaluators give the size as an argument to MapVertexAttrib**APPLE.
	
		The 1D and 2D evaluator order, domain, and coefficients are given as
	    arguments to MapVertexAttrib**APPLE, with exactly the same meaning and
	    restrictions as the same arguments to Map1f, Map2f, Map1d, & Map2d.
		The evaluator order, domain, and coefficients may be queried with
	    GetVertexAttrib*vARB, with the same operation as GetMap*v.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/APPLE/vertex_program_evaluators.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.APPLE.vertex_program_evaluators import *
from OpenGL.raw.GL.APPLE.vertex_program_evaluators import _EXTENSION_NAME

def glInitVertexProgramEvaluatorsAPPLE():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glMapVertexAttrib1dAPPLE.points size not checked against 'size,stride,order'
glMapVertexAttrib1dAPPLE= wrapper.wrapper(glMapVertexAttrib1dAPPLE).setInputArraySize(
    'points', None
)
# INPUT glMapVertexAttrib1fAPPLE.points size not checked against 'size,stride,order'
glMapVertexAttrib1fAPPLE= wrapper.wrapper(glMapVertexAttrib1fAPPLE).setInputArraySize(
    'points', None
)
# INPUT glMapVertexAttrib2dAPPLE.points size not checked against 'size,ustride,uorder,vstride,vorder'
glMapVertexAttrib2dAPPLE= wrapper.wrapper(glMapVertexAttrib2dAPPLE).setInputArraySize(
    'points', None
)
# INPUT glMapVertexAttrib2fAPPLE.points size not checked against 'size,ustride,uorder,vstride,vorder'
glMapVertexAttrib2fAPPLE= wrapper.wrapper(glMapVertexAttrib2fAPPLE).setInputArraySize(
    'points', None
)
### END AUTOGENERATED SECTION