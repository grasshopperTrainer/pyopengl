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

        childfunctions = inspect.getmembers(child, inspect.isfunction)[1:]
        childdescriptors = list(filter(lambda x:x[0][:2] != '__',inspect.getmembers(child, inspect.isdatadescriptor)))
        childmethods = dict(childfunctions + childdescriptors)

        motherfunctions = inspect.getmembers(cls, inspect.isfunction)[1:]
        motherdescriptors = list(filter(lambda x:x[0][:2] != '__',inspect.getmembers(cls, inspect.isdatadescriptor)))
        mothermethods = dict(motherfunctions + motherdescriptors)

        undefined = list(filter(lambda x: x[1] is mothermethods[x[0]], childmethods.items()))

        if len(undefined) != 0:
            head = f""" (class) {cls.__name__} should have following methods of mother(class){child.__name__}:
            """
            body = """"""
            for name, method in undefined:
                body += f"""{method.__class__} {name}
            """
            raise Exception(head + body)

        else:
            self = super().__new__(cls)
            return self
