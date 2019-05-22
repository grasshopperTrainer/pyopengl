import weakref
import numpy as np
import inspect
from collections import namedtuple
from patterns.store_instances_dict import SID


class UCD():
    _DIC = weakref.WeakKeyDictionary()
    # TODO
    latest_call_descriptor = weakref.WeakKeyDictionary()
    _TEST = np.zeros(())
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
        # print(instance, value)
        replace = True
        prop = self.get_this_properties(instance)

        # for the first set
        if not prop['init']:
            prop['init'] = True

        # value comparison
        if type(prop['value']) == type(value):
            # if value is the same with stored -> means nothing new
            # exception for numpy comparison
            if isinstance(value, np.ndarray):
                if np.array_equal(prop['value'], value):
                    replace = False
            else:
                if prop['value'] == value:
                    replace = False
        # if types are different -> means new value
        else:
            pass

        # if value different replace and raise update mark
        if replace:
            prop['updated'] = True
            prop['value'] = value
        else:
            prop['updated'] = False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        descriptor = self.get_this_properties(instance)

        if not descriptor['init']:
            return self
        else:
            self.__class__.latest_call_descriptor[instance] = self

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
                                 'updated': True,
                                 'pre_get_callback': [],
                                 'post_get_callback': [],
                                 'pre_set_callback': [],
                                 'post_set_callback': [],
                                 'init': False}
        return descriptors[self]


    def set_this_property(self, instance, property_key, value):
        d = self.get_this_properties(instance)
        d[property_key] = value

    def set_pre_get_callback(self, function):
        if callable(function):
            p = self.get_this_properties(function.__self__)
            l = p['pre_get_callback']
            if function not in l:
                l.append(function)
        else:
            raise TypeError('input is not a callable')

    @classmethod
    def get_instance_descriptor_property(cls, instance, property_key=None):
        d = cls._DIC[instance.__class__][instance]
        new_d = {}
        for desc, p_dict in d.items():
            if property_key is None:
                new_d[desc] = p_dict
            else:
                new_d[desc] = p_dict[property_key]

        return new_d

    @classmethod
    def get_descriptor_instance_property(cls, instance, descriptor, property_key=None):
        d = cls._DIC[instance.__class__]
        new_d = {}

        for ins, desc_dic in d.items():
            prep_dic = desc_dic[descriptor]
            if property_key is None:
                new_d[ins] = prep_dic
            else:
                p = prep_dic[property_key]
                new_d[ins] = p

        return new_d

    @classmethod
    def reset_descriptor_update(cls, instance, desc_attribute):
        desc = cls.latest_call_descriptor[instance]
        desc.set_this_property(instance,'updated', False)

    @classmethod
    def reset_instance_descriptors_property(cls,instance, property_key, value):
        d = cls.get_instance_descriptor_property(instance)
        for prop_dic in d.values():
            prop_dic[property_key] = value
    @classmethod
    def reset_instance_descriptors_update(cls,*instances):
        for ins in instances:
            cls.reset_instance_descriptors_property(ins,'updated', False)

    @classmethod
    def is_descriptor_updated(cls, instance, desc_attribute):
        d = cls.latest_call_descriptor[instance]
        p = d.get_this_properties(instance)
        return p['updated']

    @classmethod
    def is_any_descriptor_updated(cls, *instances):
        for ins in instances:
            des_prop = cls.get_instance_descriptor_property(ins,'updated')
            for prop in des_prop.values():
                if prop:
                    return True
        return False

    @property
    def name(self):
        return self.INSTANCE_NAME
    def __repr__(self):
        return f"descriptor named '{self.INSTANCE_NAME}'"

