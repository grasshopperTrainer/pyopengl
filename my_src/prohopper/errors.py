class MyError(Exception):
    def __init__(self, msg=None):
        self.msg = None
        if msg != None and not isinstance(msg, str):
            raise TypeError

class MyWarning(UserWarning):
    def __init__(self, msg=None):
        self.msg = None
        if msg != None and not isinstance(msg, str):
            raise TypeError

class AllnumberError(MyError):
    def __str__(self):
        if self.msg == None:
            return 'all values should be numeric(Number type)'
        return self.msg
class NotFlatError(MyError):
    def __str__(self):
        if self.msg == None:
            return 'given is not flat'
        return self.msg
class FunctionNotDefinedError(MyError):
    def __str__(self):
        if self.msg == None:
            return 'Function is not yet defined'
        return self.msg

class InvalidInputWarning(MyWarning):
    def __str__(self):
        if selfmsg == None:
            return "Input is Invalid."
        else:
            return self.msg
class NullOutputWarning(MyWarning):
    def __str__(self):
        if self.msg == None:
            return "Couldn't generate output."
        else:
            return self.msg
class NotAllPointsWarning(MyWarning):
    def __str__(self):
        return "All input portion should represents Point"

class TempInstanceWarning(MyWarning):
    def __str__(self):
        if self.msg == None:
            return "Instance is not fully constructed yet."
        else:
            return self.msg

class WrongInputTypeError(Exception):
    def __init__(self, given_value=None, *target_type):
        if given_value == None:
            self.msg = f'Input type is incorrect'
        else:
            if len(target_type) == 0:
                target = ''
            elif len(target_type) == 1:
                target = f'Instance of <{target_type[0].__name__}> should be given.'
            else:
                target_str = ''
                for i in target_type:
                    target_str += f'<{i.__name__}>,'
                target = f'Instance of {target_str} should be given.'
            self.msg = f'Type of given input is <{given_value.__class__.__name__}>. ' +target

    def __str__(self):
        return self.msg

class NotCoordinateLikeError(Exception):
    def __init__(self, given_value=None):
        if given_value == None:
            self.msg = "input iterable doesn't resemble coordinate values"
        else:
            self.msg = f"input values {given_value} doesn't resemble coordinate values"

    def __str__(self):
        return self.msg
