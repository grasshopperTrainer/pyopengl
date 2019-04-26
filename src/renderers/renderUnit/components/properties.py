import numpy as np
from numpy.lib.recfunctions import merge_arrays, append_fields
import weakref


# class _Block:
#     def __init__(self, name, typ, val=None, loc=None, dtype=None):
#         if 'vec' in typ:
#             n = int(typ.split('vec')[1].strip())
#         elif 'sampler2D' in typ:
#             n = 1
#
#         if val is None:
#             val = (0,) * n
#         if dtype is None:
#             dtype = np.float32
#         self._array = np.zeros((1, n), dtype)
#
#         self._name = name
#         self._loc = loc
#
#         self._flag_changed = False
#
#     def __getitem__(self, item):
#         return self._array[item]
#
#     def __setitem__(self, key, value):
#         self._flag_changed = True
#         value = list(value)
#
#         if isinstance(key, int):
#             if not len(self._array) > key:
#                 self._array.resize((key,self._array.shape[1]))
#         elif isinstance(key, slice):
#             self._array.resize((key.stop,self._array.shape[1]))           # end = key.stop
#
#         for i, v in enumerate(value):
#             if self._array.shape[1] - len(v) > 0:
#                 n = self._array.shape[1] - len(v)
#                 value[i] += [0, ] * n
#             else:
#                 value[i] = v[:self._array.shape[1]]
#         self._array[key] = value
#
#     @property
#     def flag_chaged(self):
#         return self._flag_changed
#
#     @property
#     def loc(self):
#         return self._loc
#
#     @loc.setter
#     def loc(self, value):
#         if isinstance(value, int):
#             self._loc = value
#         else:
#             raise TypeError('location should be integer')
#
#     @property
#     def name(self):
#         return self._name
#
#     @property
#     def dtype(self):
#         return self._array.dtype
#
#     @dtype.setter
#     def dtype(self, value):
#         try:
#             self._array = self._array.astype(value)
#         except:
#             raise TypeError('incorrect dtype')
#
#     def __repr__(self):
#         return str(self._array)
#
#     @property
#     def flag_changed(self):
#         return self._flag_changed
class Block:
    def __init__(self, buffer, name):
        self._buffer = buffer  # type: np.ndarray
        self._name = name

        self._location = None
        self._flag_changed = False

    def __setitem__(self, key, value):
        self._flag_changed = True
        value = list(value)
        block = self._buffer[self._name]
        # add new row if calling out of index
        # for index
        if isinstance(key, int):
            # if indexing out of range add more data
            # to get to the indexed length
            if not len(block) > key:
                block.resize(key)
        # for slicing
        elif isinstance(key, slice):
            self._buffer.resize(key.stop, refcheck=False)
        # short long values to match element length of the block
        for i, v in enumerate(value):
            val_num = block.shape[1]
            if val_num > len(v):
                n = val_num - len(v)
                value[i] += [0, ] * n
            else:
                value[i] = v[:val_num]

        # put value
        self._buffer[self._name][key] = value

    def __getitem__(self, item):
        return self._buffer[self._name][item]


# class Block_modifier:
#     def __init__(self,array, name):
#         self._array = array
#         self._name = name
#
#     def __setitem__(self, key, value):
#         self._flag_changed = True
#         value = list(value)
#
#         # add new row if calling out of index
#         if isinstance(key, int):
#             if not len(self._array[self._name]) > key:
#                 self._array.resize(key)
#         elif isinstance(key, slice):
#             self._array.resize((key.stop,),refcheck = False)  # end = key.stop
#         # short long values
#         for i, v in enumerate(value):
#             val_num = self._array[self._name].shape[1]
#             if val_num > len(v):
#                 n = val_num - len(v)
#                 value[i] += [0,] * n
#             else:
#                 value[i] = v[:val_num]
#
#         # put value
#         self._array[self._name][key] = value
#
#     def __getitem__(self, item):
#         return self._array[self._name][item]

class _Property:

    def __init__(self):
        # self._blocks = {}
        self._buffer = None
        self._locations = []
        self._itercount = 0
        self._blocks = {}

    # def __iter__(self):
    #     return self
    #
    # def __next__(self):
    #     if self._itercount < len(self._blocks):
    #         self._itercount += 1
    #         return list(self._blocks.values())[self._itercount - 1]
    #     else:
    #         self._itercount = 0
    #         raise StopIteration

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

        self._blocks[name] = Block(self._buffer, name)

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


class _Uniforms:
    pass

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
        print(self.attribute.buffer, id(self.attribute.buffer))
        print(self.uniform.buffer)
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

    @property
    def blocks(self):
        a = self.attribute.blocks
        b = self.uniform.blocks
        a += b
        return a
