import inspect

class SMI:
    """

    """
    def __new__(cls, *args, **kwargs):
        tree = inspect.getmro(cls)
        child = None
        for i, cla in enumerate(tree):
            if cla.__name__ == 'SMI':
                child = tree[i - 1]

        childmethods = dict(inspect.getmembers(child, inspect.isfunction)[1:])
        mothermethods = dict(inspect.getmembers(cls, inspect.isfunction)[1:])

        undefined = list(filter(lambda x: childmethods[x] is mothermethods[x], childmethods))

        if len(undefined) != 0:
            head = f""" (class){cls.__name__} should have following methods
            of mother(class){child.__name__} defined:
            """
            body = """"""
            for n in undefined:
                body += f"""(function){n}
            """
            raise Exception(head + body)

        else:
            self = super().__new__(cls)
            return self
