

class A:
    def __init__(self,a:int, b:int):
        pass
    pass

class B:
    def __init__(self,a:str, b:str):
        pass
    pass


def C(self, *args, **kwargs):
    print('dkdkd')
    if isinstance(args, int):
        return A
    else:
        return B
K = C()
c = K()