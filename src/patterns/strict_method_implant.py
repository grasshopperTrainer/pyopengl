import inspect


class SMI:
    def __new__(cls, *args, **kwargs):
        tree = inspect.getmro(cls)
        child = None
        for i, cla in enumerate(tree):
            if cla.__name__ == 'SMI':
                child = tree[i - 1]
        print(child)

        childmethods = dict(inspect.getmembers(child, inspect.isfunction)[1:])
        mothermethods = dict(inspect.getmembers(cls, inspect.isfunction)[1:])

        print(childmethods)
        for i in childmethods:
            if not childmethods[i] is mothermethods[i]:

        self = super().__new__(cls)
        self.__init__(*args, **kwargs)
        return self

    pass
