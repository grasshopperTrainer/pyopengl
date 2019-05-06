import numpy as np
from prohopper.tools.primitives import Primitive


class Vector(Primitive):

    def __init__(self, x, y, z):
        self._data = np.array([x, y, z, 0])


a = Vector(1, 2, 0)

a = np.array([1, 2, 3])
b = np.zeros((3, 1))

print(a, a.shape)
print(b, b.shape)
print(a.dot(b), a)
for i in a:
    i = 10
print(a)
a = np.arange(0, 20).reshape((2, 10))
print(a)

for i in a:
    print('그냥', i, type(i))

for i in range(a[1].abs_size):
    print(i)
    a[1, i] = 10

a[1, range(a[1].abs_size)] = 5

print(a)
