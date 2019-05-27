# from collections import namedtuple
#
#
#
# a = namedtuple('d', ['g','f','d'])
#
# print(a._fields)
import inspect
attribute_with_name = 10

def a(first, second):
    print(first)
    f = inspect.currentframe().f_back
    f_info = inspect.getframeinfo(f)
    for i in f_info:
        print(i)
    att_input = f_info.code_context[0].split('(')[1].split(')')[0]

    print(att_input)
    print(inspect.getfullargspec(a))
    print(inspect.attr)

a(attribute_with_name, 10)