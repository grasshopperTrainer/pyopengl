import weakref
import copy

from .windows import Windows


class Callback_repository:
    def __init__(self, window, callback_names):
        self._window = weakref.ref(window)

        self._callbacks_struct = {}
        for i in callback_names:
            self._callbacks_struct[i] = []

        self._callbacks_repo = weakref.WeakKeyDictionary()

    @property
    def window(self):
        return self._window()

    def exec(self, callback_name, *args, **kwargs):
        window_swap = None
        if Windows.get_current() != self.window:
            window_swap = Windows.get_current()
            Windows.set_current(self.window)
            self.window.make_window_current()

        for dic in self._callbacks_repo.values():
            to_delete = []
            for callback in dic[callback_name]:
                f, a, k, i, s = callback
                for fi,ai,ki in zip(f,a,k):
                    if isinstance(f, weakref.ReferenceType):
                        if fi() is None:
                            to_delete.append(n)
                        else:
                            if s:  # remove if instant
                                to_delete.append(n)
                            else:
                                fi = fi()
                    fi(*ai, **ki)

            for i in to_delete:
                del dic[callback_name][i]

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

        new_set = (function, args, kwargs, identifier, instant)
        append = True
        for func_set in callbacks:
            if all(a==b for a,b in zip(func_set, new_set)):
                append = False
                break
        if append:
            callbacks.append([function, args, kwargs, identifier, instant])

        # return wrapper