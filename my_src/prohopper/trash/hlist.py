from primitives import Primitive
import inspect
import copy


class Hlist(Primitive):
    def __init__(self, *data, title: str = None):
        """
        definition of rood data type List(which is not a built in list)

        add functions inside the class if it is about only instance itself
        ex) def(self,~,~,~)

        if functions requires other instances
        ex) def(a:List,b:List,~,~,~)

        add it inside this MODULE not inside this class

        :param data: should bo instances of List or list of python builtin
        do not insert list of (class instance)Lists*
        """
        self.branch = tuple
        self._data = []
        self._dimension = int
        self._shape = list
        self._issimple = True
        # check if input is not List itself
        # if not this instance is a 'simple' List
        data_length = 0
        for i in data:
            if isinstance(i, Hlist):
                # this instance is not 'simple'
                self._issimple = False
                '''
                auto match structure operation should be here
                '''
                break
        # always maintain data as iterable
        self._data = [*data]

    def cal_item(return_copy: bool = False):
        """
        decorator for culculating with every item
        use this as described under:
        @cla_item(True,or False)
        def function(self):
            # consider self as an item of the Hlist
            result = do_somthing_with_self(self, *args)
            return result
        :return: new Hlist if copy sign is Ture. Else return None
        """

        def firstWrapper(func):

            def secondwrapper(*args, **kwargs):

                args = list(args)
                self = args[0]
                args.pop(0)
                if return_copy:
                    copied = copy.deepcopy(self)
                    reference = copied.get_refsimples()
                else:
                    reference = self.get_refsimples()

                for n in range(len(reference)):
                    datalist = reference[n].get_data()
                    for m in range(len(datalist)):
                        datalist[m] = func(datalist[m], *args, **kwargs)
                if return_copy:
                    return copied

            return secondwrapper

        return firstWrapper

    def cal_list(return_copy: bool = False):
        """
        decorator for culculating with every item
        use this as described under:
        @cla_list(True,or False)
        def function(self):
            # consider self as a list of items of Hlist
            result = do_somthing_with_self(self, *args)
            return result
        :return: new Hlist if copy sign is Ture. Else return None
        """

        def firstWrapper(func):
            def secondwrapper(*args, **kwargs):
                args = list(args)
                self = args[0]
                args.pop(0)
                if return_copy:
                    copied = copy.deepcopy(self)
                    reference = copied.get_refsimples()
                else:
                    reference = self.get_refsimples()

                for n in range(len(reference)):
                    data = func(reference[n].get_data(), *args, **kwargs)
                    reference[n].insert_data(data)
                if return_copy:
                    return copied

            return secondwrapper

        return firstWrapper

    def __add__(self, other):
        @cal_manyitems
        def func(a, b):
            return a + b

        return func(self, other)

    def __sub__(self, other):
        @cal_manyitems
        def func(a, b):
            return a - b

        return func(self, other)

    @cal_list(True)
    def __getitem__(self, item):
        return self[item]

    def issimple(self):
        return self._issimple

    def get_data(self, index: int = None) -> list:
        if index is None:
            return self._data
        else:
            return self._data[index]

    def get_refsimples(self) -> list:
        if self.issimple():
            return [self]
        else:
            simples = []
            for i in self.get_data():
                simples += i.get_refsimples()
            return simples

    def get_data_aslist(self):
        copied_data = []
        # recursion exit statement
        if self.issimple():
            return self._data
        else:
            for i in self._data:
                copied_data.append(i.get_data_aslist())
        return copied_data

    def get_flatlist(self):
        copied_data = []
        # recursion exit statement
        if self.issimple():
            return self.get_data()
        else:
            for i in self._data:
                copied_data += i.get_flatlist()
        return copied_data

    def add(self, x, flip: bool = False):
        if flip:
            def _add(a, b):
                if isinstance(a, str):
                    b = str(b)
                return b + a
        else:
            def _add(a, b):
                if isinstance(a, str):
                    b = str(b)
                return a + b
        # read data and calculate
        return self._self(_add, x)

    def print_data(self, _count=0, asList=False):
        text = []

        # unicode characters fox drawing blocks

        if self.issimple():
            # recursion base condition
            text = []
            # get max lengths for formating string
            text_max_len = 0
            type_max_len = 0
            for i in self.get_data():
                text_len = len(str(i))
                type_len = len(i.__class__.__name__)
                text_max_len = text_len if text_max_len < text_len else text_max_len
                type_max_len = type_len if type_max_len < type_len else type_max_len

            # format text
            for i in self.get_data():
                # add spaces to match line width
                a = i.__class__.__name__ + ' ' * (type_max_len - len(i.__class__.__name__))
                b = str(i) + ' ' * (text_max_len - len(str(i)))
                text.append(f'{vr} {a} : {b} {vr}')

            # add top bottom enclosure
            text.insert(0, lu + hr * (text_max_len + type_max_len + 5) + ru)
            text.append(ld + hr * (text_max_len + type_max_len + 5) + rd)

        else:
            # recursion condition
            block = []
            for i in self._data:
                block.append(i.print_data(_count=_count + 1))

            # get width to draw top bottom enclosure lines
            block_max_length = 0
            text_max_len = 0
            for i in block:
                # get longest of inner blocks
                for n in range(len(i)):
                    # flatten lists
                    text.append(i[n])
                    # while reading all the lines... save widest
                    text_max_len = len(i[n]) if len(i[n]) > text_max_len else len(i[n])
                block_max_length = text_max_len if text_max_len > block_max_length else block_max_length

            # formatting
            for i in range(len(text)):
                line = text[i]
                text[i] = vr + line + ' ' * (block_max_length - len(line)) + vr
            # insert enclosure
            text.insert(0, lu + hr * block_max_length + ru)
            text.append(ld + hr * block_max_length + rd)

        # after recursion is over
        if _count is 0 and asList is False:
            for i in text:
                print(i)

        return text

    def print_structure(self, _count=0, asList=False):
        text = []

        # unicode characters fox drawing blocks
        lu = u'\u2554'
        ru = u'\u2557'
        ld = u'\u255a'
        rd = u'\u255d'
        vr = u'\u2551'
        hr = u'\u2550'

        if self.issimple():
            # recursion base condition
            text = []
            # get max lengths for formating string
            length = 8
            # make block
            text.append(lu + hr * length + ru)
            text.append(vr + '#' * length + vr)
            text.append(ld + hr * length + rd)

        else:
            # recursion condition
            block = []
            for i in self._data:
                block.append(i.print_structure(_count=_count + 1))

            # get width to draw top bottom enclosure lines
            block_max_length = 0
            text_max_len = 0
            for i in block:
                # get longest of inner blocks
                for n in range(len(i)):
                    # flatten lists
                    text.append(i[n])
                    # while reading all the lines... save widest
                    text_max_len = len(i[n]) if len(i[n]) > text_max_len else len(i[n])
                block_max_length = text_max_len if text_max_len > block_max_length else block_max_length

            # formatting
            for i in range(len(text)):
                line = text[i]
                text[i] = vr + line + ' ' * (block_max_length - len(line)) + vr
            # insert enclosure
            text.insert(0, lu + hr * block_max_length + ru)
            text.append(ld + hr * block_max_length + rd)

        # after recursion is over
        if _count is 0 and asList is False:
            for i in text:
                print(i)
        return text

    def get_ref_lists(self, _count=0) -> list:

        if self.issimple():
            return [self]
        else:
            data = []
            for i in self._data:
                data_list = i.get_ref_lists(_count=_count + 1)
                for i in data_list:
                    data.append(i)
        # while ascending from base
        if _count is not 0:
            return data
        else:
            return data

    @cal_item(True)
    def get_nulled(self) -> 'Hlist':
        return None

    @cal_list(True)
    def get_empty(self) -> 'Hlist':
        return None

    @cal_list(True)
    def list_item(self, index) -> 'Hlist':
        return self[index]

    def get_unwrap(self, level: int = 0, _count=0):
        # base condition
        if self.issimple():
            return self
        else:
            data = []
            for i in self.get_data():
                data += i.get_data()

            if level is _count:
                return Hlist(*data)
            else:
                return Hlist(*data).get_unwrap(level, _count=_count + 1)

    def get_wrap(self, level: int = 0, _count=0):
        new = Hlist(self)
        if level is not _count:
            return new.get_wrap(level, _count=_count + 1)
        else:
            return new

    #
    # def data_wrap(self, level: int = 0, _count = 0):
    #     if _count is level: # base condition
    #         if self.issimple():
    #             print('simple', self.get_data())
    #             new_Lists = []
    #             for i in self.get_data():
    #                 new_Lists.append(Hlist(i))
    #             return Hlist(*new_Lists)
    #         else:
    #             return Hlist(self)
    #     else:
    #         data = []
    #         _count += 1
    #         for i in self.get_data():
    #             print('not there', _count, level, self)
    #             data.append(i.data_wrap(level, _count))
    #         return Hlist(*data)

    def get_maxdepth(self, _level=0) -> int:
        """
        returns dimension of a HList
        0 means simple HList
        :param _level: DO NOT TOUCH arg for inner use
        :return: maximum level
        """
        if self.issimple():
            return _level
        else:
            _level += 1
            depth = []
            for i in self.get_data():
                depth.append(i.get_maxdepth(_level))

        return max(depth)

    def set_data(self, data, index=None):
        if index is None:
            if not isinstance(data, list):
                data = [data]
            for i in data:
                if isinstance(i, Hlist):
                    # this instance is not 'simple'
                    self._issimple = False
                    '''
                    auto match structure operation should be here
                    '''
                    break
            self._data = data
        else:
            if isinstance(data, Hlist):
                self._issimple = False
            self._data[index] = data

    def isList(self):
        return True

    def insert_data(self, data: list):
        if not isinstance(data, list):
            data = [data]
        for i in data:
            if isinstance(i, Hlist):
                # this instance is not 'simple'
                self._issimple = False
                '''
                auto match structure operation should be here
                '''
                break
        self._data = data


