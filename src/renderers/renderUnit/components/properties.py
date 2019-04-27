import numpy as np
from numpy.lib.recfunctions import merge_arrays, append_fields
import weakref


class _Block:
    def __init__(self, property, name, glsltype):
        self._property = property
        self._name = name
        self._glsltype = glsltype

        self._location = None
        self._flag_changed = False

    def __setitem__(self, key, value):
        self._flag_changed = True
        if not isinstance(value[0], (tuple, list)):
            value = [list(value)]
        else:
            value = list(value)

        block = self.buffer[self._name]
        # add new row if calling out of index
        # for index
        if isinstance(key, int):
            # if indexing out of range add more data
            # to get to the indexed length
            if not len(block) > key:
                self._property._flag_new_buffer_formchange = True
                self.buffer.resize(key, refcheck=False)
            chunk_len = 1

        # for slicing
        elif isinstance(key, slice):
            stop = 0
            if key.stop is None:
                pass
            else:
                stop = key.stop
                if stop > len(block):
                    self._property._flag_new_buffer_formchange = True
                    self.buffer.resize(stop, refcheck=False)

            s = 0 if key.start is None else key.start
            e = self.buffer.size if key.stop is None else key.stop
            st = 1 if key.step is None else key.step
            chunk_len = len(range(s, e, st))

        elif key is None:
            self.buffer[self._name] = value
            return

        # short long values to match number of chunks
        # chunk_len = self.buffer.size
        if chunk_len > len(value):
            value += [[0, ]] * (chunk_len - len(value))
        elif chunk_len == len(value):
            pass
        else:
            value = value[:chunk_len]
        # short long values to match element length of the block
        for i, v in enumerate(value):
            val_num = block.shape[1]
            if val_num > len(v):
                n = val_num - len(v)
                value[i] += [0, ] * n
            else:
                value[i] = v[:val_num]

        if len(value) == 1:
            value = value[0]

        # put value
        self.buffer[self._name][key] = value
        # print(self.buffer[self._name][key].dtype)


    def __getitem__(self, item):
        return self.buffer[self._name][item]

    @property
    def block(self):
        return self._property.buffer[self._name]

    @property
    def buffer(self):
        return self._property.buffer

    @property
    def data(self):
        return self._property.buffer[self._name]

    @property
    def location(self):
        return self._location
    @property
    def name(self):
        return self._name

    @property
    def glsltype(self):
        return self._glsltype

    @property
    def is_changed(self):
        if self._flag_changed:
            self._flag_changed = False
            return True
        else:
            return False

    def __str__(self):
        d = str(self.data).splitlines()

        string = 'buffer block info:\n'
        string += f'    name     : {self._name}\n' \
            f'    glsltype : {self._glsltype}\n' \
            f'    location : {self._location}\n' \
            f'    data     : {d[0]}\n'

        for i in d[1:]:
            string += f'               {i}\n'

        return string


class _Property:

    def __init__(self):
        # self._blocks = {}
        self._buffer = None
        self._locations = []
        self._itercount = 0
        self._blocks = {}

        self._flag_new_buffer_formchange = False

    def __getitem__(self, item):
        return self._blocks[item]

    def insert_new_block(self, name, typ, val=None, loc=None, dtype=None):
        # default dtype
        if dtype is None:
            dtype = np.float32
        # number of value
        if 'vec' in typ:
            n = int(typ.split('vec')[1].strip())
        if 'sampler2D' in typ:
            n = 1
        # first call
        if self._buffer is None:
            self._buffer = np.zeros(1, ([(name, dtype, n)]))
        else:
            temp = np.zeros(len(self._buffer), [(name, dtype, n)])
            self._buffer = merge_arrays([self._buffer, temp], flatten=True)
        # dict of seperate blocks.
        # stores referenced raw array, and other information
        self._blocks[name] = _Block(self, name, typ)

        # TODO for further dynamic shader implementation
        # set statement saying form of buffer has been changed
        self._flag_new_buffer_formchange = True

    @property
    def blocks(self):
        items = [i[1] for i in list(self._blocks.items())]
        return items

    def __str__(self):
        return str(self._blocks)

    @property
    def names(self):
        try:
            return self._buffer.dtype.names
        except:
            return []
    @property
    def buffer(self):
        return self._buffer

    def set_location(self, value):
        self._locations = value

    @property
    def updated(self):
        result = []
        for block in self.blocks:
            if block.is_changed:
                result.append(block)
        return result

    @property
    def is_buffer_formchange(self):

        if not self._flag_new_buffer_formchange:
            return False
        else:
            self._flag_new_buffer_formchange = False
            return True

    def posof_block(self, name):
        return self.buffer.dtype.names.index(name)

    @property
    def locations(self):
        loc = []
        for block in self.blocks:
            loc.append(block._location)
        return loc

class Properties:

    def __init__(self, shader):
        self._shader = shader
        self._attribute = _Property()
        self._uniform = _Property()

    def __getitem__(self, item):
        if item in self._attribute.names:
            return self._attribute[item]

        elif item in self._uniform.names:
            return self._uniform[item]

        else:
            raise KeyError("glsl shader doesn't contain such name of attribute or uniform")

    def __setitem__(self, key, value):
        if key in self.attribute.names:
            self.attribute._blocks[key].__setitem__(None, value)
        elif key in self.uniform.names:
            self.uniform._blocks[key].__setitem__(None, value)

        else:
            raise KeyError("glsl shader doesn't contain such name of attribute or uniform")

    # def __setitem__(self, key, value):
    #     pass

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

    @property
    def blocks(self):
        a = self.attribute.blocks
        b = self.uniform.blocks
        a += b
        return a

    @property
    def buffer_formchanged(self):
        cond_properties = []

        if self.attribute.is_buffer_formchange:
            cond_properties.append(self.attribute)
        if self.uniform.is_buffer_formchange:
            cond_properties.append(self.uniform)

        return cond_properties
