class A:

    def __new__(cls, *args, **kwargs):
        print(super())
        print(super().__new__)
        print(object.__new__)



a = A()
print(A.__new__)