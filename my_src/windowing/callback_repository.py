import weakref
import copy
from collections import namedtuple

from .windows import Windows


class Callback_repository:
    def __init__(self, window, callback_names):
        self._window = weakref.ref(window)
        self._callback_names = callback_names
        self._callbacks_struct = {}
        self._callback_struct = namedtuple('callback', ['function','args','kwargs','identifier','singular',])
        for i in callback_names:
            self._callbacks_struct[i] = []

        self._callbacks_repo = weakref.WeakKeyDictionary()
    @property
    def deleters(self):
        return list(self._callbacks_repo.keys())
    @property
    def window(self):
        return self._window()

    def exec(self, callback_name, *args, **kwargs):
        # set window
        window_swap = None
        if Windows.get_current() != self.window:
            window_swap = Windows.get_current()
            Windows.set_current(self.window)
            self.window.make_window_current()

        # !!! prevent memory leak !!!
        # while looking into dict as well as check if deleter is useless
        # TODO is it fast enough to repeat it in every call?
        to_delete = []
        for deleter, dic in self._callbacks_repo.items():
            empty = True
            for i in dic.values():
                if len(i) != 0:
                    empty = False
                    break
            if empty:
                to_delete.append(deleter)

            # if not an empty run regularly
            else:
                for callback in dic[callback_name]:
                    f, a, k, i, s = callback
                    for fi,ai,ki in zip(f,a,k):
                        if isinstance(fi, weakref.ReferenceType):
                            if fi() is None:
                                dic[callback_name].remove(callback)
                                continue
                            else:
                                fi = fi()
                        fi(*ai, **ki)

                    if s:
                        dic[callback_name].remove(callback)

        # delete empty deleter-dict
        for i in to_delete:
            del self._callbacks_repo[i]

        # reset window
        if window_swap != None:
            Windows.set_current(window_swap)
            window_swap.make_window_current()

        # return wrapper

    def setter(self, callback_name, function, args: tuple = (), kwargs: dict = {}, identifier: str = 'not_given', instant=False,
                    deleter=None):

        if isinstance(function, (tuple, list)):
            if len(args) == 0:
                args = [(),]*len(function)
            else:
                if len(args) != len(function):
                    raise

            if len(kwargs) == 0:
                kwargs = [(),]*len(function)
            else:
                if isinstance(kwargs, dict):
                    raise
                else:
                    if len(kwargs) != len(function):
                        raise
        else:
            if callable(function):
                if not isinstance(args, tuple):
                    raise TypeError
                if not isinstance(kwargs, dict):
                    raise TypeError
                function = [function,]
                args = [args,]
                kwargs = [kwargs,]

            else:
                raise TypeError

        # call dict by deleter
        if deleter is None:
            deleter = self
        # if deleter is weak
        if deleter not in self._callbacks_repo:
            callbacks_set = copy.deepcopy(self._callbacks_struct)
            if isinstance(deleter, weakref.ProxyType):
                deleter = deleter.__repr__.__self__
            self._callbacks_repo[deleter] = callbacks_set
        else:
            callbacks_set = self._callbacks_repo[deleter]
        #
        # # check callback equality
        # exist = True
        # need_new_name = True
        #
        # # func_name = function.__qualname__
        callbacks = callbacks_set[callback_name]
        # if func_name in callbacks:
        #     f, a, k, i, s = callbacks[func_name]
        #     # if length is the same need to inspect farther
        #     if identifier == i and len(f) == len(function):
        #         # gonna check all
        #         for s1,s2 in zip(zip(f,a,k), zip(function,args,kwargs)):
        #             fi,ai,ki = s1
        #             fii,aii,kii = s2
        #             if isinstance(fi, weakref.ReferenceType):
        #                 # if weakref dead i can override
        #                 if fi() is None:
        #                     # if at least one dead this callback set is useless
        #                     need_new_name = False
        #                     exist = False
        #                     break
        #                 # else need to check
        #                 else:
        #                     fi = fi()
        #             else:
        #                 pass
        #
        #             if fii.__code__ == fi.__code__ and all(a == b for a, b in zip(ai, aii)) and all(a == b for a, b, in zip(ki, kii)):
        #                 # if a function set is identical need to check rest
        #                 continue
        #             else:
        #                 exist = False
        #                 break
        #     else:
        #         exist = False
        #
        # else:
        #     need_new_name = False
        #     exist = False
        #
        # if need_new_name:
        #     # make name for similar
        #     count = 0
        #     while True:
        #         temp_name = f'{func_name}{count}'
        #         if temp_name in callbacks:
        #             count += 1
        #         else:
        #             func_name = temp_name
        #             break
        for i,func in enumerate(function):
            if hasattr(func, '__self__'):
                function[i] = weakref.WeakMethod(func)
            else:
                # function[i] = weakref.proxy(func)
                # raise
                pass
        new_set = (function, args, kwargs, identifier, instant)
        append = True
        for func_set in callbacks:
            if all(a==b for a,b in zip(func_set, new_set)):
                append = False
                break
        if append:
            callbacks.append(self._callback_struct(function, args, kwargs, identifier, instant))

        # return wrapper
    def __len__(self):
        # self.print_full()
        return len(self._callbacks_repo)
    @property
    def callback_names(self):
        return self._callback_names
    def get_callback_named(self, name):
        # new = weakref.WeakKeyDictionary()
        new = []
        for deleter, dict_of_callbacks in self._callbacks_repo:
            new.append(dict_of_callbacks[name] + [deleter,])
        return new
    # def print_full(self):
    #     for d,i in self._callbacks_repo.items():
    #         print()
    #         print('deleter is =', d)
    #         for n,l in i.items():
    #             print('name', n)
    #             print(l)
    #             # for n,l in ii:
    #             #     for ii in l:
    #             #         print(ii)
    def remove_by_deleter(self, deleter):
        if deleter in self._callbacks_repo:
            del self._callbacks_repo[deleter]

    def remove(self, deleter= None, identifier=None):
        if deleter == None:
            # TODO
            pass
        else:
            if deleter in self._callbacks_repo:
                if identifier is None:
                    del self._callbacks_repo[deleter]
                else:
                    callback_dicts = self._callbacks_repo[deleter]
                    # print('deleter', deleter)
                    for n,named_tuple_list in callback_dicts.items():
                        # print('name and list', n, named_tuple_list)
                        to_delete = None
                        for i,np in enumerate(named_tuple_list):
                            if np.identifier == identifier:
                                to_delete = i
                                break
                        if to_delete != None:
                            named_tuple_list.pop(to_delete)
                        # print('after')
                        # print('name and list', n, named_tuple_list)

