import numpy as np
from windowing.IO_device.mouse import Mouse
import weakref
from numbers import Number
import prohopper as pr


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
        # self._near = 0
        # self._far = 100
        # # render range of xy plane
        # self._left = 0
        # self._right = viewport.pixel_w
        # self._bottom = 0
        # self._top = viewport.pixel_h

        # self.scale_factor = [1,1,1]

        # to make PM just in time set refresh function
        self._PM = np.eye(4)
        self._mouse = None
        self._flag_recalculate_pm = True

        # what is the best coordinate definition for a camera?
        self._plane = pr.primitives.Plane((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        # simple projection matrix centered at the center of viewport
        n,f,w,h = 0,-1000,viewport.pixel_w/2, viewport.pixel_h/2
        # how to handle ratio? <- don't need it at the beginning
        self._clip_space = pr.primitives.Hexahedron([-w,h,f],[-w, -h, f],[w, -h, f],[w,h,f],
                                                    [-w,h,n],[-w, -h, n],[w,-h,n],[w,h,n])

    @property
    def near(self):
        near = (self._far+self._near)/2 - (self._far-self._near)/2*self.scale_factor[2]

        return near

    def set_near(self, v):
        self._near = v
    def accumulate_near(self, v):
        print('accumulating near', self._near,v)
        self._near += v


    def trans_move(self, x, y, z):
        self._plane = pr.trans.move(pr.primitives.Vector(x, y, z), self._plane)

    def trans_pitch(self, angle, degree=True):
        if not isinstance(angle, Number):
            raise
        axis = pr.line.con_point_vector(self._plane.origin, self._plane.x_axis)
        self._plane = pr.trans.rotate_around_axis(self._plane, axis, angle, degree)

    def trans_yaw(self, angle, degree=True):
        if not isinstance(angle, Number):
            raise
        axis = pr.line.con_point_vector(self._plane.origin, self._plane.y_axis)
        self._plane = pr.trans.rotate_around_axis(self._plane, axis, angle, degree)

    def trans_roll(self, angle, degree=True):
        if not isinstance(angle, Number):
            raise
        axis = pr.line.con_point_vector(self._plane.origin, self._plane.z_axis)
        self._plane = pr.trans.rotate_around_axis(self._plane, axis, angle, degree)

    def trans_look_at(self, target_point, upright=True):
        # need to match -z_axis head target_point
        p = pr.Point(*target_point)
        v_p_to_o = pr.vector.con_two_points(p, self._plane.origin)
        if upright:
            # and if upright set camera y_axis be on xz plane
            ref_p = pr.trans.move(pr.Vector(0,0,1),self._plane.origin)
        else:
            # TODO what is the meaning of this
            ref_p = pr.trans.move(self._plane.origin, self._plane.y_axis)
        self._plane = pr.plane.con_vector_point(v_p_to_o, ref_p, 'z', 'y',self._plane.origin)

    def from_look_at(self, source_point, target_point, upright=True):
        pass

    def scale(self,x=1,y=1,z=1):
        self.scale_factor = (x,y,z)



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
                # this is pixel_true_2D projection origin set to left bottom of the viewport
                self._mode = 2
                # camera should be centered viewport and use ortho for pm
                w, h = self._viewport.pixel_w, self._viewport.pixel_h
                self._plane.raw[:3,0] = w/2, h/2, 0
                # cliping area is defined as follow
                # build front area and extrude
                pr.primitives.Rectangle([-w/2,h/2,0],[-],[],[])

        elif isinstance(mode, int):
            self._mode = mode

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
    def nflrbt(self):
        arr = self._clip_space.raw
        return arr[2,4],arr[2,0],arr[0,4],arr[0,7],arr[1,5],arr[1,4]

    def report_pm_changed(self):
        self._flag_recalculate_pm = True

    @property
    def PM(self):

        n,d,l,r,b,t = self.nflrbt
        # what about mode? when to recalculate PM?
        # 1. when clip space have changed
        # 2. when mode has changed
        # 3. when viewport property has changed

        print(self._mode)
        if self._flag_recalculate_pm:

            self._PM = None
        return self._PM

        exit()
        if self._mode == 0:
            n, f, r, l, t, b = self.near, self.far, self.right, self.left, self.top, self.bottom
            exit()
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

        elif self._mode == 1:
            pass
        elif self._mode == 2:
            pass
        else:
            raise TypeError

    @property
    def VM(self):
        x = pr.matrix.trans_from_plane_to_origin(self._plane)

        return x.raw

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
        return self._plane.origin

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