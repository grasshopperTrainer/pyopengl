def tile_list(*lists):
    lists = list(lists)
    for i, v in enumerate(lists):
        if not isinstance(v, (list, tuple)):
            lists[i] = [v]

    maxlen = max([len(i) for i in lists])
    tiled = []
    # print(lists,maxlen)
    for i in lists:
        d = divmod(maxlen, len(i))
        tiled.append(i * d[0] + i[:d[1]])

    if len(lists) is 1:
        return tiled[0]
    else:
        return tiled


def flip2dlist(listoflists: list):
    flipped = []
    for i in range(len(listoflists[0])):
        columns = []
        for ii in range(len(listoflists)):
            columns.append(listoflists[ii][i])
        flipped.append(columns)
    return flipped
