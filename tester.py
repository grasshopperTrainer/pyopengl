import weakref
#
#
class A:
    def __init__(self):
        self.a = None

    def s(self, f):
        self.a = weakref.WeakMethod(f)

    def r(self):
        print(self.a)
        self.a()()
    def pp(self):
        print('kkk')
# def k():
#     print('kkk')
#     pass

d = A()
b = A()
d.s(b.pp)
del b
d.r()
# print(b)
# print(b)
#
# class C:
#     def m(self):
#         print('kkk')
#
# c = C()
#
# a = weakref.WeakMethod(c.m)
# a()()