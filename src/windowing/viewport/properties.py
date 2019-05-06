import weakref
import numpy as np
import inspect

from patterns.store_instances_dict import SID


class _Property():
    _gdict = dict()

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

        self.__setattr__('INSTANCE_NAME', instance_name)

        return self

    def __init__(self):
        self._updated = True
        self._dict = dict()

    def __set__(self, instance, value):
        if instance.__class__ not in self._gdict:
            self._gdict[instance.__class__] = dict()
        if instance not in self._gdict[instance.__class__]:
            self._gdict[instance.__class__][instance] = dict()

        dic = self._gdict[instance.__class__][instance]
        if self not in dic:
            dic[self] = value
        else:
            replace = True
            stored = dic[self]
            if type(stored) == type(value):
                if isinstance(value, np.ndarray):
                    if np.array_equal(stored, value):
                        replace = False
                else:
                    if stored == value:
                        replace = False

            if replace:
                self._updated = True
                dic[self] = value

    def __get__(self, instance, owner):
        # print(self._dict[instance.__class__][instance])
        # print(self._dict)
        return self._gdict[instance.__class__][instance][self]

    def is_updated(self):
        return self._updated

    def reset_update(self):
        self._updated = False

    @classmethod
    def get_class_descriptors(cls, _class):
        return cls._gdict[_class]

    @classmethod
    def get_instance_descriptors(cls, _instance):
        return cls._gdict[_instance.__class__][_instance]

    @classmethod
    def is_instance_descriptors_any_update(cls, _instance):
        ds = cls.get_instance_descriptors(_instance)
        for descriptor in ds:
            if descriptor.is_updated():
                return True

        return False

    def __repr__(self):
        return self.INSTANCE_NAME
