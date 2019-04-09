import inspect
import weakref
import sys
import os

from functools import reduce
from error_handler import print_message

class Namespace:
    def __init__(self):
        self._namespaces = [{}, ]

    def __getitem__(self, item):
        # return stored value
        if isinstance(item, str):

            for dic in self._namespaces:
                if item in dic:
                    return dic[item]

        # return namespace
        elif isinstance(item, int):
            return self._namespaces[item]

    def __setitem__(self, key, value):
        # first see if there already is a variable name
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
        # """
        # Add new or existing namespaces in back of this instance's namespace.
        #
        # Back means when namespce is looked up for a value of a variable,
        # this variable_name - value dict will be looked only if
        # existing dicts in front doesn't have the value.
        #
        # :param value: dictionary or Namespace instance to add on front
        # :return: None
        # """
        # if isinstance(value, dict):
        #     self._namespaces.insert(0, value)
        #
        # # elif isinstance(value, (tuple, list)):
        # #     dic = dict(zip(value, [None]*len(value)))
        # #     self._namespaces.insert(0, dic)
        #
        # elif isinstance(value, Namespace):
        #     self._namespaces = value._namespaces + self._namespaces
        pass

    @property
    def names(self):
        names = []
        for dicts in self._namespaces:
            names += list(dicts.keys())
        return names

    @property
    def all_items(self):
        flattened_dict = {}
        for dic in reversed(self._namespaces):
            flattened_dict.update(dic)
        return flattened_dict


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

    def append_scope_byfunc(self, func, position = 0):
        """
        Expends scope by function. Will grab all variables
        inside function and copy into this instance's name space.

        :param func: function to parse
        :param position: describes override position. Front is the
        surface of search. Thus if position is 1(True)
        variables processed will be placed on the existing namespace.
        This means matching names will be overridden. In contrast,
        if position is 0(False) new variables will be places back of
        existing namewpace. Meaning only new names will be appended to
        the namespace.
        :return: None
        """

        # variables load
        vars = func.__code__.co_varnames
        # append new namespace
        if position == 0:
            self.namespace.append_front(vars)
        else:
            self.namespace.append_rear(vars)

        # run to save values
        source = self.func_to_exec_source(func)
        translated = self.source_replace_var_name(source, self.namespace.names)
        code = compile(translated, func.__module__, 'exec')
        exec(code)

    @staticmethod
    def func_to_exec_source(func, tolines = False):
        source = inspect.getsource(func).splitlines()[2:]
        source = list(map(lambda x: x[4:], source))
        if tolines:
            return source
        else:
            source = reduce(lambda x,y: x + '\n' + y, source)
            return source

    @staticmethod
    def source_replace_var_name(source: list, old: list) -> str:
        source = source.splitlines()

        translated = ''
        for line in source:
            line = line.rstrip()
            remainder = line


            # for module import
            # if context is from ~ import
            if line.find('from') == 0:

                if 'import' in line:
                    mark = 'import'
                else:
                    mark = 'as'

                searching = line
                while True:
                    start_i = searching.find(mark)
                    end_i = start_i + len(mark)-1

                    if searching[start_i - 1] is ' ' and searching[end_i + 1] is ' ':
                        name = searching[end_i + 1:].strip()
                        break
                    else:
                        searching = searching[end_i + 1 : ]

                translated += line + '\n'
                translated += f'self.namespace["{name}"] = {name}' + '\n'
                continue

            # else if context is import ~
            elif line.find('import') == 0:
                translated += line + '\n'
                if 'as' in line:
                    while True:

                        start_i = line.find('as')
                        end_i = start_i + 1

                        if line[start_i-1] is ' ' and line[end_i + 1] is ' ':
                            name = line[end_i + 1:].strip()
                            break
                    translated += f'self.namespace["{name}"] = {name}' + '\n'
                else:
                    name = line.split('import')[1].strip()
                    translated += f'self.namespace["{name}"] = {name}' + '\n'

                continue

            # for variable names
            else:
                for old_name in old:
                    processed = ''

                    while True:
                        start_index = remainder.find(old_name)
                        if start_index == -1:
                            if len(processed) is not 0:
                                remainder = processed + remainder
                            break

                        else:
                            end_index = start_index + len(old_name) - 1
                            front_cond = True
                            end_cond = True

                            if start_index is not 0:
                                front = remainder[start_index - 1]
                                conditions = [
                                    front.isalpha(),
                                    front.isnumeric(),
                                    front is '.',
                                    front is "'",
                                    front is '"'
                                ]
                                if sum(conditions) > 0:
                                    front_cond = False
                            if end_index is not len(remainder) - 1:
                                end = remainder[end_index + 1]
                                conditions = [
                                    end.isalpha(),
                                    end.isnumeric(),
                                    end is "'",
                                    end is '"'
                                ]
                                if sum(conditions) > 0:
                                    end_cond = False

                            # meaning a substring is a variable name
                            if front_cond and end_cond:
                                processed += remainder[:end_index + 1].replace(old_name, f'self.namespace["{old_name}"]')
                            else:
                                processed += remainder[:end_index + 1]

                            if end_index is not len(remainder) - 1:
                                remainder = remainder[end_index + 1:]
                            else:
                                remainder = processed
                                break

                translated += remainder + '\n'

        return translated

    def run_func(self, func):
        # do nothing
        if func is None:
            return

        if func in self._code_dict:
            try:
                exec(self._code_dict[func])
            except Exception as e:
                lineno = sys.exc_info()[2].tb_next.tb_lineno
                head = []
                source = inspect.getsource(func).splitlines()
                for i,line in enumerate(source):

                    if len(line) is 0 or line[0] is ' ':
                        head = source[:i]
                        source = source[i:]
                        break

                head = reduce(lambda x,y: x+' - '+ y, head)
                error_line = source[lineno-1]
                print_message(str(e),header='error',where_from=head[:-1], var_info = f'source: {error_line}')

                exit()

        else:
            # initiation, first call
            source = self.func_to_exec_source(func)
            translated = self.source_replace_var_name(source, self.namespace.names)
            code = compile(translated, func.__module__, 'exec')
            self._code_dict[func] = code

            # go back to execution
            self.run_func(func)

