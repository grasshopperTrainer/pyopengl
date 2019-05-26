'''OpenGL extension SGIS.blended_overlay

This module customises the behaviour of the 
OpenGL.raw.GLX.SGIS.blended_overlay to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension augments the set of transparency types for GLX
	visuals (defined by the EXT_visual_info GLX extension).  A new
	transparency type designated BLENDED_RGBA_SGIS is defined for
	overlay windows supporting an alpha color component.  Instead of
	using a particular transparent pixel or color value to indicate
	transparency, a window created with a BLENDED_RGBA_SGIS
	transparency type visual blends with the lower frame buffer layers
	based on the overlay window's per-pixel alpha component.
	
	The overlay blend function is:
	
	  if ( Cu is color index pixel type ) then
	
	    if ( Ao > 0.0 ) then
	      Cd = Co    /* Non-zero overlay alpha simply uses overlay color */
	    else
	      Cd = Cu    /* Note: later CI cmap turns Cd index into true color */
	    endif
	
	  else    /* Cu is an RGBA, RGB, L, or LA pixel type */
	
	    /* blend overlay color with normal color based on overlay alpha */
	    Cd = Co * (Ao,Ao,Ao,Ao) + Cu * ( (1,1,1,1) - (Ao,Ao,Ao,Ao) )
	
	  endif
	
	where Cd is the resulting displayed color.  Co is the RGBA
	quadruplet for the overlay RGBA parts of the overlay window
	pixel.  Ao is the alpha component for the overlay alpha component
	of the overlay window pixel.  Cu is the RGBA quadruplet for the
	RGBA parts of the displayed pixel if no overlay where present
	in the overlay window's layer (or any higher level).  Think of Cu
	as the displayable color "under" the BLENDED_RGBA_SGIS overlay
	pixel.
	
	In the case of extended range frame buffer formats, the overlay
	blend function is applied post-clamping to the [0,1] range.
	
	Here are some of the uses for blended RGBA overlays:
	
	  Render antialiased lines, points, and polygons in the overlays
	  with GL_LINE_SMOOTH, GL_POINT_SMOOTH, and GL_POLYGON_SMOOTH.
	
	  Alpha blended antiliasing could be used on the overlay boundaries
	  of overlay control panels and boat hulls.
	
	  Clean blending of overlaid mattes for live video.  Live video
	  stream could be overlaid by computer generated overlaid
	  graphics.
	
	  Swank user interface support for sweeping out irregular screen
	  regions by painiting the region in the overlay with a fractional
	  alpha to blend the sweeped region with some constant color in the
	  overlay.
	
	  Swank brush shapes for 3D painting that let you see the blended
	  pixels underneather the overlay brush shape.
	
	  Really smooth (ie, subpixel positioned), full-color, antialiased
	  cursors (application drawn into a blended RGBA overlay).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIS/blended_overlay.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLX import _types, _glgets
from OpenGL.raw.GLX.SGIS.blended_overlay import *
from OpenGL.raw.GLX.SGIS.blended_overlay import _EXTENSION_NAME

def glInitBlendedOverlaySGIS():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION