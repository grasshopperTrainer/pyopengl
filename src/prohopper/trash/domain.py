from primitives import Primitive
from prohopper.tools.hlist import *


class Domain(Primitive):

    def __new__(cls, *args, **kwargs):
        start = float
        end = float
        try:
            start = float(args[0])
            end = float(args[1])
        except:
            print('(class)Domain :\n'
                  f'input start : {args[0]} should be float\n'
                  f'input end : {args[1]} should be float\n'
                  f"can't for an instance of Domain")
            return None
        return super().__new__(cls)

    def __init__(self, start, end, title: str = None):
        self.start = start
        self.end = end
        """
        :param start: start of domain
        :param end: end of domain
        :param title: title of domain
        """
        # in case only one var is given
        super().__init__([self.start, self.end], title)

    # def __repr__(self):
    #     return f'Domain {self.start} to {self.end}'

    def __str__(self):
        return f'{__class__.__name__} {self.start} to {self.end}'


@cal_manylists
def domain_numbers(numbers: Hlist):
    low = min(numbers)
    high = max(numbers)
    return Domain(low, high)


a = Domain(2, 3)
