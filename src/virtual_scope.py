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
        if isinstance(item, str):
            for dic in self._namespaces:
                if item in dic:
                    return dic[item]

        elif isinstance(item, int):
            return self._namespaces[item]

    def __setitem__(self, key, value):
        for dic in self._namespaces:
            if key in dic:
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
        if isinstance(value, Namespace):
            self._namespaces = value._namespaces + self._namespaces

    def append_rear(self):
        pass

    @property
    def names(self):
        names = []
        for dicts in self._namespaces:
            names += list(dicts.keys())
        return names

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
        # modules import
        # TODO temporary
        #   do i need automated module import?
        #   check and think of more concrete ways
        frame = inspect.currentframe().f_back.f_back
        global_func = inspect.getsource(frame).splitlines()
        for line in global_func:

            if line.find('from') != -1:
                start_index = line.find('from')
            elif line.find('import') != -1:
                start_index = line.find('import')
            else:
                continue

            front = line[:start_index]
            if len(front.strip()) == 0:
                exec(line)

        # variables load
        dic = {}
        vars = func.__code__.co_varnames

        source = self.func_to_exec_source(func)
        exec(source)

        for var in vars:
            dic[var] = eval(var)
            exec(f'del {var}')

        if position == 0:
            self.namespace.append_front(dic)

        else:
            self.namespace.append_rear(dic)

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
    def source_replace_var_name(source: list, old: list, new:list) -> str:
        source = source.splitlines()

        translated = ''
        for line in source:
            line = line.rstrip()

            remainder = line

            for old_name,new_name in zip(old, new):
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
                            processed += remainder[:end_index + 1].replace(old_name, new_name)
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
        if func is None:
            pass
        else:

            if func in self._code_dict:
                try:
                    exec(self._code_dict[func])
                except Exception as e:
                    lineno = sys.exc_info()[2].tb_next.tb_lineno
                    head = []
                    source = inspect.getsource(func).splitlines()
                    for i,line in enumerate(source):
                        if line[0] is ' ':
                            head = source[:i]
                            source = source[i:]
                            break

                    head = reduce(lambda x,y: x+' - '+ y, head)
                    error_line = source[lineno-1]
                    print_message(str(e),where_from=head[:-1], var_info = f'source: {error_line}')

                    exit()


            else:
                source = self.func_to_exec_source(func)

                new_names = [f'self.namespace["{var}"]' for var in self.namespace.names]
                # need to manually parse?
                translated = self.source_replace_var_name(source, self.namespace.names, new_names)

                code = compile(translated, func.__module__, 'exec')

                self._code_dict[func] = code
                self.run_func(func)
