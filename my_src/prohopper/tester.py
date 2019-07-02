# import weakref
#
# class D:
#     def __set__(self, instance, value):
#         pass
#     def __get__(self, instance, owner):
#         print(instance, owner)
#         if instance is None:
#             return self
#         pass
#     def ff(self, instance):
#         print(instance)
#
#
# class K:
#     a = D()
#     def __init__(self):
#         self.a = 10
#         self.cls = self.__class__
#     def f(self):
#         self.__class__.a.ff(self)
#         self.cls.a
#
# k = K()
# print(k.a)
# k.f()
#
# a = weakref.WeakSet()
# b = {10,20}
# print(list(a))

print(lambda)