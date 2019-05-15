'''OpenGL extension ARB.vertex_attrib_64bit

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.vertex_attrib_64bit to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides OpenGL shading language support for vertex shader
	inputs with 64-bit floating-point components and OpenGL API support for
	specifying the value of those inputs using vertex array or immediate mode
	entry points.  This builds on the support for general-purpose support for
	64-bit floating-point values in the ARB_gpu_shader_fp64 extension.
	
	This extension provides a new class of vertex attribute functions,
	beginning with "VertexAttribL" ("L" for "long"), that can be used to
	specify attributes with 64-bit floating-point components.  This extension
	provides no automatic type conversion between attribute and shader
	variables; single-precision attributes are not automatically converted to
	double-precision or vice versa.  For shader variables with 64-bit
	component types, the "VertexAttribL" functions must be used to specify
	attribute values.  For other shader variables, the "VertexAttribL"
	functions must not be used.  If a vertex attribute is specified using the
	wrong attribute function, the values of the corresponding shader input are
	undefined.  This approach requiring matching types is identical to that
	used for the "VertexAttribI" functions provided by OpenGL 3.0 and the
	EXT_gpu_shader4 extension.
	
	Additionally, some vertex shader inputs using the wider 64-bit components
	may count double against the implementation-dependent limit on the number
	of vertex shader attribute vectors.  A 64-bit scalar or a two-component
	vector consumes only a single generic vertex attribute; three- and
	four-component "long" may count as two.  This approach is similar to the
	one used in the current GL where matrix attributes consume multiple
	attributes.
	
	Note that 64-bit generic vertex attributes were nominally supported
	beginning with the introduction of vertex shaders in OpenGL 2.0.  However,
	the OpenGL Shading Language at the time had no support for 64-bit data
	types, so any such values were automatically converted to 32-bit.
	
	Support for 64-bit floating-point vertex attributes in this extension can
	be combined with other extensions.  In particular, this extension provides
	an entry point that can be used with EXT_direct_state_access to directly
	set state for any vertex array object.  Also, the related
	NV_vertex_attrib_integer_64bit extension provides an entry point to
	specify bindless vertex attribute arrays with 64-bit components, integer
	or floating-point.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/vertex_attrib_64bit.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.ARB.vertex_attrib_64bit import *
from OpenGL.raw.GL.ARB.vertex_attrib_64bit import _EXTENSION_NAME

def glInitVertexAttrib64BitARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glVertexAttribL1dv= wrapper.wrapper(glVertexAttribL1dv).setInputArraySize(
    'v', 1
)
glVertexAttribL2dv= wrapper.wrapper(glVertexAttribL2dv).setInputArraySize(
    'v', 2
)
glVertexAttribL3dv= wrapper.wrapper(glVertexAttribL3dv).setInputArraySize(
    'v', 3
)
glVertexAttribL4dv= wrapper.wrapper(glVertexAttribL4dv).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribLPointer.pointer size not checked against size
glVertexAttribLPointer= wrapper.wrapper(glVertexAttribLPointer).setInputArraySize(
    'pointer', None
)
glGetVertexAttribLdv= wrapper.wrapper(glGetVertexAttribLdv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION