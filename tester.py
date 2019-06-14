# # class B:
# #     pass
# #
# # class A:
# #     def __enter__(self):
# #         print('engetr')
# #         return self
# #
# #     def __exit__(self, exc_type, exc_val, exc_tb):
# #         pass
# #     def make(self):
# #         self.a = B()
# #     def d(self):
# #         del self.a
# #
# # a = A()
# #
# # a.make()
# # a.d()
# # print(a.a)
# def f(a = 20):
#     a = 10
#
# print(f.a)
class A:
    def f():
        pass

print(A.f.__dir__())
for i in A.f.__dir__():
    print()
    print(i)
    try:
        exec(f'print(A.f.{i}())')
    except:
        exec(f'print(A.f.{i})')