def print_compared_data(*Lists):
    for i in Lists:
        try:
            i.isList()
        except:
            print("def print_compare_data : all the input shoud be an instance of (class)List")

    lines = [i.print_data(asList=True) for i in Lists]
    length = max([len(i) for i in lines])
    parr = []
    for i in range(length):
        line = ''
        space = ' '
        for n in lines:
            try:
                line += space + n[i]
            except:
                line += space + ' ' * len(n[0])
        parr.append(line)
    for i in parr:
        print(i)


# def new_flattened(source:Hlist, _count = 0) -> Hlist:
#     # recursion base condition
#     if source.issimple():
#         def push():
#             for i in source.get_data():
#                 yield i
#         return push()
#     else:
#         data = []
#         for i in source._data:
#             data += new_flattened(i,_count = _count+1)
#     # while ascending from base
#     if _count is not 0:
#         return data
#     else:
#         return Hlist(*data)

def data_match_assend(reference, target):
    new_List = Hlist()

    return new_List


def match_descend(reference: Hlist, target: Hlist) -> Hlist:
    """

    :param reference:
    :param target:
    :return:
    """
    # when got into the bottom of reference return longest list
    if reference.issimple():
        a = reference.get_data()
        b = target.get_flatlist()
        matched = data_tile(a, b)
        # print(matched)
        return Hlist(*matched[1])
    else:
        a = reference.get_data()
        if target.issimple():
            b = [target]
        else:
            b = target.get_data()
        matched = data_tile(a, b)
        data = []

        for i in range(len(matched[1])):
            data.append(match_descend(matched[0][i], matched[1][i]))
        return Hlist(*data)


def data_tile(*data: list, length=None):
    """
    duplicate iterable to match certain length
    :param data: lists to compare
    :param length: length to match to
    :return: list of lists
    """

    # if length is not given search for longest
    if length is None:
        length = max([len(i) for i in data])

    result = []
    for i in data:
        d = divmod(length, len(i))
        result.append(i * d[0] + i[:d[1]])
    if len(result) is 1:
        return result[0]
    else:
        return result


def deepest(*hlists: Hlist) -> Hlist:
    """
    returns first Hlist that is of a deepest dimension
    :param hlists: instances of Hlist to compare
    :return: first one that is of a deepest
    """
    # incase comparings are simple return longest
    if sum([i.issimple() for i in hlists]) is len(hlists):
        lengths = [len(i.get_data()) for i in hlists]
        longest = list(hlists).pop(lengths.index(max(lengths)))
        return longest
    # else comparing multi dimensionals
    else:
        deepest = hlists[0]
        last_depth = hlists[0].get_maxdepth()
        for i in hlists:
            depth = i.get_maxdepth()
            if depth > last_depth:
                deepest = i
            last_depth = depth

        return deepest


def list_item(source: Hlist, index: int):
    @source.cal_list()
    def func(l, index):
        return l[index]

    result = func(source, index)
    return result


def list_flip(*lists: list) -> list:
    """
    flip 2d list of lists
    from: ( [a1, a2, a3],  get: ( [a1, b1],
            [b1, b2, b3] )        [a2, b2],
                                  [a3, b3] )

    :param lists: var arg of lists ( [...], [...], [...] )
                  numbers of elements in child list must be equal
    :return: fliped tuple of lists
    """
    row = len(lists)
    column = len(lists[0])
    print(row, column)
    list_fliped = []
    for n in range(column):
        new_row = []
        for m in lists:
            new_row.append(m[n])
        list_fliped.append(new_row)

    return list_fliped


def cal_manyitems(original_func):
    """
    use this wrapper to use native python context in making functions of Hlists
    :param original_func:
    :return:
    """

    def wrapper(*args, **kwargs):
        source = deepest(*args)
        matched_args = [match_descend(source, i) for i in args]
        # print_compared_data(*matched_args)
        ref = [i.get_ref_lists() for i in matched_args]
        # print(ref)
        newlist = matched_args[0].get_nulled()
        frame = newlist.get_ref_lists()
        # print(frame)
        for q in range(len(ref[0][0].get_data())):
            for m in range(len(ref[0])):
                dataset = []
                for n in range(len(ref)):
                    dataset.append(ref[n][m].get_data()[q])
                # try calculation and return None when can't
                try:
                    output = original_func(*dataset, **kwargs)
                except:
                    print(f'from.({original_func.__class__.__name__}){original_func.__name__}: input type missmatch')
                    output = None

                # but why not isinstance(output, Hlist)?

                frame[m].set_data(output, q)

        return newlist

    return wrapper


def cal_manylists(original_func):
    def wrapper(*args, **kwargs):
        source = deepest(*args)
        matched_args = [match_descend(source, i) for i in args]
        # print_compared_data(*matched_args)
        ref = [i.get_ref_lists() for i in matched_args]
        # print(ref)
        newlist = matched_args[0].get_nulled()
        frame = newlist.get_ref_lists()

        for m in range(len(ref[0])):
            dataset = []
            for n in range(len(ref)):
                dataset.append(ref[n][m].get_data())
            frame[m].insert_data(original_func(*dataset, **kwargs))

        return newlist

    return wrapper


@cal_manylists
def list_merge(*hlists: Hlist):
    merged = []
    for i in hlists:
        merged += i
    return merged


@cal_manyitems
def cal(a: str, b: str, c: str, x=None):
    new = a + c * 2 + b * 3
    return new

# a = Hlist('a','b','c')
# b = Hlist('d','e',3)
# c = Hlist('m','n','q')
# d = Hlist('x','y','z')
# ab = Hlist(a,b)
# cd = Hlist(c,d)
# abcd = Hlist(ab,cd)
# abc = Hlist(ab,c)
# x = [0,0,0,0]
# y = [0,0,0]
# z = [0,0]
# k = cal(a,b,abcd)
# k.print_data()
# ab[0].print_data()
# wrapped = abcd.get_wrap(2)
# unwrapped = wrapped.get_unwrap(5)
# print_compared_data(ab,wrapped,abcd,unwrapped)

# print(ab.test())
# ab.print_data()
# # ab.sum()
# # ab.print_data()
# ab.get_nulled().print_data()
# # print_compared_data(cal_many(ab,abcd,abc),abcd)
# # cal_many(ab,abcd,abc)
# # testtest()
# # def func(args):
# #     return args+ 'x'
# # kkk = ab.cal_item(func)
# # kkk.print_data()
# # ab.print_data()
# # kkk.get_nulled().print_data()
# # kkk.get_empty().print_data()

# a = Hlist(1,2,3,4)
# b = Hlist(5,5,5,5)
# x = b-a
# y = a+b
# x.print_data()
# y.print_data()
