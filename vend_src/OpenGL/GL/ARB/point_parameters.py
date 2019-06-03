'''OpenGL extension ARB.point_parameters

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.point_parameters to provide a more
Python-friendly API

Overview (from the spec)
	
	This extension supports additional geometric characteristics of
	points. It can be used to render particles or tiny light sources,
	commonly referred to as "Light points".
	
	The raster brightness of a point is a function of the point area,
	point color, point transparency, and the response of the display's
	electron gun and phosphor. The point area and the point transparency
	are derived from the point size, currently provided with the <size>
	parameter of glPointSize.
	
	The primary motivation is to allow the size of a point to be
	affected by distance attenuation. When distance attenuation has an
	effect, the final point size decreases as the distance of the point
	from the eye increases.
	
	The secondary motivation is a mean to control the mapping from the
	point size to the raster point area and point transparency. This is
	done in order to increase the dynamic range of the raster brightness
	of points. In other words, the alpha component of a point may be
	decreased (and its transparency increased) as its area shrinks below
	a defined threshold.
	
	This extension defines a derived point size to be closely related to
	point brightness. The brightness of a point is given by:
	
	                    1
	    dist_atten(d) = -------------------
	                    a + b * d + c * d^2
	
	    brightness(Pe) = Brightness * dist_atten(|Pe|)
	
	where 'Pe' is the point in eye coordinates, and 'Brightness' is some
	initial value proportional to the square of the size provided with
	PointSize. Here we simplify the raster brightness to be a function
	of the rasterized point area and point transparency.
	
	                brightness(Pe)       brightness(Pe) >= Threshold_Area
	    area(Pe) =
	                Threshold_Area       Otherwise
	
	    factor(Pe) = brightness(Pe)/Threshold_Area
	
	    alpha(Pe) = Alpha * factor(Pe)
	
	where 'Alpha' comes with the point color (possibly modified by
	lighting).
	
	'Threshold_Area' above is in area units. Thus, it is proportional to
	the square of the threshold provided by the programmer through this
	extension.
	
	The new point size derivation method applies to all points, while
	the threshold applies to multisample points only.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/point_parameters.txt
'''
from OpenGL import wrapper
from OpenGL.raw.GL.ARB.point_parameters import *
from OpenGL.raw.GL.ARB.point_parameters import _EXTENSION_NAME

def glInitPointParametersARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glPointParameterfvARB.params size not checked against 'pname'
glPointParameterfvARB= wrapper.wrapper(glPointParameterfvARB).setInputArraySize(
    'params', None
)
### END AUTOGENERATED SECTION

