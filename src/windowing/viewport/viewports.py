from numbers import Number
import OpenGL.GL as gl
import numpy as np
import weakref


class _CameraProperty:
    def __init__(self):
        self._dict = weakref.WeakKeyDictionary()

    def __set__(self, instance, value):
        self._dict[instance] = value

    def __get__(self, instance, owner):
        return self._dict[instance]


class _Camera:
    near = _CameraProperty()
    far = _CameraProperty()
    left = _CameraProperty()
    right = _CameraProperty()
    bottom = _CameraProperty()
    top = _CameraProperty()

    def __init__(self):
        self._mode = 1

        self.near = 5
        self.far = 1000
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1

        self._view_matrix = np.eye(4)
        self._projectioin_matrix = np.eye(4)

        self.build_PM()

    def move(self, value, x, y, z):
        if not isinstance(value, (tuple, list)):
            value = [-value, ] * 3
        else:
            value = [-i for i in value]

        matrix = np.eye(4)
        matrix[:, 3] = bool(x) * value[0], bool(y) * value[1], bool(z) * value[2], 1

        self._view_matrix = matrix.dot(self._view_matrix)

    def rotate(self, angle, x, y, z, radian=False):
        if radian:
            angle = -angle
        else:
            angle = np.radians(-angle)
        matrix = np.eye(4)

        if bool(x):
            new = np.eye(4)
            new[1] = 0, np.cos(angle), -np.sin(angle), 0
            new[2] = 0, np.sin(angle), np.cos(angle), 0
            matrix = new.dot(matrix)

        if bool(y):
            new = np.eye(4)
            new[0] = np.cos(angle), 0, np.sin(angle), 0
            new[2] = -np.sin(angle), 0, np.cos(angle), 0
            matrix = new.dot(matrix)

        if bool(z):
            new = np.eye(4)
            new[0] = np.cos(angle), -np.sin(angle), 0, 0
            new[1] = np.sin(angle), np.cos(angle), 0, 0
            matrix = new.dot(matrix)

        self._view_matrix = matrix.dot(self._view_matrix)

    def scale(self):
        # ???
        pass

    def lookat(self, to_point, from_point=None):
        if from_point is None:
            from_point = self._view_matrix.dot(np.array([[0, 0, 0, 1]]).T)
        else:
            self._view_matrix = np.eye(4)
            self.move(from_point, 1, 1, 1)
            from_point = np.array([from_point + [1, ]]).T

        to_point = np.array([to_point + [1, ]]).T
        vec = to_point - from_point

        x = vec[1]
        y = -vec[0]
        angle = np.arccos(x / np.sqrt(x * x + y * y))
        if y <= 0:
            angle = -angle
        self.rotate(angle, 0, 0, 1, True)

        y = np.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        z = vec[2]
        angle = np.arccos(z / np.sqrt(z * z + y * y)) - np.pi
        if y >= 0:
            angle = -angle
        self.rotate(angle, 1, 0, 0, True)

    def change_mode(self, mode):
        if isinstance(mode, str):
            if 'ortho' in mode:
                self._mode = 0
            elif 'proj' in mode:
                self._mode = 1
        else:
            self._mode = mode

    def build_PM(self):
        if self._mode == 0:
            if self.right == -self.left and self.top == -self.bottom:
                self._projectioin_matrix[[0, 1, 2, 2], [0, 1, 2, 3]] = \
                    [1 / self.right, \
                     1 / self.top, \
                     -2 / (self.far - self.near), \
                     -(self.far + self.near) / (self.far - self.near)]

            else:
                self._projectioin_matrix[[0, 0, 1, 1, 2, 2], [0, 3, 1, 3, 2, 3]] = \
                    [2 / (self.r - self.l),
                     -(self.r + self.l) / (self.r - self.l),
                     2 / (self.t - self.b),
                     -(self.t + self.b) / (self.t - self.b),
                     -2 / (self.f - self.n),
                     -(self.f + self.n) / (self.f - self.n)]

            self._projectioin_matrix[3] = 0, 0, 0, 1

        elif self._mode == 1:
            if self.right == -self.left and self.top == -self.bottom:
                self._projectioin_matrix[[0, 1, 2, 2], [0, 1, 2, 3]] = \
                    [self.near / self.right,
                     self.near / self.top,
                     -(self.far + self.near) / (self.far - self.near),
                     -2 * self.far * self.near / (self.far - self.near)]

            else:
                self._projectioin_matrix[[0, 0, 1, 1, 2, 2], [0, 2, 1, 2, 2, 3]] = \
                    [2 * self.near / (self.right - self.left),
                     (self.right + self.left) / (self.right - self.left),
                     2 * self.near / (self.top - self.bottom),
                     (self.top + self.bottom) / (self.top - self.bottom),
                     -(self.far + self.near) / (self.far - self.near),
                     -2 * self.far * self.near / (self.far - self.near)]

            self._projectioin_matrix[3] = 0, 0, -1, 0

    @property
    def width(self):
        return self.right - self.left

    @width.setter
    def width(self, w):
        self.right = w / 2
        self.left = -w / 2
        self.build_PM()

    @property
    def height(self):
        return self.top - self.bottom

    @height.setter
    def height(self, h):
        self.top = h / 2
        self.bottom = -h / 2
        self.build_PM()

    @property
    def VM(self):
        return self._view_matrix

    @property
    def PM(self):
        return self._projectioin_matrix


class _Viewport:
    def __init__(self, name, x, y, width, height):
        self._name = name
        self._posx = x
        self._posy = y
        self._width = width
        self._height = height

        self._current_viewport = None

        self._camera = _Camera()

    @property
    def posx(self):
        return self._posx

    @property
    def posy(self):
        return self._posy

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def camera(self):
        return self._camera

class Viewports:
    _current_viewport = None

    def __init__(self, window):
        self._window = window
        self._viewports = {}

    def new(self, x, y, width, height, name):
        if not all([isinstance(i, Number) for i in (x, y, width, height)]):
            raise TypeError('value should be expressed by float of int')

        self._viewports[name] = _Viewport(name, x, y, width, height)

        # gl.glViewportIndexedf(len(self._viewports) - 1, x, y, width, height)

    def open(self, index):

        size = self._window.size
        if isinstance(index, int):
            vp = self._viewports[list(self._viewports.keys())[index]]
        elif isinstance(index, str):
            vp = self._viewports[index]

        self.make_viewport_current(vp)

        if isinstance(vp.posx, float):
            x = int(vp.posx * size[0])
        else:
            x = vp.posx

        if isinstance(vp.posy, float):
            y = int(vp.posy * size[1])
        else:
            y = vp.posy

        if isinstance(vp.width, float):
            w = int(vp.width * size[0])
        else:
            w = vp.width

        if isinstance(vp.height, float):
            h = int(vp.height * size[1])
        else:
            h = vp.height

        gl.glViewport(x, y, w, h)

    def make_viewport_current(self, viewport):
        self.__class__._current_viewport = viewport

    def close(self):
        wsize = self._window.size
        gl.glViewport(0, 0, wsize[0], wsize[1])
        pass

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._viewports[item]
        elif isinstance(item, int):
            return list(self._viewports.items())[item][1]


    def __call__(self, func):
        print(func)
        func()

    @property
    def current_viewport(self):
        return self.__class__._current_viewport
