import numpy as np
import copy
from .primitives import *


def translation(vec: Vector):
    if not isinstance(vec,Vector):
        raise TypeError
    matrix = np.eye(4)
    matrix[:3, 3] = vec.xyz
    return Matrix().from_raw(matrix)


def scaling():
    pass

def rotation_x(angle, degrees=False):
    matrix = np.eye(4)
    if degrees:
        angle = np.radians(angle)
    matrix[1] = 0, np.cos(angle), -np.sin(angle), 0
    matrix[2] = 0, np.sin(angle), np.cos(angle), 0

    return Matrix().from_raw(matrix)

def rotation_y(angle, degrees=False):
    matrix = np.eye(4)
    if degrees:
        angle = np.radians(angle)
    matrix[0] = np.cos(angle), 0, np.sin(angle), 0
    matrix[2] = -np.sin(angle), 0, np.cos(angle), 0
    return Matrix().from_raw(matrix)


def rotation_z(angle, degrees=False):
    matrix = np.eye(4)
    if degrees:
        angle = np.radians(angle)
    matrix[0] = np.cos(angle), -np.sin(angle), 0, 0
    matrix[1] = np.sin(angle), np.cos(angle), 0, 0
    return Matrix().from_raw(matrix)

def transform(matrix:Matrix, geometry):
    pass

def transformation_2_planes(from_plane:Plane, to_plane:Plane):

    pass

def combine_matrix(*matrix):
    result = np.eye(4)
    for m in reversed(matrix):
        new_r = m.raw.copy()
        result = new_r.dot(result)
    return Matrix.from_raw(result)
#
# def rotation(x=None, y=None, z=None):
#     if x is None:
#         mx = np.eye(4)
#     else:
#         mx = np.ndarray([[1, 0, 0, 0],
#                          [np.cos(x), -np.sin(x), 0, 0],
#                          [np.sin(x), np.cod(x), 0, 0],
#                          [0, 0, 0, 1]])
#     if y is None:
#         my
#     my = None
#     mz = None
#     np.cos
#
#     pass
#
# def transform(matrix:Matrix, vector:Vector):
#
#     pass
