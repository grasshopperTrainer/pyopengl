import inspect


class MC:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        # TODO maybe types checking can be strengthend by converting deep
        #   ex. in case arg [2,4] and want to convert it into
        #   [<int>, <int>] not <list>
        p_types = [type(i) for i in args] + [type(i) for i in kwargs]
        init = None

        for n,m in cls.__dict__.items():
            if n.find('__init') == 0:
                anno = list(inspect.getfullargspec(m)[6].values())
                if all(s == t for s,t in zip(p_types, anno)):
                    init = m
                else:
                    continue
        # redirect __init__ into new
        # is this necessary?
        instance.__init__ = init
        init(instance, *args, **kwargs)

        return instance