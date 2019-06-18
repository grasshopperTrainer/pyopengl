# import weakref
# class A:
#     dict = weakref.WeakKeyDictionary()
#     def __init__(self, obj):
#         self.dict[obj] = self
#         self.k = []
#     pass
#
#     @staticmethod
#     def setter(func):
#         def wrapper(self,*args, **kwargs):
#             print(args, kwargs)
#
#             pass
#         return wrapper
#
#
#
# class B:
#     def __init__(self):
#         self.r = A(self)
#
#     @A.setter
#     def kkk(self):
#         print('this')
#
#
# B().kkk()
#

a = [1,2,[3,]]
b = [1,2,[3,]]
print(a == b)