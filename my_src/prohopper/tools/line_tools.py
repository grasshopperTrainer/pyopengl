from .primitives import *
import math


def perpendicularP(point: Point, line: Line):
    return line(pointLinePerimeter(point, line))


def pointLinePerimeter(point: Point, line: Line):
    a = Line(point, line.end).length
    b = Line(point, line.start).length
    c = line.length
    x = (b * b - a * a + c * c) / (2 * c)
    p = x / c
    return p


def flip(line: Line):
    return Line(line.end, line.start)
