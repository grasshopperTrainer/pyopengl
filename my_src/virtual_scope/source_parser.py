import inspect
from functools import reduce


class Source_parser:

    def __new__(cls, *args, **kwargs):
        raise SyntaxError("use static methods only")

    @classmethod
    def split_func_headbody(cls, func, return_sign=None, as_list=False):
        source = Source(func)
        source = source.lines

        indent = cls.count_source_indent(func)

        if source[0].strip()[0] == '@':
            head = source[:2]
            body = source[2:]
        else:
            head = source[:1]
            body = source[1:]

        if as_list:
            body = list(map(lambda x: x[indent + 4:], body))
        if not as_list:
            head = reduce(lambda x, y: x + '\n' + y, head)
            body = reduce(lambda x, y: x + '\n' + y, map(lambda x: x[indent + 4:], body)) + '\n'

        if return_sign is None:
            return (head, body)
        elif return_sign:
            return body
        else:
            return head

    @classmethod
    def search_func_name(cls, obj):
        if callable(obj):
            header = Source_parser.split_func_headbody(obj, 0, True)
            for line in header:
                if line.finde('def ') == 0:
                    name = line.split('def ')[1].split('(')[0].strip()
                    return name

        elif isinstance(obj, str):
            try:
                return obj.split('def ')[1].split('(')[0].strip()
            except:
                return None

        elif isinstance(obj, list):
            if all([isinstance(line) for line in obj]):
                for line in obj:
                    try:
                        return obj.split('def ')[1].split('(')[0].strip()
                    except:
                        return None

        # if search fails
        return None

    @classmethod
    def get_source(cls, obj, as_list=False):
        if callable(obj):
            return inspect.getsource(obj)
        elif isinstance(obj, str):
            return obj.splitlines()
        elif isinstance(obj, list):
            if all([isinstance(line) for line in obj]):
                return obj
        else:
            raise TypeError('type incorrect')

    @classmethod
    def type(cls, obj):
        if callable(obj):
            return 0
        elif isinstance(obj, str):
            return 1
        elif isinstance(obj, list):
            if all([isinstance(line) for line in obj]):
                return 2
        else:
            raise TypeError('type incorrect')

    @classmethod
    def count_source_indent(cls, obj):
        obj = Source(obj)
        indent = 0
        for l in obj.source:
            if l == ' ':
                indent += 1
            else:
                break
        return indent

    @classmethod
    def clean_indent(cls, obj):
        indent = Source_parser.count_source_indent(obj)

    @classmethod
    def strip_source(cls, source):
        if isinstance(source, str):
            pass
        elif isinstance(source, list):
            pass
        else:
            Source_parser._typeError()

    @classmethod
    def search_imports(cls, obj, return_sign=None):
        """
        the function doesn't check python syntax.
        input sould be syntactically correct.
        :param obj:
        :return:
        """
        obj = Source(obj)

        source = obj.lines
        name_value = {}

        for line in source:
            # for module import
            # if context is from ~ import
            if line.find('from ') == 0:

                mark = ' import ' if ' import ' in line else ' as '
                value = line.split('from ')[1].split(mark)[0].strip()
                name = line.split(mark)[1].strip()

                name_value[name] = value

            # else if context is import ~
            elif line.find('import ') == 0:
                if ' as ' in line:
                    value = line.split('import ')[1].split(' as ')[0].strip()
                    name = line.split(' as ')[1].strip()
                else:
                    name = line.split('import ')[1].strip()
                    value = name

                name_value[name] = value

        if return_sign is None:
            return name_value
        elif return_sign:
            return tuple(name_value.values())
        else:
            return tuple(name_value.keys())

    @classmethod
    def search_assigned_variables(cls, obj):
        obj = Source(obj)
        source = obj.lines

        names = []
        for line in source:
            if line.find('#') == 0:
                continue
            elif line.find('import ') == 0 or line.find('from ') == 0:
                continue
            elif line.find('def ') == 0:
                continue
            elif line.find('class ') == 0:
                continue
            else:
                quot_poses = cls.search_quotation_pos(line)

                # look for what? 1. = and .(dot)
                if '=' in line:
                    quot = False
                    for pos in quot_poses:
                        if pos[0] < line.find('=') < pos[1]:
                            quot = True
                    if quot:
                        pass
                    else:
                        # = mark is not inside the quot
                        name = line.split('=')[0].strip()
                        if name.find('.') == -1 and name not in names:
                            names.append(name)

        return names

    @classmethod
    def search_def(cls, obj):
        source = Source(obj)

    @classmethod
    def search_quotation_pos(cls, line):

        poses = []
        start = 0
        while True:
            a = line.find("'", start)
            b = line.find('"', start)
            if a != -1 and (a < b or b == -1):
                start = a
                mark = "'"
            elif b != -1 and (b < a or a == -1):
                start = b
                mark = '"'
            else:
                break

            end = line.find(mark, start + 1)
            if end == -1:
                start = end + 1
            else:
                poses.append((start, end))
                if end == len(line) - 1:
                    break
                else:
                    start = end + 1

        if len(poses) == 0:
            return ((-1, -1),)
        else:
            return tuple(poses)

    @classmethod
    def search_all_variables(cls, obj):
        a = cls.search_imports(obj, 0)
        b = cls.search_assigned_variables(obj)

        r = set(a).union(set(b))
        return tuple(r)

    @classmethod
    def replace_names(cls, source, old, new):

        source = Source(source).lines
        translated = ''

        for line in source:
            # if empty
            if len(line.strip()) == 0:
                translated += line + '\n'
                continue
            # if decorator
            elif line[0] == '@':
                translated += line + '\n'
                continue
            # if comment
            elif line.strip()[0] == '#':
                translated += line + '\n'
                continue

            elif line.find('import ') == 0 or line.find('from ') == 0:
                name = cls.search_imports(line, 0)[0]
                i = old.index(name)
                translated += line + '\n'
                translated += f'{new[i]} = {name}\n'
                continue

            left = ''
            right = line
            # if not comment
            for name, replacement in zip(old, new):
                while len(right) != 0:
                    # print()
                    # print('start:')
                    # print('left;', left)
                    # print('right:', right)
                    # print('name:', name)
                    # if there is a candidate
                    if name in right:
                        # print('---------')
                        # print(name)
                        # print(left)
                        # print(right)
                        # print()
                        poses = cls.search_quotation_pos(right)
                        quot = False

                        for i, pos in enumerate(poses):
                            if pos[0] < right.find(name) < pos[1]:
                                quot = True
                                where = i
                                break

                        if quot:
                            left += right[:poses[where][1] + 1]
                            right = right[poses[where][1] + 1:]
                            continue

                        else:
                            # need to check if it full name
                            cond_right = True
                            cond_left = True
                            start_i = right.find(name)
                            end_i = start_i + len(name) - 1
                            if start_i != 0:
                                l = right[start_i - 1]
                                conditions = [
                                    l.isnumeric(),
                                    l.isalpha(),
                                    l == '.',
                                    l == '_'
                                ]
                                if sum(conditions) > 0:
                                    cond_left = False

                            if end_i != len(right) - 1:
                                r = right[end_i + 1]
                                conditions = [
                                    r.isnumeric(),
                                    r.isalpha(),
                                    r == '_'
                                ]
                                if sum(conditions) > 0:
                                    cond_right = False

                            # its a name!
                            if cond_left and cond_right:

                                left += right[:end_i + 1].replace(name, replacement)
                                right = right[end_i + 1:]
                            # not a name
                            else:
                                left += right[:end_i + 1]
                                right = right[end_i + 1:]

                    # no candidate
                    else:
                        left += right
                        break

                # all replaced for one name
                right = left
                left = ''

            # all names looked through
            translated += right + '\n'
        # all lines looked through
        return translated

    @classmethod
    def source(cls, obj):
        return Source(obj).source


