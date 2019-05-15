'''Autogenerated by xml_generate script, do not edit!'''
from OpenGL import platform as _p, arrays
# Code generation uses this
from OpenGL.raw.GLES2 import _types as _cs
# End users want this...
from OpenGL.raw.GLES2._types import *
from OpenGL.raw.GLES2 import _errors
from OpenGL.constant import Constant as _C

import ctypes
_EXTENSION_NAME = 'GLES2_EXT_shadow_samplers'
def _f( function ):
    return _p.createFunction( function,_p.PLATFORM.GLES2,'GLES2_EXT_shadow_samplers',error_checker=_errors._error_checker)
GL_COMPARE_REF_TO_TEXTURE_EXT=_C('GL_COMPARE_REF_TO_TEXTURE_EXT',0x884E)
GL_SAMPLER_2D_SHADOW_EXT=_C('GL_SAMPLER_2D_SHADOW_EXT',0x8B62)
GL_TEXTURE_COMPARE_FUNC_EXT=_C('GL_TEXTURE_COMPARE_FUNC_EXT',0x884D)
GL_TEXTURE_COMPARE_MODE_EXT=_C('GL_TEXTURE_COMPARE_MODE_EXT',0x884C)

