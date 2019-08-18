class MyError(Exception):
    def __init__(self, msg=None):
        self.msg = None
        if msg != None and not isinstance(msg, str):
            raise TypeError

class CoordinateLikeError(MyError):
    def __str__(self):
        if self.msg is None:
            return 'input value should be iterables representing coordinate values'
        return self.msg

class AllnumberError(MyError):
    def __str__(self):
        if msg == None:
            return 'all values should be numeric(Number type)'
        return self.msg

class WrongInputTypeError(Exception):
    def __init__(self, target_type=None, given_value=None):
        if target_type == None and given_value == None:
            self.msg = f'Input type is incorrect'
        else:
            self.msg = f'Type of given input is {given_value.__class__.__name__}. Instance of {target_type.__name__} should be given.'

    def __str__(self):
        return self.msg