'''OpenGL extension ATI.envmap_bumpmap

This module customises the behaviour of the 
OpenGL.raw.GL.ATI.envmap_bumpmap to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension adds environment mapped bump mapping (EMBM) to the GL.
	The method exposed by this extension is to use a dependent texture
	read on a bumpmap (du,dv) texture to offset the texture coordinates
	read into a map on another texture unit.  This (du,dv) offset is also 
	rotated through a user-specified rotation matrix to get the texture 
	coordinates into the appropriate space.
	
	A new texture format is introduced in order for specifying the (du,dv)
	bumpmap texture.  This map represents -1 <= du,dv <= 1 offsets to
	be applied to the texture coordinates used to read into the base
	map.  Additionally, the (du,dv) offsets are transformed by a rotation
	matrix that this extension allows the user to specify.  Further, a 
	new color operation is added to EXT_texture_env_combine to specify 
	both that bumpmapping is enabled and which texture unit to apply 
	the bump offset to.  

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ATI/envmap_bumpmap.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.ATI.envmap_bumpmap import *
from OpenGL.raw.GL.ATI.envmap_bumpmap import _EXTENSION_NAME

def glInitEnvmapBumpmapATI():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glTexBumpParameterivATI.param size not checked against 'pname'
glTexBumpParameterivATI= wrapper.wrapper(glTexBumpParameterivATI).setInputArraySize(
    'param', None
)
# INPUT glTexBumpParameterfvATI.param size not checked against 'pname'
glTexBumpParameterfvATI= wrapper.wrapper(glTexBumpParameterfvATI).setInputArraySize(
    'param', None
)
glGetTexBumpParameterivATI= wrapper.wrapper(glGetTexBumpParameterivATI).setOutput(
    'param',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexBumpParameterfvATI= wrapper.wrapper(glGetTexBumpParameterfvATI).setOutput(
    'param',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION