import numpy as np
import copy
from .primitives import *
from ..tools import rect_tools as rect

def remap(value, source: Domain, target: Domain = None):
    if isinstance(value, Point):
        if isinstance(source, Domain2d) and isinstance(target, Domain2d):
            pass
        else:
            raise TypeError
    else:
        if target is None:
            target = Domain(0, 1)
        coord = (value + source.start) / source.length
        v = target.start + target.length * coord
    return v


def rectangleMorph(geometry, source: Rect, target: Rect):
    if isinstance(source, Rect) and isinstance(target, Rect):
        try:
            vertex = geometry.vertex
            perimeters = [rect.pointRectPerimiter(v, source) for v in vertex]
            mappedV = [rect.rectPerimiterPoint(target, i)() for i in perimeters]
            m = np.concatenate(mappedV, 1)
            return geometry.__class__().bymatrix(m)

        except:
            geometry.printmessage("can't map")
    else:
        geometry.printmessage("source and target sould both be rectangle")
        return None


def condomain2d(ustart, uend, vstart, vend):
    return Domain2d(Domain(ustart, uend), Domain(vstart, vend))
