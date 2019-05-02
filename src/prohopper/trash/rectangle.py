from primitives import *
from prohopper.tools.hlist import *
from prohopper.tools.point_tools import *
from prohopper.tools.domain import *


class Rect(Primitive):

    # def __new__(cls, *args, **kwargs):
    #
    #     condition1 = len(args) is 4
    #     condition2 = sum([isinstance(i, list) for i in args]) is 4
    #
    #     if not(condition1):
    #         print(f'{__class__} :\n'
    #               f'input should be 4 lists\n'
    #               f"can't form an instance of {__class__}")
    #         return None
    #
    #     if not(condition2):
    #         print(f'{__class__} :\n'
    #               f'input should be four lists'
    #               f"can't form an instance of {__class__}")
    #         return None
    #
    #     if condition1 and condition2:
    #         return super().__new__(cls)

    def __init__(self, lt: Point = None, ld: Point = None, rb: Point = None, rt: Point = None):
        # for nothing make size2 box
        if lt is None:
            lt = Point(-1, 1, 0)
        if ld is None:
            ld = Point(-1, -1, 0)
        if rb is None:
            rb = Point(1, -1, 0)
        if rt is None:
            rt = Point(1, 1, 0)

        self.vertex = Hlist(lt, ld, rb, rt)

    def __getitem__(self, item):
        return self.vertex[item]

    def get_aslist(self):
        return self.vertex

    def get_center(self) -> Hlist:
        return average(self.vertex)

    def get_aslist_tristripe(self):
        new_list = []
        new_list.append(self.lt)
        new_list.append(self.ld)
        new_list.append(self.rt)
        new_list.append(self.rb)

        return new_list

    def get_vertex(self) -> Hlist(Point):
        return self.vertex

    def get_widthheight(self) -> Hlist:
        # a = self.vertex[0]
        # b = self.vertex[1]
        # c = self.vertex[2]
        xyz = decon_point(self.vertex)
        xs = xyz[0]
        ys = xyz[1]
        width = xs[2] - xs[1]
        height = ys[0] - ys[1]

        return list_merge(width, height)

    def __str__(self):
        center = average(self.vertex).get_data()[0]
        return str(center)


@cal_manyitems
def rect_con_center(center: Hlist, x: Hlist, y: Hlist) -> Hlist:
    hfx = x / 2
    hfy = y / 2
    lt = Point(center.x - hfx, center.y + hfy, center.z)
    ld = Point(center.x - hfx, center.y - hfy, center.z)
    rb = Point(center.x + hfx, center.y - hfy, center.z)
    rt = Point(center.x + hfx, center.y + hfy, center.z)

    return Rect(lt, ld, rb, rt)


def rect_con_domain():
    pass


@cal_manyitems
def rect_vertex(rect: Rect):
    return rect.get_vertex()


def rect_decon(rects: Hlist, *select_op: int):
    """
    return rectangle's center, width and height as domain
    :param select_op: output to get return
    :return: (center:Point, extend width:Domain, extend height:Domain)
    """

    # how should i for multiple outputs?
    @cal_manyitems
    def centers(rect: Rect) -> Hlist:
        return rect.get_center()

    @cal_manyitems
    def xs(rect: Rect):
        v = rect.get_vertex()
        return decon_point(v, 0)

    @cal_manyitems
    def ys(rect: Rect):
        v = rect.get_vertex()
        return decon_point(v, 1)

    if len(select_op) is 0:
        select_op = [0, 1, 2]

    result = []
    if 0 in select_op:
        result.append(centers(rects))
    if 1 in select_op:
        result.append(xs(rects))
    if 2 in select_op:
        result.append(ys(rects))

    return tuple(result)
