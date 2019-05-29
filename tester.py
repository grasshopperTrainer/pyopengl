
class myclassmethod(classmethod):
    def __init__(self,func):
        super(func.__class__)

    def __get__(self, instance, owner):
        print(super().__get__(instance,owner))

class A:

    @myclassmethod
    def method(cls):
        print('this is a class method')


a = A()
a.method()