'''OpenGL extension AMD.shader_stencil_export

This module customises the behaviour of the 
OpenGL.raw.GL.AMD.shader_stencil_export to provide a more
Python-friendly API

Overview (from the spec)
	
	In OpenGL, the stencil test is a powerful mechanism to selectively discard
	fragments based on the content of the stencil buffer. However, facilites
	to update the content of the stencil buffer are limited to operations such
	as incrementing the existing value, or overwriting with a fixed reference
	value.
	
	This extension provides a mechanism whereby a shader may generate the
	stencil reference value per invocation. When stencil testing is enabled,
	this allows the test to be performed against the value generated in the
	shader. When the stencil operation is set to GL_REPLACE, this allows a
	value generated in the shader to be written to the stencil buffer directly.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/AMD/shader_stencil_export.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.AMD.shader_stencil_export import *
from OpenGL.raw.GL.AMD.shader_stencil_export import _EXTENSION_NAME

def glInitShaderStencilExportAMD():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION