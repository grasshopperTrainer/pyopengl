import numpy as np
import copy
import inspect


class Primitive:
    DIC = {}
    DATATYPE = np.float32

    def __init__(self, data, title: str = None):
        """
        Parent of all tools classes.
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

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # to ensure all the proceeding numpy calculation efficient
        if isinstance(value, np.ndarray):
            data = self.__class__.DATATYPE(value)
        self._data = value

    def get_data(self) -> list:
        return self._data

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
        return f'{self.__class__.__name__} : {self._data}'

    def set_data(self, data):

        # to ensure all the proceeding numpy calculation efficient
        if isinstance(data, np.ndarray):
            data = self.__class__.DATATYPE(data)
        self._data = data

    def get_data(self):
        return self._data

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


class Geometry(Primitive):

    def bymatrix(self, value):
        if isinstance(value, np.ndarray):
            self.data = value
        else:
            self.printmessage("input isn't matrix")
        return self

    @property
    def numvertex(self):

        return self().shape[1]

    @property
    def vertex(self):
        points = []
        d = self.data

        for i in range(self.numvertex):
            m = d[:, [i]]
            points.append(Point().bymatrix(m))
        return points

    @property
    def average(self):
        return Point().bymatrix(np.mean(self(), 1).reshape((4, 1)))

    @property
    def length(self):
        if self.numvertex is 1:
            return None
        else:
            segments = self.segments
            length = 0
            for i in segments:
                vec = i.vertex[1] - i.vertex[0]
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


class Vector(Geometry):

    def __init__(self, x: (int, float) = 0, y: (int, float) = 0, z: (int, float) = 0):
        self.set_data(np.array([[x], [y], [z], [0]]))

    def __str__(self):
        arr = self.get_data()
        return f'{self.__class__.__name__} : {arr[:3]}'

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            m = self() * other
            return Vector().bymatrix(self() * other)

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector().bymatrix(self() + other())

    @property
    def x(self):
        return self.data[0, 0]

    @property
    def y(self):
        return self.data[1, 0]

    @property
    def z(self):
        return self.data[2, 0]


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


class Point(Geometry):

    def __init__(self, x: (int, float) = 0, y: (int, float) = 0, z: (int, float) = 0):
        self.set_data(np.array([[x], [y], [z], [1]]))
        self.iterstart = 0

    def __str__(self, dataonly=False):
        arr = self.get_data()
        if dataonly:
            return f'{arr.T[0, :3]}'
        else:

            return f'P{arr.T[0, :3]}'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, Vector):
            return Point().bymatrix(self() + other())

    def __sub__(self, other):
        v = self() - other()
        return Vector().bymatrix(v)

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterstart < len(self.get_data()) - 1:
            self.iterstart += 1
            return self().item(self.iterstart - 1)
        else:
            self.iterstart = 0
            raise StopIteration

    @property
    def x(self):
        return self.data.item(0, 0)

    @property
    def y(self):
        return self.data.item(1, 0)

    @property
    def z(self):
        return self.data.item(2, 0)

    def get_listdata(self):
        return np.reshape(self.get_data(), (1, 4))[0, :3].tolist()


class Line(Geometry):
    def __init__(self, start: Point = Point(), end: Point = Point(10, 0)):
        self.set_data(np.concatenate((start(), end()), 1))

    def __call__(self, *args, **kwargs):
        if len(args) is 0:
            return self.data
        else:
            result = []
            for i in args:
                if isinstance(i, (float, int)):
                    v = self.vertex[1] - self.vertex[0]
                    newP = self.vertex[0] + v * i
                    result.append(newP)
                else:
                    result.append(None)
            if len(result) is 1:
                return result[0]
            else:
                return result

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Point().bymatrix(self() * other)

    def __str__(self):
        return f'Line {self.length}'

    @property
    def F(self):
        m = np.concatenate((self.vertex[1](), self.vertex[0]()), 1)

        return Line().bymatrix(m)

    @property
    def V(self):
        v = self.end - self.start
        return v

    @property
    def start(self):
        return self.vertex[0]

    @property
    def end(self):
        return self.vertex[1]


class Rect(Geometry):

    def __init__(self,
                 lu: Point = Point(-1, 1),
                 ld: Point = Point(-1, -1),
                 rd: Point = Point(1, -1),
                 ru: Point = Point(1, 1)):
        self.set_data(np.concatenate((lu(), ld(), rd(), ru()), 1))

        # self.vertex = None

    def __str__(self):
        return f'Rect{self.center().get_listdata()}'

    @property
    def domain(self):
        pass

    def center(self) -> Point:
        return self.average

    def get_size(self):
        p1 = self.vertex(0)
        p2 = self.vertex(1)
        p3 = self.vertex(2)
        width = p3.x - p2.x
        height = p1.y - p2.y
        return width, height

    def print_data(self):
        size = self.get_size()
        print(f'center: {self.center()}, width: {size[0]}, height: {size[1]}')


def wrapindex(index, end):
    if index >= 0:
        return index % end
    else:
        return -(-index % (end + 1))


class Matrix(Primitive):
    pass


class Transformation(Primitive):

    def __init__(self, array: np.ndarray):
        self.set_data(array)

    pass