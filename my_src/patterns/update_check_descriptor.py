import weakref
import numpy as np
import inspect

from patterns.store_instances_dict import SID


class UCD():
    _DIC = weakref.WeakKeyDictionary()
    latest_call_descriptor = {}

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
        # self._updated = True
        self._pre_get_callbacks = {}

    def __set__(self, instance, value):
        replace = True
        descriptor = self.get_this_properties(instance)

        # for the first set
        if not descriptor['init']:
            descriptor['init'] = True

        # value comparison
        if type(descriptor['value']) == type(value):
            # if value is the same with stored -> means nothing new
            # exception for numpy comparison
            if isinstance(value, np.ndarray):
                if np.array_equal(descriptor, value):
                    replace = False
            else:
                if descriptor == value:
                    replace = False
        # if types are different -> means new value
        else:
            pass

        # if value different replace and raise update mark
        if replace:
            descriptor['updated'] = True
            descriptor['value'] = value
        else:
            descriptor['updated'] = False

        descriptor['setcount'] += 1

    def __get__(self, instance, owner):
        descriptor = self.get_this_properties(instance)
        if not descriptor['init']:
            return self
        else:
            self.__class__.latest_call_descriptor[instance] = self
            self._DIC[instance.__class__][instance][self]['getcount'] += 1
            for f in self.get_this_properties(instance)['pre_get_callback']:
                f()

            return descriptor['value']

    def get_this_properties(self, instance):
        # first call
        if instance.__class__ not in self.__class__._DIC:
            self.__class__._DIC[instance.__class__] = weakref.WeakKeyDictionary()
        if instance not in self._DIC[instance.__class__]:
            self.__class__._DIC[instance.__class__][instance] = weakref.WeakKeyDictionary()

        descriptors = self._DIC[instance.__class__][instance]
        # first call of new descriptor name
        # structure
        if self not in descriptors:
            # won't set value yet for initiation identification
            descriptors[self] = {'value': None,
                                 'getcount': 0,
                                 'setcount': 0,
                                 'updated': True,
                                 'pre_get_callback': [],
                                 'post_get_callback': [],
                                 'pre_set_callback': [],
                                 'post_set_callback': [],
                                 'init': False}

        return descriptors[self]

    @classmethod
    def reset_this_descriptor_update(cls, instance, descriptor):
        property_dicts = cls.get_instance_descriptor_properties(instance)

        for d in property_dicts:
            d['updated'] = False
            d['getcount'] = 0
    @classmethod
    def reset_descriptor_getcount(cls, instance, attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        p['getcount'] = 0

    @classmethod
    def reset_descriptor_update(cls, instance, attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        p['update'] = False

    @classmethod
    def get_instance_descriptor_properties(cls, instance):
        ds = cls._DIC[instance.__class__][instance]
        v_dict = []

        for d in ds.values():
            v_dict.append(d)

        return v_dict

    @classmethod
    def get_descriptor_getcount(cls, instance, attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        p['getcount'] -= 1
        return p['getcount']

    @classmethod
    def get_descriptor_setgetcount(cls, instance, attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        p['getcount'] -= 1

        return p['getcount'] + p['setcount']

    @classmethod
    def get_descriptor_update(cls, instance, attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        p['getcount'] -= 1
        return p['update']

    @classmethod
    def get_instance_descriptors(cls, instance):
        return cls._DIC[instance.__class__][instance]

    @classmethod
    def is_instance_any_update(cls, *instances):
        for ins in instances:
            descriptors = cls.get_instance_descriptors(ins)
            for properties in descriptors.values():
                if properties['updated']:
                    return True

        return False


    @classmethod
    def reset_instance_updates(cls, *instances):
        for ins in instances:
            ps = cls._DIC[ins.__class__][ins].values()
            for p in ps:
                p['updated'] = False

    def set_pre_get_callback(self, function):
        if callable(function):
            p = self.get_this_properties(function.__self__)
            l = p['pre_get_callback']
            if function not in l:
                l.append(function)

        else:
            raise TypeError('input is not a callable')

    @property
    def name(self):
        return self.INSTANCE_NAME
    def __repr__(self):
        return f"descriptor named '{self.INSTANCE_NAME}'"

