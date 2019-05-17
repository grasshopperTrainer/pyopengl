'''OpenGL extension SGIX.polynomial_ffd

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.polynomial_ffd to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/polynomial_ffd.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.SGIX.polynomial_ffd import *
from OpenGL.raw.GL.SGIX.polynomial_ffd import _EXTENSION_NAME

def glInitPolynomialFfdSGIX():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDeformationMap3dSGIX.points size not checked against 'target,ustride,uorder,vstride,vorder,wstride,worder'
glDeformationMap3dSGIX= wrapper.wrapper(glDeformationMap3dSGIX).setInputArraySize(
    'points', None
)
# INPUT glDeformationMap3fSGIX.points size not checked against 'target,ustride,uorder,vstride,vorder,wstride,worder'
glDeformationMap3fSGIX= wrapper.wrapper(glDeformationMap3fSGIX).setInputArraySize(
    'points', None
)
### END AUTOGENERATED SECTION