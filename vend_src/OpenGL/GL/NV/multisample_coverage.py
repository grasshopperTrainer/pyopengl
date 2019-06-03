'''OpenGL extension NV.multisample_coverage

This module customises the behaviour of the 
OpenGL.raw.GL.NV.multisample_coverage to provide a more
Python-friendly API

Overview (from the spec)
	
	The ARB_multisample extension provides a mechanism for antialiasing
	primitives.  This mechanism allows an application to request an
	additional buffer, the multisample buffer, that is added to the
	framebuffer.  An application can request the number of samples per
	fragment that are stored in the multisample buffer.  Rendering 
	proceeds by writing color, depth, and stencil values for each 
	sample to the multisample buffer.  The results are automatically
	resolved to a single displayable color each time a pixel is 
	updated.
	
	Coverage Sample Anti-Aliasing (CSAA) is an extension to multisample
	antialiasing.  The technique separates "samples" into two types of
	samples.  "Color samples" are samples with color, depth, and 
	stencil information stored in the multisample buffer.  "Coverage
	samples" include both color samples and additional samples that only
	provide pixel coverage information.
	
	This extension follows the example of the
	NV_framebuffer_multisample_coverage extension, which adds CSAA
	support for framebuffer objects.  The base description of 
	multisample rendering is written in terms of coverage samples and
	color samples.  The windows system notion of "samples"
	(SAMPLES_ARB) is layered on top of coverage and color samples.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/multisample_coverage.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.multisample_coverage import *
from OpenGL.raw.GL.NV.multisample_coverage import _EXTENSION_NAME

def glInitMultisampleCoverageNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION