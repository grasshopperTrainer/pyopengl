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

            # else if context is import ~
            elif line.find('import ') == 0:
                if ' as ' in line:
                    value = line.split('import ')[1].split(' as ')[0].strip()
                    name = line.split(' as ')[1].strip()

            name_value[name] = value

        if return_sign is None:
            return name_value
        elif return_sign:
            return tuple(name_value.values())
        else:
            return tuple(name_value.keys())

    @classmethod
    def search_body_variables(cls, obj):
        obj = Source(obj)
        source = obj.lines

        name_value = {}
        for line in source:
            if line.find('#') == 0:
                continue
            elif line.find('import ') == 0:
                continue
            elif line.find('from ') == 0:
                continue

            print(line)

        return name_value

    @classmethod
    def search_all_variables(cls, obj):
        a = cls.search_imports(obj)
        b = cls.search_body_variables(obj)
        a.update(b)
        return a


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
            return self.source.splitlines()
        elif self.type == 2:
            return self._obj
