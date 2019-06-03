'''OpenGL extension NV.explicit_multisample

This module customises the behaviour of the 
OpenGL.raw.GL.NV.explicit_multisample to provide a more
Python-friendly API

Overview (from the spec)
	
	In traditional multisample specs, the API only allows access to the samples
	indirectly through methods such as coverage values and downsampled
	readbacks. NV_explicit_multisample adds a set of new capabilities to allow
	more precise control over the use of multisamples. Specifically, it adds:
	
	 * A query in the API to query the location of samples within the pixel
	
	 * An explicit control for the multisample sample mask to augment the
	   control provided by SampleCoverage
	
	 * A new texture target to wrap a renderbuffer and allow a restricted class
	   of accesses to the samples
	
	 * The ability to fetch a specific sample from a multisampled texture from
	   within a shader
	
	 * A program option to enable the new behavior

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/explicit_multisample.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.NV.explicit_multisample import *
from OpenGL.raw.GL.NV.explicit_multisample import _EXTENSION_NAME

def glInitExplicitMultisampleNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetMultisamplefvNV= wrapper.wrapper(glGetMultisamplefvNV).setOutput(
    'val',size=(2,),orPassIn=True
)
### END AUTOGENERATED SECTION