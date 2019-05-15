'''OpenGL extension APPLE.object_purgeable

This module customises the behaviour of the 
OpenGL.raw.GL.APPLE.object_purgeable to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides the ability to mark the storage of OpenGL
	objects as "purgeable".
	
	Many of today's modern virtual memory systems include the concept of
	purgeability in order to avoid unnecessary paging when the object
	contents are no longer needed.  In OpenGL, objects such as textures,
	vertex buffers, pixel buffers, and renderbuffers all have
	significant storage requirements.  By default, the OpenGL is
	required to preserve the contents of these objects regardless of
	system resource stress, such as vram shortage or physical memory
	shortage.  Often this is accomplished by temporarily paging the
	contents of objects that are not currently needed to some kind of
	secondary storage area.  This paging operation can be an unnecessary
	computational expense in the cases where the data is not going to be
	used again or where the content can be reproduced by the application
	with less expense than the paging operation would require.
	
	This extension defines a mechanism for the application to mark the
	storage of OpenGL objects as "purgeable" in order to influence these
	paging operations.  The application can further control the
	semantics of making object storage "purgeable" with two options
	("volatile" and "released") and "unpurgeable" with two options
	("undefined" and "retained")
	
	Applications that use this extension will typically follow one of
	two operational models.  The typical model for most applications is
	to mark an object storage as "purgeable" with the "volatile" option,
	and then later mark the storage as "unpurgeable" with the "retained"
	option. When this happens, the application may or may not need to
	respecify the object contents, depending on the whether the object
	storage was actually released.  The application can find out whether
	the storage was released by examining the return value of the
	function which marks the storage as "unpurgeable".  This model is
	useful when the application does not know at the time it marks the
	object storage as "purgeable" whether it will later need those
	contents to be valid.
	
	Another operational model is for an application to mark the storage
	for an object as "purgeable" with the "released" option, and then
	later mark the object "unpurgeable" with the "undefined" option.  In
	this latter model, the application intends to unconditionally reload
	the object contents later on, and so it tells the GL that it is okay
	if the contents are "undefined" when the storage is re-allocated.
	
	Note that in both models, it is possible for the contents to become
	undefined since they could have actually been purged from the system
	in either case.  The various options are still useful, however,
	since they give more information to the GL about what the
	application expects to happen and the GL can use this information to
	make better predictions about which paging choices will be more
	efficient.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/APPLE/object_purgeable.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.APPLE.object_purgeable import *
from OpenGL.raw.GL.APPLE.object_purgeable import _EXTENSION_NAME

def glInitObjectPurgeableAPPLE():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetObjectParameterivAPPLE= wrapper.wrapper(glGetObjectParameterivAPPLE).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION