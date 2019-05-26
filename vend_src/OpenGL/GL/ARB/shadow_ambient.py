'''OpenGL extension ARB.shadow_ambient

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.shadow_ambient to provide a more
Python-friendly API

Overview (from the spec)
	
	This is based on the GL_SGIX_shadow_ambient extension and is layered
	upon the GL_ARB_shadow extension.
	
	Basically, this extension allows the user to specify the texture
	value to use when the texture compare function fails.  Normally
	this value is zero.  By allowing an arbitrary value we can get
	functionality which otherwise requires an advanced texture
	combine extension (such as GL_NV_register_combiners) and multiple
	texture units.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/shadow_ambient.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.shadow_ambient import *
from OpenGL.raw.GL.ARB.shadow_ambient import _EXTENSION_NAME

def glInitShadowAmbientARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION