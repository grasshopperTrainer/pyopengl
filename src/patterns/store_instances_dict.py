import inspect
import weakref


class SID:
    _INSTANCES_DICT = dict()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        f = inspect.currentframe().f_back
        instance_name = ''
        while True:
            code_context = inspect.getframeinfo(f).code_context[0]
            if f' {cls.__name__}(' in code_context and '=' in code_context:
                instance_name = code_context.split('=')[0].strip()
                break
            else:
                f = f.f_back
        name = cls.__name__
        if name not in cls._INSTANCES_DICT:
            cls._INSTANCES_DICT[name] = weakref.WeakValueDictionary()
        cls._INSTANCES_DICT[name][instance_name] = self

        return self

    @classmethod
    def _instances_(cls):
        return cls._INSTANCES_DICT[cls.__name__]
