'''OpenGL extension APPLE.texture_range

This module customises the behaviour of the 
OpenGL.raw.GL.APPLE.texture_range to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a method to specify the range of client address
	space that may be used by a texture.  In general, the storage size of a
	texture may be easily determined by the texture's data type and geometry.
	However, driver optimizations may be realized if an extended address
	range is specified to encompass the storage of multiple textures, or to
	encompass potential future changes in the size of a texture.  A typical
	usage of this extension is to specify an identical address range for
	several textures in a particular working set that encompasses the storage
	of all the textures in the set.  This allows the driver to make a single
	memory mapping for all of the textures.
	
	Further, a mechanism is provided to allow the application to give the GL
	driver a hint regarding the storage requirements of the texture data.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/APPLE/texture_range.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.APPLE.texture_range import *
from OpenGL.raw.GL.APPLE.texture_range import _EXTENSION_NAME

def glInitTextureRangeAPPLE():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glTextureRangeAPPLE.pointer size not checked against length
glTextureRangeAPPLE= wrapper.wrapper(glTextureRangeAPPLE).setInputArraySize(
    'pointer', None
)
glGetTexParameterPointervAPPLE= wrapper.wrapper(glGetTexParameterPointervAPPLE).setOutput(
    'params',size=(1,),orPassIn=True
)
### END AUTOGENERATED SECTION