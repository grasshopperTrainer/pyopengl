import inspect
import sys
import traceback
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
            raise KeyError('no key in namespace')

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

    def append_scope_byitems(self, names, values, position=0):
        if not isinstance(names, (tuple, list)):
            names = [names, ]
            values = [values, ]
        dic = dict(zip(names, values))

        if position == 0:
            self.namespace.append_front(dic)
        else:
            self.namespace.append_rear(dic)

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

    def append_scope_byfunc(____, func, position=0):
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
            ____.namespace.append_front(vars)
        else:
            ____.namespace.append_rear(vars)

        # run to save values
        source = ____.get_content_source(func)
        translated = ____.source_replace_var_name(source, ____.namespace.names)

        code = compile(translated, func.__module__, 'exec')
        exec(code)

    @staticmethod
    def get_content_source(obj, tolines=False):
        if callable(obj):
            source = inspect.getsource(obj).splitlines()
        elif isinstance(obj, str):
            source = obj.splitlines()
        elif isinstance(obj, list):
            source = obj

        indent = 0
        for line in source:
            if line.strip()[0] == '\n':
                continue
            elif line.strip()[0] == '#':
                continue

            for i, l in enumerate(line):
                if l != ' ':
                    indent = i
                    break
            break

        source = [line[indent:] for line in source]
        head_i = -1
        # check if source is a definition of function
        for i, line in enumerate(source):
            if line.find('def') == 0:
                head_i = i
                break

        source = source[head_i + 1:]
        source = list(map(lambda x: x[4:], source))

        if tolines:
            return source
        else:
            source = reduce(lambda x,y: x + '\n' + y, source)
            return source

    @staticmethod
    def clean_source(source):
        source = source.splitlines()

        # find valid first line
        first_line = ''
        first_line_i = 0
        for i, line in enumerate(source):
            if line.strip()[0] == '\n':
                continue
            if line.strip()[0] == '#':
                continue
            else:
                first_line = line
                first_line_i = i
                break

        # look for margin
        margin = 0
        for l in first_line:
            if l == ' ':
                margin += 1
            else:
                break

        # remove margins
        for i, line in enumerate(source):
            if line.strip()[0] == '#':
                i = line.find('#')
                move = margin - i
                # if comment is in fron margin push
                if move > 0:
                    source[i] = ' ' * move + line
            else:
                source[i] = line[margin:]

        return source

    @staticmethod
    def search_defined_varnames_manually(source):
        # find valid first line
        if isinstance(source, str):
            source = source.splitlines()
        elif isinstance(source, list):
            pass
        else:
            raise TypeError('source is not a string or list of strings')

        first_line = ''
        first_line_i = 0
        for i, line in enumerate(source):
            if line.strip()[0] == '\n':
                continue
            if line.strip()[0] == '#':
                continue
            else:
                first_line = line
                first_line_i = i
                break

        # by type of source look for filename and content block
        # TODO maybe I need to cover class definition too
        if source[first_line_i][:3] == 'def':
            filename = source[first_line_i][4:source[first_line_i].find('(')]
            content = [line[4:] for line in source[first_line_i + 1:]]
        elif source[0][0] == '@':
            filename = source[first_line_i + 1][4:source[first_line_i + 1].find('(')]
            content = [line[4:] for line in source[first_line_i + 2:]]
        else:
            content = source

        # search for variable names by looking through each line
        varnames = []
        for line in content:
            # ignore blank and comment line
            if line.strip()[0] == '\n':
                continue
            if line.strip()[0] == '#':
                continue

            # if a line has a hint of variable name
            if '=' in line:
                index = line.find('=')
                isquot = False

                # check if '=' is inside a quotation
                quot_pos_start = [line.find("'"), line.find('"')]
                if max(quot_pos_start) != -1:
                    mark = ''
                    if quot_pos_start[0] > quot_pos_start[1]:
                        mark = "'"
                        quot_pos_start = quot_pos_start[0]
                    else:
                        mark = '"'
                        quot_pos_start = quot_pos_start[1]

                    quot_pos_end = reversed(line).find(mark)
                    if quot_pos_end != -1:
                        quot_pos_end = len(line) - 1 - quot_pos_end
                        if index > quot_pos_start and index < quot_pos_end:
                            isquot = True
                    else:
                        raise SyntaxError('annotation incorrect')

                # proceed when not a part of a quotation
                if not isquot:
                    name_value = line.split('=')
                    name = name_value[0].strip()
                    varnames.append(name)

        return varnames

    @staticmethod
    def source_replace_var_name(source: list, var_names: list, new_format='____.namespace["{}"]') -> str:
        if isinstance(source, str):
            source = source.splitlines()
        else:
            pass

        translated = ''
        for line in source:
            line = line.rstrip()
            remainder = line


            # for module import
            # if context is from ~ import
            if line.find('from ') == 0:

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
                translated += f'{new_format.format(name)} = {name}' + '\n'
                continue

            # else if context is import ~
            elif line.find('import ') == 0:
                translated += line + '\n'
                if 'as' in line:
                    while True:

                        start_i = line.find('as')
                        end_i = start_i + 1

                        if line[start_i-1] is ' ' and line[end_i + 1] is ' ':
                            name = line[end_i + 1:].strip()
                            break

                    translated += f'{new_format.format(name)} = {name}' + '\n'
                else:
                    name = line.split('import')[1].strip()
                    translated += f'{new_format.format(name)} = {name}' + '\n'

                continue

            # for variable names
            else:
                for name in var_names:
                    processed = ''

                    while True:
                        start_index = remainder.find(name)
                        if start_index == -1:
                            if len(processed) is not 0:
                                remainder = processed + remainder
                            break

                        else:
                            end_index = start_index + len(name) - 1
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
                                processed += remainder[:end_index + 1].replace(name, new_format.format(name))
                            else:
                                processed += remainder[:end_index + 1]

                            if end_index is not len(remainder) - 1:
                                remainder = remainder[end_index + 1:]
                            else:
                                remainder = processed
                                break

                translated += remainder + '\n'

        return translated

    def compile(self, obj):
        should_recompile = False
        # compiling object is a function
        filename = 'arbitrary'
        if callable(obj):
            # initiation, first call
            source = self.get_content_source(obj)
            filename = obj.__module__
            varnames = obj.__code__.co_varnames
            self.namespace.add_new_variable(varnames)

        # compiling object is a string of source
        elif isinstance(obj, str):
            source = self.get_content_source(obj)
            varnames = self.search_defined_varnames_manually(source)
            # if there is a new varnames
            if self.namespace.add_new_variable(varnames):
                # recompile stored sources
                for code in self._code_dict:
                    compiled = self.compile(code)
                    # self._code_dict[code] = compiled

        # translate with namespace
        translated = self.source_replace_var_name(source, self.namespace.names)
        # compile
        code = compile(translated, filename, 'exec')
        self._code_dict[obj] = code
        return code

    def run(____, obj):
        # do nothing
        if obj is None:
            return

        if obj in ____._code_dict:
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
