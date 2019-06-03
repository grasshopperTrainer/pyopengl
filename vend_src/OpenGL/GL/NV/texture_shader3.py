'''OpenGL extension NV.texture_shader3

This module customises the behaviour of the 
OpenGL.raw.GL.NV.texture_shader3 to provide a more
Python-friendly API

Overview (from the spec)
	
	NV_texture_shader3 extends the NV_texture_shader functionality by
	adding several new texture shader operations, extending several
	existing texture shader operations, adding a new HILO8 internal
	format, and adding new and more flexible re-mapping modes for dot
	product and dependent texture shader operations.
	
	See the NV_texture_shader extension for information about the
	texture shader operational model.
	
	The fourteen new texture shader operations are:
	
	<offset textures>
	
	24.  OFFSET_PROJECTIVE_TEXTURE_2D_NV - Transforms the signed (ds,dt)
	     parts of a previous texture unit by a 2x2 floating-point
	     matrix and then uses the result to offset the stage's texture
	     coordinates for a 2D non-projective texture.
	
	25.  OFFSET_PROJECTIVE_TEXTURE_2D_SCALE_NV - Same as above except
	     the magnitude component of the previous texture unit result
	     scales the red, green, and blue parts of the unsigned RGBA
	     texture 2D access.
	
	26.  OFFSET_PROJECTIVE_TEXTURE_RECTANGLE_NV - Similar to
	     OFFSET_TEXTURE_2D_NV except that the texture access is into a
	     rectangular non-projective texture.
	
	27.  OFFSET_PROJECTIVE_TEXTURE_RECTANGLE_SCALE_NV - Similar to
	     OFFSET_PROJECTIVE_TEXTURE_2D_SCALE_NV except that the texture
	     access is into a rectangular non-projective texture.
	
	28.  OFFSET_HILO_TEXTURE_2D_NV - Similar to OFFSET_TEXTURE_2D_NV
	     but uses a (higher-precision) HILO base format texture rather
	     than a DSDT-type base format.
	
	29.  OFFSET_HILO_TEXTURE_RECTANGLE_NV - Similar to
	     OFFSET_TEXTURE_RECTANGLE_NV but uses a (higher-precision)
	     HILO base format texture rather than a DSDT-type base format.
	
	30.  OFFSET_HILO_PROJECTIVE_TEXTURE_2D_NV - Similar to
	     OFFSET_PROJECTIVE_TEXTURE_2D_NV but uses a (higher-precision)
	     HILO base format texture rather than a DSDT-type base format.
	
	31.  OFFSET_HILO_PROJECTIVE_TEXTURE_RECTANGLE_NV - Similar to
	     OFFSET_PROJECTIVE_TEXTURE_RECTANGLE_NV but uses a
	     (higher-precision) HILO base format texture rather than a
	     DSDT-type base format.
	
	     (There are no "offset HILO texture scale" operations because
	     HILO textures have only two parts with no third component
	     for scaling.)
	
	<dependent textures>
	
	32.  DEPENDENT_HILO_TEXTURE_2D_NV - Converts the hi and lo parts
	     of a previous shader HILO result into an (s,t) texture coordinate
	     set to access a 2D non-projective texture.
	
	33.  DEPENDENT_RGB_TEXTURE_3D_NV - Converts the red, green, and
	     blue parts of a previous shader RGBA result into an (s,t,r)
	     texture coordinate set to access a 3D non-projective texture.
	
	34.  DEPENDENT_RGB_TEXTURE_CUBE_MAP_NV - Converts the red, green,
	     and blue parts of a previous shader RGBA result into an
	     (s,t,r) texture coordinate set to access a cube map texture.
	
	<dot product pass through>
	
	35.  DOT_PRODUCT_PASS_THROUGH_NV - Computes a dot product in the
	     manner of the DOT_PRODUCT_NV operation and the result is [0,1]
	     clamped and smeared to generate the texture unit RGBA result.
	
	<dot product textures>
	
	36.  DOT_PRODUCT_TEXTURE_1D_NV - Computes a dot product in the manner
	     of the DOT_PRODUCT_NV operation and uses the result as the s
	     texture coordinate to access a 2D non-projective texture.
	
	<dot product depth replace>
	
	37.  DOT_PRODUCT_AFFINE_DEPTH_REPLACE_NV - Computes a dot product
	     in the manner of the DOT_PRODUCT_NV operation and the result
	     is [0,1] clamped and replaces the fragment's window-space
	     depth value.  The texture unit RGBA result is (0,0,0,0).
	
	Two new internal texture formats have been added: HILO8_NV and
	SIGNED_HILO8_NV.  These texture formats allow HILO textures to be
	stored in half the space; still the filtering for these internal
	texture formats is done with 16-bit precision.
	
	One new unsigned RGBA dot product mapping mode (FORCE_BLUE_TO_ONE_NV)
	forces the blue component to be 1.0 before computing a dot product.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/texture_shader3.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.texture_shader3 import *
from OpenGL.raw.GL.NV.texture_shader3 import _EXTENSION_NAME

def glInitTextureShader3NV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION