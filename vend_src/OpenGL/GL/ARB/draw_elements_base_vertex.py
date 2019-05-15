'''OpenGL extension ARB.draw_elements_base_vertex

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.draw_elements_base_vertex to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a method to specify a "base vertex offset"
	value which is effectively added to every vertex index that is
	transferred through DrawElements.
	
	This mechanism can be used to decouple a set of indices from the
	actual vertex array that it is referencing. This is useful if an
	application stores multiple indexed models in a single vertex array.
	The same index array can be used to draw the model no matter where
	it ends up in a larger vertex array simply by changing the base
	vertex value. Without this functionality, it would be necessary to
	rebind all the vertex attributes every time geometry is switched and
	this can have larger performance penalty.
	
	For example consider the (very contrived and simple) example of
	drawing two triangles to form a quad. In the typical example you
	have the following setup:
	
	      vertices                indices
	     ----------                -----
	  0 | (-1,  1) |            0 |  0  |
	  1 | (-1, -1) |            1 |  1  |
	  2 | ( 1, -1) |            2 |  2  |
	  3 | ( 1,  1) |            3 |  3  |
	     ----------             4 |  0  |
	                            5 |  2  |
	                               -----
	which is normally rendered with the call
	
	   DrawElements(TRIANGLES, 6, UNSIGNED_BYTE, &indices).
	
	Now consider the case where the vertices you want to draw are not at
	the start of a vertex array but are instead located at offset 100
	into a larger array:
	
	       vertices2             indices2
	       ----------             -----
	          ....             0 | 100 |
	  100 | (-1,  1) |         1 | 101 |
	  101 | (-1, -1) |         2 | 102 |
	  102 | ( 1, -1) |         3 | 103 |
	  103 | ( 1,  1) |         4 | 100 |
	          ....             5 | 102 |
	       ----------             -----
	
	The typical choices for rendering this are to rebind your vertex
	attributes with an additional offset of 100*stride, or to create an
	new array of indices (as indices2 in the example). However both
	rebinding vertex attributes and rebuilding index arrays can be quite
	costly activities.
	
	With the new drawing commands introduced by this extension you can
	instead draw using vertices2 and the new draw call:
	
	   DrawElementsBaseVertex(TRIANGLES, 6, UNSIGNED_BYTE, &indices, 100)

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/draw_elements_base_vertex.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.ARB.draw_elements_base_vertex import *
from OpenGL.raw.GL.ARB.draw_elements_base_vertex import _EXTENSION_NAME

def glInitDrawElementsBaseVertexARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawElementsBaseVertex.indices size not checked against 'count,type'
glDrawElementsBaseVertex= wrapper.wrapper(glDrawElementsBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glDrawRangeElementsBaseVertex.indices size not checked against 'count,type'
glDrawRangeElementsBaseVertex= wrapper.wrapper(glDrawRangeElementsBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glDrawElementsInstancedBaseVertex.indices size not checked against 'count,type'
glDrawElementsInstancedBaseVertex= wrapper.wrapper(glDrawElementsInstancedBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glMultiDrawElementsBaseVertex.count size not checked against 'drawcount'
# INPUT glMultiDrawElementsBaseVertex.indices size not checked against 'drawcount'
# INPUT glMultiDrawElementsBaseVertex.basevertex size not checked against 'drawcount'
glMultiDrawElementsBaseVertex= wrapper.wrapper(glMultiDrawElementsBaseVertex).setInputArraySize(
    'count', None
).setInputArraySize(
    'indices', None
).setInputArraySize(
    'basevertex', None
)
### END AUTOGENERATED SECTION