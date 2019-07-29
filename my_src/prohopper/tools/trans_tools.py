import numpy as np
import copy
# from tools import *
from ..tools import matrix_tools as matrix
from .primitives import *
from ..tools import tlist_tools as tlist
from ..tools import vector_tools as vector


# @tlist.calitem
def move(vec: Vector, geometry:Geometry):
    x = matrix.translation(vec)
    return transform(geometry, x)

@tlist.calitem
def test(x, y):
    print(x, y)
    pass


def transform(geometry:Geometry, *matrix:Matrix):
    r = geometry.raw
    for m in reversed(matrix):
        r = m.raw.dot(r)
    return geometry.__class__().from_raw(r)

@tlist.calitem
def rect_mapping(geometry: Geometry, source: Rect, target: Rect):
    source_v = source.vertex()
    target_v = target.vertex()
    m_trans = matrix.translation(vector.con2pt(source_v[0], target_v[0]))
    m_rotate = None
    m_scale = None
    m_sheer = None

    # t = target()*np.invert(source())
    # print(t)
    # vectors = vector.con2pt(source.vertex(),target.vertex())
    # average = vector.average(vectors)

    pass
def rotate_around_axis(geometry:Geometry, axis, angle, radian=False):
    pass

def rotate_around_x(geometry:Geometry, angle, degree=False, ):
    x = matrix.rotation_x(angle, degree)
    return transform(geometry,x)

def rotate_around_y(geometry:Geometry, angle, degree=False):
    x = matrix.rotation_y(angle, degree)
    return transform(geometry,x)

def rotate_around_z(geometry:Vector, angle, degree=False):
    x = matrix.rotation_z(angle, degree)
    return transform(geometry,x)

