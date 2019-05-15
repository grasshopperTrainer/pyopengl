import numpy as np
from .primitives import *

def wrap(tlist: Tlist, times: int = 1):
    return tlist.copy().growbottom(times)


def unwrap(tlist: Tlist, times: int = 1):
    return tlist.copy().prunebottom(times)


def printdata(*trees: Tlist):
    longlines = []
    lines = [tree.print_data(True) for tree in trees]

    maxlen = max([len(i) for i in lines])
    for i in range(maxlen):
        line = ''
        for ii in range(len(lines)):
            try:
                line += f'{lines[ii][i]} '
            except:
                line += f'{len(lines[ii][0]) * " "} '
        longlines.append(line)

    for i in longlines:
        print(i)


def match_tallest(*trees: Tlist):
    # is it necessary?
    trees = copy.deepcopy(trees)

    branches = []
    for i in trees:
        if i.isleaf():
            branches.append([i])
        else:
            branches.append(i.get_data())

    isallleaf = all([all([i.isleaf() for i in tree]) for tree in branches])

    numbranches = [len(tree) for tree in branches]
    maxnum = max(numbranches)

    divmods = [divmod(maxnum, num) for num in numbranches]
    for i, v in enumerate(branches):
        d = divmods[i]
        newbranches = []
        for ii in range(d[0]):
            if ii is 0:
                newbranches += v
            else:
                newbranches += copy.deepcopy(v)

        newbranches += copy.deepcopy(v[:d[1]])
        branches[i] = newbranches

    if isallleaf:
        branches = pu.flip2dlist(branches)
        for i in branches:
            maxlen = max([len(n) for n in i])
            for ii in i:
                ii.tile(maxlen)
        branches = pu.flip2dlist(branches)
        branches = [Tlist(i) for i in branches]
        return branches
    else:

        flipped = [match_tallest(*i) for i in pu.flip2dlist(branches)]
        flipped = pu.flip2dlist(flipped)
        newtrees = [Tlist(i) for i in flipped]

        return newtrees


def calitem(orifunc):
    def wrapper(*args, makenew=True, **kwargs):

        # if i'm deeling with trees
        if all([isinstance(i, Tlist) for i in args]):
            matchedtrees = match_tallest(*args)
            allitems = [i.get_allitems() for i in matchedtrees]
            f = pu.flip2dlist(allitems)
            for items in f:
                if makenew:
                    items = copy.deepcopy(items)
                result = orifunc(*items, **kwargs)
                items[0].set_data(result)

            return matchedtrees[0]
        # else they are singular
        else:

            samelength = pu.tile_list(*args)
            samelength = pu.flip2dlist(samelength)
            results = []
            for i in samelength:
                if makenew:
                    i = copy.deepcopy(i)
                results.append(orifunc(*i, **kwargs))

            if len(results) is 1:
                return results[0]
            else:
                return results

    return wrapper


def calbranch(orifunc):
    def wrapper(*args, **kwargs):
        if all([isinstance(i, Tlist) for i in args]):
            matchedtrees = match_tallest(*args)
            allleafs = [i.get_allleafs() for i in matchedtrees]
            allleafs = pu.flip2dlist(allleafs)
            for leafs in allleafs:
                items = [[item() for item in leaf.get_allitems()] for leaf in leafs]
                r = orifunc(*items, **kwargs)

                if not isinstance(r, list):
                    r = [r]
                leafs[0].set_data(r)

            return matchedtrees[0]
        else:
            args = pu.tile_list(*args)
            result = orifunc(*args, **kwargs)
            return result

    return wrapper


@calitem
def test(x, y):
    return x + y


@calbranch
def test2(x, y):
    result = []
    for i, j in zip(x, y):
        result.append(i + j)
    return sum(result)


def empty(structure):
    if isinstance(structure, (list, tuple)):
        print(structure)
        # for i in structure
        #     if


def fromlist(data):
    if isinstance(data, (list, tuple)):
        simples = []
        iterables = []
        for i in data:
            if isinstance(i, (list, tuple)):
                iterables.append(i)
            else:
                simples.append(i)
        simples = Tlist(*simples)

        branches = []
        for i in iterables:
            branches.append(fromlist(i))
        return Tlist(simples, *branches)

    else:
        return Tlist(data)

# a = [[1,2,3,4,5],[2,3,3]]
# b = [[9,9,9,9,9],[3,4,4]]
# print(test2(a,b))
