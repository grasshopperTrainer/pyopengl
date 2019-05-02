from prohopper.tools.hlist import *
from prohopper.tools.rectangle import *
from prohopper.tools.point_tools import *


class trans(Primitive):

    def __init__(self):
        pass


@cal_manyitems
def trans_point(points: Hlist, source: Rect, target: Rect):
    sourcev = source.get_vertex()
    targetv = source.get_vertex()
    print_compared_data(sourcev, targetv)
    # print(type(points),type(source),type(target))
