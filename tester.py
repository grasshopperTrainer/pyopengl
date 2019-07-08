from collections import namedtuple



a = namedtuple('d', ['g','l'])

b = a(10,20)
print(b.l)