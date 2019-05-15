'''OpenGL extension SGI.color_table

This module customises the behaviour of the 
OpenGL.raw.GL.SGI.color_table to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension defines a new RGBA-format color lookup mechanism.  It does
	not replace the color lookups defined by the GL Specification, but rather
	provides additional lookup capabilities with different operation.  The key
	difference is that the new lookup tables are treated as 1-dimensional images
	with internal formats, like texture images and convolution filter images.
	From this follows the fact that the new tables can operate on a subset of
	the components of passing pixel groups.  For example, a table with internal
	format ALPHA modifies only the A component of each pixel group, leaving the
	R, G, and B components unmodified.
	
	If EXT_copy_texture is implemented, this extension also defines methods to
	initialize the color lookup tables from the framebuffer, in addition to the
	standard memory source mechanisms.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGI/color_table.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL import _glgets
from OpenGL.raw.GL.SGI.color_table import *
from OpenGL.raw.GL.SGI.color_table import _EXTENSION_NAME

def glInitColorTableSGI():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glColorTableSGI.table size not checked against 'format,type,width'
glColorTableSGI= wrapper.wrapper(glColorTableSGI).setInputArraySize(
    'table', None
)
# INPUT glColorTableParameterfvSGI.params size not checked against 'pname'
glColorTableParameterfvSGI= wrapper.wrapper(glColorTableParameterfvSGI).setInputArraySize(
    'params', None
)
# INPUT glColorTableParameterivSGI.params size not checked against 'pname'
glColorTableParameterivSGI= wrapper.wrapper(glColorTableParameterivSGI).setInputArraySize(
    'params', None
)
# OUTPUT glGetColorTableSGI.table COMPSIZE(target,format,type) 
glGetColorTableParameterfvSGI= wrapper.wrapper(glGetColorTableParameterfvSGI).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetColorTableParameterivSGI= wrapper.wrapper(glGetColorTableParameterivSGI).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION