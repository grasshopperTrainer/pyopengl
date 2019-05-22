import inspect

class SMI:
    """
    Inheritance class for forcing method, argument overriding
    Inherit this class to a template (class A(SMI):) and define arguments and methods
    to force (class B(A):) override hinted arg, methods by following context

    to warn user:
        1. a = SMI.should_arg
        2.
        @SMI.should_func
        def some_method(self):
            pass
    this will print warning message

    to force user:
        1. a = SMI.must_arg
        2.
        @SMI.must_func
        def some_method(self):
            pass
    this will raise Exception

    """

    def __new__(cls, *args, **kwargs):
        tree = inspect.getmro(cls)
        child = None
        for i, cla in enumerate(tree):
            if cla.__name__ == 'SMI':
                child = tree[i - 1]

        child_should_methods = {}
        child_must_methods = {}

        child_should_arguments = {}
        child_must_arguments = {}

        for n, v in child.__dict__.items():
            if isinstance(v, tuple):
                f = v[0]
                if f == SMI.must_func:
                    child_must_methods[n] = v
                if f == SMI.should_func:
                    child_should_methods[n] = v

            elif callable(v):
                if v == SMI.must_arg:
                    child_must_arguments[n] = v
                elif v == SMI.should_arg:
                    child_should_arguments[n] = v

        mother_dict = dict(filter(lambda x: x[0][:2] != '__', inspect.getmembers(cls)))

        def undefined_method_check(source, pool):
            return_list = []
            for n,v in source.items():
                target = pool[n]
                if v is target:
                    return_list.append((n,v[1]))
                else:
                    if not callable(target):
                        if v[1] is target:
                            return_list.append((n,v[1]))
                    elif type(v[1]) != type(target):
                        return_list.append((n,v[1]))
            return return_list

        def undefined_argument_check(source, pool):
            return_list = []
            for n, v in source.items():
                target = pool[n]
                if v is target:
                    return_list.append((n,v))
                else:

                    if isinstance(target, property):
                        return_list.append((n,target))
                    elif target.__name__ == n:
                        return_list.append((n,target))
            return return_list

        should_methods_undefined = undefined_method_check(child_should_methods, mother_dict)
        must_methods_undefined = undefined_method_check(child_must_methods, mother_dict)

        should_arguments_undefined = undefined_argument_check(child_should_arguments,mother_dict)
        must_arguments_undefined = undefined_argument_check(child_must_arguments, mother_dict)

        # print(should_methods_undefined)
        # print(must_methods_undefined)
        # print(should_arguments_undefined)
        # print(must_arguments_undefined)

        # build warning message
        whole_message = ''
        # build should message
        if len(should_methods_undefined + should_arguments_undefined) != 0:
            should_header = f'Warning from SMI: (class) {cls.__name__} should have'

            # for method
            should_method_head = f'following methods of mother (class) {child.__name__} overriden:'
            should_method_body = []
            for name, method in should_methods_undefined:
                should_method_body.append(f'({method.__class__.__name__}) {name}')

            # for argument
            should_argument_head =f'following arguments of mother (class) {child.__name__} overriden:'
            should_argument_body = []
            for name, method in should_arguments_undefined:
                m = ''
                if isinstance(method, property):
                    m = '(overriden by property) '
                elif method != SMI.should_arg:
                    m = '(overriden by function) '
                should_argument_body.append(f'{m}{name}')

            # format message
            whole_message += f'''
    {should_header}'''
            if len(should_method_body) != 0:
                whole_message += f'''
        {should_method_head}'''
                for line in should_method_body:
                    whole_message += f'''
            {line}'''
            if len(should_argument_body) != 0:
                whole_message += f'''
        {should_argument_head}'''
                for line in should_argument_body:
                    whole_message += f'''
            {line}'''

        # build must message
        if len(must_methods_undefined + must_arguments_undefined) != 0:
            must_header = f'Error from SMI: (class) {cls.__name__} must have'

            must_method_head = f'following methods of mother(class) {child.__name__} overriden:'
            must_method_body = []
            for n,method in must_methods_undefined:
                must_method_body.append(f'({method.__class__.__name__}) {n}')

            must_argument_head = f'following arguments of mother(class) {child.__name__} overriden:'
            must_argument_body = []
            for name,method in must_arguments_undefined:
                m = ''
                if isinstance(method, property):
                    m = '(overriden by property) '
                elif method != SMI.must_arg:
                    m = '(overriden by function) '
                must_argument_body.append(f'{m}{name}')

            # format message
            s = '\n' if len(whole_message) != 0 else ''
            whole_message += f'''{s}
    {must_header}'''
            if len(must_method_body) != 0:
                whole_message += f'''
        {must_method_head}'''
                for line in must_method_body:
                    whole_message += f'''
            {line}'''
            if len(must_argument_body) != 0:
                whole_message += f'''
        {must_argument_head}'''
                for line in must_argument_body:
                    whole_message += f'''
            {line}'''

            raise Exception(whole_message)

        # if only should just print and continue
        print(whole_message)

        self = super().__new__(cls)
        return self


    @classmethod
    def must_func(cls, func):
        return SMI.must_func, func

    @classmethod
    def must_arg(cls):
        return SMI.must_arg

    @classmethod
    def should_arg(cls):
        return SMI.should_arg

    @classmethod
    def should_func(cls, func):
        return SMI.should_func, func