class Source:
    def __init__(self, obj):
        self._itercount = 0
        self._obj = obj

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        return self

    def __next__(self):
        self._temp = self.lines
        if self._itercount < len(self._temp):
            self._itercount += 1
            return self._temp[self._itercount - 1]
        else:
            self._itercount = 0
            del self._temp
            raise StopIteration

    # @staticmethod
    # def clean_source(source):
    #     source = source.splitlines()
    #
    #     # find valid first line
    #     first_line = ''
    #     first_line_i = 0
    #     for i, line in enumerate(source):
    #         if line.strip()[0] == '\n':
    #             continue
    #         if line.strip()[0] == '#':
    #             continue
    #         else:
    #             first_line = line
    #             first_line_i = i
    #             break
    #
    #     # look for margin
    #     margin = 0
    #     for l in first_line:
    #         if l == ' ':
    #             margin += 1
    #         else:
    #             break
    #
    #     # remove margins
    #     for i, line in enumerate(source):
    #         if line.strip()[0] == '#':
    #             i = line.find('#')
    #             move = margin - i
    #             # if comment is in fron margin push
    #             if move > 0:
    #                 source[i] = ' ' * move + line
    #         else:
    #             source[i] = line[margin:]
    #
    #     return source

    @property
    def type(self):
        if callable(self._obj):
            return 0
        elif isinstance(self._obj, str):
            return 1
        elif isinstance(self._obj, (list, tuple)):
            if all([isinstance(line) for line in obj]):
                return 2
        else:
            raise TypeError('unsuppored type')

    @property
    def source(self):
        if self.type == 0:
            return inspect.getsource(self._obj)

        elif self.type == 1:

            if self.indent > 0:
                source = self._obj.splitlines()
                self._obj = reduce(lambda x, y: x + '\n' + y, map(lambda x: x[self.indent:], source))
            return self._obj

        elif self.type == 2:
            self._obj = [line[self.indent:] for line in self._obj]
            merged = reduce(lambda x, y: x + '\n' + y, self._obj)
            return merged

    @property
    def indent(self):
        if self.type == 0:
            return 0

        elif self.type == 1:
            indent = 0
            for l in self._obj:
                if l == ' ':
                    indent += 1
                elif l == '#':
                    if '\n' in self._obj:
                        splited = self._obj.split('\n')
                        self._obj = splited[1]
                        sub_indent = self.indent
                        to_move = indent - sub_indent
                        if to_move >= 0:
                            self._obj = splited[0][to_move:] + '\n' + self._obj
                        else:
                            self._obj = ' ' * (-to_move) + splited[0] + '\n' + self._obj
                        return sub_indent
                else:
                    break
            return indent

        elif self.type == 2:
            line = self._obj[0]
            indent = 0
            for l in self._obj:
                if l == ' ':
                    indent += 1
                else:
                    break
            return indent

    @property
    def lines(self):
        if self.type == 0:
            return self.source.splitlines()
        elif self.type == 1:
            return self._obj.splitlines()
        elif self.type == 2:
            return self._obj
