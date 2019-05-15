import numpy as np
import copy
from .primitives import *


def translation(vector: Vector):
    trans = np.eye(4)
    trans[:3, 3] = vector()[:3, 0]
    return trans


def scaling():
    pass


def rotation_x(radian):
    pass


def rotation_y(radian):
    pass


def rotation_z(radian):
    pass


def rotation(x=None, y=None, z=None):
    if x is None:
        mx = np.eye(4)
    else:
        mx = np.ndarray([[1, 0, 0, 0],
                         [np.cos(x), -np.sin(x), 0, 0],
                         [np.sin(x), np.cod(x), 0, 0],
                         [0, 0, 0, 1]])
    if y is None:
        my
    my = None
    mz = None
    np.cos

    pass
