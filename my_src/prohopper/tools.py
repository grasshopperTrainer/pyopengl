# from .primitives import *
from .constants import *

import numpy as np
import copy
import inspect
import weakref
from typing import *
from numbers import Number
from .errors import *
from .constants import *

# def mymethod(func):
#     args_names, var_args, var_kwargs, defaults, kwonlyargs, kwonlydefaults,annotations = inspect.getfullargspec(func)
#
#     def wrapper(*args, **kwargs):
#         # TODO just enough for now need improvement?
#         # input checking
#         if var_args == None and var_kwargs == None:
#             given = len(args)+ len(kwargs)
#             if defaults == None:
#                 if given != len(args_names):
#                     raise TypeError('missing argument')
#             else:
#                 if not (given  >= len(args_names) - len(defaults) and given <= len(args_names)):
#                     # print(args, kwargs, args_names)
#                     # print(args_names)
#                     # print(var_args)
#                     # print(var_kwargs)
#                     # print(defaults)
#                     # print(kwonlyargs)
#                     # print(kwonlydefaults)
#                     # print(annotations)
#                     raise TypeError('missing argument')
#         else:
#             if len(args)+ len(kwargs) < len(args_names):
#                 raise
#
#         # type checking
#         # need to build combined args list first
#         arg_dict = {}
#         args_list = args[len(args_names):]
#         kwargs_dict = {}
#         for a_name,a in zip(args_names, args):
#             arg_dict[a_name] = a
#         for a in kwargs:
#             # if given input is not a part of kwargs but args but given with name
#             if a in args_names:
#                 # if its not for one that's already given through *args
#                 if not a in arg_dict:
#                     arg_dict[a] = kwargs[a]
#                 else:
#                     raise
#             else:
#                 # real kwargs
#                 kwargs_dict[a] = kwargs[a]
#
#         # for arguments
#         for a_name,a in arg_dict.items():
#             # if it has type hint
#             if a_name in annotations:
#                 types = annotations[a_name]
#                 if isinstance(types, (list, tuple)):
#                     istype = False
#                     # if arg can be one of types
#                     for t in types:
#                         if isinstance(a,t):
#                             istype = True
#                     if not istype:
#                         raise TypeError
#                 elif isinstance(types, type(List)):
#                     pass
#                 elif not isinstance(a, types):
#                     raise WrongInputTypeError(a, types)
#
#         # for variable arguments
#         if var_args in annotations:
#             types = annotations[var_args]
#             for a in args_list:
#                 if isinstance(types, (list, tuple)):
#                     istype = False
#                     for t in types:
#                        if isinstance(a, t):
#                            istype = True
#                     if not istype:
#                         raise TypeError
#                 elif isinstance(types, type(List)):
#                     pass
#                 elif not isinstance(a, types):
#                     raise WrongInputTypeError(a, types)
#
#         # for variable keyword arguments
#         if var_kwargs in annotations:
#             types = annotations[var_kwargs]
#             types = list(types)
#             for a in kwargs_dict.values():
#                 if isinstance(types, (tuple, list)):
#                     istype = False
#                     for t in types:
#                         if isinstance(a, t):
#                             istype = True
#                     if not istype:
#                         raise TypeError
#                 elif isinstance(types, type(List)):
#                     pass
#                 elif not isinstance(a, types):
#                     raise TypeError
#
#         return func(*args, **kwargs)
#
#     return wrapper

def list_executer(func, args, kwargs):
    pass

class Primitive:
    DIC = {}
    DATATYPE = np.float32
    TOLORENCE = 1.e-9

    def __init__(self, data, title: str = None):
        """
        Parent of all tools_building classes.
        rule#1_ in child class functions never return Hlist
        - add functions for general management and meta control -
        :param data:
        :param title:
        """
        # make new dict for child class
        if self.DIC == Primitive.DIC:
            self.__class__.DIC = {}

        # make name for indexing
        if title is None:
            title = str(len(self.keys()) + 1)
        self._dict_insert_unique(self.__class__.DIC, title, data)
        self._data = data

    def _dict_insert_unique(self, dic: dict, key: str, value=None, preffix: str = 'new_', suffix: str = ''):
        key_list = list(dic.keys())

        def make_unique_name(source: list, target: str, preffix: str, suffix: str):
            # function for detecting coincident name
            new_name = target
            for i in source:
                if i == target:
                    source.remove(i)
                    new_target = preffix + target + suffix
                    new_name = make_unique_name(source, new_target, preffix, suffix)
                    """
                    If coincident name is found, There is no need to continue iteration.
                    Else recursion is called to compare with the elements that were passed
                    in front in parent iteration. Coincident element is removed from
                    the original list to avoid pointless iteration.
                    """
                    break
            # finishing condition for recursive action
            # return value only if 'for' is fully iterated -
            # without getting into 'if' branch
            return new_name

        dic[make_unique_name(key_list, key, preffix, suffix)] = value

    def __call__(self):
        return self._data

    @classmethod
    def get_from_dic(cls, title: str):
        return cls.dic[title]

    @classmethod
    def make_new(cls, data, title: str = None):
        instance = cls(cls.DIC, data, title)

    @classmethod
    def get_dic(cls):
        return cls.DIC

    @classmethod
    def keys(cls):
        return cls.DIC.keys()

    def print_data(self):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}'

    # def set_data(self, data):
    #     # to ensure all the proceeding numpy calculation efficient
    #     if isinstance(data, np.ndarray):
    #         data = self.__class__.DATATYPE(data)
    #     self._data = data

    # def get_data(self):
    #     return self._data

    def printmessage(self, text: str, header: str = 'ERROR '):
        func_name = inspect.currentframe().f_back.f_code.co_name
        fullvarinfo = inspect.getargvalues(inspect.currentframe().f_back)
        varvalue = [fullvarinfo[3][i] for i in fullvarinfo[0]]
        varinfo = []
        for name, value in zip(fullvarinfo[0], varvalue):
            varinfo.append(f'{name} : {str(value)}')

        head = f'FROM {self.__class__.__name__}.{func_name}: '

        varhead = ' ' * (len(head) - 6) + 'ARGS: ' + varinfo[0]
        for i, j in enumerate(varinfo):
            varinfo[i] = ' ' * len(head) + j

        top = header + '-' * (len(head + text) - len(header))
        bottom = '-' * len(head + text)

        lines = top, head + text, varhead, *varinfo[1:], bottom

        for i in lines:
            print(i)


class Item:

    def __init__(self, data):
        if not isinstance(data, Item):
            self._data = data
        else:
            self._data = data._data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self._data

    def __setitem__(self, key, value):
        self._data = value

    def __call__(self):
        return self._data

    def __add__(self, other):
        return self._data + other._data

    def set_data(self, v):
        self.__init__(v)

    def type(self):
        return self._data.__class__


# A stands for array? array list?
class Tlist(Primitive):

    def __init__(self, data: (list, tuple)):
        """
        write cases and rules
        rule 1: Tlist either leaf or node
        rule 2: leafs can contain any generics
        rule 3: nods can contain only other Tlists
        rule 4: input data should be given as list representing structure?
        rule 5: if a user want to put generic iterables,
        other function will be provided

        case1 input generics and make leaf
        case2 input Tlists and make node
        :param data:
        """

        self._data = []
        # check input type
        if not isinstance(data, (list, tuple)):
            self.printmessage('input should be list or tuple')
            return None

        self._data = self._parslist(data)
        self._checkifleaf()

    def _parslist(self, input: list):

        # if all([isinstance(i,Item) for i in input]):
        #     return input

        if all([not isinstance(i, (list, tuple, Tlist)) for i in input]):
            referenced = []
            for i in input:
                if isinstance(i, Item):
                    referenced.append(i)
                else:
                    referenced.append(Item(i))
            return referenced

        else:
            self._isleaf = False
            parsed = []
            for i in input:
                '''
                for example input is very complex:
                [0,2,[2,3],Tlist,[Tlist,Tlist]]
                target1 : generics? no generics remove this
                target2 : Tlist
                target3 : (list, tuple)
                I'm gonna read from above into bottom
                should i match the length of all branches?

                '''
                if not isinstance(i, (tuple, list, Tlist)):
                    self.printmessage('inputs must be tuple, list, or Tlist')
                    break
                elif isinstance(i, (tuple, list)):

                    branch = Tlist(self._parslist(i))
                    branch._checkifleaf()
                    parsed.append(branch)
                elif isinstance(i, Tlist):
                    i._checkifleaf()
                    parsed.append(i)
            return parsed

    def _checkifleaf(self):
        a = all([isinstance(i, Item) for i in self.get_data()]) and len(self.get_data()) is not 0
        if len(self.get_data()) is 0:
            a = True
        self._isleaf = a

    def append(self, shape):
        pass

    def insert(self, shape):
        pass

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __add__(self, object):
        try:
            if self.isleaf() and object.isleaf():
                return Tlist(self.get_data() + object.get_data())
            else:
                # newdata = []
                # if self.isleaf():
                #     newdata.append(self)
                # else:
                #     newdata += self.get_data()
                #
                # if object.isleaf():
                #     newdata.append(object)
                # else:
                #     newdata += object.get_data()
                return Tlist([self, object])

        except:
            self.printmessage("can't add object")
            return self

    def add(self, object):
        a = copy.copy(self) + object
        self.set_data(a.get_data())

    def tile(self, length: int):
        data = self._data
        d = divmod(length, len(data))
        self.set_data(data * d[0] + data[:d[1]])

    def __getitem__(self, item):
        # if item is not multiple...
        if not isinstance(item, tuple):
            # base condition
            if self.isleaf():
                """
                supports several syntax for easy editing
                1. [x] integer
                2. [x:y] slice
                3. [[x,y,z]] integers
                4. [...] ellipsis
                """
                try:
                    if isinstance(item, int):
                        # to find value over index
                        datalength = len(self._data)
                        if item >= datalength:
                            item -= datalength
                        elif item < -len(self._data):
                            item += datalength
                        # ???
                        return self._data[item]
                    elif isinstance(item, (slice, int)):
                        return Tlist(self._data[item])
                    elif isinstance(item, list):
                        items = []
                        for i in item:
                            items.append(self._data[i])
                        return Tlist(items)
                    elif item is Ellipsis:
                        return self.get_data()
                    else:
                        self.printmessage('indexing type incorrect')
                        return None

                except:
                    self.printmessage('index out of bound')
                    return None
            else:
                if isinstance(item, (slice, int)):
                    newdata = self.get_data()[item]
                    if isinstance(newdata, Tlist):
                        return newdata
                    else:
                        return Tlist(newdata)
                elif isinstance(item, list):
                    branches = []
                    for i in item:
                        branches.append(self[i])
                    return Tlist(branches)
                elif item is Ellipsis:
                    print('get with ellipsis')
                    return self
        else:

            itemfront = item[0]
            itemnext = item[1:]
            if len(itemnext) is 1:
                itemnext = itemnext[0]
            """
            how many cases?
            1.int x
            2.list containing ints [x,y]
            3.slice [:]
            4.ellipsis [...]
            """
            if isinstance(itemfront, int):
                return self[itemfront][itemnext]
            elif isinstance(itemfront, list):
                if self.isleaf():
                    return self[itemfront][itemnext]
                else:
                    branches = []
                    for i in itemfront:
                        branches.append(self._data[i][itemnext])
                    return Tlist(branches)
            elif isinstance(itemfront, slice):

                if self.isleaf():
                    return self[itemfront][itemnext]
                else:
                    branches = self._data[itemfront]
                    for i, v in enumerate(branches):
                        branches[i] = v[itemnext]
                        if not isinstance(branches[i], Tlist):
                            branches[i] = Tlist([branches[i]])
                    # isalltlists = [isinstance(i,Tlist) for i in branches]
                    # isallprims = all([not i for i in isalltlists])
                    # isalltlists = all(isalltlists)
                    # ismixed = isallprims or isalltlists
                    # # print()
                    # # print(branches,ismixed)
                    # if not ismixed:
                    #     for i,v in enumerate(branches):
                    #         if not isinstance(v,Tlist):
                    #             branches[i] = Tlist([v])
                    # # print(branches)
                    return Tlist(branches)
            elif itemfront is Ellipsis:
                maxdepth = self.get_maxdepth()
                if isinstance(itemnext, tuple):
                    lennext = len(itemnext)
                else:
                    lennext = 1
                newitem = [slice(None, None, None)] * (maxdepth - lennext)

                if not isinstance(itemnext, tuple):
                    newitem.append(itemnext)
                else:
                    newitem += itemnext
                return self[tuple(newitem)]
            else:
                self.printmessage('incorrect item type')
                raise

    def get_maxdepth(self, _count=1):
        depths = []
        for i in self._data:
            if not isinstance(i, Item):
                depths.append(i.get_maxdepth(_count=_count + 1))
            else:
                return _count
            # return depths
            # depths.append(_count)
        return max(depths)

    def __setitem__(self, key, value):
        print('set')
        """
        cases
        1. key is slice [:]
        2. key is single integer [x]
        3. key is multiple integers [x,y,z]
        4. ellipsis [...]
        :param key:
        :param value:
        :return:
        """
        # make input iterable(list)
        if not isinstance(value, tuple):
            value = [value]
        else:
            value = list(value)

        # input check first all has to be tlist or not tlists
        # try:
        istlists = [isinstance(i, Tlist) for i in value]
        isprims = all([not i for i in istlists])
        istlists = all(istlists)
        # if data types are coherent proceed
        if isprims or istlists:
            # case 1,2
            if isinstance(key, (slice, int)):
                # transform integer into slice
                if isinstance(key, int):
                    if key < 0:
                        key = key + len(self._data)
                    key = slice(key, key + 1)
                # case data is branches
                if istlists:
                    # branches replace items
                    if self.isleaf():
                        newtree = self[:key.start] + self[key] + self[key.stop:]
                        self.set_data(newtree.get_data())
                    # branches replace branches
                    else:
                        self._data[key] = value
                # case data is python primitives
                else:
                    # primitives replace items
                    if self.isleaf():
                        value = [Item(i) for i in value]
                        self._data[key] = value
                    # primitives replace branches
                    else:
                        self.printmessage("can't replace branches with items", 'ANNOUNCE')
                        raise
            # case 3
            elif isinstance(key, tuple):
                # need to match number of value
                # match length to key len
                d = divmod(len(key), len(value))
                matched = []
                for i in range(d[0]):
                    if i is 0:
                        matched += value
                    else:
                        matched += copy.deepcopy(value)
                matched += copy.deepcopy(value)[:d[1]]
                for k, v in zip(key, matched):
                    self.__setitem__(k, v)

            # case 4
            elif key is Ellipsis:
                print('set with ellipsis')
                pass
            # false case
            else:
                self.printmessage('key type incorrect')

        # except:
        #     self._printmessage('input types incorrect')
        #     pass

    def set_data(self, data):
        ids = []
        for i, v in enumerate(data):
            ids.append(id(v))
            if id(v) in ids:
                data[i] = copy.deepcopy(v)
            if not isinstance(data[i], Tlist):
                data[i] = Item(data[i])
        self._data = data
        self._checkifleaf()

    # def view(self):
    #     return Tlist([self])

    def isleaf(self):
        return self._isleaf

    def get_allleafs(self):
        leafs = []
        if self.isleaf():
            leafs.append(self)
        else:
            for i in self.get_data():
                leafs += i.get_allleafs()
        return leafs

    def get_allitems(self):
        items = []
        if self.isleaf():
            items += self.get_data()
            return items
        else:
            for i in self.get_data():
                items += i.get_allitems()

        return items

    def items(self, _count=0):
        return Tlist(self.get_allitems())

    def leafs(self):
        return Tlist(self.get_allleafs())

    def isleafsonly(self):
        return all([i.isleaf() for i in self])

    def pickleafs(self):
        self.set_data(self.get_allleafs())

    def growequal(self):
        if self.isleaf():
            return self
        else:
            branches = []
            allleafs = all([i.isleaf() for i in self.get_data()])
            if not allleafs:
                for i in range(len(self.get_data())):
                    if self[i].isleaf():
                        self[i].set_data(Tlist([self[i]]))
                    else:
                        pass
                newbranches = []
                for i in self:
                    newbranches += i.get_data()

                allleafs = all([i.isleaf() for i in newbranches])
                if not allleafs:
                    Tlist(newbranches).growequal()
                else:
                    pass

    def pruneall(self):
        if self.isleaf():
            return True
        else:
            for i in self:
                if i.isleaf():
                    pass
                elif len(i) is 1:
                    cut = True
                    while cut:
                        data = i.get_data()[0].get_data()

                        i.set_data(data)
                        if i.isleaf():
                            cut = False
                else:
                    pass
            # check
            branches = []
            for i in self:
                if not i.isleaf():
                    branches += i.get_data()
            a = Tlist(branches)
            a.pruneall()

    def flatten(self, _count=0):
        self.set_data(self.get_allitems())

    def __len__(self):
        return len(self._data)

    def prunebottom(self, times: int = 1):
        # repeat
        for i in range(times):
            if not self.isleaf():
                branches = []
                numsimple = 0
                for i in self:

                    if i.isleaf():
                        branches.append(i)
                        numsimple += 1
                    else:
                        a = i.get_data()
                        branches += i.get_data()

                # incase unwrapping when reached clean 2D structure
                if numsimple is len(self.get_data()):
                    flattened = []
                    for i in branches:
                        flattened += i.get_data()
                    branches = flattened
                self.set_data(branches)
            else:
                self.printmessage('Tlist is already flat', 'ANNOUNCE')
                break

    def growbottom(self, times: int = 1):

        for i in range(times):
            self.__init__([self.get_data()])
            copy.copy(self)
            # self.set_data([Tlist(self._data)])

    def print_data(self, strings=False, _count=0):
        lu = u'\u2554'
        ru = u'\u2557'
        ld = u'\u255a'
        rd = u'\u255d'
        vr = u'\u2551'
        hr = u'\u2550'
        lines = []
        # base condition
        if self.isleaf():
            # condition for empty list
            if len(self.get_data()) is not 0:
                types = []
                texts = []
                lentypes = []
                lentexts = []
                for i in self.get_data():
                    types.append(i.type().__name__)
                    texts.append(str(i))
                    lentypes.append(len(str(i.type())))
                    lentexts.append(len(str(i)))

                max_lentype = max(lentypes)
                max_lentext = max(lentexts)
                checkodd = ' ' * ((max_lentype + max_lentext + 1) % 2)  # add extra space to align
                # format to match length of text line
                types = [j + ' ' * (max_lentype - lentypes[i]) for i, j in enumerate(types)]
                texts = [j + ' ' * (max_lentext - lentexts[i]) for i, j in enumerate(texts)]
                lines = [vr + i + ':' + j + checkodd + vr for i, j in zip(types, texts)]
                top = lu + hr * (len(lines[0]) - 2) + ru
                bottom = ld + hr * (len(lines[0]) - 2) + rd
                lines.insert(0, top)
                lines.append(bottom)

            else:

                lines.append(lu + hr + ru)
                lines.append(ld + hr + rd)

        # recursion
        else:
            lines = []
            blocklen = []

            for i in self._data:
                data = i.print_data(_count=_count + 1)
                lines += data
                blocklen.append(len(data[0]))

            # for empty leaf
            try:
                max_blocklen = max(blocklen)
            except:
                max_blocklen = 0

            # wrap for parent dimension
            for i in range(len(lines)):
                line = lines[i]
                # format style: match position of dimension closure
                if line[0] == vr:
                    lines[i] = vr + line[0] + line[1:-1].center(max_blocklen - 2) + line[-1] + vr
                else:
                    lines[i] = vr + line[0] + line[1:-1].center(max_blocklen - 2, hr) + line[-1] + vr
            # enclose blocks
            top = lu + hr * (max_blocklen) + ru
            bottom = ld + hr * (max_blocklen) + rd
            lines.insert(0, top)
            lines.append(bottom)

        # when recursion is over print
        if _count is 0:
            if strings:
                return lines
            else:
                for i in lines:
                    print(i)
        else:
            return lines

    def null(self):
        items = self.get_allitems()
        for i in items:
            i[0] = None

    def empty(self):
        leafs = self.leafs()
        for i in leafs:
            i.set_data([])


class Raw_array:
    def __init__(self):
        self._d = weakref.WeakKeyDictionary()

    def __set__(self, instance, value):
        self._d[instance] = np.array(value, dtype=np.float64)

    def __get__(self, instance, owner):
        try:
            return self._d[instance]
        except:
            return None

class Geometry(Primitive):
    _raw = Raw_array()

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        raise Exception('not defined for this primitive yet')

    # def bymatrix(self, value):
    #     if isinstance(value, np.ndarray):
    #         self.data = value
    #     else:
    #         self.printmessage("input isn't matrix")
    #     return self

    @property
    def numvertex(self):

        return self().shape[1]

    @property
    def length(self):
        if self.numvertex is 1:
            return None
        else:
            segments = self.segments
            length = 0
            for i in segments:
                vec = i.vertices[1] - i.vertices[0]
                length += np.linalg.norm(vec())
            return length

    @property
    def segments(self):
        lines = []

        vertex = self.vertex

        for i in range(self.numvertex):
            v1 = vertex[i]
            if i is self.numvertex - 1:
                v2 = vertex[0]
            else:
                v2 = vertex[i + 1]
            lines.append(Line(v1, v2))
        return lines

    @property
    def matrix(self):
        pass

    @matrix.setter
    def matrix(self, value):
        pass

    def __repr__(self):
        return self.__str__()

    @property
    def raw(self) -> np.ndarray:
        return self._raw

    @raw.setter
    def raw(self, v):
        self._raw = v


class Domain2d(Primitive):
    '''
    ???
    '''

    def __init__(self, domain1, domain2):
        self.set_data([domain1, domain2])
        pass


class Domain(Primitive):
    def __init__(self, start: (int, float) = None, end: (int, float) = None):
        if start is None and end is None:
            self.set_data(np.array([0, 1]))
        else:
            if end is None and start is not 0:
                self.set_data(np.array([0, start]))
            else:
                if start is not end:
                    self.set_data(np.array([start, end]))
                else:
                    self._0lengthexception()
                return

        self.start = None
        self.end = None
        self.length = None

    def _0lengthexception(self):
        self.printmessage("can't make 0 length domain", 'MESSEGE')

    @property
    def start(self):
        return self._data[0]

    @start.setter
    def start(self, value):
        if value is not self.end:
            self._data[0] = value
        else:
            self._0lengthexception()

    @property
    def end(self):
        return self._data[1]

    @end.setter
    def end(self, value):
        if value is not self.start:
            self._data[1] = value
        else:
            self._0lengthexception()

    @property
    def length(self):
        se = self._data
        return se[1] - se[0]


class Vector_Point:
    def __new__(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if raw.shape != (4, 1):
            raise ValueError

        # point
        if raw[3, 0] == 1:
            return Point().from_raw(raw)
        # vector
        elif raw[3, 0] == 0:
            return Vector().from_raw(raw)
        else:
            raise ValueError


class Point(Geometry):

    def __init__(self, x: Number = 0, y: Number = 0, z: Number = 0):
        self.raw = [[x], [y], [z], [1]]
        self.iterstart = 0

    def __str__(self):
        return f'{self.__class__.__name__} : {[round(i, 2) for i in self.raw[:3, 0]]}'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, Vector):
            return Point.from_raw(self.raw + other.raw)
        else:
            raise

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Point.from_raw(self.raw - other.raw)
        else:
            raise

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterstart < len(self.get_data()) - 1:
            self.iterstart += 1
            return self().item(self.iterstart - 1)
        else:
            self.iterstart = 0
            raise StopIteration

    # def __add__(self, other):
    #     if isinstance(other, Point):
    #         pass
    #     elif isinstance(other, (tuple, list)):
    #         if len(other) == 3 and all([isinstance(i, Number) for i in other]):
    #             self.raw += [[i] for i in other] + [[0]]
    #     elif isinstance(other, np.ndarray):
    #         raise
    #     return self

    def __radd__(self, other):
        raise
        pass

    # def __eq__(self, other):
    #     if isinstance(other, (tuple, list)):
    #         raise
    #     elif isinstance(other, Point):
    #         if all([np.isclose(a,b,atol=DEF_TOLERANCE) for a,b in zip(self.xyz, other.xyz)]):
    #             return True
    #         else:
    #             return False

    @property
    def x(self):
        return self.raw[0, 0]

    @x.setter
    def x(self, v):
        if isinstance(v, Number):
            self.raw[0, 0] = v

    @property
    def y(self):
        return self.raw[1, 0]

    @y.setter
    def y(self, v):
        if isinstance(v, Number):
            self.raw[1, 0] = v

    @property
    def z(self):
        return self.raw[2, 0]

    @z.setter
    def z(self, v):
        if isinstance(v, Number):
            self.raw[2, 0] = v

    @property
    def xyz(self):
        return self.raw[:3, 0].tolist()

    def from_vector(self):
        raise
        pass

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if raw.shape != (4, 1) or raw[3, 0] != 1:
            raise ValueError

        return cls(*raw[:3, 0])


class Vector(Geometry):

    def __init__(self, x: Number = 0, y: Number = 0, z: Number = 0):
        self.raw = [[x], [y], [z], [0]]

    def __str__(self):
        return f'{self.__class__.__name__} : {[round(i, 2) for i in self.raw[:3, 0]]}'

    def __add__(self, other):
        if isinstance(other, Vector):
            new = self.raw.copy()
            return Vector().from_raw(new + other.raw)
        else:
            raise

    # def __truediv__(self, other):
    #     if isinstance(other, Number):
    #         v = self.raw.copy()
    #         xyz= v[:3,0]/other
    #         return Vector(*xyz)
    #     else:
    #         raise

    def __mul__(self, other):
        if isinstance(other, Number):
            v = self.raw.copy()
            xyz = v[:3, 0] * other
            return Vector(*xyz)
        elif isinstance(other, Vector):
            return self.raw * other.raw

    def dot(self, other):
        return self.raw.flatten().dot(other.raw.flatten())

    @property
    def x(self):
        return self.raw[0, 0]

    @property
    def y(self):
        return self.raw[1, 0]

    @property
    def z(self):
        return self.raw[2, 0]

    @property
    def xyz(self):
        return self.raw[:3, 0].tolist()

    def from_point(self, point: Point):
        if not isinstance(point, Point):
            raise
        raw = point.raw.copy()
        raw[3, 0] = 0
        self.raw = raw
        return self

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if raw.shape != (4, 1):
            raise TypeError
        return cls(*raw.transpose().tolist()[0][:3])

    # functions that recieve single vector and returns single vector should be methods?
    # or functions that mutates self should be methods?
    # functions that return basic properties should be methods
    @property
    def length(self):
        x, y, z = self.xyz
        return np.sqrt(x * x + y * y + z * z)

    def __neg__(self):
        return self.__class__().from_raw(self.raw.copy() * (-1))

    def flip(self):
        self.raw = -self.raw
        return self

class String(Geometry):
    """
    class identifier reprisenting string
    """

    @property
    def vertices(self):
        return self.raw[:3].transpose().tolist()
    @property
    def start(self):
        return self.raw[:3,0].tolist()
    @property
    def end(self):
        return self.raw[:3, -1].tolist()

    @property
    def n_vertex(self):
        return self.raw.shape[1]

    @property
    def length(self):
        totall = 0
        vertices = self.vertices
        for i in range(self.n_vertex -1):
            vec = []
            for a,b in zip(vertices[i], vertices[i+1]):
                vec.append(b-a)
            l = np.sqrt(vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2])
            totall += l
        return totall

    def flip(self):
        raw = np.flip(self.raw, 1)
        self.raw = raw

    def append(self, *new_element):
        for e in new_element:

            # this means raw not initiated and value is None
            if not isinstance(self.raw, np.ndarray):
                self.raw = e.raw.copy()
                continue

            if isinstance(e, Point):
                if not point.coinside(string.end(self),e):
                    self.raw = np.hstack((self.raw, e.raw.copy()))
                else:
                    raise

            elif isinstance(e, Line):
                if point.coinside(string.end(self), line.start(e)):
                    self.raw = np.hstack((self.raw, line.end(e).raw.copy()))
                elif point.coinside(string.end(self), line.end(e)):
                    self.raw = np.hstack((self.raw, line.start(e).raw.copy()))
                else:
                    self.raw = np.hstack((self.raw, e.raw.copy()))

            elif isinstance(e, Polyline):
                if point.coinside(string.end(self), string.start(e)):
                    self.raw = np.hstack((self.raw, e.raw[1:].copy()))
                elif point.coinside(string.end(self), string.end(e)):
                    self.raw = np.hstack((self.raw, np.flip(e.raw.copy(),1)[1:]))
                else:
                    self.raw = np.hstack((self.raw, e.raw.copy()))

            elif isinstance(e, (list, tuple)):
                if len(e) == 3 and all([isinstance(n,Number) for n in e]):
                    self.raw = np.hstack((self.raw, np.array([ [n] for n in e]+[1])))
            else:
                raise TypeError
        return self

    def insert(self, new_element, index):
        if isinstance(new_element, Point):
            pass
        elif isinstance(new_element, Line):
            pass
        elif isinstance(new_element, Polyline):
            pass

        elif isinstance(new_element, (list, tuple)):
            pass
        else:
            raise TypeError



class Line(String):
    def __init__(self, start: (list, tuple) = [0, 0, 0], end: (list, tuple) = [1, 0, 0]):
        if len(start) != 3 or len(end) != 3:
            raise ValueError
        if not all([all([isinstance(ii, Number) for ii in i]) for i in (start, end)]):
            raise TypeError

        start, end = start + [0], end + [0]
        self.raw = np.array((start, end)).transpose()

    def __str__(self):
        return f'Line ' + '{:.3f}'.format(self.length)

class Flat(Geometry):
    """
    for flat surface
    """

    def __init__(self, coordinates):
        # need flatness check
        pass

    pass


class Polyline(String):

    def __init__(self, *points_coord):
        if len(points_coord) == 0:
            pass
        else:
            for coord in points_coord:
                if not isinstance(coord, (tuple, list)):
                    raise NotCoordinateLikeError
                if len(coord) not in (3, 2):
                    print(len(coord))
                    raise NotCoordinateLikeError
                if not all([isinstance(i, Number) for i in coord]):
                    raise AllnumberError

            # convert into arrays stack and transpose?
            raw = None
            for i, coord in enumerate(points_coord):
                # do i need to remove duplicated point?
                # if previous is the same with current ignore
                if i != 0:
                    if all([a == b for a, b in zip(points_coord[i - 1], coord)]):
                        continue

                # else append to array
                if len(coord) == 3:
                    coord = list(coord) + [1]
                else:
                    coord = list(coord) + [0, 1]
                arr = np.array(coord)
                if raw is None:
                    raw = arr
                else:
                    raw = np.vstack([raw, arr])
            self.raw = raw.transpose()



    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if not all([i == 1 for i in raw[3]]):
            raise ValueError

        ins = cls()
        ins.raw = raw
        return ins


class Polygone(Flat, Polyline, Geometry):
    """
    what is polygone and condition of it?
    it has to be flat and consists of vertices and must be closed
    """

    def __init__(self, *coordinates):
        if len(coordinates) == 0:
            return

        super().__init__(coordinates)
        ps = []
        for i in coordinates:
            if not isinstance(i, (tuple, list)):
                raise
            if len(i) > 3:
                raise NotCoordinateLikeError(i)
            i = i + [0 for i in range(3 - len(i))]
            ps.append(Point(*i))

        # close check
        if not point.coinside(ps[0], ps[-1]):
            raise
        #
        # # anti-clockwise check
        # pla = planar[1]
        # clockwise = point.clockwise_check(ps, pla)
        # if clockwise == 0:
        #     ps = reversed(ps)
        # else:
        #     pass

        self.raw = polyline.con_points(ps).raw


    @property
    def center(self):
        coord = []
        v_n = self.raw.shape[0]
        for i in self.raw.tolist():
            coord.append(sum(i) / v_n)
        return Point(*coord[:3])

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        shape = raw.shape
        if not (shape[0] == 4 and shape[1] >= 4):
            raise
        # all has to be points
        if not all([i == 1 for i in raw[3]]):
            raise

        coordinates = raw[:3].transpose().tolist()
        inst = cls(*coordinates)
        return inst
    def __str__(self):
        return f'<Polygone> {self.raw.shape[1]-1} edges'

class Triangle(Polygone):

    def __init__(self, a, b, c):
        """
        all inputs should be points
        :param args: coordinate of points
        """
        super().__init__(a, b, c)
        # anti-clockwise check?
        # general method usage?

"""
need configuration for complex shape
"""


class Brep:
    pass


class CSG:
    pass


class Tetragon(Polygone):
    def __init__(self, a, b, c, d):
        """
        vectors represent order:

        a------d
        ;      ;
        ;      ;
        ;      ;
        b------c

        :param a,b,c,d: vertex of tetragon
        """
        super().__init__(a,b,c,d)


    def __str__(self):
        return f'{self.__class__.__name__} centered {self.center}'


class Trapezoid(Tetragon):
    def __init__(self, a, b, c, d):
        """

        :param a:
        :param b:
        :param c:
        :param d:
        """
        super.__init__(a,b,c,d)
        edges = polyline.edges()
        # at least one pair has to be parallel
        if not vector.is_parallel(edges[0],edges[2]) and not vector.is_parallel(edges[1], edges[3]):
            raise


class Parallelogram(Tetragon):
    pass


class Rectangle(Parallelogram):
    pass


class Rhombus(Parallelogram):
    pass


class Square(Rectangle):
    pass


class Hexahedron(Geometry):
    def __init__(self,
                 a=[-50, 50, -50], b=[-50, -50, -50], c=[50, -50, -50], d=[50, 50, -50],
                 e=[-50, 50, 50], f=[-50, -50, 50], g=[50, -50, 50], h=[50, 50, 50]):
        """
        input vectors should follow order as shown below:
             +z
              :
              :
            e-;------h
           /; ;     /l
          / ; :    / l
         /  ; :   /  l
        f--------g   l
        l   a....l...d
        l  .  ;  l  /
        l .   o--l-/------ +x
        l.       l/
        b------- c

        yet raw array will store vertex values as following order -> d,c,b,a,e,f,g,h
             +z
              :
              :
            4-;------7
           /; ;     /l
          / ; :    / l
         /  ; :   /  l
        5--------6   l
        l   3....l...0
        l  .  ;  l  /
        l .   o--l-/------ +x
        l.       l/
        2------- 1


        :param a,b,c,d: vertex of top face going anti_clockwise
        :param e,f,g,h: vertex of bottom face going anti_clockwise
        """
        # default box of size 100,100,100 centered at origin(0,0,0)
        vertex = d, c, b, a, e, f, g, h
        for i, v in enumerate(vertex):
            if not isinstance(v, (list, tuple)):
                raise
            if len(v) != 3:
                raise
            if not all([isinstance(ii, Number) for ii in v]):
                raise
            vertex[i].append(1)
        array = np.array(vertex).transpose()
        self.raw = array

    @property
    def vertex(self):
        l = self.raw[:3].transpose().tolist()
        return l

    @property
    def center(self):
        coord = []
        for i in self.raw.tolist():
            coord.append(sum(i) / 8)
        return Point(*coord[:3])

    def __str__(self):
        return f'{self.__class__.__name__} centered {self.center}'


class Box(Hexahedron):
    def __init__(self,
                 a, b, c, d,
                 e, f, g, h):
        # box check first
        super().__init__(a, b, c, d, e, f, g, h)


class Plane(Geometry):
    """"""

    def __init__(self,
                 origin: (tuple, list) = [0, 0, 0],
                 axis_x: (tuple, list) = [1, 0, 0],
                 axis_y: (tuple, list) = [0, 1, 0],
                 axis_z: (tuple, list) = [0, 0, 1]):

        axis = axis_x, axis_y, axis_z
        if not all([isinstance(i, (tuple, list)) for i in axis]):
            print(axis)
            raise
        axis = [list(i) for i in axis]

        # check dot product for perpendicularity 3 times!!!
        xy_dp = sum((np.array(axis_x) * np.array(axis_y)).tolist())
        yz_dp = sum((np.array(axis_y) * np.array(axis_z)).tolist())
        zx_dp = sum((np.array(axis_z) * np.array(axis_x)).tolist())
        if not np.isclose(sum([xy_dp, yz_dp, zx_dp]), 0., atol=self.TOLORENCE):
            print(axis_x, axis_y, axis_z)
            raise ValueError('given 3 vectors not perpendicular')
        # TODO should right-hand right-hand be checked too? do i support right_handed LCS?
        #   is it already checked by perpendicularity check?

        # unitize
        for i in axis:
            l = np.sqrt(i[0] * i[0] + i[1] * i[1] + i[2] * i[2])
            i[:] = i[0] / l, i[1] / l, i[2] / l
        axis_x, axis_y, axis_z = axis

        # one point three vectors
        self.raw = np.array([[*origin, 1], [*axis_x, 0], [*axis_y, 0], [*axis_z, 0]]).transpose()

    def __str__(self):
        return f'{self.__class__.__name__} of origin {self.origin}'

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if raw.shape != (4, 4):
            raise
        if not all([a == b for a, b in zip(raw[3], (1, 0, 0, 0))]):
            raise
        listed = [i[:3] for i in raw.transpose().tolist()]
        return cls(*listed)

    @property
    def origin(self):
        return Point(*self.raw[:3, 0])

    @property
    def x_axis(self):
        return Vector(*self.raw[:3, 1])

    @property
    def y_axis(self):
        return Vector(*self.raw[:3, 2])

    @property
    def z_axis(self):
        return Vector(*self.raw[:3, 3])


class Matrix(Primitive):
    def __init__(self,
                 e00: Number = 1, e01: Number = 0, e02: Number = 0, e03: Number = 0,
                 e10: Number = 0, e11: Number = 1, e12: Number = 0, e13: Number = 0,
                 e20: Number = 0, e21: Number = 0, e22: Number = 1, e23: Number = 0,
                 e30: Number = 0, e31: Number = 0, e32: Number = 0, e33: Number = 1):

        elements = [e00, e01, e02, e03,
                    e10, e11, e12, e13,
                    e20, e21, e22, e23,
                    e30, e31, e32, e33]
        if not all([isinstance(i, Number) for i in elements]):
            raise ValueError
        self.raw = np.array(elements).reshape((4, 4))

    @classmethod
    def from_raw(cls, raw):
        if not isinstance(raw, np.ndarray):
            raise
        if raw.shape != (4, 4):
            raise ValueError
        return cls(*raw.flatten().tolist())

    def __str__(self):
        listed = self.raw.tolist()

        for r, row in enumerate(listed):
            for c, ii in enumerate(row):
                listed[r][c] = '{: .2f}'.format(ii)
            listed[r] = str(row)

        listed[0] = f'{self.__class__.__name__} : ' + listed[0]
        return '{:>45}\n{:>45}\n{:>45}\n{:>45}'.format(*listed)


class Transformation(Primitive):

    def __init__(self, array: np.ndarray):
        self.set_data(array)

    pass


class intersection:
    @staticmethod
    def pline_line(pol:(Polyline,Polygone), lin:Line):
        # TODO how to define plane of polyline
        if lin.vertices[0][2] != 0 or lin.vertices[1][2] != 0:
            raise Exception('not defined yet for 3d line')
        edges = polyline.edges(pol)
        inter = [[],[]]
        for e in edges:
            i = intersection.line_line(e,lin,on_line=True)
            if i != None:
                if isinstance(i, Point):
                    inter[0].append(i)
                elif isinstance(i, Line):
                    inter[1].append(i)

        inter[0] = point.unique_points(inter[0])[0]

        # if has line remove points coinside with line's vertex
        if len(inter[1]) != 0:
            line_vertices = []
            for l in inter[1]:
                line_vertices += line.decon(l)
            line_vertices = point.unique_points(line_vertices)[0]
            mask = point.in_points(line_vertices, *inter[0])
            inter[0] = data.cull_pattern(inter[0],mask,flip_mask=True)
        inter = inter[0]+inter[1]

        return inter

    @staticmethod
    def line_line(line1:Line, line2:Line, on_line=True):
        if not isinstance(line1,Line) or not isinstance(line2,Line):
            raise TypeError
        # need to define what is correct intersection
        # 1.if two lines coinside
        # 2.if two lines coinside partially
        # 3.if vertex of one line touches another
        # 4.if two lines intersect through the point
        # 5.if imaginary extension of two lines intersect eventually
        # let except #5 be considered as intersection
        # if line1.vertex
        (a,b),(c,d) = line.decon(line1), line.decon(line2)
        directional1 = vector.con_line(line1)
        directional2 = vector.con_line(line2)
        if vector.is_parallel(directional1, directional2):

            #1
            if line.coinside(line1,line2) or line.coinside(line1, line.flipped(line2)):
                return Line(a.xyz, b.xyz)
            #2
            elif point.is_on_line(line1,c):
                small, big = sorted((a.xyz[0], b.xyz[0]))
                if c.x > small:
                    if point.is_on_line(line1, d):
                        return Line(c.xyz, d.xyz)
                    elif d.xyz[0] < small:
                        return Line(a.xyz, c.xyz)
                    elif d.xyz[0] > big:
                        return Line(c.xyz, b.xyz)
                else:
                    return c

            elif point.is_on_line(line2, a):
                small, big = sorted((c.xyz[0], d.xyz[0]))
                if a.x > small:
                    if point.is_on_line(line2,b):
                        return Line(a.xyz, b.xyz)
                    elif b.xyz[0] > big:
                        return Line(a.xyz,d.xyz)
                    elif b.xyz[0] < small:
                        return Line(c.xyz, a.xyz)
                else:
                    return a

        else:
            #3 is merged with #4
            # TODO 4 vector method? need to understand this more fluently
            cross_two_directional = vector.cross(directional2,directional1)
            if cross_two_directional.length == 0:
                return None
            else:
                cross = vector.cross(directional2, vector.con_2_points(a, c))
                r = cross.length / cross_two_directional.length
                u = directional1*r
                if vector.is_parallel(cross, cross_two_directional) == 1:
                    new_p = a+u
                else:
                    new_p = a-u

                if on_line:
                    x = new_p.x
                    (x1,x2),(x3,x4) = sorted([a.x, b.x]), sorted([c.x, d.x])
                    if x >= x1 and x <= x2 and x >= x3 and x <= x4:
                        return new_p
                    else:
                        return None
                else:
                    return new_p


