from .primitives import *
import numpy as np
from ..tools import vector,trans, matrix

def plane_from_vector_point(x_axis:Vector, point:Point, origin:Point = Point(0,0,0)):
    if not isinstance(point, (Point, Vector)):
        raise TypeError
    if not isinstance(x_axis, Vector):
        raise TypeError
    if not isinstance(origin, Point):
        raise

    # first find two angles
    # need to apply transformations and then reverse it?
    x_axis = Vector(100,100,100)
    obj = np.hstack((x_axis.raw, point.raw))
    # TODO is this the best way?
    x,y,z = x_axis.xyz
    xy = vector.project_on_xyplane(x_axis)
    # angle1
    quarter = None
    if xy.y >= 0:
        if xy.x >= 0: # vector is in first quarter
            quarter = 0
        else:
            quarter = 1
    else:
        if xy.x >=0:
            quarter = 3
        else:
            quarter = 2

    rotation_z = np.arccos(xy.x/xy.length)
    if quarter == 0 or quarter == 1:
        rotation_z_matrix = matrix.rotation_z(rotation_z)
        # seeing at direction from origin rotation goes clockwise so...
        # need to negative
        obj = matrix.rotation_z(-rotation_z).raw.dot(obj)
    if quarter == 2 or quarter == 3:
        rotation_z_matrix = matrix.rotation_z(-rotation_z)
        obj = matrix.rotation_z(rotation_z).raw.dot(obj)

    # angle2
    # x_axis already projected on xz plane so
    xz = Vector().from_raw(obj[:4,[0]])
    rotation_y = np.arccos(xz.x/xz.length)
    if xz.x >= 0:
        if xz.z >= 0:
            quarter = 2
        else:
            quarter = 3
    else:
        if xz.z >= 0:
            quarter = 0
        else:
            quarter = 1
    if quarter == 0 or quarter == 1:
        rotation_y_matrix = matrix.rotation_y(rotation_y)
        obj = matrix.rotation_y(-rotation_y).raw.dot(obj)
    else:
        rotation_y_matrix = matrix.rotation_y(-rotation_y)
        obj = matrix.rotation_y(rotation_y).raw.dot(obj)

    # angle 3
    # need to find with second point
    yz = obj[:3,1]
    yz[0] = 0
    yz = Vector(*yz)
    rotation_x = np.arccos(yz.y/yz.length)
    if yz.z >= 0:
        if yz.y >= 0:
            quarter = 0
        else:
            quarter = 1
    else:
        if yz.y >= 0:
            quarter = 3
        else:
            quarter = 2
    if quarter == 0 or quarter == 1:
        rotation_x_matrix = matrix.rotation_x(rotation_x)
        obj = matrix.rotation_x(-rotation_x).raw.dot(obj)
    else:
        rotation_x_matrix = matrix.rotation_x(-rotation_x)
        obj = matrix.rotation_x(rotation_x).raw.dot(obj)

    # transformation info collected
    rotations = rotation_z_matrix, rotation_y_matrix, rotation_x_matrix
    z = trans.transform(Vector(0,0,1),*rotations)
    exit()