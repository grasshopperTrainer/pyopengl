import numpy as np
# from tools import *
import tlist_tools as tlist
from primitives import *


@tlist.calbranch
def average(*vectors: Vector):
    v = [i() for i in vectors]
    pass


@tlist.calitem
def con2pt(start: Point, end: Point):
    newv = Vector()
    newv.set_data(np.subtract(end(), start()))
    return newv
