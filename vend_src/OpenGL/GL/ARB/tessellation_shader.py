'''OpenGL extension ARB.tessellation_shader

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.tessellation_shader to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension introduces new tessellation stages and two new shader types
	to the OpenGL primitive processing pipeline.  These pipeline stages
	operate on a new basic primitive type, called a patch.  A patch consists
	of a fixed-size collection of vertices, each with per-vertex attributes,
	plus a number of associated per-patch attributes.  Tessellation control
	shaders transform an input patch specified by the application, computing
	per-vertex and per-patch attributes for a new output patch.  A
	fixed-function tessellation primitive generator subdivides the patch, and
	tessellation evaluation shaders are used to compute the position and
	attributes of each vertex produced by the tessellator.
	
	When tessellation is active, it begins by running the optional
	tessellation control shader.  This shader consumes an input patch and
	produces a new fixed-size output patch.  The output patch consists of an
	array of vertices, and a set of per-patch attributes.  The per-patch
	attributes include tessellation levels that control how finely the patch
	will be tessellated.  For each patch processed, multiple tessellation
	control shader invocations are performed -- one per output patch vertex.
	Each tessellation control shader invocation writes all the attributes of
	its corresponding output patch vertex.  A tessellation control shader may
	also read the per-vertex outputs of other tessellation control shader
	invocations, as well as read and write shared per-patch outputs.  The
	tessellation control shader invocations for a single patch effectively run
	as a group.  A built-in barrier() function is provided to allow
	synchronization points where no shader invocation will continue until all
	shader invocations have reached the barrier.
	
	The tessellation primitive generator then decomposes a patch into a new
	set of primitives using the tessellation levels to determine how finely
	tessellated the output should be.  The primitive generator begins with
	either a triangle or a quad, and splits each outer edge of the primitive
	into a number of segments approximately equal to the corresponding element
	of the outer tessellation level array.  The interior of the primitive is
	tessellated according to elements of the inner tessellation level array.
	The primitive generator has three modes:  "triangles" and "quads" split a
	triangular or quad-shaped patch into a set of triangles that cover the
	original patch; "isolines" splits a quad-shaped patch into a set of line
	strips running across the patch horizontally.  Each vertex generated by
	the tessellation primitive generator is assigned a (u,v) or (u,v,w)
	coordinate indicating its relative location in the subdivided triangle or
	quad.
	
	For each vertex produced by the tessellation primitive generator, the
	tessellation evaluation shader is run to compute its position and other
	attributes of the vertex, using its (u,v) or (u,v,w) coordinate.  When
	computing final vertex attributes, the tessellation evaluation shader can
	also read the attributes of any of the vertices of the patch written by
	the tessellation control shader.  Tessellation evaluation shader
	invocations are completely independent, although all invocations for a
	single patch share the same collection of input vertices and per-patch
	attributes.
	
	The tessellator operates on vertices after they have been transformed by a
	vertex shader.  The primitives generated by the tessellator are passed
	further down the OpenGL pipeline, where they can be used as inputs to
	geometry shaders, transform feedback, and the rasterizer.
	
	The tessellation control and evaluation shaders are both optional.  If
	neither shader type is present, the tessellation stage has no effect.  If
	no tessellation control shader is present, the input patch provided by the
	application is passed directly to the tessellation primitive generator,
	and a set of default tessellation level parameters is used to control
	primitive generation.  In this extension, patches may not be passed beyond
	the tessellation evaluation shader, and an error is generated if an
	application provides patches and the current program object contains no
	tessellation evaluation shader.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/tessellation_shader.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.ARB.tessellation_shader import *
from OpenGL.raw.GL.ARB.tessellation_shader import _EXTENSION_NAME

def glInitTessellationShaderARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glPatchParameterfv.values size not checked against 'pname'
glPatchParameterfv= wrapper.wrapper(glPatchParameterfv).setInputArraySize(
    'values', None
)
### END AUTOGENERATED SECTION