class tests:
    @staticmethod
    def triangulatioin(pol:Polygone):
        edges, vertices = polyline.decon(pol)

        vertices = vertices[:-1]
        unique_x = sorted(set(pol.raw[0]))
        x_min,x_max = unique_x[0], unique_x[-1]
        x_start = x_min - 1
        c_line_length = x_max-x_min+2
        # sort for convenience
        vertices = point.sort(vertices, 'y')
        ys = point.y(*vertices)
        vertices_sorted = data.sublist_by_unique_key(vertices, ys)
        for i, l in enumerate(edges):
            s, e = line.decon(l)
            if s.y > e.y:
                l.flip()
            elif s.y == e.y:
                if s.x > e.x:
                    l.flip()

        # trapezoidal Decomposition
        trapezoid = []
        for y, vs in vertices_sorted.items():
            # first draw a line and find intersecting points
            c_line = line.con_point_vector(Point(x_start,y,0), Vector(c_line_length,0,0))
            print()
            print('vertex', vs)
            print('crossing line:', c_line.vertices)
            p_inter = []
            e_under = []
            e_cross = []
            for e in edges:
                # all intersection given as a point or a line
                if e.start[1] == y:
                    # ignore because there must be another conneted to this edge's start
                    p_inter.append(line.start(e))
                elif e.start[1] < y and y < e.end[1]:
                    p_inter.append(intersection.line_line(c_line, e))
                    e_cross.append(e)

                elif e.end[1] == y:
                    if e.start[1] != y:
                        # edge below
                        e_under.append(e)
                        p_inter.append(line.end(e))

                elif e.end[1] < y:
                    # this must be left over from provious iteration
                    e_under.append(e)

            # no detection must be when another co_linear another vertex has finished cut off
            if len(e_under+e_cross) == 0:
                continue
            # remove collected edges
            for e in e_under+e_cross:
                edges.remove(e)

            # make intersections unique
            print(p_inter)
            p_inter = point.unique_points(p_inter)[0]
            p_inter = point.sort(p_inter,'x')

            # several cased for number of intersection points
            n = len(p_inter)
            print(' intersections', p_inter)
            if n == 0:
                # this can't happen except for the point lowest
                raise
            elif n == 1:
                # peak dealing will be after segments are delt
                pass
            else:
                # need to look for valid c_line segment
                # find position of vertex
                segments = []
                for i in range(len(p_inter)-1):
                    middle_p = point.average([p_inter[i], p_inter[i+1]])
                    print(middle_p)
                    condition1 = polygone.point_in(pol, middle_p) == 2 # condition1; not on but in
                    condition2 = False # condition2; at least one vertex is a part of the segment
                    print('dddddddddddddd', vs)
                    for y in vs:
                        print(y, p_inter[i], p_inter[i+1])
                        if point.coinside(y, p_inter[i]) or point.coinside(y, p_inter[i+1]):
                            condition2 = True
                            break
                    print('     conditions ', condition1, condition2)
                    print('     ', y, p_inter[i], p_inter[i+1])
                    print('     ', point.coinside(y, p_inter[i]) or point.coinside(y, p_inter[i+1]))
                    if condition1 and condition2:
                        print(vs)
                        print(' correct segment', p_inter[i],p_inter[i+1])
                        segments.append(line.con_points(p_inter[i], p_inter[i + 1]))

                    else:
                        # segments.append(None)
                        pass

                # this is to leave peak candidate
                segments_vertex = []
                for s in segments:
                    segments_vertex += line.decon(s)
                segments_vertex = point.unique_points(segments_vertex)[0]
                to_remove = []
                print('+++++++++++++++++')
                print(segments_vertex)
                print(vs)
                for y in vs:
                    for i in segments_vertex:
                        if point.coinside(i,y):
                            to_remove.append(y)
                            break
                for i in to_remove:
                    vs.remove(i)


                edges += segments
                print('     segments', segments)
                # now i have correct c_line_segment so cut original polyline and make trapezioid out or it
                for s in segments:
                    print(s)
                    s_vertex = line.decon(s)
                    print('         e_cross', e_cross)
                    for e in e_cross:
                        mask = point.is_on_line(e, *s_vertex)
                        print('----------------', mask, e, s_vertex)
                        if any(mask):
                            p = data.cull_pattern(s_vertex, mask)[0]
                            e_vertex = line.decon(e)

                            # need to split
                            down = line.con_points(e_vertex[0], p)
                            up = line.con_points(p, e_vertex[1])

                            # record for next local, global search
                            print('     appending down', down.vertices)
                            e_under.append(down)
                            edges.append(up)
                            # need this removal cus rest gonna be added to edges list
                            e_cross.remove(e)
                            break
                edges += e_cross
                print(segments)
                print(e_cross)
                print(e_under)
                e_under += segments
                for s in segments:
                    if s in e_under:
                        e_under.remove(s)
                    else:
                        # previouse iteration could have removed a segment
                        # as taking it as a part of its boundary
                        continue

                    building_trapeziod = [s]
                    # track edges
                    default_plane = Plane()
                    trace = line.start(s)
                    vec_trace = vector.con_2_points(*reversed(line.decon(s)))
                    while True:
                        # how to move anti_clockwise
                        flag_found = False
                        print('eeee', e_under)
                        for e in e_under:
                            has = line.has_vertex(e, trace)
                            print(e.vertices)
                            print('kkk',has)
                            if has:
                                v_next = line.decon(e)[has[1]-1]
                                new_vec_trace = vector.con_2_points(trace, v_next)
                                # anti clockwise condition
                                side,angle = vector.right_left_halfspace(vec_trace, new_vec_trace)
                                if math.any_one_of(side, 1, 2):
                                    building_trapeziod.append(e)
                                    trace = v_next
                                    vec_trace = new_vec_trace
                                    e_under.remove(e)
                                    flag_found = True
                                    break

                        if not flag_found:
                            # seen through all edges but couldn't find one
                            # -> something is wrong
                            print(s.vertices)
                            print(building_trapeziod)
                            raise
                        # if shape is closed
                        if point.coinside(trace, line.end(s)):
                            # replace colinear edges to pline and organize
                            left = building_trapeziod.pop(1)
                            keys = [line.middle(l).y for l in building_trapeziod]
                            building_trapeziod = data.sublist_by_unique_key(building_trapeziod, keys)
                            building_trapeziod = sorted(building_trapeziod.items(), key = lambda x:x[0])

                            flag_poly = False
                            for i, (y,l) in enumerate(building_trapeziod):
                                if len(l) != 1:
                                    flag_poly = True
                                    building_trapeziod[i] = polyline.con_from_strings(l)
                                else:
                                    building_trapeziod[i] = l[0]

                            building_trapeziod.insert(0,left)
                            # index 0 is alway top and goes clockwise
                            building_trapeziod = data.shift(building_trapeziod, -1)
                            if flag_poly:
                                # add crossing lines and then round up partially with segments
                                up_down = [building_trapeziod[0],building_trapeziod[2]]
                                v_lists = []
                                for i in up_down:
                                    if isinstance(i, Line):
                                        v_lists.append(string.vertices(i)[0])
                                    else:
                                        v_lists.append(string.vertices(i)[1:-1])
                                matched = data.long(*v_lists)
                                split_edges = []
                                for s,e in zip(matched[1],matched[0]):
                                    split_edges.append(line.con_points(s, e))
                                shape = polyline.join(*building_trapeziod)
                                shapes = polygone.split(shape, *split_edges)
                                exit()
                            else:
                                trapezoid.append(building_trapeziod)
                            break

            # dealing with peak and basin
            # condition
            if len(e_under) != 0 and len(vs) != 0:
                print('-----------------')
                print('dealing with basin')
                print(vs)
                print(segments)
                print(edges)
                print(e_under, len(e_under))
                peaks,basins = [],[]
                # find basins
                for l in edges:
                    s,e = line.decon(l)
                    mark = []
                    # see if it's on the c_line
                    for y in vs:
                        if point.coinside(y, s):
                            mark.append(y)
                            break
                    for y in vs:
                        if point.coinside(y, e):
                            mark.append(y)
                            break
                    if len(mark) == 2:
                        vs.remove(mark[0])
                        vs.remove(mark[1])
                        basins.append(l)
                for i in basins:
                    edges.remove(i)
                # rest are peaks
                peaks = vs

                # find peaks
                for p in peaks:
                    vs.remove(p)
                    building_peak = []
                    for e in e_under:
                        if point.coinside(line.end(e), p):
                            building_peak.append(e)
                        if len(building_peak) == 2:
                            break
                    print('ddd',p,building_peak)
                    vertex = line.start(building_peak[0]), line.start(building_peak[1])
                    for e in e_under:
                        print(e.vertices, point.is_on_line(e, *vertex))
                        if all(point.is_on_line(e, *vertex)):
                            building_peak.insert(0,e)
                            break
                    if len(building_peak) != 3:
                        print(p)
                        print(vertex)
                        print(building_peak)
                        print(e_under)
                        raise
                    for i in building_peak:
                        e_under.remove(i)
                    trapezoid.append(building_peak)

                # find basins
                e_under += basins
                print(e_under)
                for b in basins:
                    if b not in basins:
                        continue
                    building_basin = [b]
                    e_under.remove(b)
                    trace, end = line.decon(b)
                    vec_trace = vector.con_line(b).flip()
                    while True:
                        flag_found = False
                        # next edge is always the side of trapeziod
                        # but next can have multiple edges connected to the end of previous
                        candidates = []
                        print(e_under)
                        for e in e_under:
                            has = line.has_vertex(e, trace)
                            print(e.vertices, has, trace)
                            if has:
                                next_trace = line.decon(e)[has[1]-1]
                                directional = vector.con_2_points(trace, next_trace)
                                side, angle = vector.right_left_halfspace(vec_trace, directional)
                                print(side, math.any_one_of(side, 1, 2))
                                if math.any_one_of(side, 1, 2):
                                    candidates.append((angle,directional,e,next_trace))
                                    flag_found = True
                                    print('ddddddd', candidates)
                        print('ddddddd', candidates)
                        if not flag_found:
                            print(e_under[0].vertices)
                            print(b)
                            print(trace)
                            print(candidates)
                            print(building_basin)
                            raise

                        if len(candidates) != 1:
                            _,vec_trace,e,trace = math.biggest(candidates,key=lambda x:x[0])
                            building_basin.append(e)
                            e_under.remove(e)
                        else:
                            _,vec_trace,e,trace = candidates[0]
                            print('xxx', e, trace)
                            building_basin.append(e)
                            e_under.remove(e)

                        if point.coinside(trace, end):
                            break

                    trapezoid.append(building_basin)

            edges += e_under

        if len(edges) != 0:
            raise

        for i in trapezoid:
            print(i)

        # monotone Subdivision
        # basic tactic is to read stack and see if any of monotonal adjustant with bottom of inspected
        # another thing to check is parallelity of sides.
        # if any polyline is seen then this needs self division
        monotone = []
        for t in trapezoid:
            if len(monotone) == 0:
                top_edge = t[0]
                shape = polygone.con_edges(t)
                # or if manually checking horizontal edges
                print(shape)
                monotone.append([top_edge, shape])
                continue
            else:
                # find bottom
                shape = len(t)
                if shape == 3:
                    adding_bottom_e = t[0]
                    adding_top_e = None
                elif shape == 4:
                    adding_bottom_e = t[2]
                    adding_top_e = t[0]

                for i,(top_edge, m) in enumerate(monotone):
                    if top_edge == None:
                        # top edge none means its closed, its monotone
                        continue

                    if isinstance(adding_bottom_e, Polyline) or isinstance(adding_top_e, Polyline):
                        # if horizontal of trapezoid is polyline, means it has to be segmented?
                        # or had it be done already?
                        raise

                    else:
                        if line.coinside(top_edge, adding_bottom_e,consider_direction=True):
                            print(m)
                            pl1 = polyline.remove_edge(m,adding_bottom_e)
                            t.remove(adding_bottom_e)
                            pl2 = polyline.con_from_strings(t)

                            print(pl1.vertices)
                            print(pl2.vertices)
                            new_mono = polyline.join(pl1,pl2)
                            print(new_mono)
                            new_mono = polyline.iron(new_mono)
                            print(new_mono)
                            # monotone[i][1] = polygone.merge(m,adding_shape)
                            break


                pass


        # triangulation
        # deed to considier out of shape triangulation


class morph:
    @staticmethod
    def extrude(geo:Geometry, direction:Vector) -> Geometry:
        if isinstance(geo, Flat):
            pass


        elif isinstance(geo, Line):
            raise
        else:
            raise

class trans:

    @staticmethod
    def orient(geo:Geometry, source:Plane, target:Plane) -> Geometry:
        """
        orient given geometry from source plane to target plane
        :param geo: thing to orient
        :param source: reference plane of geo
        :param target: result plane of geo
        :return: geo
        """
        tom,_ = matrix.trans_between_origin_and_plane(source)
        _,tpm = matrix.trans_between_origin_and_plane(target)
        geo = trans.transform(geo, tom)
        geo = trans.transform(geo, tpm)
        return geo

    @staticmethod
    def move(geo:Geometry, vec: Vector):
        x = matrix.translation(vec)
        return trans.transform(geo, x)
    
    # @tlist.calitem
    # def test(x, y):
    #     print(x, y)
    #     pass
    
    @staticmethod
    def transform(geometry:Geometry, *matrices:Matrix):
        r = geometry.raw
        for m in reversed(matrices):
            r = m.raw.dot(r)
        return geometry.__class__.from_raw(np.array(r))
    
    # @tlist.calitem
    # def rect_mapping(geometry: Geometry, source: Rect, target: Rect):
    #     source_v = source.vertex()
    #     target_v = target.vertex()
    #     m_trans = matrix.translation(vector.con2pt(source_v[0], target_v[0]))
    #     m_rotate = None
    #     m_scale = None
    #     m_sheer = None
    #
    #     # t = target()*np.invert(source())
    #     # print(t)
    #     # vectors = vector.con2pt(source.vertex(),target.vertex())
    #     # average = vector.average(vectors)

    @staticmethod
    def rotate_around_axis(geometry:Geometry, axis:Line, angle, degree=False):
        if not isinstance(axis,Line):
            if isinstance(axis, Vector):
                axis = line.con_from_vector(axis)
            else:
                raise TypeError
        axis_start,_ = line.decon(axis)
        # vector from axis
        axis_vector = vector.con_line(axis)
        # what is this for? want to fine another vector that is close to x and perpendicular
        ref_point = Point(1,0,0)

        projected_point = point.perpendicular_on_vector(axis_vector,ref_point)
        perpen_v = vector.con_2_points(projected_point, ref_point)
        # and build a reference plane
        ref_plane = plane.con_2_vectors(axis_vector, perpen_v, 'z', 'x', axis_start)
        xpo,xop = matrix.trans_between_origin_and_plane(ref_plane)

        # back force move
        geometry = trans.transform(geometry, xpo)
        # using rotation z because input axis is set as z while building ref_plane
        geometry = trans.rotate_around_z(geometry,angle,degree)
        geometry = trans.transform(geometry, xop)

        return geometry

    @staticmethod
    def rotate_around_x(geometry:Geometry, angle, degree=False, ):
        x = matrix.rotation_x(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_y(geometry:Geometry, angle, degree=False):
        x = matrix.rotation_y(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_z(geometry:Vector, angle, degree=False):
        x = matrix.rotation_z(angle, degree)
        return trans.transform(geometry,x)


class line:
    @staticmethod
    def touching_another(lin1:Line, lin2:Line):
        order = None
        if point.coinside(line.end(lin1), line.start(lin2)):
            order = 1,0
        elif point.coinside(line.end(lin1),line.end(lin2)):
            order = 1,1
        elif point.coinside(line.start(lin1), line.start(lin2)):
            order = 0,0
        elif point.coinside(line.start(lin1), line.end(lin2)):
            order = 0,1
        return order

    # @staticmethod
    # def pick_polygons(line_list:(tuple,list), pla:Plane):
    #     print(line_list)
    #     print(pla)
    #     while True:
    #         temp_lines = []
    #         for i in line_list:
    #             print('looking for a line', i.vertices)
    #             touching = []
    #             for ii in line_list:
    #                 touch_sign = line.touching_another(i,ii)
    #                 if touch_sign != None:
    #                     if touch_sign[0] == 1:
    #                         if touch_sign[1] == 0:
    #                             touching.append(ii)
    #                         else:
    #                             touching.append(line.flipped(ii))
    #
    #             if len(touching) == 0:
    #                 print('no touching line')
    #                 continue
    #             else:
    #                 print('     touching lines')
    #                 for i in touching:
    #                     print('     ', i.vertices)
    #
    #                 temp_lines.append(i)
    #                 line_list.remove(i)
    #
    #         if len(line_list) == 0:
    #             break
    #
    #     exit()
    #     pass
    @staticmethod
    def unique_lines(lines:(list, tuple), consider_direction = False) -> list:
        to_compare= lines.copy()
        unique = []
        while True:
            for l in to_compare:
                to_compare.remove(l)
                unique.append(l)
                similar = []
                for ll in to_compare:
                    if line.coinside(l, ll, consider_direction=consider_direction):
                        similar.append(ll)
                for i in similar:
                    to_compare.remove(i)
                break

            if len(to_compare) == 0:
                break

        return unique

    @staticmethod
    def is_parallel(line1:Line, line2:Line) -> bool:
        vector1, vector2 = vector.con_line(line1), vector.con_line(line2)
        if math.any_one_of(vector.is_parallel(vector1, vector2), -1,1):
            return True
        return False

    @staticmethod
    def start(lin:Line) -> Point:
        return Point(*lin.start)

    @staticmethod
    def end(lin:Line) -> Point:
        return Point(*lin.end)

    @staticmethod
    def decon(lin:Line):
        return [Point(*lin.raw.copy()[:3, 0]), Point(*lin.raw.copy()[:3, 1])]

    @staticmethod
    def has_vertex(lin:Line, poi:Point):
        start, end = lin.vertices
        coord = poi.xyz
        if all([a==b for a,b in zip(start,coord)]):
            return [ True, 0 ]
        elif all([a==b for a,b in zip(end, coord)]):
            return [ True, 1 ]
        else:
            return False

    @staticmethod
    def middle(lin:Line):
        if not isinstance(lin, Line):
            raise TypeError
        coord = []
        for a,b in zip(*lin.vertices):
            coord.append((a+b)/2)
        return Point(*coord)

    @staticmethod
    def coinside(line1:Line, line2:Line, consider_direction = True) -> bool:
        if consider_direction:
            return np.sum(np.equal(line1.raw, line2.raw)) == 8
        else:
            return any([
                np.sum(np.equal(line1.raw, line2.raw)) == 8,
                np.sum(np.equal(line1.raw, np.flip(line2.raw,1))) == 8])

    @staticmethod
    def flipped(lin:Line):
        return Line(lin.end,lin.start)

    @staticmethod
    def con_points(start:Point, end:Point) -> Line:
        return Line(start.xyz, end.xyz)

    @staticmethod
    def con_point_vector(start:Point, vec:Vector) -> Line:
        return line.con_points(start, trans.move(start, vec))

    @staticmethod
    def con_from_vector(vector:Vector):
        end = vector.raw.copy().transpose().tolist()[0][:3]
        return Line([0,0,0],end)


class data:

    @staticmethod
    def long(lis1:(tuple, list),lis2:(tuple, list),style=0)-> (tuple, list):
        """
        lengthen lists to match longest list
        style;
        0 - duplicates last to fill gap
        1 - repeat whole list to fill gap

        :param lis:
        :param style:
        :return:
        """
        new1, new2 = lis1.copy(),lis2.copy()
        if len(new1) == len(new2):
            return [new1, new2]

        gap = len(new1)-len(new2)
        flipped = False
        if gap > 0:
            big_small = [new1, new2]
        else:
            big_small = [new2, new1]
            flipped = True

        gap = abs(gap)
        # means list1 is bigger than list2
        if style == 0:
            big_small[1] += [big_small[1][-1]]*gap

        elif style == 1:
            # list1 is bigger than list2
            l_small = len(big_small[1])
            quotient, remainder = gap // l_small, gap % l_small
            big_small[1] += big_small[1]*quotient + big_small[1][:remainder]

        else:
            FunctionNotDefinedError()

        if flipped:
            return [big_small[1], big_small[0]]
        else:
            return big_small

    @staticmethod
    def short():
        pass

    @staticmethod
    def filter_type(lis:(tuple, list), *t:type, include_exclude = True) -> list:
        if include_exclude:
            new_list = []
        else:
            new_list = lis.copy()

        for i in lis:
            for ii in t:
                if isinstance(i, ii):
                    if include_exclude:
                        new_list.append(i)
                    else:
                        new_list.remove(i)

        return new_list


    @staticmethod
    def shift(lis,step):
        new_lis = []
        l = len(lis)
        index = step%l
        for i in lis:
            new_lis.append(lis[index])
            index = (index+1)%l
        return new_lis

    @staticmethod
    def sublist_by_unique_key(lis:(list,tuple), keys:(list, tuple)):
        if not isinstance(lis, (list,tuple)) or not isinstance(keys,(list,tuple)):
            raise TypeError
        if len(lis) != len(keys):
            raise ValueError

        unique_keys = set(keys)
        dic = dict(zip(unique_keys, [[] for i in range(len(unique_keys))]))
        for k,i in zip(keys, lis):
            dic[k].append(i)

        return dic

    @staticmethod
    def cull_pattern(lis:(tuple,list), mask:(tuple, list), flip_mask = False) -> list:
        if isinstance(lis, (tuple, list)):
            if len(lis) != len(mask):
                raise
            if flip_mask:
                mask = [ not m for m in mask]

            new_list = []
            for v,m in zip(lis, mask):
                if m:
                    new_list.append(v)

            return new_list

        else:
            raise Exception('not defined yet')

    @staticmethod
    def split_pattern(lis:(tuple, list), mask:(tuple, list), flip_mask=False) -> list:
        if isinstance(lis, (tuple, list)):
            if len(lis) != len(mask):
                raise TypeError
            true_list = []
            false_list = []
            for v,m in zip(lis, mask):
                if m:
                    true_list.append(v)
                else:
                    false_list.append(v)
            if flip_mask:
                return [ false_list, true_list ]
            else:
                return [ true_list, false_list]

        else:
            raise Exception('not defined yet')

    @staticmethod
    def list_item(lis:(tuple, list), *index:int):
        if isinstance(lis, (tuple, list)):
            if len(index) == 0:
                return None

            new_list = []
            for i in index:
                i = i% len(lis)
                new_list.append(lis[i])

            if len(new_list) == 1:
                return new_list[0]
            else:
                return new_list

        else:
            raise Exception('not defined yet')
class string:
    @staticmethod
    def vertex(stri:String, index):
        raw = stri.raw[:3,index].copy()
        return Point(*raw)

    @staticmethod
    def start(stri:String) -> Point:
        return Point(*stri.raw[:3, 0])
    @staticmethod
    def end(stri:String) -> Point:
        return Point(*stri.raw[:3, -1])
    @staticmethod
    def flip(stri:String) -> String:
        raw = np.flip(stri.raw.copy(), 1)
        return stri.__class__.from_raw(raw)

    @staticmethod
    def vertices(stri:String):
        raw = stri.raw[:3].transpose().tolist()
        points = []
        for i in raw:
            points.append(Point(*i))
        return points

    @staticmethod
    def edges(stri:String):
        edges = []
        vertices = stri.vertices
        for i in range(len(vertices) -1):
            edges.append(Line(vertices[i], vertices[i+1]))
        return edges

    @staticmethod
    def decon(stri:String):
        raw = np.flip(stri.raw[:3].transpose().tolist())
        points = []
        for i in raw:
            points.append(Point(*i))
        edges = []
        for i in range(len(points)-1):
            edges.append(line.con_points(points[i], points[i + 1]))
        return [edges, points]

class polyline:
    @staticmethod
    def iron(poll:Polyline) -> Polyline:
        # look through each edge and see the vector of it
        edges = polyline.edges(poll)

        for i,e in enumerate(edges):
            this_v = vector.con_line(e)
            para_edges = []
            index = i
            while True:
                index = (index+1)%len(edges)
                next_e = edges[index]
                next_v = vector.con_line(next_e)
                if vector.is_parallel(this_v, next_v) == 1:
                    para_edges.append(next_e)
                else:
                    break
            if len(para_edges) != 0:
                s,e = line.start(e), line.end(para_edges[-1])
                ironned = line.con_points(s, e)
                edges[i] = ironned
                for i in para_edges:
                    edges.remove(i)

        new_poll = poll.__class__().append(*edges)
        return new_poll

    @staticmethod
    def remove_edge(poll:Polyline, edge:Line) -> Polyline:
        poll_vertices = polyline.vertices(poll)
        split = None
        s,e = line.decon(edge)
        for i,v in enumerate(poll_vertices[1:-1]):
            if point.coinside(v, s):
                if point.coinside(poll_vertices[i+2],e):
                    split = i+1
                elif point.coinside(poll_vertices[i], e):
                    split = i

        if split is None:
            return poll
        first, second = poll_vertices[:split+1],poll_vertices[split+1:]
        if point.coinside(first[0], second[-1]):
            merged = second+first[1:]
            return polyline.con_points(merged)
        else:
            return [polyline.con_points(first), polyline.con_points(second)]

    @staticmethod
    def con_polygone(polg:[Polygone, Polyline],a:str, *b:int, **c:dict):
        poll = Polyline()
        poll.raw = polg.raw.copy()
        return poll

    @staticmethod
    def start(pol: Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return Point(*pol.raw[:3, 0])

    @staticmethod
    def end(pol: Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return Point(*pol.raw[:3, -1])

    @staticmethod
    def start_end(pol:Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return [ Point(*pol.raw[:3, 0]), Point(*pol.raw[:3, -1]) ]

    @staticmethod
    def join(*segments:(tuple, list)):
        """
        excepts segments and return joined
        :return:
        """
        new_p_lists = []
        for l in segments:
            if not isinstance(l, String):
                raise WrongInputTypeError(l, String)
            new_p_lists.append(string.vertices(l))

        print('new p list',len(new_p_lists), new_p_lists)
        organized = []
        while True:
            for l in new_p_lists:
                print('join looking for joint ', l)
                organized.append(l)
                new_p_lists.remove(l)
                to_remove = []
                for ll in new_p_lists:
                    to_remove.append(ll)
                    # search for joint
                    if point.coinside(l[0],ll[0]):
                        l[:] = list(reversed(ll)) + l[1:]
                    elif point.coinside(l[0],ll[-1]):
                        l[:] = ll + l[1:]
                    elif point.coinside(l[-1],ll[0]):
                        l[:] = l + ll[1:]
                    elif point.coinside(l[-1],ll[-1]):
                        l[:] = l + list(reversed(ll)[1:])
                    else:
                        to_remove.remove(ll)

                for i in to_remove:
                    new_p_lists.remove(i)

                break
            if len(new_p_lists) == 0:
                break

        shapes = []
        for l in organized:
            shape = polyline.con_points(l)
            if polyline.is_closed(shape):
                shape = polygone.con_polyline(shape)
            shapes.append(shape)

        if len(shapes) == 1:
            return shapes[0]
        return shapes


    @staticmethod
    def con_from_strings(lines:(tuple, list)) -> Polyline:
        """
        Join given strings and form single polyline.
        :param lines:
        :return:
        """
        for i in lines:
            print(i.vertices)
        if not isinstance(lines, (tuple, list)):
            raise TypeError
        if len(lines) == 0:
            return None
        lines = lines.copy()
        starting_line= lines.pop(0)
        sorted_vertex = string.vertices(starting_line)
        while True:
            flag_found = False
            to_remove = []
            for l in lines:
                cloud = sorted_vertex[0], sorted_vertex[-1]
                # if the line can be joined from start or end of collected
                vs = string.vertices(l)
                s,e = vs[0],vs[-1]
                if any(point.in_points(cloud, s,e)):
                    flag_found = True
                    if point.coinside(sorted_vertex[0], s):
                        sorted_vertex = list(reversed(vs))[:-1] + sorted_vertex
                    elif point.coinside(sorted_vertex[0], e):
                        sorted_vertex = vs[:-1] + sorted_vertex
                    elif point.coinside(sorted_vertex[-1], s):
                        sorted_vertex += vs[1:]
                    elif point.coinside(sorted_vertex[-1], e):
                        sorted_vertex += list(reversed(vs))[1:]
                    to_remove.append(l)

            if not flag_found:
                return None

            for i in to_remove:
                lines.remove(i)

            if len(lines) == 0:
                break

        return polyline.con_points(sorted_vertex)

    @staticmethod
    def con_points(points_list:(tuple, list)) -> Polyline:
        if not isinstance(points_list, (tuple, list)):
            raise TypeError
        if len(points_list) == 0:
            return None

        raw = points_list[0].raw.copy()
        for p in points_list[1:]:
            if not isinstance(p, Point):
                raise
            raw = np.hstack((raw, p.raw.copy()))

        return Polyline.from_raw(raw)



    @staticmethod
    def decon(pol:Union[Polyline,Polygone]) -> list:
        """
        deconstructs polyline into points and lines
        :param pol:
        :return: [ list of lines, list of points ]
        """
        coords = pol.raw[:3].transpose().tolist()
        points = []
        for i in coords:
            points.append(Point(*i))

        lines = []
        for i in range(len(points)-1):
            lines.append(line.con_points(points[i], points[i + 1]))

        return [lines, points]

    @staticmethod
    def vertices(poll):
        return string.vertices(poll)

    @staticmethod
    def edges(pol:Polyline):
        lines = []
        points = polyline.vertices(pol)
        for i in range(len(points)-1):
            lines.append(line.con_points(points[i], points[i + 1]))
        return lines

    @staticmethod
    def is_closed(pol:Polyline):
        raw = pol.raw
        if all(np.equal(raw[:3,-1], raw[:3,0])):
            return True
        else:
            return False

class polygone:

    @staticmethod
    def string_in(polg:Polygone, line:String):
        pass

    @staticmethod
    def point_in(pol: Polygone, poi: Point):
        """
        tests whether point is (out in on) the polyline
        returns:
        0 if point is out
        1 if point is on the boundary
        2 if point is in
        :param pol: closed Polygon
        :param poi: Point to test
        :return: out, in, on sign
        """
        if not polyline.is_closed(pol):
            return None
        edges, vertices = polyline.decon(pol)

        # see point on polyline
        for e in edges:
            if poi.x == 7 and poi.y == 7:
                print(e.vertices, point.is_on_line(e, poi))
            if point.is_on_line(e, poi):
                return 1

        # see point in out polyline
        x_max = sorted(set(pol.raw[0]))[-1]
        end_point = Point(*poi.xyz)
        end_point.x = x_max + 1

        c_line = line.con_points(poi, end_point)
        iter_count = 0

        while True:
            flag_break = True
            # if can't find the case something is wrong
            if iter_count == 100:
                raise

            # see if crossing is valid
            inter = intersection.pline_line(pol, c_line)
            # if any one of intersection is a line or a vertex do it again
            print(inter)
            print('sss', data.filter_type(inter, Line))

            if len(data.filter_type(inter,Line)) != 0:
                flag_break = False
            elif any(point.in_points(vertices, *inter)):
                flag_break = False

            if flag_break:
                break
            else:
                c_line.raw[1,1] += 1
                iter_count += 1

        # # check peaks
        # if len(inter) != 0:
        #     mask = point.in_points(cloud, *inter)
        #     inter = data.cull_pattern(inter, mask, flip_mask=True)

        # count intersection
        if len(inter) % 2 == 0:
            return 0
        else:
            return 2

    @staticmethod
    def con_edges(edges:List[Line]):
        # need edge crossing checking
        poll = polyline.con_from_strings(edges)
        if poll is None:
            return None
        return polygone.con_polyline(poll)

    @staticmethod
    def con_polyline(poll:Polyline):
        if not polyline.is_closed(poll):
            return None
        return Polygone.from_raw(poll.raw.copy())


    @staticmethod
    def merge(polg1:Polygone, polg2:Polygone, iron=True):
        raise
        print(polg1, polg2)
        edges1, edges2 = polyline.edges(polg1), polyline.edges(polg2)
        print(edges1)
        print(edges2)
        # find all intersections
        intersec = [[],[]]
        for e in edges1:
            for ee in edges2:
                i = intersection.line_line(e, ee)
                if isinstance(i, Line):
                    print('intersection', e.vertices, ee.vertices)
                    intersec[0].append(i)
                elif isinstance(i, Point):
                    intersec[1].append(i)
        print(intersec)
        intersec[0] = line.unique_lines(intersec[0])
        intersec[1] = point.unique_points(intersec[1])[0]
        print('ddd')
        print(intersec)
        for i in intersec[0]:
            print(i.vertices)
        lines_point_pool = []
        for l in intersec[0]:
            lines_point_pool += line.decon(l)
        mask = point.in_points(lines_point_pool, *intersec[1])
        intersec[1] = data.cull_pattern(intersec[1], mask, flip_mask=True)


        pass

    @staticmethod
    def split(polg:Polygone, *lin_cutter:Line) -> List[Polygone]:
        # check planarity
        shapes = [polg]
        # check intersections
        for c in lin_cutter:
            new_shapes = []
            for shape in shapes:
                edges = string.edges(shape)
                inter_points = []
                splited_vertices = [line.start(edges[0])]
                split_increment = 0
                for b,e in enumerate(edges):
                    # find intersection
                    inter = intersection.line_line(e,c)
                    s,e = line.decon(e)
                    splited_vertices.append(e)
                    if isinstance(inter, Point):
                        # consider when intersection is below end
                        # if this is not considered next edges will create cuplicated intersection
                        if point.coinside(inter, s):
                            pass
                        elif point.coinside(inter, e):
                            inter_points.append([b+1+split_increment, inter])
                        else:
                            inter_points.append([b+1+split_increment, inter]) # i+ is to indicate vertex index
                            split_increment += 1
                            # and how can at the same time split edge and store?
                            # adding as a list not to change length, not to interfear iteration
                            splited_vertices.insert(-1,inter)

                if len(inter_points) < 2:
                    new_shapes.append(shape)
                    continue
                # now need to find portals
                # need to order points on line then pick valid segments
                # then porsion lists then combine lists to form a shape
                print(inter_points)
                _, index = point.sort_on_line([i[1] for i in inter_points],c)
                inter_points = data.list_item(inter_points, *index)
                # s,e = string.vertex(shape,0), string.vertex(shape,-2)
                bridges = []
                splits = set()
                for b in range(len(inter_points) -1):
                    print(inter_points)
                    p1,p2 = inter_points[b][1], inter_points[b+1][1]
                    split = set((inter_points[b][0], inter_points[b+1][0]))

                    mid_point = point.average([p1,p2])
                    # if point is in
                    if polygone.point_in(shape,mid_point) == 2:
                        # TODO for curved or pline need more generalization of segment
                        if isinstance(c, Line):
                            segment = line.con_points(p1,p2)
                        elif isinstance(c, Polyline):
                            raise FunctionNotDefinedError()
                        else:
                            raise FunctionNotDefinedError()
                        bridges.append([p1, p2, segment])
                        splits = splits.union(split)

                if len(splits) < 2:
                    new_shapes.append(shape)
                    continue

                # split edges
                splits = sorted(splits)
                sub_edge_list = []
                print(splits)
                # manage very end
                front = list(reversed(splited_vertices[splits[-1]:][:-1]))
                back = splited_vertices[:splits[0]+1]
                sub_edge_list.append([front[0],back[-1], polyline.con_points(front+back)])

                for b in range(len(splits)-1):
                    s_i,e_i = splits[b], splits[b+1]
                    vertices = splited_vertices[s_i:e_i+1]
                    sub_edge_list.append([vertices[0],vertices[-1],polyline.con_points(vertices)])

                # not jump with portals
                edges_list = []
                while True:
                    new_set = []
                    start, end, edge = sub_edge_list.pop()
                    new_set.append(edge)
                    while True:
                        # look for all bridge connection
                        bridges_copy = bridges.copy()
                        while True:
                            flag_not_found = True
                            for b in bridges_copy:
                                print(end,b[:2])
                                mask = point.in_points([end], *b[:2])
                                print(mask)
                                if any(mask):
                                    bridges_copy.remove(b)
                                    new_set.append(b[2])
                                    end = data.cull_pattern(b[:2],mask, flip_mask=True)[0]
                                    flag_not_found = False
                                    break
                                else:
                                    pass

                            if flag_not_found:
                                break
                        # if travel is closed
                        if point.coinside(start, end):
                            edges_list.append(new_set)
                            break
                        # look for another chunk
                        else:
                            for sub in sub_edge_list:
                                if point.coinside(end, sub[0]):
                                    sub_edge_list.remove(sub)
                                    new_set.append(sub[2])
                                    end = sub[1]
                                    break

                    if len(sub_edge_list) == 0:
                        break

                # form new polygon
                for i,l in enumerate(edges_list):
                    edges_list[i] = polygone.con_edges(l)

                new_shapes += edges_list

            shapes = new_shapes

        return  shapes



class point:
    @staticmethod
    def decon(poi:Point) -> [Number,Number,Number]:
        """
        Deconstructs point into x,y,z coordinates.
        :param poi:
        :return:
        """
        return poi.raw[:3,0].transpose().tolist()

    @staticmethod
    def dist_2_points(poi1:Point, poi2:Point) -> Number:
        """
        Calculates distance between two points.
        :param poi1:
        :param poi2:
        :return:
        """
        v = []
        for a,b in zip(point.decon(poi1), point.decon(poi2)):
            v.append(b-a)
        l = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
        return l

    @staticmethod
    def dist_to_line(poi:Point, lin:Line) -> Number:
        """
        Calculates shortest distence between the line and the point

        :param poi:
        :param lin:
        :return:
        """
        p_poi = point.project_on_line(poi, lin)
        return point.dist_2_points(poi,p_poi)

    @staticmethod
    def project_on_line(poi:Point, lin:Line) -> Point:
        """
        Project point on line of which projection line draws
        shortest between the point ant the line.

        :param poi:
        :param lin:
        :return:
        """
        origin = line.start(lin)
        v_to_poi = vector.con_2_points(origin,poi)
        v_from_start = vector.project_on_another(vector.con_line(lin), v_to_poi)
        p_p = trans.move(origin,v_from_start)
        return p_p

    @staticmethod
    def sort_on_line(points:(tuple,list), lin:Line) -> (tuple,list):
        """
        sorts points along the line
        if dirctional value is the same, point closer to line will come first
        :param points:
        :param lin:
        :return:
        """
        origin = line.start(lin)
        vec_lin = vector.con_line(lin)
        vectors = {}
        for i,p in enumerate(points):
            vec_o_to_p = vector.con_2_points(origin, p)
            vec_pro = vector.project_on_another(vec_lin, vec_o_to_p)
            dist_f_origin = vector.length(vec_pro)
            dist_f_pp = point.dist_2_points(trans.move(origin,vec_pro), p)
            if dist_f_origin not in vectors:
                vectors[dist_f_origin] = []
                vectors[dist_f_origin].append([dist_f_pp, i, p])
            else:
                vectors[dist_f_origin].append([dist_f_pp, i, p])

        # outer sort
        s = [i[1] for i in sorted(vectors.items(), key = lambda x:x[0])]
        points = []
        index = []
        for l in s:
            if len(l) == 1:
                points.append(l[0][2])
                index.append(l[0][1])
            else:
                # inner sort
                index_point = [i[1:] for i in sorted(l, key=lambda x:x[0])]
                points += [i[1] for i in index_point]
                index += [i[0] for i in index_point]
        return [points, index]

    @staticmethod
    def coplanar(points:Union[Tuple[Number,Number,Number], List[Number]]):
        raise


    @staticmethod
    def clockwise_check(points:(tuple, list), pla:Plane=Plane()):
        """
        see if points are ordered clockwise or anti-clockwise
        signs indicate followings;
        0 - clockwise
        1 - anti-clockwise
        None - can't define

        :param points: list of points to test
        :param pla: reference plane
        :return: one of (0,1,None)
        """
        if len(points) <= 2:
            # can't know order
            return None
        for p in points:
            if not isinstance(p, Point):
                raise WrongInputTypeError(Point, p)

        vectors = []
        for i in range(len(points)-1):
            vectors.append(vector.con_2_points(points[i], points[i+1]))

        order = 2
        for i in range(len(vectors)-1):
            o = vector.right_left_halfspace(vectors[i], vectors[i + 1], pla)
            if o == 3:
                return None

            if o == 2:
                continue
            else:
                if order == 2:
                    order = o
                else:
                    if order == 0:
                        if o == 0:
                            pass
                        else:
                            return None
                    else:
                        if o == 1:
                            pass
                        else:
                            return None
        if order == 2:
            return None
        else:
            return order


    @staticmethod
    def xyz(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.xyz)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def x(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis. append(p.x)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def y(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.y)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def z(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.z)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def in_points(cloud:(tuple, list), *points:Point) -> List[bool]:
        mask = []
        if len(points) == 0:
            return []

        for p in points:
            co = False
            for i in cloud:
                if point.coinside(p, i):
                    co = True
                    break
            mask.append(co)
        return mask

    @staticmethod
    def unique_points(points:(list, tuple)) -> List[Point]:
        """
        leave only unique points
        :param points:
        :return: [ [unique_points], [uniqueness index of all input] ]
        """
        # what index? index of uniqueness?
        unique_points = []
        unique_index = []
        for p in points:
            if not isinstance(p, Point):

                raise WrongInputTypeError(p, Point)

            unique = True
            for i,up in enumerate(unique_points):
                # if there is one that has same coordinate value don't add
                # if all is looked and there's isn't one coinside then add
                coinsides = True
                for a,b in zip(up.xyz, p.xyz):
                    # if any component is different go to next
                    if a != b:
                        coinsides = False
                        break
                # for all components equal inspecting point is not unique
                if coinsides:
                    unique = False
                    unique_index.append(i)
                    break
                else:
                    unique_index.append(len(unique_points))
                    continue

            if unique:
                unique_points.append(p)
            else:
                continue
        return [unique_points, unique_index]

    @staticmethod
    def coinside(point1:Point, point2:Point, atol=None) -> bool:
        if atol != None:
            raise
        else:
            return all(np.equal(point1.raw, point2.raw).flatten())

    @staticmethod
    def sort(points, mask:str = 'x'):
        """
        sort points by given ingredient

        :param mask: key to sort with, one of 'x','y','z'
        :param points: points to sort
        :return: sorted list of points
        """
        mask_index = {'x':0,'y':1,'z':2}
        if not mask in mask_index:
            raise ValueError
        if not all([isinstance(p, Point) for p in points]):

            raise TypeError

        keys = []
        i = mask_index[mask]
        for p in points:
            keys.append(p.xyz[i])
        sorted_list = sorted(zip(keys, points),key=lambda x: x[0])

        points = [i[1] for i in sorted_list]
        return points

    @staticmethod
    def sort_chunck():
        pass

    @staticmethod
    def equal(point1:Point, point2:Point) -> bool:
        if not isinstance(point1, Point) or not isinstance(point2, Point):
            return TypeError
        for a,b in zip(point1.xyz, point2.xyz):
            if not np.isclose(a,b, atol=DEF_TOLERANCE):
                return False
        return True

    @staticmethod
    def is_on_line(lin:Line, *points:(tuple, list)) -> bool:
        results = []
        directional1 = vector.con_line(lin)
        for poi in points:
            if not isinstance(poi, Point):
                raise TypeError

            if line.has_vertex(lin,poi):
                results.append(True)
                continue

            directional2 = vector.con_2_points(Point(*lin.start), poi)
            if vector.is_parallel(directional1, directional2):
                vertex = [lin.start[0], lin.end[0]]
                vertex = sorted(vertex)
                x = poi.x
                print(x,vertex)
                if x >= vertex[0] and x <= vertex[1]:
                    results.append(True)
                else:
                    results.append(False)
            else:
                results.append(False)

        if len(results) == 1:
            return results[0]
        return results

    @staticmethod
    def con_from_vector(vec:Vector):
        return Point(*vec.xyz)

    @staticmethod
    def perpendicular_on_vector(vec: Vector, poi: Point):
        vec2 = vector.con_point(poi)
        a = vector.angle_2_vectors(vec, vec2)
        l = np.cos(a) * vec2.length
        new_v = vector.amplitude(vec, l)
        return point.con_from_vector(new_v)

    @staticmethod
    def average(points:(list, tuple)) -> Point:
        coords = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            coords.append(p.xyz)
        coords = np.array(coords).transpose()
        new = []
        for l in coords:
            new.append(sum(l)/len(points))
        return Point(*new)


class math:

    """
    this wrapping is for precision control
    """
    @staticmethod
    def biggest(values, key=None):
        if key == None:
            return sorted(values)[-1]
        elif isinstance(key, callable):
            return sorted(values, key)[-1]
        elif isinstance(key, (list, tuple)):
            if len(values) != len(key):
                raise ValueError
            return sorted(zip(key, values), key=lambda x:x[0])[-1][1]
        else:
            raise TypeError

    @staticmethod
    def smallest(values, key=None):
        if key == None:
            return sorted(values)[0]
        elif isinstance(key, callable):
            return sorted(values, key)[0]
        elif isinstance(key, (list, tuple)):
            if len(values) != len(key):
                raise ValueError
            return sorted(zip(key, values), key=lambda x: x[0])[0][1]
        else:
            raise TypeError

    @staticmethod
    def any_one_of(compared, *values):
        for v in values:
            if compared == v:
                return True
        return False

    @staticmethod
    def sqrt(v):
        return np.sqrt(v, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def square(v):
        return np.square(v, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def power(base, exponent):
        return np.power(base, exponent, dtype=DEF_FLOAT_FORMAT)

class trigonometry:
    """
    this wrapping is for precision control
    """
    pi = np.pi
    pi2 = np.pi*2
    pih = np.pi/2

    @staticmethod
    def sin(v):
        np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def cos(v):
        np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def tan(v):
        np.tan(v,dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def arccos(cos_v):
        return np.arccos(cos_v,dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def arcsin(sin_v):
        return np.arcsin(sin_v, dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def degree_radian(degree):
        return np.radians(degree, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def radian_degree(radian):
        return np.degrees(radian, dtype=DEF_FLOAT_FORMAT)

class tri(trigonometry):
    pass

class vector:
    @staticmethod
    def con_zero_vector():
        """
        Returns new zero vector
        :return:
        """
        return Vector(0,0,0)

    @staticmethod
    def decon(vec:Vector):
        """
        Returns vector x,y,z elements
        :param vec:
        :return:
        """
        return vec.raw[:3, 0].transpose().tolist()

    @staticmethod
    def is_zero(vec:Vector):
        x,y,z = vector.decon(vec)
        if x == 0 and y == 0 and z == 0:
            return True
        else:
            return False

    @staticmethod
    def is_unit(vec:Vector):
        if vector.length(vec) == 1:
            return True
        return False



    @staticmethod
    def right_left_halfspace(vec_reference:Vector, vec_target:Vector, pla:Plane= Plane()) -> int:
        """
        identifies whether vector is on the left or right half space
        signs indicate followings;

        0 - right
        1 - left
        2 - same direction
        3 - reversed direction

        :param vec_reference:
        :param vec_target:
        :param pla:
        :return: [ right_left_sign, angle_to_left_right ]
        """
        quarter = vector.quarter_plane(vec_reference, pla=pla)
        ref_angle = vector.angle_plane(vec_reference,pla=pla)
        target_angle = vector.angle_plane(vec_target, pla=pla)

        if np.isclose(target_angle, ref_angle, atol=DEF_TOLERANCE):
            return [2, 0]
        else:
            if quarter == 0:
                if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
                    return [1,target_angle - ref_angle]
                elif target_angle < ref_angle:
                    return [0, ref_angle - target_angle]
                else:
                    return [0, ref_angle - (target_angle - tri.pi2)]
            elif quarter == 1:
                if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
                    return [1, target_angle - ref_angle]
                elif target_angle < ref_angle:
                    return [0, ref_angle - target_angle]
                else:
                    return [0, target_angle - (ref_angle + tri.pi)]
            elif quarter == 2:
                if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle -tri.pi and target_angle < ref_angle:
                    return [0, ref_angle - target_angle]
                elif target_angle < ref_angle - tri.pi:
                    return [1, ref_angle - tri.pi - target_angle]
                else:
                    return [1, target_angle - ref_angle]
            elif quarter == 3:
                if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle < ref_angle and target_angle > ref_angle - tri.pi:
                    return [0, ref_angle - target_angle]
                elif target_angle > ref_angle:
                    return [1, target_angle - ref_angle]
                else:
                    return [1, ref_angle - tri.pi - target_angle]


    @staticmethod
    def project_on_another(vec_projected_on:Vector, vec_projecting:Vector) -> Vector:
        u1,u2 = vector.unit(vec_projected_on), vector.unit(vec_projecting)
        if u1 is None or u2 is None:
            return vector.con_zero_vector()

        cos_v = vector.dot(u1,u2)
        projected = vector.amplitude(vec_projected_on, cos_v * vector.length(vec_projecting))
        return projected

    @staticmethod
    def length(vec:Vector) -> float:
        x,y,z = vec.xyz
        return np.sqrt(x*x + y*y + z*z)

    @staticmethod
    def dot(vec1:Vector, vec2:Vector) -> float:
        print(vec1, vec2)
        return vec1.raw.flatten().dot(vec2.raw.flatten())

    @staticmethod
    def cross(vec1:Vector, vec2:Vector) -> Vector:
        if not isinstance(vec1, Vector) or not isinstance(vec2, Vector):
            raise TypeError
        cross = np.cross(vec1.raw[:3,0], vec2.raw[:3,0])
        return Vector(*cross)

    @staticmethod
    def is_parallel(vec1:Vector, vec2:Vector) -> int:
        """
        definition of return value
        -1 opposite direction
        0 non-parallel
        +1 same direction

        :param vec1:
        :param vec2:
        :return:
        """
        unit1, unit2 = vector.unit(vec1), vector.unit(vec2)
        if unit1 == None or unit2 == None:
            return None

        cos_v = vector.dot(unit1, unit2)

        if np.isclose(cos_v, 1, atol=DEF_TOLERANCE):
            return 1
        elif np.isclose(cos_v, -1, atol=DEF_TOLERANCE):
            return -1
        else:
            return 0

    @staticmethod
    def con_2_points(start:Point, end:Point) -> Vector:
        coord = []
        for a,b in zip(start.xyz, end.xyz):
            coord.append(b-a)
        return Vector(*coord)

    @staticmethod
    def quarter_plane(vec:Vector, pla:Plane = Plane()) -> int:
        angle = vector.angle_plane(vec,pla)
        if angle >= 0 and angle <= np.pi/2:
            return 0
        elif angle > np.pi/2 and angle <= np.pi:
            return 1
        elif angle > np.pi and angle <= np.pi*1.5:
            return 2
        else:
            return 3

    @staticmethod
    def quarter_on_plane(vec:Vector, plane_hint:str):
        if not isinstance(vec, Vector):
            raise TypeError
        x,y,z = vec.xyz
        if plane_hint == 'xy' or plane_hint == 'yx':
            if x >= 0:
                if y >= 0:
                    return 0
                else:
                    return 3
            else:
                if y >= 0:
                    return 1
                else:
                    return 2

        elif plane_hint == 'yz' or plane_hint == 'zy':
            if y >= 0:
                if z >= 0:
                    return 0
                else:
                    return 3
            else:
                if z >= 0:
                    return 1
                else:
                    return 2

        elif plane_hint == 'zx' or plane_hint == 'xz':
            if z >= 0:
                if x >= 0:
                    return 0
                else:
                    return 3
            else:
                if x >= 0:
                    return 1
                else:
                    return 2
        else:
            raise ValueError

    @staticmethod
    def con_point(poi:Point):
        return Vector(*poi.xyz)


    # @tlist.calbranch
    # def average(*vectors: Vector):
    #     v = [i() for i in vectors]
    #     pass
    #
    #
    # @tlist.calitem
    # def con2pt(start: Point, end: Point):
    #     newv = Vector()
    #     newv.set_data(np.subtract(end(), start()))
    #     return newv

    @staticmethod
    def con_line(line:Line):
        if not isinstance(line, Line):
            raise TypeError
        xyz = []
        for a, b in zip(line.start, line.end):
            xyz.append(b - a)
        return Vector(*xyz)

    @staticmethod
    def unit(vec:Vector):
        if not isinstance(vec, Vector):
            raise WrongInputTypeError(Vector, vec)
        if vec.length == 0:
            return None
        xyz = []
        for i in vec.xyz:
            xyz.append(i/vec.length)
        return Vector(*xyz)

    @staticmethod
    def divide(vector:Vector, v, raw=False):
        pass

    # @staticmethod
    # def multiply(vector:Vector, v, ):
    #     if raw:
    #         return vector.raw*v
    #     else:
    #         return vector*v

    @staticmethod
    def amplitude(vector:Vector, amp:Number):
        new_v = vector*(amp/vector.length)
        return new_v

    @staticmethod
    def flip(vector:Vector):
        if not isinstance(vector, Vector):
            raise TypeError
        return Vector().from_raw(vector.raw*[[-1],[-1],[-1],[0]])

    @staticmethod
    def angle_2_vectors(from_vector, to_vector, degree=False):
        u1,u2 = vector.unit(from_vector), vector.unit(to_vector)
        if any([i==None for i in (u1,u2)]):
            return None
        cos_value = u1.raw.flatten().dot(u2.raw.flatten())
        angle = tri.arccos(cos_value)
        if degree:
            return tri.radian_degree(angle)
        else:
            return angle

    @staticmethod
    def angle_plane(vec:Vector, pla:Plane, degree:bool=False) -> Number:
        if not isinstance(vec,Vector):
            raise WrongInputTypeError(Vector, vec)
        if not isinstance(pla, Plane):
            raise WrongInputTypeError(Plane, pla)
        if not isinstance(degree, bool):
            raise WrongInputTypeError(bool, degree)

        o,x,y,z = plane.decon(pla)
        vec = vector.unit(vec)
        cos_value1, cos_value2 = vector.dot(x,vec), vector.dot(y,vec)
        if cos_value1 >= 0:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi*2 - tri.arccos(cos_value1)
        else:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi*2 - tri.arccos(cos_value1)
        print(angle)
        if degree:
            return tri.radian_degree(angle)
        else:
            return angle




    @staticmethod
    def decon_into_vectors(vec:Vector):
        on_xy = vec.raw.copy()
        on_xy[2,0] = 0
        on_yz = vec.raw.copy()
        on_yz[0,0] = 0
        on_xz = vec.raw.copy()
        on_xz[1,0] = 0
        return Vector().from_raw(on_xy),Vector().from_raw(on_yz),Vector().from_raw(on_xz)

    @staticmethod
    def project_on_xyplane(vec:Vector):
        new = vec.raw.copy()
        new[2,0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_yzplane(vec:Vector):
        new = vec.raw.copy()
        new[0, 0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_xzplane(vec:Vector):
        new = vec.raw.copy()
        new[1, 0] = 0
        return Vector().from_raw(new)

class matrix:
    @staticmethod
    def trans_from_origin_to_plane(pla:Plane) -> Matrix:
        return matrix.trans_between_origin_and_plane(pla)[1]
    @staticmethod
    def trans_from_plane_to_origin(pla:Plane) -> Matrix:
        return matrix.trans_between_origin_and_plane(pla)[0]

    @staticmethod
    def trans_between_origin_and_plane(pla:Plane) -> (Matrix, Matrix):
        """
        calculates two transform matrices
            [0] to_origin_matrix: transform matrix from plane to origin
            [1] to_plane_matrix: transform matrix from origin to plane

        :param pla: target plane
        :return: (tom, tpm)
        """
        to_origin_matrices = []
        to_plane_matrices = []
        origin, axis_x, axis_y, axis_z = plane.decon(pla)
        # this is the last move
        to_plane_vector = vector.con_point(origin)
        to_origin_matrices.append(matrix.translation(-to_plane_vector))
        to_plane_matrices.append(matrix.translation(to_plane_vector))

        # need to match each vectors
        # gonna match x,y,z
        # so looking into z rotation first

        # look for a vector that can be rotated
        vector_on_xy = vector.project_on_xyplane(axis_x)
        if vector_on_xy.length != 0:
            angle = vector.angle_2_vectors(Vector(1,0,0), vector_on_xy)
        else:
            vector_on_xy = vector.project_on_xyplane(axis_y)
            angle = vector.angle_2_vectors(Vector(0,1,0), vector_on_xy)
        quarter = vector.quarter_on_plane(vector_on_xy,'xy')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_z(angle)
        to_plane = matrix.rotation_z(-angle)
        to_origin_matrices.insert(0,to_origin)
        to_plane_matrices.append(to_plane)
        axis_x = trans.transform(axis_x, to_origin)
        axis_y = trans.transform(axis_y, to_origin)
        axis_z = trans.transform(axis_z, to_origin)

        # look into x rotation
        vector_on_yz = vector.project_on_yzplane(axis_y)
        if vector_on_yz.length != 0:
            angle = vector.angle_2_vectors(Vector(0,1,0), vector_on_yz)
        else:
            vector_on_yz = vector.project_on_yzplane(axis_z)
            angle = vector.angle_2_vectors(Vector(0,0,1), vector_on_yz)
        quarter = vector.quarter_on_plane(vector_on_yz, 'yz')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_x(angle)
        to_plane = matrix.rotation_x(-angle)
        to_origin_matrices.insert(0,to_origin)
        to_plane_matrices.append(to_plane)
        axis_x = trans.transform(axis_x, to_origin)
        axis_y = trans.transform(axis_y, to_origin)
        axis_z = trans.transform(axis_z, to_origin)

        # look into y rotation
        vector_on_xz = vector.project_on_xzplane(axis_z)
        if vector_on_xz.length != 0:
            angle = vector.angle_2_vectors(Vector(0,0,1), vector_on_xz)
        else:
            vector_on_xz = vector.project_on_xzplane(axis_x)
            angle = vector.angle_2_vectors(Vector(1,0,0), vector_on_xz)
        quarter = vector.quarter_on_plane(vector_on_xz, 'xz')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_y(angle)
        to_plane = matrix.rotation_y(-angle)
        to_origin_matrices.insert(0, to_origin)
        to_plane_matrices.append(to_plane)

        # all matrices collected
        to_origin_matrix = matrix.combine_matrix(*to_origin_matrices)
        to_plane_matrix = matrix.combine_matrix(*to_plane_matrices)

        return to_origin_matrix, to_plane_matrix

    @staticmethod
    def translation(vec: Vector):
        if not isinstance(vec, Vector):
            raise TypeError
        matrix = np.eye(4)
        matrix[:3, 3] = vec.xyz
        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_x(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = tri.degree_radian(angle)
        matrix[1] = 0, np.cos(angle), -tri.sin(angle), 0
        matrix[2] = 0, tri.sin(angle), np.cos(angle), 0

        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_y(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = tri.cos(angle), 0, tri.sin(angle), 0
        matrix[2] = -tri.sin(angle), 0, tri.cos(angle), 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_z(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = tri.cos(angle), -tri.sin(angle), 0, 0
        matrix[1] = tri.sin(angle), tri.cos(angle), 0, 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def scale(x,y,z):
        return Matrix(x,0,0,0,
                      0,y,0,0,
                      0,0,z,0,
                      0,0,0,1)

    @staticmethod
    def rotation_vector(vec:Vector, angle:Number, degree=False):
        raise

    @staticmethod
    def transform(matrix: Matrix, geometry):
        pass

    @staticmethod
    def transformation_2_planes(from_plane: Plane, to_plane: Plane):
        if not isinstance(from_plane, Plane) or not isinstance(to_plane, Plane):
            raise TypeError
        exit()

    @staticmethod
    def combine_matrix(*mat):
        result = np.eye(4)
        for m in reversed(mat):
            x = m.raw.copy()
            result = x.dot(result)
        return Matrix.from_raw(result)

class plane:
    @staticmethod
    def con_from_points():
        pass

    @staticmethod
    def relocate(pla:Plane, new_origin:Point) -> Plane:
        new_raw = pla.raw.copy()
        new_raw[:3, 0] = new_origin.xyz
        return Plane.from_raw(new_raw)

    @staticmethod
    def decon(pla:Plane) -> [Point, Vector, Vector, Vector]:
        """
        deconstruct plane
        returns origin, vector-x, vector-y, vectorz-z
        :param pla: plane to deconstruct
        :return: [ Point, Vector, Vector, Vector ]
        """
        return [Point(*pla.raw[:3,0]), Vector(*pla.raw[:3, 1]),Vector(*pla.raw[:3, 2]),Vector(*pla.raw[:3, 3])]

    @staticmethod
    def con_2_vectors(axis1: Vector, axis2: Vector, axis1_hint: str, axis2_hint: str, origin:Point):

        """
        Build a plane from given two axis.
        If given axes are not perpendicular axis2 will be transformed to make it correct as axis2_hint.

        :param origin: origin of the new plane
        :param axis1: first axis of the plane
        :param axis2: second axis of the plane
        :param axis1_hint: one of ('x','y','z')
        :param axis2_hint: one of ('x','y','z')
        :return: plane
        """
        projected = vector.project_on_another(axis1, axis2)
        axis2 = vector.con_2_points(point.con_from_vector(projected), point.con_from_vector(axis2))
        axis3 = vector.cross(axis1, axis2)

        axis_dic = {'x':None,'y':None,'z':None}
        axis_dic[axis1_hint] = axis1
        axis_dic[axis2_hint] = axis2
        for i in axis_dic:
            if i == None:
                axis_dic[i] = axis3

        if any([i is None for i in axis_dic.values()]):
            raise
        return plane.con_3_vectors(*axis_dic.value(),origin)

        # # check perpendicularity and if not build new axis2
        # if not np.isclose(vector.dot(axis1, axis2), 0.0, atol=DEF_TOLERANCE):
        #     p = point.con_from_vector(axis2)
        #     p_on_v = point.perpendicular_on_vector(axis1, p)
        #     axis2 = vector.con_2_points(p_on_v, p)
        # # make a set
        # axis = {'x':None, 'y':None, 'z':None}
        # axis[axis1_hint] = axis1
        # axis[axis2_hint] = axis2
        #
        # matrices_origin_to_plane = [matrix.translation(vector.con_from_point(origin))]
        # if axis['x'] != None:
        #     # if axis is given need to match to origin's axis
        #     # determine by rotating which origin axis y or z
        #     # TODO what to do with tolarence
        #     # if np.isclose(v.z,0.0,atol=TOLERANCE):
        #     if not np.isclose(axis['x'].z,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around y axis
        #         projected = vector.project_on_xzplane(axis['x'])
        #         q = vector.quarter_on_plane(projected,'xz')
        #         angle = vector.angle_2_vectors(Vector(1,0,0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_y(angle)
        #         to_plane = matrix.rotation_y(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['x'].y,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xyplane(axis['x'])
        #         q = vector.quarter_on_plane(projected, 'xy')
        #         angle = vector.angle_2_vectors(Vector(1,0,0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_z(angle)
        #         to_plane = matrix.rotation_z(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # if axis['y'] != None:
        #     if not np.isclose(axis['y'].z,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around x axis
        #         projected = vector.project_on_yzplane(axis['y'])
        #         q = vector.quarter_on_plane(projected, 'yz')
        #         angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_x(angle)
        #         to_plane = matrix.rotation_x(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['y'].x,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xyplane(axis['y'])
        #         q = vector.quarter_on_plane(projected, 'xy')
        #         angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_z(angle)
        #         to_plane = matrix.rotation_z(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # if axis['z'] != None:
        #     # if axis is given need to match to origin's axis
        #     # determine by rotating which origin axis y or z
        #     # TODO what to do with tolarence
        #     # if np.isclose(v.z,0.0,atol=TOLERANCE):
        #     if not np.isclose(axis['z'].y,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around y axis
        #         projected = vector.project_on_yzplane(axis['z'])
        #         q = vector.quarter_on_plane(projected, 'yz')
        #         angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_x(angle)
        #         to_plane = matrix.rotation_x(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['z'].x,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xzplane(axis['z'])
        #         q = vector.quarter_on_plane(projected, 'xz')
        #         angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_y(angle)
        #         to_plane = matrix.rotation_y(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # default_plane = Plane([0,0,0],[1,0,0],[0,1,0],[0,0,1])
        # default_plane = trans.transform(default_plane, *matrices_origin_to_plane)
        # return default_plane

    @staticmethod
    def con_vector_point(axis: Vector, poi: Point, axis_hint: str, point_hint: str, origin: Point = Point(0, 0, 0)):
        projected_point = point.perpendicular_on_vector(axis, poi)
        perpen_v = vector.con_2_points(projected_point, poi)
        # and build a reference plane
        ref_plane = plane.con_2_vectors(axis, perpen_v, axis_hint, point_hint, origin)
        return ref_plane

    @staticmethod
    def con_3_vectors(x_axis: Vector, y_axis: Vector, z_axis: Vector, origin: Point = Point(0, 0, 0)):
        if not all([isinstance(i, Vector) for i in (x_axis, y_axis, z_axis)]):
            raise TypeError

        return Plane(origin.xyz, x_axis.xyz, y_axis.xyz, z_axis.xyz)

class rectangle:
    @staticmethod
    def con_center_width_height(plane:(Plane,Point), width:Number, height:Number) -> Rectangle:
        if not isinstance(width,Number) or not isinstance(height, Number):
            raise TypeError

        if isinstance(plane, Point):
            x,y,z = plane.xyz
            w,h = width/2, height/2
            return Rectangle([x-w,y+h,z],[x-w,y-h,z],[x+w,y-h,z],[x+w,y+h,z])

        elif isinstance(plane, Plane):
            rect = Rectangle([-w,+h,0],[-w,-h,0],[+w,-h,0],[+w,+h,0])
            return trans.orient(rect, Plane(), plane)

        else:
            raise TypeError


class hexahedron:

    @staticmethod
    def decon(hexa:Hexahedron) -> (Point,
                                   (Point,Point,Point,Point,Point,Point,Point,Point),
                                   (Rectangle,Rectangle,Rectangle,Rectangle,Rectangle,Rectangle)):
        pass
    @staticmethod
    def face_of(hexa:Hexahedron, *index:int):
        """
        how to correctly order vertex and faces
        face[0] = vertex 0,1,2,3 bottom
        face[1] = vertex 0,7,6,1
        face[2] = vertex 1,6,5,2
        face[3] = vertex 2,5,4,3
        face[4] = vertex 3,4,7,0
        face[5] = vertex 4,5,6,7 top

        :param index:
        :return:
        """
        if len(index) == 0 :
            raise ValueError
        if not all([isinstance(i, Number) for i in index]):
            raise ValueError
        vertex = hexa.vertex
        faces = []
        for i in index:
            i = i % 6
            if i == 0:
                a,b,c,d = vertex[0:4]
            elif i == 5:
                a,b,c,d = vertex[4:8]
            else:
                a,b,c,d = i-1%4, 8-i, 5+i, i%4
                a,b,c,d = vertex[a],vertex[b],vertex[c],vertex[d]
            faces.append(Tetragon(a,b,c,d))

        if len(faces) == 1:
            return faces[0]
        return faces

