
def f():
    print('kkk')
    pass

k = lambda : f() if False else None

k()