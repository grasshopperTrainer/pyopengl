'''OpenGL extension NV.shader_atomic_float

This module customises the behaviour of the 
OpenGL.raw.GL.NV.shader_atomic_float to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension provides GLSL built-in functions and assembly opcodes
	allowing shaders to perform atomic read-modify-write operations to buffer
	or texture memory with floating-point parts.  The set of atomic
	operations provided by this extension is limited to adds and exchanges.
	Providing atomic add support allows shaders to atomically accumulate the
	sum of floating-point values into buffer or texture memory across multiple
	(possibly concurrent) shader invocations.
	
	This extension provides GLSL support for atomics targeting image uniforms
	(if GLSL 4.20, ARB_shader_image_load_store, or EXT_shader_image_load_store
	is supported) or floating-point pointers (if NV_gpu_shader5 is supported).
	Additionally, assembly opcodes for these operations is also provided if
	NV_gpu_program5 is supported.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/shader_atomic_float.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.shader_atomic_float import *
from OpenGL.raw.GL.NV.shader_atomic_float import _EXTENSION_NAME

def glInitShaderAtomicFloatNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION