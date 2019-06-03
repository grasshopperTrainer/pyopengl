'''OpenGL extension ARB.timer_query

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.timer_query to provide a more
Python-friendly API

Overview (from the spec)
	
	Applications can benefit from accurate timing information in a number of
	different ways.  During application development, timing information can
	help identify application or driver bottlenecks.  At run time,
	applications can use timing information to dynamically adjust the amount
	of detail in a scene to achieve constant frame rates.  OpenGL
	implementations have historically provided little to no useful timing
	information.  Applications can get some idea of timing by reading timers
	on the CPU, but these timers are not synchronized with the graphics
	rendering pipeline.  Reading a CPU timer does not guarantee the completion
	of a potentially large amount of graphics work accumulated before the
	timer is read, and will thus produce wildly inaccurate results.
	glFinish() can be used to determine when previous rendering commands have
	been completed, but will idle the graphics pipeline and adversely affect
	application performance.
	
	This extension provides a query mechanism that can be used to determine
	the amount of time it takes to fully complete a set of GL commands, and
	without stalling the rendering pipeline.  It uses the query object
	mechanisms first introduced in the occlusion query extension, which allow
	time intervals to be polled asynchronously by the application.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/timer_query.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.ARB.timer_query import *
from OpenGL.raw.GL.ARB.timer_query import _EXTENSION_NAME

def glInitTimerQueryARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetQueryObjecti64v= wrapper.wrapper(glGetQueryObjecti64v).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetQueryObjectui64v= wrapper.wrapper(glGetQueryObjectui64v).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION