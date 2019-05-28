class A:
    def __init__(self,func):

        def repeat_func():
            for i in range(10):
                return_v = func()
            return return_v

        self.func = repeat_func

    def __call__(self, *args, **kwargs):
        return self.func()

class B:
    def __init__(self,func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func

    def __call__(self, *args, **kwargs):
        return self.func()

@B
@A
def a():
    print('function call')
    return 10
# a = B(A(a))
# def a():
#     print('kkk')
#     pass
@B
def k():
    print('function k')
    return 20
# a = A(a)
def b():
    pass
print(a)
b = a()
print(b)
print(k)
print(k())
# a()