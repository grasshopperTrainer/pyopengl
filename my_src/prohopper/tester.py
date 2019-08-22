class A:

    def mymethod(func):
        print(func)
        def wrapper(*args, **kwargs):
            print(*args, **kwargs)
            func(*args, **kwargs)
        return wrapper

    @classmethod
    def f(cls):
        print(cls)

    @mymethod
    def ff(first, second):
        print('function ff')
        print(first, second)
        pass

a = A()
b = A()
a.ff(b)
A.ff(a,b)
