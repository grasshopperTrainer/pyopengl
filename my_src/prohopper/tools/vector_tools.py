import numpy as np
# from tools import *
from ..tools import tlist_tools as tlist
from .primitives import *


@tlist.calbranch
def average(*vectors: Vector):
    v = [i() for i in vectors]
    pass


@tlist.calitem
def con2pt(start: Point, end: Point):
    newv = Vector()
    newv.set_data(np.subtract(end(), start()))
    return newv


def unit(vector:Vector, ):
    if not isinstance(vector, Vector):
        raise TypeError
    return vector/vector.length

def divide(vector:Vector, v, raw=False):
    pass

def multiply(vector:Vector, v, ):
    if raw:
        return vector.raw*v
    else:
        return vector*v

def amplitude(vector:Vector, amp:Number):
    new_v = vector*(amp/vector.length)
    return new_v

def flip(vector:Vector):
    if not isinstance(vector, Vector):
        raise TypeError
    return Vector().from_raw(vector.raw*[[-1],[-1],[-1],[0]])

def angle_2_vectors(from_vector, to_vector, deegrees=False):
    u1,u2 = unit(from_vector), unit(to_vector)
    cos_value = u1.raw.flatten().dot(u2.raw.flatten())
    angle = np.arccos(cos_value)
    if deegrees:
        return np.degrees(angle)
    else:
        return angle

def project_point_on_vector(point:Point, vector:Vector):
    if not isinstance(point, (Point,Vector)):
        raise TypeError
    if not isinstance(vector, Vector):
        raise TypeError

    angle = angle_2_vectors(point, vector)
    return amplitude(vector, np.cos(angle)*point.length)

def deconstruct(vector:Vector, ):
    on_xy = vector.raw.copy()
    on_xy[2,0] = 0
    on_yz = vector.raw.copy()
    on_yz[0,0] = 0
    on_xz = vector.raw.copy()
    on_xz[1,0] = 0
    return Vector().from_raw(on_xy),Vector().from_raw(on_yz),Vector().from_raw(on_xz)

def project_on_xyplane(vector:Vector, ):
    new = vector.raw.copy()
    new[2,0] = 0
    return Vector().from_raw(new)

def project_on_yzplane(vector:Vector, raw=False):
    new = vector.raw.copy()
    new[0, 0] = 0
    return Vector().from_raw(new)

def project_on_xzplane(vector:Vector, raw=False):
    new = vector.raw.copy()
    new[1, 0] = 0
    return Vector().from_raw(new)