import inspect
import copy

def print_message(text:str, header:str = '', where_from = None, var_info = None):
    """
    print with info about function and class of place
    of messege transmition.
    Will disturb destroying origin of weakref proxy.
    TODO think of relationship between inspect and weakref proxy
    I think that's because of 'inspect'.
    So use only for debuging before it is fixed for general use.
    :param text: comment to print
    :param header: category indication to print
    :return: None
    """
    # format header
    header = header.upper()
    # construct file path
    if where_from is None:
        path = ''
        stack = inspect.stack()
        for i,frameinfo in enumerate(stack):

            if i is not 0:
                path = f'.{frameinfo[3]}{path}'
            argvalues = inspect.getargvalues(frameinfo[0])
            if 'self' in argvalues[0]:
                instance = argvalues[3]['self']
                path = f'{instance.__class__.__name__}{path}'
                break
            elif 'cls' in argvalues[0]:
                instance = argvalues[3]['cls']
                path = f'{instance.__name__}{path}'
                break
    else:
        path = where_from

    #construct information about input variables
    if var_info is None:
        fullvarinfo = inspect.getargvalues(inspect.currentframe().f_back)
        varvalue = [fullvarinfo[3][i] for i in fullvarinfo[0]]
        varinfo = []
        for name, value in zip(fullvarinfo[0], varvalue):
            varinfo.append(f'{name} : {str(value)}')
    else:
        if isinstance(var_info, (tuple, list)):
            varinfo = var_info
        else:
            varinfo = [var_info]


    head = f'[from] {path}: '

    varhead = ' ' * (len(head) - 6) + 'ARGS: ' + varinfo[0]
    for i, j in enumerate(varinfo):
        varinfo[i] = ' ' * len(head) + j

    top = header + '-' * (len(head + text) - len(header))
    bottom = '-' * len(head + text)

    lines = top, head + text, varhead, *varinfo[1:], bottom

    for i in lines:
        print(i)