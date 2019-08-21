class A:
    def f(self):
        print('from A')
class B:
    def f(self):
        print('from B')

class C(A,B):
    pass


c = C()
c.f()