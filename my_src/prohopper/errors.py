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