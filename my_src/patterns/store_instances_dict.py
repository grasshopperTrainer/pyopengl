import inspect
import weakref


class SID:
    """
    >for class inheritance<
    Stores instances inside the class.
    Assigned names are:
    (class arg) _INSTANCES_DICT
    (classmethod) _instances_()

    """

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        # add new dict
        if not hasattr(cls,'_INSTANCE_DICT'):
            cls._INSTANCE_DICT = weakref.WeakValueDictionary()

        # to recover name of instance look back
        f = inspect.currentframe()
        instance_name = ''
        while True:
            if f is None:
                # what does this mean?
                break
            code_context = inspect.getframeinfo(f).code_context[0]
            # detection of instance declaration
            if f' {cls.__name__}(' in code_context and '=' in code_context:
                instance_name = code_context.split('=')[0].strip()
                cls._INSTANCE_DICT[instance_name] = self
                break
            else:
                f = f.f_back

        return self

    @classmethod
    def _instances_(cls):
        return cls._INSTANCE_DICT[cls.__name__]


# class A(SID):
#     pass
#
# class B(SID):
#     pass
#
# a = A()
# aa = A()
# print(list(aa._INSTANCE_DICT.items()))
#
# b = B()
# bb = B()
# print(list(bb._INSTANCE_DICT.items()))
# print(list(aa._INSTANCE_DICT.items()))


