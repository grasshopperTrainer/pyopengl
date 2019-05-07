import weakref

import numpy as np

from .update_check_descriptor import UCD


class _Camera:
    near = UCD()
    far = UCD()
    left = UCD()
    right = UCD()
    bottom = UCD()
    top = UCD()
    VM = UCD()
    PM = UCD()

    def __init__(self, viewport):
        self._viewport = viewport

        self._mode = 1

        self.near = 1
        self.far = 100000
        self.left = -1
        self.right = 1
        self.bottom = -0.5
        self.top = 0.5

        self.VM = np.eye(4)
        self.PM.function_when_get(self.build_PM)
        self.PM = np.eye(4)
        # UCD.get_descriptor('PM')
        self._latestviewportsize = [None, None]

        self._flag_isupdated = True

        self.build_PM()

    def move(self, value, x, y, z):
        if not isinstance(value, (tuple, list)):
            value = [-value, ] * 3
        else:
            value = [-i for i in value]

        x, y, z = [bool(i) for i in [x, y, z]]
        if len(value) < sum([x, y, z]):
            raise ValueError('insufficient number of input')

        matrix = np.eye(4)
        vx, vy, vz = 0, 0, 0
        if x:
            vx = value.pop(0)
        if y:
            vy = value.pop(0)
        if z:
            vz = value.pop(0)

        matrix[:, 3] = vx, vy, vz, 1
        self.VM = matrix.dot(self.VM)

    def rotate(self, angle, x, y, z, radian=False):
        if not isinstance(angle, (list, tuple)):
            angle = [angle, ] * 3

        if radian:
            angle = [-a for a in angle]
        else:
            angle = [np.radians(-a) for a in angle]

        x, y, z = [bool(i) for i in [x, y, z]]
        if len(angle) < sum([x, y, z]):
            raise ValueError('insufficient number of input')

        matrix = np.eye(4)
        if x:
            new = np.eye(4)
            a = angle.pop(0)
            new[1] = 0, np.cos(a), -np.sin(a), 0
            new[2] = 0, np.sin(a), np.cos(a), 0
            matrix = new.dot(matrix)

        if y:
            new = np.eye(4)
            a = angle.pop(0)
            new[0] = np.cos(a), 0, np.sin(a), 0
            new[2] = -np.sin(a), 0, np.cos(a), 0
            matrix = new.dot(matrix)

        if z:
            new = np.eye(4)
            a = angle.pop(0)
            new[0] = np.cos(a), -np.sin(a), 0, 0
            new[1] = np.sin(a), np.cos(a), 0, 0
            matrix = new.dot(matrix)

        self.VM = matrix.dot(self.VM)

    def scale(self):
        # ???
        pass

    def lookat(self, to_point, from_point=None):
        if from_point is None:
            from_point = -self.VM.dot(np.array([[0, 0, 0, 1]]).T)
            from_point[3] = 1
        else:
            self.VM = np.eye(4)
            self.move(from_point, 1, 1, 1)
            from_point = np.array([from_point + [1, ]]).T

        to_point = np.array([to_point + [1, ]]).T
        vec = (to_point - from_point).T[0]

        x = vec[1]
        y = -vec[0]
        angle = np.arccos(x / np.sqrt(x * x + y * y))
        # print(angle, np.degrees(angle),x,y)
        if not np.isnan(angle):
            if y <= 0:
                angle = -angle
            self.rotate(angle, 0, 0, 1, True)

        y = -vec[2]
        z = np.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        angle = np.arcsin(z / np.sqrt(z * z + y * y))
        # print(angle, np.degrees(angle),x,y)
        if not np.isnan(angle):
            if z <= 0:
                angle = -angle
            if y <= 0:
                angle = np.pi - angle
            self.rotate(angle, 1, 0, 0, True)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if isinstance(mode, str):
            if 'ortho' in mode:
                self._mode = 0
            elif 'proj' in mode:
                self._mode = 1
            elif '2D' in mode:
                self._mode = 2

        elif isinstance(mode, int):
            self._mode = mode

        self.build_PM()

    def build_PM(self, major='v'):
        if self._viewport._mother.window.is_buffer_swap_required():
            vp = self._viewport
            if vp.abs_height == 0 or vp.abs_height == 0:
                return

            n, f, r, l, t, b = self.near, self.far, self.right, self.left, self.top, self.bottom
            ratio = vp.abs_width / vp.abs_height
            if major == 'v':
                r, l = (t - b) * ratio / 2, -(t - b) * ratio / 2
            elif major == 'h':
                t, b = (r - l) / ratio / 2, -(r - l) / ratio / 2
            else:
                pass

            if self._mode == 0:
                if r == -l and t == -b:
                    self.PM = np.array(
                        [[1 / r, 0, 0, 0],
                         [0, 1 / t, 0, 0],
                         [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                         [0, 0, 0, 1]])

                else:
                    self.PM = np.array(
                        [[2 / (r - l), 0, 0, -(r + l) / (r - l)],
                         [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                         [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                         [0, 0, 0, 1]])

            elif self._mode == 1:
                if r == -l and t == -b:
                    self.PM = np.array(
                        [[n / r, 0, 0, 0],
                         [0, n / t, 0, 0],
                         [0, 0, -(f + n) / (f - n), -2 * f * n / (f - n)],
                         [0, 0, -1, 0]])

                else:
                    self.PM = np.array(
                        [[2 * n / (r - l), 0, (r + l) / (r - l), 0],
                         [0, 2 * n / (t - b), (t + b) / (t - b), 0],
                         [0, 0, -(f + n) / (f - n), -2 * f * n / (f - n)],
                         [0, 0, -1, 0]]
                    )

            if self._mode == 2:
                self.near = 0
                self.far = 100
                self.left = 0
                self.right = self._viewport.abs_width
                self.bottom = 0
                self.top = self._viewport.abs_height

                n, f, r, l, t, b = self.near, self.far, self.right, self.left, self.top, self.bottom
                # if self._viewport._mother.window.name == 'third':
                #     print('windowsize', self._viewport._mother.window.size)
                #     print(n,f,l,r,b,t)
                # print()
                self.PM = np.array(
                    [[2 / (r - l), 0, 0, -(r + l) / (r - l)],
                     [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                     [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                     [0, 0, 0, 1]]
                )

    @property
    def w(self):
        return self.right - self.left

    @w.setter
    def w(self, w):
        self.right = w / 2
        self.left = -w / 2
        self.build_PM()

    @property
    def h(self):
        return self.top - self.bottom

    @h.setter
    def h(self, h):
        self.top = h / 2
        self.bottom = -h / 2
        self.build_PM()

    # @property
    # def VM(self):
    #     return self._VM
    #
    # @property
    # def PM(self):
    #     window = self._viewport._mother.window
    #     if window.resized:
    #         self.build_PM()
    #         window.resized = False
    #
    #     return self._PM

    @property
    def is_updated(self):
        if self._flag_isupdated:
            self._flag_isupdated = False
            return True
        else:
            return False
