import numpy as np
import copy
# from tools import *
import matrix_tools as matrix
from primitives import *
import tlist_tools as tlist
import vector_tools as vector


@tlist.calitem
def move(obj: Geometry, vec: Vector):
    # new = copy.deepcopy(obj)
    transform(obj, matrix.translation(vec))

    return obj


@tlist.calitem
def test(x, y):
    print(x, y)
    pass


def transform(geometry: Geometry, t: Transformation):
    newarr = np.dot(t, geometry())
    geometry.set_data(newarr)


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
