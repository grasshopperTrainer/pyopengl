from primitives import Primitive
from prohopper.tools.hlist import *
import numpy as np


class Point(Primitive):

    # def __new__(cls, *args, **kwargs):
    #     condition1 = len(args) is 3
    #     condition2 = sum([isinstance(i,float) or isinstance(i, int) for i in args]) is 3
    #     if not condition1:
    #         print(f'{__class__} :\n'
    #               f'input should be 3 argument\n'
    #               f"can't form an instance of {__class__}")
    #         return None
    #     if not condition2:
    #         print(f'{__class__} :\n'
    #               f'input should numeric'
    #               f"can't form an instance of {__class__}")
    #         return None
    #
    #     if condition1 and condition2:
    #         return super().__new__(cls)

    def __init__(self, x, y, z):
        # print(x,y,z)
        self.coord = np.array([x, y, z, 1])
        # print('numpy', self.coord)
        self.x = self.coord[0]
        self.y = self.coord[1]
        self.z = self.coord[2]

    def __str__(self):
        x = str(self.coord[0])[:5]
        y = str(self.coord[1])[:5]
        z = str(self.coord[2])[:5]

        return f'[{x}, {y}, {z}]'

    def get_data(self):
        return self.coord
    # def decon(self):
    #     return *self.coord


@cal_manyitems
def con_xyz(x: Hlist, y: Hlist, z: Hlist) -> Hlist:
    """
    construct point by x y z coordinate
    :param x: coordinate x
    :param y: coordinate y
    :param z: coordinate z
    :return: Hlist of Point
    """
    return Point(x, y, z)


@cal_manylists
def average(points: Hlist):
    x = sum([i.x for i in points]) / len(points)
    y = sum([i.y for i in points]) / len(points)
    z = sum([i.z for i in points]) / len(points)
    return Point(x, y, z)


def decon_point(points: Hlist, *select_op: int):
    @cal_manyitems
    def xs(point: Point):
        if isinstance(point, Point):
            return point.x
        else:
            return None

    @cal_manyitems
    def ys(point: Point):
        if isinstance(point, Point):
            return point.y
        else:
            return None

    @cal_manyitems
    def zs(point: Point):
        if isinstance(point, Point):
            return point.z
        else:
            return None

    if len(select_op) is 0:
        select_op = [0, 1, 2]

    result = []
    if 0 in select_op:
        result.append(xs(points))
    if 1 in select_op:
        result.append(ys(points))
    if 2 in select_op:
        result.append(zs(points))
    if len(result) is 1:
        return result[0]
    else:
        return tuple(result)

# x = Hlist(1,2,3,4,5)
# print(x.__class__)
#
# print(isinstance(x,Hlist))
# y = Hlist(0,2)
# z = Hlist(9,9,9,9,9,10)
# a = con_xyz(x,y,z)
# r = decon_point(a,2,1)
#
# k = average(a)
#
# k.print_data()
