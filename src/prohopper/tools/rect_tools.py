import numpy as np
# from tools import *
from primitives import *
import line_tools as line
import trans_tools as trans


def con_center(center: Point, sizex, sizey=None):
    if sizey is None:
        sizey = sizex
    x = sizex / 2
    y = sizey / 2

    p1 = trans.move(center, Vector(-x, y))
    p2 = trans.move(center, Vector(-x, -y))
    p3 = trans.move(center, Vector(x, -y))
    p4 = trans.move(center, Vector(x, y))
    return Rect(p1, p2, p3, p4)


def pointRectPerimiter(point: Point, rect: Rect):
    vecy = rect.segments[0].F
    vecx = rect.segments[1]
    px = line.pointLinePerimeter(point, vecx)
    py = line.pointLinePerimeter(point, vecy)
    return Point(px, py)


def rectPerimiterPoint(rect: Rect, perimeter: Point):
    segments = rect.segments
    # print(segments[1],segments[0],perimeter.y)
    x = segments[1].V * perimeter.x
    y = segments[0].F.V * perimeter.y
    v = x + y
    point = rect.vertex[1] + v
    return point
