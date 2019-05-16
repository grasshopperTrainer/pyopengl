import weakref
import numpy as np
import inspect

from patterns.store_instances_dict import SID


class UCD():
    _DIC = dict()

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
        self._get_functions = {}

    def __set__(self, instance, value):
        if instance.__class__ not in self._DIC:
            self._DIC[instance.__class__] = dict()
        if instance not in self._DIC[instance.__class__]:
            self._DIC[instance.__class__][instance] = dict()

        dic = self._DIC[instance.__class__][instance]
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
        # print(self._DIC[instance.__class__][instance][self])
        # try:
        # print(instance, owner, self)
        try:
            if instance in self._get_functions:
                for f in self._get_functions[instance]:
                    f()
            else:
                pass
            return self._DIC[instance.__class__][instance][self]
        except KeyError:
            return self

    def is_updated(self):
        return self._updated

    def reset_update(self):
        self._updated = False

    @classmethod
    def get_class_descriptors(cls, _class):
        return cls._DIC[_class]

    @classmethod
    def get_instance_descriptors(cls, _instance):
        return cls._DIC[_instance.__class__][_instance]

    @classmethod
    def is_instance_descriptors_any_update(cls, *instances):
        for ins in instances:
            des = cls.get_instance_descriptors(ins)
            for descriptor in des:
                if descriptor.is_updated():
                    return True

        return False

    @classmethod
    def reset_instance_descriptors_update(cls, *instances):
        for ins in instances:
            des = cls.get_instance_descriptors(ins)
            for descriptor in des:
                descriptor.reset_update()

    @classmethod
    def reset_descriptor_update(cls, instance, name):
        pass

    @classmethod
    def get_descriptor(cls, name):
        pass

    def test(self):
        print('dkdkdkdkdkdk')

    def function_when_get(self, function):
        if self in self._get_functions:
            self._get_functions[function.__self__].append(function)
        else:
            self._get_functions[function.__self__] = [function,]

    def __repr__(self):
        return f"descriptor of '{self.INSTANCE_NAME}'"
