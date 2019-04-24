import numpy as np
import weakref


class _Block:
    def __init__(self, name, typ, val=None, loc=None, dtype=None):
        if 'vec' in typ:
            n = int(typ.split('vec')[1].strip())
        elif 'sampler2D' in typ:
            n = 1

        if val is None:
            val = (0,) * n
        if dtype is None:
            dtype = np.float32
        self._array = np.zeros((1, n), dtype)

        self._name = name
        self._loc = loc

        self._flag_changed = False

    def __getitem__(self, item):
        return self._array[item]

    def __setitem__(self, key, value):
        self._flag_changed = True
        value = list(value)

        if isinstance(key, int):
            if not len(self._array) > key:
                n = len(self._array[0])
                sub = np.array((0,) * n)
                self._array = np.insert(self._array, len(self._array), sub, 0)
            self._array[key] = value
        elif isinstance(key, slice):
            end = key.stop
            start = len(self._array)
            sub = np.array((0,) * self._array.shape[1])
            for i in range(start, end):
                self._array = np.insert(self._array, i, sub, 0)
            for i, v in enumerate(value):
                if self._array.shape[1] - len(v) > 0:
                    n = self._array.shape[1] - len(v)
                    value[i] += [0, ] * n
                else:
                    value[i] = v[:self._array.shape[1]]
            self._array[key] = value

    @property
    def flag_chaged(self):
        return self._flag_changed

    @property
    def loc(self):
        return self._loc

    @loc.setter
    def loc(self, value):
        if isinstance(value, int):
            self._loc = value
        else:
            raise TypeError('location should be integer')

    @property
    def name(self):
        return self._name

    @property
    def dtype(self):
        return self._array.dtype

    @dtype.setter
    def dtype(self, value):
        try:
            self._array = self._array.astype(value)
        except:
            raise TypeError('incorrect dtype')

    def __repr__(self):
        return str(self._array)

    @property
    def flag_changed(self):
        return self._flag_changed


class _Property:

    def __init__(self):
        self._blocks = {}
        self._buffer = None
        self._itercount = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._itercount < len(self._blocks):
            self._itercount += 1
            return list(self._blocks.values())[self._itercount - 1]
        else:
            self._itercount = 0
            raise StopIteration

    def __getitem__(self, item):
        return self._blocks[item]

    def insert_new_block(self, name, typ, val=None, loc=None, dtype=None):
        self._blocks[name] = _Block(name, typ, val, loc, dtype)

    def __str__(self):
        return str(self._blocks)

    @property
    def blocks(self):
        return self._blocks

    @property
    def buffer(self):
        print(self.blocks)


class Properties:

    def __init__(self, shader):
        self._shader = shader
        self._attribute = _Property()
        self._uniform = _Property()

    def __getitem__(self, item):
        if item in self._attribute._blocks:
            return self._attribute[item]  # type:_Block
        elif item in self._uniform._blocks:
            return self._uniform[item]  # type:_Block
        else:
            raise KeyError("glsl shader doesn't contain such name of uniform")

    def new_attribute(self, name, typ, val=None, loc=None, dtype=None):
        self._attribute.insert_new_block(name, typ, val, loc)
        pass

    def new_uniform(self, name, typ, val=None, loc=None, dtype=None):
        self._uniform.insert_new_block(name, typ, val, loc)
        pass

    @property
    def attribute(self):
        return self._attribute

    @property
    def uniform(self):
        return self._uniform

    @property
    def is_updated(self):
        blocks = self.attribute.blocks
        for name in blocks:
            block = blocks[name]
            if block.flage_changed:
                buffer = self.attribute.buffer
        self.uniform.bu
        self._attribute
        return

    def info(self):
        string = f'glsl properties of (Shader){self._shader}:\n'
        for i in ('attribute', 'uniform'):
            head = f'    {i}:\n'
            body = ''
            for block in eval(f'self.{i}'):
                body += f'      {block.name} :\n'
                d = ['            ' + line for line in str(block).splitlines()]
                for i in d:
                    body += i + '\n'
            string += head + body + '\n'
        return string

    def __str__(self):
        return f'glsl properties of (Shader){self._shader}'
