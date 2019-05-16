import inspect
import weakref


class SID:
    """
    >for class inheritance<
    stores instances inside the class.
    """
    _INSTANCES_DICT = weakref.WeakKeyDictionary()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        # to recover name of instance look back
        f = inspect.currentframe().f_back
        instance_name = ''
        while True:
            code_context = inspect.getframeinfo(f).code_context[0]
            # detection of instance declaration
            if f' {cls.__name__}(' in code_context and '=' in code_context:
                instance_name = code_context.split('=')[0].strip()
                break
            else:
                f = f.f_back

        cls._INSTANCES_DICT[self] = instance_name

        return self

    @classmethod
    def _instances_(cls):
        return cls._INSTANCES_DICT[cls.__name__]
