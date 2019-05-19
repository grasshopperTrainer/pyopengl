import inspect
import sys
import traceback

import weakref
from functools import reduce
from .source_parser import Source_parser as prs

from error_handler import print_message


class Namespace:
    def __init__(self):
        self._top_namespace = {}
        self._namespaces = [{}, ]

    def __getitem__(self, item):

        # return stored value
        if isinstance(item, str):
            if item in self.top_namespace:
                return self.top_namespace[item]
            else:
                for dic in self._namespaces:
                    if item in dic:
                        return dic[item]

            raise KeyError('no key in namespace')

        # return namespace
        elif isinstance(item, int):
            return self._namespaces[item]

    def __setitem__(self, key, value):
        # first check if key is assigned
        if key in self.top_namespace:
            raise KeyError("can't change value of assigned variable name")

        # second see if there already is a variable name
        for dic in self._namespaces:
            if key in dic:
                dic[key] = value
                break

        # else there is no variable defined
        # gonna append as a new variable at the front
        dic = self._namespaces[0]
        dic[key] = value

    def append_front(self, value):
        """
        Add new or existing namespaces in front of this instance's namespace.

        Front means when namespce is looked up for a value of a variable,
        first variable_name - value dict will be a dictionary placed at front.

        :param value: dictionary or Namespace instance to add on front
        :return: None
        """
        if isinstance(value, dict):
            self._namespaces.insert(0, value)

        elif isinstance(value, (tuple, list)):
            dic = dict(zip(value, [None]*len(value)))
            self._namespaces.insert(0, dic)

        elif isinstance(value, Namespace):
            self._namespaces = value._namespaces + self._namespaces

    def append_rear(self, value):
        """
        Add new or existing namespaces in back of this instance's namespace.

        Back means when namespce is looked up for a value of a variable,
        this variable_name - value dict will be looked only if
        existing dicts in front doesn't have the value.

        :param value: dictionary, list, tuple or Namespace instance to add on front
        :return: None
        """
        if isinstance(value, dict):
            self._namespaces.append(value)

        elif isinstance(value, (tuple, list)):
            dic = dict(zip(value, [None]*len(value)))
            self._namespaces.append(dic)

        elif isinstance(value, Namespace):
            self._namespaces = self._namespaces + value._namespaces
        pass

    def add_new_variable(self, names, values=None, position=0):
        if not isinstance(names, (list, tuple)):
            names = [names, ]
        if not isinstance(values, (list, tuple)):
            values = [values, ]

        if values is None:
            values = [None, ] * len(names)

        for name, value in zip(names, values):
            try:
                self[name]
            except:
                self._namespaces[position][name] = value
                return True


    @property
    def names(self):
        names = []
        names += list(self.top_namespace.keys())
        for dicts in self._namespaces:
            names += list(dicts.keys())
        return names

    @property
    def all_items(self):
        flattened_dict = {}
        for dic in reversed(self._namespaces):
            flattened_dict.update(dic)
        return flattened_dict

    @property
    def top_namespace(self):
        return self._top_namespace

    @top_namespace.setter
    def top_namespace(self, value):
        if isinstance(value, dict):
            self._top_namespace = value

class Virtual_scope:
    def __init__(self):

        self._code_dict = {}
        self._ref_vars = []
        self._namespaces = Namespace()

    def append_scope_byscope(self, scope, position = 0):
        if position == 0:
            self.namespace.append_front(scope.namespace)
        else:
            self.namespace.append_rear(scope.namespace)

    # def append_scope_byitems(self, name_value: dict, position=0):
    #     if not isinstance(name_value, dict):
    #         raise TypeError('input sould be dict of varname_value')
    #     if position == 0:
    #         self.namespace.append_front(name_value)
    #     else:
    #         self.namespace.append_rear(name_value)

    def set_assigned(self, name_value: dict):
        if not isinstance(name_value, dict):
            raise TypeError('input sould be dict of varname_value')

        self.namespace.top_namespace = name_value

    @property
    def namespace(self):
        return self._namespaces
    @property
    def variables(self):
        return self._namespaces.names

    def search_value_bytype(self, type):
        result = []
        # print(self.namespace, type)
        for item in self.namespace.all_items.items():
            if isinstance(item[1], type):
                result.append(item)

        return result


    def get_value(self, var):
        return eval(f'self.{var}')

    def append_scope(____, obj, position=0):
        """
        Expends scope by function. Will grab all variables
        inside function and copy into this instance's name space.

        :param obj: function to parse
        :param position: describes override position. Front is the
        surface of search. Thus if position is 1(True)
        variables processed will be placed on the existing namespace.
        This means matching names will be overridden. In contrast,
        if position is 0(False) new variables will be places back of
        existing namewpace. Meaning only new names will be appended to
        the namespace.
        :return: None
        """
        if callable(obj):
            # variables load
            vars = obj.__code__.co_varnames
            headbody = prs.split_func_headbody(obj)
            source = headbody[1]
            filename = prs.search_func_name(headbody[0])
        elif isinstance(obj, str):
            vars = prs.search_all_variables(obj)
            source = obj
            filename = 'unknown'

        # append new namespace
        if position == 0:
            ____.namespace.append_front(vars)
        else:
            ____.namespace.append_rear(vars)

        new_format = '____.namespace["{}"]'
        new_names = []
        for name in ____.namespace.names:
            new_names.append(new_format.format(name))
        # print('source is ')
        # print(source)
        try:
            translated = prs.replace_names(source, ____.namespace.names, new_names)
        except:
            print(source)
            raise

        # TODO filename: what should it be?
        code = compile(translated, filename, 'exec')
        # run to save values
        try:
            exec(code)
        except Exception as e:
            print(e)
            raise

    def compile(self, obj):
        # compiling object is a function
        source = prs.split_func_headbody(obj, 1)

        if callable(obj):
            filename = obj.__module__
            varnames = obj.__code__.co_varnames
            self.namespace.add_new_variable(varnames)

        # compiling object is a string of source
        elif isinstance(obj, str):
            varnames = prs.search_all_variables(source)
            filename = 'unknown'
            # if there is a new varnames
            if self.namespace.add_new_variable(varnames):
                # recompile stored sources
                for code in self._code_dict:
                    self.compile(code)

        # translate with namespace
        new_format = '____.namespace["{}"]'
        new_names = [new_format.format(name) for name in self.namespace.names]
        translated = prs.replace_names(source, self.namespace.names, new_names)
        # compile
        code = compile(translated, filename, 'exec')
        self._code_dict[obj] = code
        return code

    def run(____, obj):
        # do nothing
        if obj is None:
            return

        elif obj in ____._code_dict:
            try:
                exec(____._code_dict[obj])

            except Exception as e:
                lineno = sys.exc_info()[2].tb_next.tb_lineno
                head = []
                if callable(obj):
                    source = inspect.getsource(obj).splitlines()
                elif isinstance(obj, str):
                    source = obj.splitlines()

                for i,line in enumerate(source):

                    if len(line) is 0 or line[0] is ' ':
                        head = source[:i]
                        source = source[i:]
                        break

                head = reduce(lambda x,y: x+' - '+ y, head)
                error_line = source[lineno-1]
                print_message(str(e),header='error',where_from=head[:-1], var_info = f'source: {error_line}')
                print(traceback.format_exc())
                exit()

        else:
            code = ____.compile(obj)
            ____._code_dict[obj] = code
            # go back to execution
            ____.run(obj)
