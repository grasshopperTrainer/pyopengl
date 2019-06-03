'''OpenGL extension MESA.drm_image

This module customises the behaviour of the 
OpenGL.raw.EGL.MESA.drm_image to provide a more
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/MESA/drm_image.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.EGL import _types, _glgets
from OpenGL.raw.EGL.MESA.drm_image import *
from OpenGL.raw.EGL.MESA.drm_image import _EXTENSION_NAME

def glInitDrmImageMESA():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION