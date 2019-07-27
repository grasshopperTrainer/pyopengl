import numpy as np
from windowing.IO_device.mouse import Mouse
import weakref


from windowing.frame_buffer_like.frame_buffer_like_bp import FBL

class _Camera:
    """
    Camera for viewport.
    This object stores properties of Camera position, characteristics
    to form ViewMatrix(VM) and ProjectionMatrix(PM).
    VM and PM is referenced by (class) RenderUnit.update_variables and passed to opengl shader.
    """

    def __init__(self, viewport):
        self._viewport = viewport

        self._mode = 2
        # following is basic setting for mode2 - true 2D projection
        # render range of z
        self._near = 0
        self._far = 100
        # render range of xy plane
        self._left = 0
        self._right = viewport.pixel_w
        self._bottom = 0
        self._top = viewport.pixel_h

        self.scale_factor = [1,1,1]

        # to make PM just in time set refresh function
        self._PM = np.eye(4)
        self._VM = np.eye(4)
        self._mouse = None

    @property
    def near(self):
        near = (self._far+self._near)/2 - (self._far-self._near)/2*self.scale_factor[2]

        return near

    def set_near(self, v):
        self._near = v
    def accumulate_near(self, v):
        print('accumulating near', self._near,v)
        self._near += v

    @property
    def far(self):
        far = (self._far+self._near)/2 + (self._far-self._near)/2*self.scale_factor[2]
        return far
    @property
    def left(self):
        left = (self._right+self._left)/2 - (self._right-self._left)/2*self.scale_factor[0]
        return left
    @property
    def right(self):
        right = (self._right + self._left) / 2 + (self._right - self._left) / 2 * self.scale_factor[0]
        return right
    @property
    def bottom(self):
        bottom = (self._top + self._bottom) / 2 - (self._top - self._bottom) / 2 * self.scale_factor[1]
        return bottom
    @property
    def top(self):
        top = (self._top + self._bottom) / 2 + (self._top - self._bottom) / 2 * self.scale_factor[1]
        return top

    def trans_move(self, x, y, z):
        # move camera
        matrix = np.eye(4)
        matrix[:, 3] = -x, -y, -z, 1
        self._VM = matrix.dot(self._VM)

    def trans_rotate(self, x, y, z, order=[0,1,2], radian=False):
        """
        rotate around axit
        :param x:
        :param y:
        :param z:
        :param order:
        :param radian:
        :return:
        """
        if radian:
            x,y,z = -x,-y,-z
        else:
            x, y, z = [np.radians(-i) for i in [x,y,z]]

        combined_matrix = np.eye(4)
        rotate_x = np.eye(4)
        rotate_y = np.eye(4)
        rotate_z = np.eye(4)

        if x != 0:
            rotate_x[1] = 0, np.cos(x), -np.sin(x), 0
            rotate_x[2] = 0, np.sin(x), np.cos(x), 0
        if y != 0:
            rotate_y[0] = np.cos(y), 0, np.sin(y), 0
            rotate_y[2] = -np.sin(y), 0, np.cos(y), 0
        if z != 0:
            rotate_z[0] = np.cos(z), -np.sin(z), 0, 0
            rotate_z[1] = np.sin(z), np.cos(z), 0, 0
        s = sorted(zip(order,(rotate_x, rotate_y, rotate_z)))
        for _,m in s:
            combined_matrix = m.dot(combined_matrix)
        self._VM = combined_matrix.dot(self._VM)

    def scale(self,x=1,y=1,z=1):
        self.scale_factor = (x,y,z)

    def trans_look_at(self, to_point:(tuple, list), from_point:(tuple, list)=None):
        """
        position camera so so it look at 'to_point' from 'from_point'

        :param to_point: camera to look at
        :param from_point: camera to look from
        :return:
        """
        if from_point is None:
            from_point = -self.VM.dot(np.array([[0, 0, 0, 1]]).T)
            from_point[3] = 1
        else:
            self._VM = np.eye(4)
            self.trans_move(*from_point)
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
            self.trans_rotate(0, 0, angle, radian=True)

        y = -vec[2]
        z = np.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        angle = np.arcsin(z / np.sqrt(z * z + y * y))
        # print(angle, np.degrees(angle),x,y)
        if not np.isnan(angle):
            if z <= 0:
                angle = -angle
            if y <= 0:
                angle = np.pi - angle
            self.trans_rotate(angle, 0, 0, radian=True)

    def set_mode(self, mode):
        """
        currently three modes supported
        0. orthonographic
        1. projection
        2. orthonographic pixel_true 2D plane

        :param mode:
        :return:
        """
        if isinstance(mode, str):
            if 'ortho' in mode:
                self._mode = 0
            elif 'proj' in mode:
                self._mode = 1
            elif '2D' in mode:
                self._mode = 2

        elif isinstance(mode, int):
            self._mode = mode

        # set camera properties
        if self._mode == 2:
            self._near = 0
            self._far = 100
            # render range of xy plane
            self._left = 0
            self._right = self._viewport.pixel_w
            self._bottom = 0
            self._top = self._viewport.pixel_h
        else:
            self._near = 1
            self._far = 1000000
            self._left = -1
            self._right = 1
            self._top = 1
            self._bottom = -1

        self.build_PM()
    # @property
    # def mode(self):
    #     return self._mode
    #
    # @mode.setter
    # def mode(self, mode):


    def set_test_mouse(self, mouse):
        if not isinstance(mouse,Mouse):
            raise TypeError
        self._mouse = weakref.ref(mouse)
        mouse.set_scroll_down_callback(
            lambda : self.trans_move(0,0,2)
        )
        mouse.set_scroll_up_callback(
            lambda : self.trans_move(0,0,-2)
        )

    @property
    def PM(self):
        self.build_PM()
        return self._PM
    @property
    def VM(self):
        return self._VM

    def build_PM(self, major='v'):

        # need to find correct filter condition
        if True:
            vp = self._viewport
            if vp.pixel_h == 0 or vp.pixel_h == 0:
                return

            if self._mode == 0 or self._mode == 1:
                if major == 'v':
                    ratio = vp.pixel_w / vp.pixel_h
                    distance = self._top - self._bottom
                    self._right, self._left = distance * ratio / 2, -distance * ratio / 2
                elif major == 'h':
                    ratio = vp.pixel_h / vp.pixel_w
                    distance = self._right - self._left
                    self._top, self._bottom = distance * ratio / 2, -distance * ratio / 2
                else:
                    raise

                n, f, r, l, t, b = self.near, self.far, self.right, self.left, self.top, self.bottom
                if self._mode == 0:
                    if r == -l and t == -b:
                        self._PM = np.array(
                            [[1 / r, 0, 0, 0],
                             [0, 1 / t, 0, 0],
                             [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                             [0, 0, 0, 1]])

                    else:
                        self._PM = np.array(
                            [[2 / (r - l), 0, 0, -(r + l) / (r - l)],
                             [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                             [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                             [0, 0, 0, 1]])

                else:
                    if r == -l and t == -b:
                        self._PM = np.array(
                            [[n / r, 0, 0, 0],
                             [0, n / t, 0, 0],
                             [0, 0, -(f + n) / (f - n), -2 * f * n / (f - n)],
                             [0, 0, -1, 0]])

                    else:
                        self._PM = np.array(
                            [[2 * n / (r - l), 0, (r + l) / (r - l), 0],
                             [0, 2 * n / (t - b), (t + b) / (t - b), 0],
                             [0, 0, -(f + n) / (f - n), -2 * f * n / (f - n)],
                             [0, 0, -1, 0]]
                        )

            elif self._mode == 2:
                # self.near = 0
                # self.far = 100
                # self.left = 0
                self._right = self._viewport.pixel_w * self.scale_factor[0]
                # self.bottom = 0
                self._top = self._viewport.pixel_h * self.scale_factor[1]

                n, f, r, l, t, b = self.near, self.far, self.right, self.left, self.top, self.bottom
                # if self._viewport._mother.window.name == 'third':
                #     print('windowsize', self._viewport._mother.window.size)
                #     print(n,f,l,r,b,t)
                self._PM = np.array(
                    [[2 / (r - l), 0, 0, -(r + l) / (r - l)],
                     [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                     [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                     [0, 0, 0, 1]]
                )
    @property
    def position(self):
        origin = np.array([[0],[0],[0],[1]])
        print(origin)
        print(self._VM)
        a = self._VM.copy()
        return self._VM.dot(origin)
    @property
    def w(self):
        return self.right - self.left

    @w.setter
    def w(self, w):
        self.right = w / 2
        self.left = -w / 2

    @property
    def h(self):
        return self.top - self.bottom

    @h.setter
    def h(self, h):
        self.top = h / 2
        self.bottom = -h / 2