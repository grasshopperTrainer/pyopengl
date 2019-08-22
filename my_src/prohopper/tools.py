# from .primitives import *
from .constants import *

import numpy as np
import copy
import inspect
import weakref
from typing import *
from numbers import Number
from .errors import *
from .constants import *
from .family_tree_list import Family_tree_list


def mymethod(func):
    args_names, var_args, var_kwargs, defaults, kwonlyargs, kwonlydefaults,annotations = inspect.getfullargspec(func)
    def wrapper(*args, **kwargs):
        flag_mutate_self = False
        if hasattr(args[0], '_caller'):
            flag_mutate_self == True
            args = list(args)
            args[0] = args[0]._caller

        # TODO just enough for now need improvement?
        # input checking
        if var_args == None and var_kwargs == None:
            given = len(args)+ len(kwargs)
            if defaults == None:
                if given != len(args_names):
                    raise TypeError('missing argument')
            else:
                if not (given  >= len(args_names) - len(defaults) and given <= len(args_names)):
                    # print(args, kwargs, args_names)
                    # print(args_names)
                    # print(var_args)
                    # print(var_kwargs)
                    # print(defaults)
                    # print(kwonlyargs)
                    # print(kwonlydefaults)
                    # print(annotations)
                    raise TypeError('missing argument')
        else:
            if len(args)+ len(kwargs) < len(args_names):
                raise

        # type checking
        # need to build combined args list first
        arg_dict = {}
        args_list = args[len(args_names):]
        kwargs_dict = {}
        for a_name,a in zip(args_names, args):
            arg_dict[a_name] = a
        for a in kwargs:
            # if given input is not a part of kwargs but args but given with name
            if a in args_names:
                # if its not for one that's already given through *args
                if not a in arg_dict:
                    arg_dict[a] = kwargs[a]
                else:
                    raise
            else:
                # real kwargs
                kwargs_dict[a] = kwargs[a]

        # for arguments
        for a_name,a in arg_dict.items():
            # if it has type hint
            if a_name in annotations:
                types = annotations[a_name]
                if isinstance(types, (list, tuple)):
                    istype = False
                    # if arg can be one of types
                    for t in types:
                        if isinstance(a,t):
                            istype = True
                    if not istype:
                        raise TypeError
                elif isinstance(types, type(List)):
                    pass
                elif not isinstance(a, types):
                    raise WrongInputTypeError(a, types)

        # for variable arguments
        if var_args in annotations:
            types = annotations[var_args]
            for a in args_list:
                if isinstance(types, (list, tuple)):
                    istype = False
                    for t in types:
                       if isinstance(a, t):
                           istype = True
                    if not istype:
                        raise TypeError
                elif isinstance(types, type(List)):
                    pass
                elif not isinstance(a, types):
                    raise WrongInputTypeError(a, types)

        # for variable keyword arguments
        if var_kwargs in annotations:
            types = annotations[var_kwargs]
            types = list(types)
            for a in kwargs_dict.values():
                if isinstance(types, (tuple, list)):
                    istype = False
                    for t in types:
                        if isinstance(a, t):
                            istype = True
                    if not istype:
                        raise TypeError
                elif isinstance(types, type(List)):
                    pass
                elif not isinstance(a, types):
                    raise TypeError

        result = func(*args, **kwargs)
        if 'return' in annotations:
            if isinstance(result, annotations['return']) and flag_mutate_self:
                args[0].raw = result.raw
                return args[0]
            else:
                return result
        else:
            return result

    return wrapper

class Raw_array:
    def __init__(self):
        self._d = weakref.WeakKeyDictionary()

    def __set__(self, instance, value):
        self._d[instance] = np.array(value, dtype=np.float64)

    def __get__(self, instance, owner):
        try:
            return self._d[instance]
        except:
            return None

class Primitive:
    pass

class Geometric_value:
    _raw = Raw_array()

    @property
    def raw(self):
        return self._raw
    def reset_raw(self, array:np.ndarray):
        if isinstance(v, np.ndarray):
            self._raw = v
    def copy(self):
        new = copy.deepcopy(self)
        new._raw = self.raw.copy()
        return new

    # @raw.setter
    # def raw(self, v):
    #     self._raw = v

class Plane(Geometric_value):
    _tree = Family_tree_list()
    _raw = Raw_array()
    def __init__(self,
                 o: (tuple, list) = [0, 0, 0],
                 x: (tuple, list) = [1, 0, 0],
                 y: (tuple, list) = [0, 1, 0],
                 z: (tuple, list) = [0, 0, 1],
                 master=None):

        print('init of plane')
        if master == None:
            # this means it's in the outermost world coordinate system
            # there is no other coordinate system wrapping this plane
            self._tree.invite_member(self)
            master = None
        elif not isinstance(master, Plane):
            raise WrongInputTypeError(master, Plane)
        else:
            # hierarchy
            self._tree.invite_as_child_of(master, self)

        # format origin
        if not isinstance(o, (tuple, list)):
            raise NotCoordinateLikeError(o)
        if len(o) != 3:
            raise NotCoordinateLikeError(o)

        # format axis
        axis = x, y, z
        for i,a in enumerate(axis):
            if not isinstance(a, (tuple, list)):
                raise NotCoordinateLikeError(a)
            if len(a) != 3:
                raise NotCoordinateLikeError(a)
            # make unit vectors
            x,y,z = a
            l = np.sqrt(x*x +y*y +z*z,dtype=DEF_FLOAT_FORMAT)
            for ii, v in enumerate(a):
                a[ii] = np.divide(v,l,dtype=DEF_FLOAT_FORMAT)


        # sinbular object to wrap
        self.object = None
        self._raw = np.vstack((np.array([o, *axis]).transpose(), np.array([1, 0, 0, 0])))

    @property
    def family_tree(self):
        return self._tree

    # def __str__(self):
    #     return f'<Plane {self._raw[:3,0]}>'

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if raw.shape != (4, 4):
            raise
        if not all([a == b for a, b in zip(raw[3], (1, 0, 0, 0))]):
            raise
        listed = [i[:3] for i in raw.transpose().tolist()]
        return cls(*listed)

    @property
    def origin(self):
        return self._raw[:3, 0]

    @property
    def x_axis(self):
        return self._raw[:3,1]

    @property
    def y_axis(self):
        return self._raw[:3,2]

    @property
    def z_axis(self):
        return self._raw[:3,3]

    def get_x_axis(self):
        return Vector(*self.x_axis)
    def get_y_axis(self):
        return Vector(*self.y_axis)
    def get_z_axis(self):
        return Vector(*self.z_axis)
    def get_origin(self):
        return Point.con_xyz(*self.origin)

    def is_default(self):
        if all(np.equal(self._raw, np.array([[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0]])).flatten()):
            return True
        return False
#     @staticmethod
#     def con_from_points():
#         pass
#
#     @staticmethod
#     def relocate(pla:Plane, new_origin:Point) -> Plane:
#         new_raw = pla.raw.copy()
#         new_raw[:3, 0] = new_origin.xyz
#         return Plane.from_raw(new_raw)
#

    def decon(self):
        """
        deconstruct plane
        returns origin, vector-x, vector-y, vectorz-z
        :param pla: plane to deconstruct
        :return: [ Point, Vector, Vector, Vector ]
        """

        return [self.get_origin(),self.get_x_axis(),self.get_y_axis(),self.get_z_axis()]
#
#     @staticmethod
#     def con_2_vectors(axis1: Vector, axis2: Vector, axis1_hint: str, axis2_hint: str, origin:Point):
#
#         """
#         Build a plane from given two axis.
#         If given axes are not perpendicular axis2 will be transformed to make it correct as axis2_hint.
#
#         :param origin: origin of the new plane
#         :param axis1: first axis of the plane
#         :param axis2: second axis of the plane
#         :param axis1_hint: one of ('x','y','z')
#         :param axis2_hint: one of ('x','y','z')
#         :return: plane
#         """
#         projected = vector.project_on_another(axis1, axis2)
#         axis2 = vector.con_2_points(point.con_from_vector(projected), point.con_from_vector(axis2))
#         axis3 = vector.cross(axis1, axis2)
#
#         axis_dic = {'x':None,'y':None,'z':None}
#         axis_dic[axis1_hint] = axis1
#         axis_dic[axis2_hint] = axis2
#         for i in axis_dic:
#             if i == None:
#                 axis_dic[i] = axis3
#
#         if any([i is None for i in axis_dic.values()]):
#             raise
#         return plane.con_3_vectors(*axis_dic.value(),origin)
#
#
#     @staticmethod
#     def con_vector_point(axis: Vector, poi: Point, axis_hint: str, point_hint: str, origin: Point = Point()):
#         projected_point = point.perpendicular_on_vector(axis, poi)
#         perpen_v = vector.con_2_points(projected_point, poi)
#         # and build a reference plane
#         ref_plane = plane.con_2_vectors(axis, perpen_v, axis_hint, point_hint, origin)
#         return ref_plane
#
#     @staticmethod
#     def con_3_vectors(x_axis: Vector, y_axis: Vector, z_axis: Vector, origin: Point = Point()):
#         if not all([isinstance(i, Vector) for i in (x_axis, y_axis, z_axis)]):
#             raise TypeError
#
#         return Plane(origin.xyz, x_axis.xyz, y_axis.xyz, z_axis.xyz)




class Geometry:

    _raw = Raw_array()
    def __init__(self):
        self._flag_recal_wc = True
        self._wc = None
        self._pla = Plane()
        self._TM = np.eye(4)
        self._ITM = np.eye(4)
    def copy(self):
        new = copy.deepcopy(self)
        new._raw = self._raw.copy()

        return new
    # @property
    # def TM(self):
    #     return self._TM
    # @property
    # def ITM(self):
    #     return self._ITM

    # @property
    # def raw(self):
    #     return self._raw
    # @raw.setter
    # def raw(self, v):
    #     self._raw = v

    @property
    def pla(self):
        return self._pla

    def reset_plane(self, pla):
        self._flag_recal_wc = True
        self._pla = pla
    #     pass
    #
    # @pla.setter
    # def pla(self,v):
    #     self._flag_recal_wc = True
    #     if not isinstance(v, Plane):
    #         raise WrongInputTypeError(v, Plane)
    #     self._pla = v

    @property
    def LC(self):
        """
        local coordinates
        :return:
        """
        return self.raw

    @property
    def WC(self):
        """
        world coordinates
        its the coordinate at outermost plane(world
        :return:
        """
        if self._flag_recal_wc:
            print(self.pla.raw)
            m = Matrix.trans_between_origin_and_plane(self.pla)
            print(m.raw)
            exit()
            # print(self)
            # print(self.pla.raw)
            # m = matrix.trans_from_origin_to_plane(self.pla)
            # print(m)
            # print(self.trans.transform(self.pla,m).raw)
            # exit()
            # self._flag_recal_wc = False
        pass

    @mymethod
    def coord_on_level(self, l):
        """
        coordinate on the level of planes
        0 is local(LC)
        1 is outer
        ...
        -1 is outermost(WC)
        :param l:
        :return:
        """
        pass

class OneD(Geometry):
    pass
class TwoD(Geometry):
    pass
class ThreeD(Geometry):
    pass

class Point(OneD, Primitive):

    def __init__(self):
        super().__init__()

        self._raw = [[0], [0], [0], [1]]

    def __str__(self):
        return f'<Point>'


    @property
    def x(self):
        return self.raw[0, 0]

    @x.setter
    def x(self, v):
        if isinstance(v, Number):
            self.raw[0, 0] = v

    @property
    def y(self):
        return self.raw[1, 0]

    @y.setter
    def y(self, v):
        if isinstance(v, Number):
            self.raw[1, 0] = v

    @property
    def z(self):
        return self.raw[2, 0]

    @z.setter
    def z(self, v):
        if isinstance(v, Number):
            self.raw[2, 0] = v

    @property
    def xyz(self):
        return self._raw[:3, 0].tolist()

    def from_vector(self):
        raise
        pass

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if raw.shape != (4, 1) or raw[3, 0] != 1:
            raise ValueError

        return cls(*raw[:3, 0])

    @classmethod
    def con_xyz(cls, x: Number, y: Number, z: Number):
        ins = cls()
        trans.move(ins,Vector(x, y, z))
        return ins
    #
    # @mymethod
    # def coplanar(points: Union[Tuple[Number, Number, Number], List[Number]]):
    #     raise
    #
    # @staticmethod
    # def clockwise_check(points: (tuple, list), pla: Plane = Plane()):
    #     """
    #     see if points are ordered clockwise or anti-clockwise
    #     signs indicate followings;
    #     0 - clockwise
    #     1 - anti-clockwise
    #     None - can't define
    #
    #     :param points: list of points to test
    #     :param pla: reference plane
    #     :return: one of (0,1,None)
    #     """
    #     if len(points) <= 2:
    #         # can't know order
    #         return None
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise WrongInputTypeError(Point, p)
    #
    #     vectors = []
    #     for i in range(len(points) - 1):
    #         vectors.append(vector.con_2_points(points[i], points[i + 1]))
    #
    #     order = 2
    #     for i in range(len(vectors) - 1):
    #         o = vector.right_left_halfspace(vectors[i], vectors[i + 1], pla)
    #         if o == 3:
    #             return None
    #
    #         if o == 2:
    #             continue
    #         else:
    #             if order == 2:
    #                 order = o
    #             else:
    #                 if order == 0:
    #                     if o == 0:
    #                         pass
    #                     else:
    #                         return None
    #                 else:
    #                     if o == 1:
    #                         pass
    #                     else:
    #                         return None
    #     if order == 2:
    #         return None
    #     else:
    #         return order
    #
    # @staticmethod
    # def xyz(*points):
    #     lis = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise TypeError
    #         lis.append(p.xyz)
    #     if len(lis) == 1:
    #         return lis[0]
    #     return lis
    #
    # @staticmethod
    # def x(*points):
    #     lis = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise TypeError
    #         lis.append(p.x)
    #     if len(lis) == 1:
    #         return lis[0]
    #     return lis
    #
    # @staticmethod
    # def y(*points):
    #     lis = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise TypeError
    #         lis.append(p.y)
    #     if len(lis) == 1:
    #         return lis[0]
    #     return lis
    #
    # @staticmethod
    # def z(*points):
    #     lis = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise TypeError
    #         lis.append(p.z)
    #     if len(lis) == 1:
    #         return lis[0]
    #     return lis
    #
    # @mymethod
    # def in_points(cloud: (tuple, list), *points: Point) -> List[bool]:
    #     mask = []
    #     if len(points) == 0:
    #         return []
    #
    #     for p in points:
    #         co = False
    #         for i in cloud:
    #             if point.coinside(p, i):
    #                 co = True
    #                 break
    #         mask.append(co)
    #     return mask
    #
    # @mymethod
    # def unique_points(points: (list, tuple)) -> List[Point]:
    #     """
    #     leave only unique points
    #     :param points:
    #     :return: [ [unique_points], [uniqueness index of all input] ]
    #     """
    #     # what index? index of uniqueness?
    #     unique_points = []
    #     unique_index = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise WrongInputTypeError(p, Point)
    #
    #         unique = True
    #         for i, up in enumerate(unique_points):
    #             # if there is one that has same coordinate value don't add
    #             # if all is looked and there's isn't one coinside then add
    #             coinsides = True
    #             for a, b in zip(up.xyz, p.xyz):
    #                 # if any component is different go to next
    #                 if a != b:
    #                     coinsides = False
    #                     break
    #             # for all components equal inspecting point is not unique
    #             if coinsides:
    #                 unique = False
    #                 unique_index.append(i)
    #                 break
    #             else:
    #                 unique_index.append(len(unique_points))
    #                 continue
    #
    #         if unique:
    #             unique_points.append(p)
    #         else:
    #             continue
    #     return [unique_points, unique_index]
    #
    @classmethod
    def coinside(cls, point1, point2, atol=None) -> bool:
        if atol != None:
            raise
        else:
            return all(np.equal(point1._raw, point2._raw).flatten())
    #
    # @staticmethod
    # def sort(points, mask: str = 'x'):
    #     """
    #     sort points by given ingredient
    #
    #     :param mask: key to sort with, one of 'x','y','z'
    #     :param points: points to sort
    #     :return: sorted list of points
    #     """
    #     mask_index = {'x': 0, 'y': 1, 'z': 2}
    #     if not mask in mask_index:
    #         raise ValueError
    #     if not all([isinstance(p, Point) for p in points]):
    #         raise TypeError
    #
    #     keys = []
    #     i = mask_index[mask]
    #     for p in points:
    #         keys.append(p.xyz[i])
    #     sorted_list = sorted(zip(keys, points), key=lambda x: x[0])
    #
    #     points = [i[1] for i in sorted_list]
    #     return points
    #
    # @staticmethod
    # def sort_chunck():
    #     pass
    #
    # @staticmethod
    # def equal(point1: Point, point2: Point) -> bool:
    #     if not isinstance(point1, Point) or not isinstance(point2, Point):
    #         return TypeError
    #     for a, b in zip(point1.xyz, point2.xyz):
    #         if not np.isclose(a, b, atol=DEF_TOLERANCE):
    #             return False
    #     return True
    #
    # @staticmethod
    # def is_on_line(lin: Line, *points: (tuple, list)) -> bool:
    #     results = []
    #     directional1 = vector.con_line(lin)
    #     for poi in points:
    #         if not isinstance(poi, Point):
    #             raise TypeError
    #
    #         if line.has_vertex(lin, poi):
    #             results.append(True)
    #             continue
    #
    #         directional2 = vector.con_2_points(Point(*lin.start), poi)
    #         if vector.is_parallel(directional1, directional2):
    #             vertex = [lin.start[0], lin.end[0]]
    #             vertex = sorted(vertex)
    #             x = poi.x
    #             print(x, vertex)
    #             if x >= vertex[0] and x <= vertex[1]:
    #                 results.append(True)
    #             else:
    #                 results.append(False)
    #         else:
    #             results.append(False)
    #
    #     if len(results) == 1:
    #         return results[0]
    #     return results
    #
    # @staticmethod
    # def con_from_vector(vec: Vector):
    #     return Point(*vec.xyz)
    #
    # @staticmethod
    # def perpendicular_on_vector(vec: Vector, poi: Point):
    #     vec2 = vector.con_point(poi)
    #     a = vector.angle_2_vectors(vec, vec2)
    #     l = np.cos(a) * vec2.length
    #     new_v = vector.amplitude(vec, l)
    #     return point.con_from_vector(new_v)
    #
    # @staticmethod
    # def average(points: (list, tuple)) -> Point:
    #     coords = []
    #     for p in points:
    #         if not isinstance(p, Point):
    #             raise TypeError
    #         coords.append(p.xyz)
    #     coords = np.array(coords).transpose()
    #     new = []
    #     for l in coords:
    #         new.append(sum(l) / len(points))
    #     return Point(*new)


class Domain2d(Primitive):
    '''
    ???
    '''

    def __init__(self, domain1, domain2):
        self.set_data([domain1, domain2])
        pass


class Domain(Primitive):
    def __init__(self, start: (int, float) = None, end: (int, float) = None):
        if start is None and end is None:
            self.set_data(np.array([0, 1]))
        else:
            if end is None and start is not 0:
                self.set_data(np.array([0, start]))
            else:
                if start is not end:
                    self.set_data(np.array([start, end]))
                else:
                    self._0lengthexception()
                return

        self.start = None
        self.end = None
        self.length = None

    def _0lengthexception(self):
        self.printmessage("can't make 0 length domain", 'MESSEGE')

    @property
    def start(self):
        return self._data[0]

    @start.setter
    def start(self, value):
        if value is not self.end:
            self._data[0] = value
        else:
            self._0lengthexception()

    @property
    def end(self):
        return self._data[1]

    @end.setter
    def end(self, value):
        if value is not self.start:
            self._data[1] = value
        else:
            self._0lengthexception()

    @property
    def length(self):
        se = self._data
        return se[1] - se[0]


class Vector_Point:
    def __new__(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if raw.shape != (4, 1):
            raise ValueError

        # point
        if raw[3, 0] == 1:
            return Point().from_raw(raw)
        # vector
        elif raw[3, 0] == 0:
            return Vector().from_raw(raw)
        else:
            raise ValueError





class Vector(Geometric_value):
    # this is not a geometry
    def __init__(self, x: Number = 0, y: Number = 0, z: Number = 0):
        self._raw = [[x], [y], [z], [0]]

    def __str__(self):
        return f'<Vector> {self.raw[:3].tolist()}'

    def __add__(self, other):
        if isinstance(other, Vector):
            new = self.raw.copy()
            return Vector().from_raw(new + other.raw)
        else:
            raise

    # def __truediv__(self, other):
    #     if isinstance(other, Number):
    #         v = self.raw.copy()
    #         xyz= v[:3,0]/other
    #         return Vector(*xyz)
    #     else:
    #         raise

    def __mul__(self, other):
        if isinstance(other, Number):
            v = self.raw.copy()
            xyz = v[:3, 0] * other
            return Vector(*xyz)
        elif isinstance(other, Vector):
            return self.raw * other.raw

    def dot(self, other):
        return self.raw.flatten().dot(other.raw.flatten())

    @property
    def x(self):
        return self._raw[0, 0]

    @property
    def y(self):
        return self._raw[1, 0]

    @property
    def z(self):
        return self._raw[2, 0]

    @property
    def xyz(self):
        return self._raw[:3, 0].tolist()

    @property
    def length(self):
        x,y,z = self.xyz
        return np.sqrt(x*x+y*y+z*z,dtype = DEF_FLOAT_FORMAT)

    def from_point(self, point: Point):
        if not isinstance(point, Point):
            raise
        raw = point.raw.copy()
        raw[3, 0] = 0
        self.raw = raw
        return self

    def project_on_xy(self, pla:Plane= Plane()):
        if pla.is_default():
            self._raw[2,0] = 0
        else:
            on_x = self.copy().project_on_vector(pla.get_x_axis())
            on_y = self.copy().project_on_vector(pla.get_x_axis())
            new = on_x + on_y
            self._raw[:] = new[:]
        return self

    def project_on_vector(self, vec_ref):
        self.amplitude(self.dot(vec_ref)/vec_ref.length)
        return self
    # @classmethod
    # def from_raw(cls, raw: np.ndarray):
    #     if not isinstance(raw, np.ndarray):
    #         raise TypeError
    #     if raw.shape != (4, 1):
    #         raise TypeError
    #     return cls(*raw.transpose().tolist()[0][:3])
    #
    # # functions that recieve single vector and returns single vector should be methods?
    # # or functions that mutates self should be methods?
    # # functions that return basic properties should be methods
    # @property
    # def length(self):
    #     x, y, z = self.xyz
    #     return np.sqrt(x * x + y * y + z * z)
    #
    # def __neg__(self):
    #     return self.__class__().from_raw(self.raw.copy() * (-1))
    #
    #
    # @mymethod
    # def right_left_halfspace(vec_reference, vec_target, pla: Plane = Plane()) -> int:
    #     """
    #     identifies whether vector is on the left or right half space
    #     signs indicate followings;
    #
    #     0 - right
    #     1 - left
    #     2 - same direction
    #     3 - reversed direction
    #
    #     :param vec_reference:
    #     :param vec_target:
    #     :param pla:
    #     :return: [ right_left_sign, angle_to_left_right ]
    #     """
    #     quarter = vector.quarter_plane(vec_reference, pla=pla)
    #     ref_angle = vector.angle_plane(vec_reference, pla=pla)
    #     target_angle = vector.angle_plane(vec_target, pla=pla)
    #
    #     if np.isclose(target_angle, ref_angle, atol=DEF_TOLERANCE):
    #         return [2, 0]
    #     else:
    #         if quarter == 0:
    #             if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
    #                 return [3, tri.pi]
    #             elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
    #                 return [1, target_angle - ref_angle]
    #             elif target_angle < ref_angle:
    #                 return [0, ref_angle - target_angle]
    #             else:
    #                 return [0, ref_angle - (target_angle - tri.pi2)]
    #         elif quarter == 1:
    #             if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
    #                 return [3, tri.pi]
    #             elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
    #                 return [1, target_angle - ref_angle]
    #             elif target_angle < ref_angle:
    #                 return [0, ref_angle - target_angle]
    #             else:
    #                 return [0, target_angle - (ref_angle + tri.pi)]
    #         elif quarter == 2:
    #             if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
    #                 return [3, tri.pi]
    #             elif target_angle > ref_angle - tri.pi and target_angle < ref_angle:
    #                 return [0, ref_angle - target_angle]
    #             elif target_angle < ref_angle - tri.pi:
    #                 return [1, ref_angle - tri.pi - target_angle]
    #             else:
    #                 return [1, target_angle - ref_angle]
    #         elif quarter == 3:
    #             if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
    #                 return [3, tri.pi]
    #             elif target_angle < ref_angle and target_angle > ref_angle - tri.pi:
    #                 return [0, ref_angle - target_angle]
    #             elif target_angle > ref_angle:
    #                 return [1, target_angle - ref_angle]
    #             else:
    #                 return [1, ref_angle - tri.pi - target_angle]
    #
    # @mymethod
    # def project_on_another(vec_projected_on, vec_projecting):
    #     u1, u2 = vector.unit(vec_projected_on), vector.unit(vec_projecting)
    #     cos_v = vector.dot(u1, u2)
    #     projected = vector.amplitude(vec_projected_on, cos_v * vector.length(vec_projecting))
    #     return projected
    #
    # @mymethod
    # def length(vec) -> float:
    #     x, y, z = vec.xyz
    #     return np.sqrt(x * x + y * y + z * z)
    #
    def __add__(self, another):
        new_v = self.copy()
        return new_v.addition(another)

    def addition(self, vec):
        self._raw[:] = self._raw + vec._raw
        return self

    def div(self, v):
        self._raw[:] = np.divide(self._raw, np.array([[v],[v],[v],[1]]))
        return self
    def mult(self, v):
        self._raw[:] = np.multiply(self._raw, np.array([[v],[v],[v],[1]]))
        return self
    @classmethod
    def dot(cls, vec1, vec2) -> float:
        return vec1.raw.flatten().dot(vec2.raw.flatten())
    @classmethod
    def cross(cls, vec1, vec2):
        cross = np.cross(vec1.raw[:3, 0], vec2.raw[:3, 0])
        return cls(*cross)


    # @mymethod
    # def is_parallel(vec1, vec2) -> int:
    #     """
    #     definition of return value
    #     -1 opposite direction
    #     0 non-parallel
    #     +1 same direction
    #
    #     :param vec1:
    #     :param vec2:
    #     :return:
    #     """
    #     unit1, unit2 = vector.unit(vec1), vector.unit(vec2)
    #     if unit1 == None or unit2 == None:
    #         return None
    #
    #     cos_v = vector.dot(unit1, unit2)
    #
    #     if np.isclose(cos_v, 1, atol=DEF_TOLERANCE):
    #         return 1
    #     elif np.isclose(cos_v, -1, atol=DEF_TOLERANCE):
    #         return -1
    #     else:
    #         return 0
    #
    # @mymethod
    # def con_2_points(start: Point, end: Point):
    #     coord = []
    #     for a, b in zip(start.xyz, end.xyz):
    #         coord.append(b - a)
    #     return (*coord)
    #
    # @mymethod
    # def quarter_plane(vec, pla: Plane = Plane()) -> int:
    #     angle = vector.angle_plane(vec, pla)
    #     if angle >= 0 and angle <= np.pi / 2:
    #         return 0
    #     elif angle > np.pi / 2 and angle <= np.pi:
    #         return 1
    #     elif angle > np.pi and angle <= np.pi * 1.5:
    #         return 2
    #     else:
    #         return 3
    #
    # @mymethod
    # def quarter_on_plane(vec, plane_hint: str):
    #     if not isinstance(vec, ):
    #         raise TypeError
    #     x, y, z = vec.xyz
    #     if plane_hint == 'xy' or plane_hint == 'yx':
    #         if x >= 0:
    #             if y >= 0:
    #                 return 0
    #             else:
    #                 return 3
    #         else:
    #             if y >= 0:
    #                 return 1
    #             else:
    #                 return 2
    #
    #     elif plane_hint == 'yz' or plane_hint == 'zy':
    #         if y >= 0:
    #             if z >= 0:
    #                 return 0
    #             else:
    #                 return 3
    #         else:
    #             if z >= 0:
    #                 return 1
    #             else:
    #                 return 2
    #
    #     elif plane_hint == 'zx' or plane_hint == 'xz':
    #         if z >= 0:
    #             if x >= 0:
    #                 return 0
    #             else:
    #                 return 3
    #         else:
    #             if x >= 0:
    #                 return 1
    #             else:
    #                 return 2
    #     else:
    #         raise ValueError
    #

    @classmethod
    def con_point(cls, poi: Point):
        return cls(*poi.xyz)
    #
    # # @tlist.calbranch
    # # def average(*vectors):
    # #     v = [i() for i in vectors]
    # #     pass
    # #
    # #
    # # @tlist.calitem
    # # def con2pt(start: Point, end: Point):
    # #     newv = ()
    # #     newv.set_data(np.subtract(end(), start()))
    # #     return newv
    #
    # @mymethod
    # def con_line(line: Line):
    #     if not isinstance(line, Line):
    #         raise TypeError
    #     xyz = []
    #     for a, b in zip(line.start, line.end):
    #         xyz.append(b - a)
    #     return (*xyz)
    #

    #
    # @mymethod
    # def divide(vector, v, raw=False):
    #     pass
    #

    def amplitude(self, amp: Number):
        self.mult(amp/self.length)
        return self
    def flip(self):
        self.raw[:] = self.raw *[[-1],[-1],[-1],[0]]
        return self

    @classmethod
    def unit(cls, vec):
        new = vec.copy().amplitude(1)
        return new

    def unitize(self):
        self.amplitude(1)

    def decon(self):
        return self.xyz

    @classmethod
    def decon_vectors(self, pla:Plane = Plane()):
        pass

    @classmethod
    def angle_2(cls, from_vector, to_vector, degree=False) -> Number:
        u1, u2 = cls.unit(from_vector), cls.unit(to_vector)
        if any([i == None for i in (u1, u2)]):
            return None
        cos_value = u1.raw.flatten().dot(u2.raw.flatten())
        angle = tri.arccos(cos_value)
        if degree:
            return tri.radian_degree(angle)
        else:
            return angle

    @classmethod
    def angle_plane(cls, vec, pla: Plane, degree: bool = False) -> Number:
        """
        return angle in range of (0, 2pi) from x-axis of plane incrementing counter-clockwise
        :param vec:
        :param pla:
        :param degree:
        :return:
        """
        o, x, y, z = Plane.decon(pla)
        vec = Vector.unit(vec)
        cos_value1, cos_value2 = Vector.dot(x, vec), Vector.dot(y, vec)
        if cos_value1 >= 0:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi * 2 - tri.arccos(cos_value1)
        else:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi * 2 - tri.arccos(cos_value1)

        if degree:
            return tri.radian_degree(angle)
        else:
            return angle
    #
    # @mymethod
    # def deconstruct(vector, ):
    #     on_xy = vector.raw.copy()
    #     on_xy[2, 0] = 0
    #     on_yz = vector.raw.copy()
    #     on_yz[0, 0] = 0
    #     on_xz = vector.raw.copy()
    #     on_xz[1, 0] = 0
    #     return ().from_raw(on_xy), ().from_raw(on_yz), ().from_raw(on_xz)
    #
    # @mymethod
    # def project_on_xyplane(vec):
    #     new = vec.raw.copy()
    #     new[2, 0] = 0
    #     return ().from_raw(new)
    #
    # @mymethod
    # def project_on_yzplane(vec):
    #     new = vec.raw.copy()
    #     new[0, 0] = 0
    #     return ().from_raw(new)
    #
    # @mymethod
    # def project_on_xzplane(vec):
    #     new = vec.raw.copy()
    #     new[1, 0] = 0
    #     return ().from_raw(new)

class String(Geometry):
    """
    class identifier reprisenting string
    """

    @property
    def vertices(self):
        return self._raw[:3].transpose().tolist()
    @property
    def start(self):
        return self._raw[:3,0].tolist()
    @property
    def end(self):
        return self._raw[:3, -1].tolist()

    @property
    def n_vertex(self):
        return self._raw.shape[1]

    @property
    def length(self):
        totall = 0
        vertices = self.vertices
        for i in range(self.n_vertex -1):
            vec = []
            for a,b in zip(vertices[i], vertices[i+1]):
                vec.append(b-a)
            l = np.sqrt(vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2])
            totall += l
        return totall

    # def flip(self):
    #     raw = np.flip(self.raw, 1)
    #     self.raw = raw

    def append(self, *new_element):
        for e in new_element:

            # this means raw not initiated and value is None
            if not isinstance(self.raw, np.ndarray):
                self.raw = e.raw.copy()
                continue

            if isinstance(e, Point):
                if not point.coinside(string.end(self),e):
                    self.raw = np.hstack((self.raw, e.raw.copy()))
                else:
                    raise

            elif isinstance(e, Line):
                if point.coinside(string.end(self), line.start(e)):
                    self.raw = np.hstack((self.raw, line.end(e).raw.copy()))
                elif point.coinside(string.end(self), line.end(e)):
                    self.raw = np.hstack((self.raw, line.start(e).raw.copy()))
                else:
                    self.raw = np.hstack((self.raw, e.raw.copy()))

            elif isinstance(e, Polyline):
                if point.coinside(string.end(self), string.start(e)):
                    self.raw = np.hstack((self.raw, e.raw[1:].copy()))
                elif point.coinside(string.end(self), string.end(e)):
                    self.raw = np.hstack((self.raw, np.flip(e.raw.copy(),1)[1:]))
                else:
                    self.raw = np.hstack((self.raw, e.raw.copy()))

            elif isinstance(e, (list, tuple)):
                if len(e) == 3 and all([isinstance(n,Number) for n in e]):
                    self.raw = np.hstack((self.raw, np.array([ [n] for n in e]+[1])))
            else:
                raise TypeError
        return self

    def insert(self, new_element, index):
        if isinstance(new_element, Point):
            pass
        elif isinstance(new_element, Line):
            pass
        elif isinstance(new_element, Polyline):
            pass

        elif isinstance(new_element, (list, tuple)):
            pass
        else:
            raise TypeError


class Line(String):
    def __init__(self, mag:Number=1):
        super().__init__()
        self._raw = [[0,mag],[0,0],[0,0],[1,1]]

    def __str__(self):
        return f'Line ' + '{:.3f}'.format(self.length)

class Flat(Geometry):
    """
    for flat surface
    """

    def __init__(self, coordinates):
        # need flatness check
        pass

    pass


class Polyline(String):

    def __init__(self, *points_coord):
        if len(points_coord) == 0:
            pass
        else:
            for coord in points_coord:
                if not isinstance(coord, (tuple, list)):
                    raise NotCoordinateLikeError
                if len(coord) not in (3, 2):
                    print(len(coord))
                    raise NotCoordinateLikeError
                if not all([isinstance(i, Number) for i in coord]):
                    raise AllnumberError

            # convert into arrays stack and transpose?
            raw = None
            for i, coord in enumerate(points_coord):
                # do i need to remove duplicated point?
                # if previous is the same with current ignore
                if i != 0:
                    if all([a == b for a, b in zip(points_coord[i - 1], coord)]):
                        continue

                # else append to array
                if len(coord) == 3:
                    coord = list(coord) + [1]
                else:
                    coord = list(coord) + [0, 1]
                arr = np.array(coord)
                if raw is None:
                    raw = arr
                else:
                    raw = np.vstack([raw, arr])
            self.raw = raw.transpose()



    @classmethod
    def from_raw(cls, raw: np.ndarray):
        if not isinstance(raw, np.ndarray):
            raise TypeError
        if not all([i == 1 for i in raw[3]]):
            raise ValueError

        ins = cls()
        ins.raw = raw
        return ins


class Polygone(Flat, Polyline, Geometry):
    """
    what is polygone and condition of it?
    it has to be flat and consists of vertices and must be closed
    """

    def __init__(self, *coordinates):
        if len(coordinates) == 0:
            return

        super().__init__(coordinates)
        ps = []
        for i in coordinates:
            if not isinstance(i, (tuple, list)):
                raise
            if len(i) > 3:
                raise NotCoordinateLikeError(i)
            i = i + [0 for i in range(3 - len(i))]
            ps.append(Point(*i))

        # close check
        if not point.coinside(ps[0], ps[-1]):
            raise
        #
        # # anti-clockwise check
        # pla = planar[1]
        # clockwise = point.clockwise_check(ps, pla)
        # if clockwise == 0:
        #     ps = reversed(ps)
        # else:
        #     pass

        self.raw = polyline.con_from_points(ps).raw


    @property
    def center(self):
        coord = []
        v_n = self.raw.shape[0]
        for i in self.raw.tolist():
            coord.append(sum(i) / v_n)
        return Point(*coord[:3])

    @classmethod
    def from_raw(cls, raw: np.ndarray):
        shape = raw.shape
        if not (shape[0] == 4 and shape[1] >= 4):
            raise
        # all has to be points
        if not all([i == 1 for i in raw[3]]):
            raise

        coordinates = raw[:3].transpose().tolist()
        inst = cls(*coordinates)
        return inst
    def __str__(self):
        return f'<Polygone> {self.raw.shape[1]-1} edges'

class Triangle(Polygone):

    def __init__(self, a, b, c):
        """
        all inputs should be points
        :param args: coordinate of points
        """
        super().__init__(a, b, c)
        # anti-clockwise check?
        # general method usage?

"""
need configuration for complex shape
"""


class Brep:
    pass


class CSG:
    pass


class Tetragon(Polygone):
    def __init__(self, a, b, c, d):
        """
        vectors represent order:

        a------d
        ;      ;
        ;      ;
        ;      ;
        b------c

        :param a,b,c,d: vertex of tetragon
        """
        super().__init__(a,b,c,d)


    def __str__(self):
        return f'{self.__class__.__name__} centered {self.center}'


class Trapezoid(Tetragon):
    def __init__(self, a, b, c, d):
        """

        :param a:
        :param b:
        :param c:
        :param d:
        """
        super.__init__(a,b,c,d)
        edges = polyline.edges()
        # at least one pair has to be parallel
        if not vector.is_parallel(edges[0],edges[2]) and not vector.is_parallel(edges[1], edges[3]):
            raise


class Parallelogram(Tetragon):
    pass


class Rectangle(Parallelogram):
    pass


class Rhombus(Parallelogram):
    pass


class Square(Rectangle):
    pass


class Hexahedron(Geometry):
    def __init__(self,
                 a=[-50, 50, -50], b=[-50, -50, -50], c=[50, -50, -50], d=[50, 50, -50],
                 e=[-50, 50, 50], f=[-50, -50, 50], g=[50, -50, 50], h=[50, 50, 50]):
        """
        input vectors should follow order as shown below:
             +z
              :
              :
            e-;------h
           /; ;     /l
          / ; :    / l
         /  ; :   /  l
        f--------g   l
        l   a....l...d
        l  .  ;  l  /
        l .   o--l-/------ +x
        l.       l/
        b------- c

        yet raw array will store vertex values as following order -> d,c,b,a,e,f,g,h
             +z
              :
              :
            4-;------7
           /; ;     /l
          / ; :    / l
         /  ; :   /  l
        5--------6   l
        l   3....l...0
        l  .  ;  l  /
        l .   o--l-/------ +x
        l.       l/
        2------- 1


        :param a,b,c,d: vertex of top face going anti_clockwise
        :param e,f,g,h: vertex of bottom face going anti_clockwise
        """
        # default box of size 100,100,100 centered at origin(0,0,0)
        vertex = d, c, b, a, e, f, g, h
        for i, v in enumerate(vertex):
            if not isinstance(v, (list, tuple)):
                raise
            if len(v) != 3:
                raise
            if not all([isinstance(ii, Number) for ii in v]):
                raise
            vertex[i].append(1)
        array = np.array(vertex).transpose()
        self.raw = array

    @property
    def vertex(self):
        l = self.raw[:3].transpose().tolist()
        return l

    @property
    def center(self):
        coord = []
        for i in self.raw.tolist():
            coord.append(sum(i) / 8)
        return Point(*coord[:3])

    def __str__(self):
        return f'{self.__class__.__name__} centered {self.center}'


class Box(Hexahedron):
    def __init__(self,
                 a, b, c, d,
                 e, f, g, h):
        # box check first
        super().__init__(a, b, c, d, e, f, g, h)





class Matrix(Geometric_value):
    def __init__(self,
                 e00: Number = 1, e01: Number = 0, e02: Number = 0, e03: Number = 0,
                 e10: Number = 0, e11: Number = 1, e12: Number = 0, e13: Number = 0,
                 e20: Number = 0, e21: Number = 0, e22: Number = 1, e23: Number = 0,
                 e30: Number = 0, e31: Number = 0, e32: Number = 0, e33: Number = 1):

        elements = [e00, e01, e02, e03,
                    e10, e11, e12, e13,
                    e20, e21, e22, e23,
                    e30, e31, e32, e33]
        if not all([isinstance(i, Number) for i in elements]):
            raise ValueError
        self._raw = np.array(elements).reshape((4, 4))

    @classmethod
    def from_raw(cls, raw):
        if not isinstance(raw, np.ndarray):
            raise
        if raw.shape != (4, 4):
            raise ValueError
        return cls(*raw.flatten().tolist())

    def __str__(self):
        listed = self.raw.tolist()

        for r, row in enumerate(listed):
            for c, ii in enumerate(row):
                listed[r][c] = '{: .2f}'.format(ii)
            listed[r] = str(row)

        listed[0] = f'{self.__class__.__name__} : ' + listed[0]
        return '{:>45}\n{:>45}\n{:>45}\n{:>45}'.format(*listed)

    @staticmethod
    def trans_from_origin_to_plane(pla: Plane):
        return matrix.trans_between_origin_and_plane(pla)[1]

    @staticmethod
    def trans_from_plane_to_origin(pla: Plane):
        return matrix.trans_between_origin_and_plane(pla)[0]

    @staticmethod
    def trans_between_origin_and_plane(pla: Plane):
        """
        calculates two transform matrices
            [0] to_origin_matrix: transform matrix from plane to origin
            [1] to_plane_matrix: transform matrix from origin to plane

        :param pla: target plane
        :return: (tom, tpm)
        """
        to_origin_matrices = []
        to_plane_matrices = []

        pla = pla.copy()
        origin = pla.get_origin()

        # this is the last move
        if not Point.coinside(pla.get_origin(),Point()):
            to_plane_vector = Vector.con_point(origin)
            to_plane_matrices.append(Matrix.translation(to_plane_vector))
            to_origin_matrices.append(Matrix.translation(to_plane_vector.flip()))

        # match rotation
        # from z look x and match
        # from y look x and match
        # from x look y and match
        x_axis = pla.get_x_axis()
        x_on_xyplane = x_axis.project_on_xy()
        alpha = Vector.angle_plane(x_on_xyplane, Plane())
        if np.isclose(alpha, 0, atol=DEF_TOLERANCE):
            pass
        else:
            trans.rotate_around_z(pla, -alpha)
            to_origin_matrices.insert(0, Matrix.rotation_z(-alpha))
            to_plane_matrices.append(Matrix.rotation_z(alpha))
        # it must be already on yz plane
        x_on_xzplane = pla.get_x_axis()
        alpha = Vector.angle_plane(x_on_xzplane, Plane(y=[0,0,1],z=[0,-1,0]))
        if np.isclose(alpha, 0, atol=DEF_TOLERANCE):
            pass
        else:
            trans.rotate_around_y(pla, alpha)
            to_origin_matrices.insert(0, Matrix.rotation_y(alpha))
            to_plane_matrices.append(Matrix.rotation_y(-alpha))

        y_on_yzplane = pla.get_y_axis()
        alpha = Vector.angle_plane(y_on_yzplane, Plane(x=[0,1,0],y=[0,0,1],z=[1,0,0]))
        if np.isclose(alpha, 0, atol=DEF_TOLERANCE):
            pass
        else:
            trans.rotate_around_x(pla, -alpha)
            to_origin_matrices.insert(0, Matrix.rotation_x(-alpha))
            to_plane_matrices.append(Matrix.rotation_x(alpha))


        to_origin_matrix = Matrix.combine(*to_origin_matrices)
        to_plane_matrix = Matrix.combine(*to_plane_matrices)

        return to_origin_Matrix, to_plane_Matrix

    @staticmethod
    def translation(vec: Vector):
        if not isinstance(vec, Vector):
            raise TypeError
        matrix = np.eye(4)
        matrix[:3, 3] = vec.xyz
        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_x(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = tri.degree_radian(angle)
        matrix[1] = 0, np.cos(angle), -tri.sin(angle), 0
        matrix[2] = 0, tri.sin(angle), np.cos(angle), 0

        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_y(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = tri.cos(angle), 0, tri.sin(angle), 0
        matrix[2] = -tri.sin(angle), 0, tri.cos(angle), 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_z(angle, degrees=False):
        """
        counter-clockwise looking at origin
        :param angle:
        :param degrees:
        :return:
        """
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = tri.cos(angle), -tri.sin(angle), 0, 0
        matrix[1] = tri.sin(angle), tri.cos(angle), 0, 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def scale(x, y, z):
        return Matrix(x, 0, 0, 0,
                      0, y, 0, 0,
                      0, 0, z, 0,
                      0, 0, 0, 1)

    @staticmethod
    def rotation_vector(vec: Vector, angle: Number, degree=False):
        raise

    @staticmethod
    def transform(matrix, geometry):
        pass

    @staticmethod
    def transformation_2_planes(from_plane: Plane, to_plane: Plane):
        if not isinstance(from_plane, Plane) or not isinstance(to_plane, Plane):
            raise TypeError
        to_plane_from_origin = matrix.trans_from_origin_to_plane(to_plane)
        to_origin_from_plane = matrix.trans_from_plane_to_origin(from_plane)
        print(to_plane_from_origin)
        print(to_origin_from_plane)

        matrix.combine()
        exit()

    @staticmethod
    def combine(*mat):
        """
        Combine transformation matrices.
        Bear in mind that combination order goes from right to left,
        in other words, from index -1 to index 0.

        :param mat: matrices to combine
        :return: combined matrix
        """
        result = np.eye(4)
        for m in reversed(mat):
            x = m.raw.copy()
            result = x.dot(result)
        return Matrix.from_raw(result)


class Transformation(Primitive):

    def __init__(self, array: np.ndarray):
        self.set_data(array)

    pass


class intersection:
    @mymethod
    def pline_line(pol:(Polyline,Polygone), lin:Line):
        # TODO how to define plane of polyline
        if lin.vertices[0][2] != 0 or lin.vertices[1][2] != 0:
            raise Exception('not defined yet for 3d line')
        edges = polyline.edges(pol)
        inter = [[],[]]
        for e in edges:
            i = intersection.line_line(e,lin,on_line=True)
            if i != None:
                if isinstance(i, Point):
                    inter[0].append(i)
                elif isinstance(i, Line):
                    inter[1].append(i)

        inter[0] = point.unique_points(inter[0])[0]

        # if has line remove points coinside with line's vertex
        if len(inter[1]) != 0:
            line_vertices = []
            for l in inter[1]:
                line_vertices += line.decon(l)
            line_vertices = point.unique_points(line_vertices)[0]
            mask = point.in_points(line_vertices, *inter[0])
            inter[0] = data.cull_pattern(inter[0],mask,flip_mask=True)
        inter = inter[0]+inter[1]

        return inter

    @staticmethod
    def line_line(line1:Line, line2:Line, on_line=True):
        if not isinstance(line1,Line) or not isinstance(line2,Line):
            raise TypeError
        # need to define what is correct intersection
        # 1.if two lines coinside
        # 2.if two lines coinside partially
        # 3.if vertex of one line touches another
        # 4.if two lines intersect through the point
        # 5.if imaginary extension of two lines intersect eventually
        # let except #5 be considered as intersection
        # if line1.vertex
        (a,b),(c,d) = line.decon(line1), line.decon(line2)
        directional1 = vector.con_line(line1)
        directional2 = vector.con_line(line2)
        if vector.is_parallel(directional1, directional2):

            #1
            if line.coinside(line1,line2) or line.coinside(line1, line.flipped(line2)):
                return Line(a.xyz, b.xyz)
            #2
            elif point.is_on_line(line1,c):
                small, big = sorted((a.xyz[0], b.xyz[0]))
                if c.x > small:
                    if point.is_on_line(line1, d):
                        return Line(c.xyz, d.xyz)
                    elif d.xyz[0] < small:
                        return Line(a.xyz, c.xyz)
                    elif d.xyz[0] > big:
                        return Line(c.xyz, b.xyz)
                else:
                    return c

            elif point.is_on_line(line2, a):
                small, big = sorted((c.xyz[0], d.xyz[0]))
                if a.x > small:
                    if point.is_on_line(line2,b):
                        return Line(a.xyz, b.xyz)
                    elif b.xyz[0] > big:
                        return Line(a.xyz,d.xyz)
                    elif b.xyz[0] < small:
                        return Line(c.xyz, a.xyz)
                else:
                    return a

        else:
            #3 is merged with #4
            # TODO 4 vector method? need to understand this more fluently
            cross_two_directional = vector.cross(directional2,directional1)
            if cross_two_directional.length == 0:
                return None
            else:
                cross = vector.cross(directional2, vector.con_2_points(a, c))
                r = cross.length / cross_two_directional.length
                u = directional1*r
                if vector.is_parallel(cross, cross_two_directional) == 1:
                    new_p = a+u
                else:
                    new_p = a-u

                if on_line:
                    x = new_p.x
                    (x1,x2),(x3,x4) = sorted([a.x, b.x]), sorted([c.x, d.x])
                    if x >= x1 and x <= x2 and x >= x3 and x <= x4:
                        return new_p
                    else:
                        return None
                else:
                    return new_p


class tests:
    @staticmethod
    def triangulatioin(pol:Polygone):
        edges, vertices = polyline.decon(pol)

        vertices = vertices[:-1]
        unique_x = sorted(set(pol.raw[0]))
        x_min,x_max = unique_x[0], unique_x[-1]
        x_start = x_min - 1
        c_line_length = x_max-x_min+2
        # sort for convenience
        vertices = point.sort(vertices, 'y')
        ys = point.y(*vertices)
        vertices_sorted = data.sublist_by_unique_key(vertices, ys)
        for i, l in enumerate(edges):
            s, e = line.decon(l)
            if s.y > e.y:
                l.flip()
            elif s.y == e.y:
                if s.x > e.x:
                    l.flip()

        # trapezoidal Decomposition
        trapezioid = []
        for y, vs in vertices_sorted.items():
            # first draw a line and find intersecting points
            c_line = line.con_point_vector(Point(x_start,y,0), Vector(c_line_length,0,0))
            print()
            print('vertex', vs)
            print('crossing line:', c_line.vertices)
            p_inter = []
            e_under = []
            e_cross = []
            for e in edges:
                # all intersection given as a point or a line
                if e.start[1] == y:
                    # ignore because there must be another conneted to this edge's start
                    p_inter.append(line.start(e))
                elif e.start[1] < y and y < e.end[1]:
                    p_inter.append(intersection.line_line(c_line, e))
                    e_cross.append(e)

                elif e.end[1] == y:
                    if e.start[1] != y:
                        # edge below
                        e_under.append(e)
                        p_inter.append(line.end(e))

                elif e.end[1] < y:
                    # this must be left over from provious iteration
                    e_under.append(e)

            # no detection must be when another co_linear another vertex has finished cut off
            if len(e_under+e_cross) == 0:
                continue
            # remove collected edges
            for e in e_under+e_cross:
                edges.remove(e)

            # make intersections unique
            print(p_inter)
            p_inter = point.unique_points(p_inter)[0]
            p_inter = point.sort(p_inter,'x')

            # several cased for number of intersection points
            n = len(p_inter)
            print(' intersections', p_inter)
            if n == 0:
                # this can't happen except for the point lowest
                raise
            elif n == 1:
                # peak dealing will be after segments are delt
                pass
            else:
                # need to look for valid c_line segment
                # find position of vertex
                segments = []
                for i in range(len(p_inter)-1):
                    middle_p = point.average([p_inter[i], p_inter[i+1]])
                    print(middle_p)
                    condition1 = polygone.point_in(pol, middle_p) == 1 # condition1; not on but in
                    condition2 = False # condition2; at least one vertex is a part of the segment
                    print('dddddddddddddd', vs)
                    for y in vs:
                        print(y, p_inter[i], p_inter[i+1])
                        if point.coinside(y, p_inter[i]) or point.coinside(y, p_inter[i+1]):
                            condition2 = True
                            break
                    print('     conditions ', condition1, condition2)
                    print('     ', y, p_inter[i], p_inter[i+1])
                    print('     ', point.coinside(y, p_inter[i]) or point.coinside(y, p_inter[i+1]))
                    if condition1 and condition2:
                        print(vs)
                        print(' correct segment', p_inter[i],p_inter[i+1])
                        segments.append(line.con_two_points(p_inter[i],p_inter[i+1]))

                    else:
                        # segments.append(None)
                        pass

                # this is to leave peak candidate
                segments_vertex = []
                for s in segments:
                    segments_vertex += line.decon(s)
                segments_vertex = point.unique_points(segments_vertex)[0]
                to_remove = []
                print('+++++++++++++++++')
                print(segments_vertex)
                print(vs)
                for y in vs:
                    for i in segments_vertex:
                        if point.coinside(i,y):
                            to_remove.append(y)
                            break
                for i in to_remove:
                    vs.remove(i)


                edges += segments
                print('     segments', segments)
                # now i have correct c_line_segment so cut original polyline and make trapezioid out or it
                for s in segments:
                    print(s)
                    s_vertex = line.decon(s)
                    print('         e_cross', e_cross)
                    for e in e_cross:
                        mask = point.is_on_line(e, *s_vertex)
                        print('----------------', mask, e, s_vertex)
                        if any(mask):
                            p = data.cull_pattern(s_vertex, mask)[0]
                            e_vertex = line.decon(e)

                            # need to split
                            down = line.con_two_points(e_vertex[0], p)
                            up = line.con_two_points(p, e_vertex[1])

                            # record for next local, global search
                            print('     appending down', down.vertices)
                            e_under.append(down)
                            edges.append(up)
                            # need this removal cus rest gonna be added to edges list
                            e_cross.remove(e)
                            break
                edges += e_cross
                print(segments)
                print(e_cross)
                print(e_under)
                e_under += segments
                for s in segments:
                    if s in e_under:
                        e_under.remove(s)
                    else:
                        # previouse iteration could have removed a segment
                        # as taking it as a part of its boundary
                        continue

                    building_trapeziod = [s]
                    # track edges
                    default_plane = Plane()
                    trace = line.start(s)
                    vec_trace = vector.con_2_points(*reversed(line.decon(s)))
                    while True:
                        # how to move anti_clockwise
                        flag_found = False
                        print('eeee', e_under)
                        for e in e_under:
                            has = line.has_vertex(e, trace)
                            print(e.vertices)
                            print('kkk',has)
                            if has:
                                v_next = line.decon(e)[has[1]-1]
                                new_vec_trace = vector.con_2_points(trace, v_next)
                                # anti clockwise condition
                                side,angle = vector.right_left_halfspace(vec_trace, new_vec_trace)
                                if math.any_one_of(side, 1, 2):
                                    building_trapeziod.append(e)
                                    trace = v_next
                                    vec_trace = new_vec_trace
                                    e_under.remove(e)
                                    flag_found = True
                                    break

                        if not flag_found:
                            # seen through all edges but couldn't find one
                            # -> something is wrong
                            print(s.vertices)
                            print(building_trapeziod)
                            raise
                        # if shape is closed
                        if point.coinside(trace, line.end(s)):
                            # replace colinear edges to pline and organize
                            left = building_trapeziod.pop(1)
                            keys = [line.middle(l).y for l in building_trapeziod]
                            building_trapeziod = data.sublist_by_unique_key(building_trapeziod, keys)
                            building_trapeziod = sorted(building_trapeziod.items(), key = lambda x:x[0])

                            flag_poly = False
                            for i, (y,l) in enumerate(building_trapeziod):
                                if len(l) != 1:
                                    flag_poly = True
                                    building_trapeziod[i] = polyline.con_from_lines(l)
                                else:
                                    building_trapeziod[i] = l[0]

                            building_trapeziod.insert(0,left)
                            # index 0 is alway top and goes clockwise
                            building_trapeziod = data.shift(building_trapeziod, -1)
                            if flag_poly:
                                a = polyline.join(*building_trapeziod)
                                print(a)
                                raise
                            trapezioid.append(building_trapeziod)
                            break

            # dealing with peak and basin
            # condition
            if len(e_under) != 0 and len(vs) != 0:
                print('-----------------')
                print('dealing with basin')
                print(vs)
                print(segments)
                print(edges)
                print(e_under, len(e_under))
                peaks,basins = [],[]
                # find basins
                for l in edges:
                    s,e = line.decon(l)
                    mark = []
                    # see if it's on the c_line
                    for y in vs:
                        if point.coinside(y, s):
                            mark.append(y)
                            break
                    for y in vs:
                        if point.coinside(y, e):
                            mark.append(y)
                            break
                    if len(mark) == 2:
                        vs.remove(mark[0])
                        vs.remove(mark[1])
                        basins.append(l)
                for i in basins:
                    edges.remove(i)
                # rest are peaks
                peaks = vs

                # find peaks
                for p in peaks:
                    vs.remove(p)
                    building_peak = []
                    for e in e_under:
                        if point.coinside(line.end(e), p):
                            building_peak.append(e)
                        if len(building_peak) == 2:
                            break
                    print('ddd',p,building_peak)
                    vertex = line.start(building_peak[0]), line.start(building_peak[1])
                    for e in e_under:
                        print(e.vertices, point.is_on_line(e, *vertex))
                        if all(point.is_on_line(e, *vertex)):
                            building_peak.insert(0,e)
                            break
                    if len(building_peak) != 3:
                        print(p)
                        print(vertex)
                        print(building_peak)
                        print(e_under)
                        raise
                    for i in building_peak:
                        e_under.remove(i)
                    trapezioid.append(building_peak)

                # find basins
                e_under += basins
                print(e_under)
                for b in basins:
                    if b not in basins:
                        continue
                    building_basin = [b]
                    e_under.remove(b)
                    trace, end = line.decon(b)
                    vec_trace = vector.con_line(b).flip()
                    while True:
                        flag_found = False
                        # next edge is always the side of trapeziod
                        # but next can have multiple edges connected to the end of previous
                        candidates = []
                        print(e_under)
                        for e in e_under:
                            has = line.has_vertex(e, trace)
                            print(e.vertices, has, trace)
                            if has:
                                next_trace = line.decon(e)[has[1]-1]
                                directional = vector.con_2_points(trace, next_trace)
                                side, angle = vector.right_left_halfspace(vec_trace, directional)
                                print(side, math.any_one_of(side, 1, 2))
                                if math.any_one_of(side, 1, 2):
                                    candidates.append((angle,directional,e,next_trace))
                                    flag_found = True
                                    print('ddddddd', candidates)
                        print('ddddddd', candidates)
                        if not flag_found:
                            print(e_under[0].vertices)
                            print(b)
                            print(trace)
                            print(candidates)
                            print(building_basin)
                            raise

                        if len(candidates) != 1:
                            _,vec_trace,e,trace = math.biggest(candidates,key=lambda x:x[0])
                            building_basin.append(e)
                            e_under.remove(e)
                        else:
                            _,vec_trace,e,trace = candidates[0]
                            print('xxx', e, trace)
                            building_basin.append(e)
                            e_under.remove(e)

                        if point.coinside(trace, end):
                            break

                    trapezioid.append(building_basin)

            edges += e_under

        if len(edges) != 0:
            raise

        for i in trapezioid:
            print(i)

        # monotone Subdivision
        # basic tactic is to read stack and see if any of monotonal adjustant with bottom of inspected
        # another thing to check is parallelity of sides.
        # if any polyline is seen then this needs self division
        monotone = []
        for t in trapezioid:
            if len(monotone) == 0:
                top_edge = t[0]
                shape = polygone.con_edges(t)
                # or if manually checking horizontal edges
                print(shape)
                monotone.append([top_edge, shape])
                continue
            else:
                # find bottom
                shape = len(t)
                if shape == 3:
                    adding_bottom_e = t[0]
                    adding_top_e = None
                elif shape == 4:
                    adding_bottom_e = t[2]
                    adding_top_e = t[0]

                for i,(top_edge, m) in enumerate(monotone):
                    if top_edge == None:
                        # top edge none means its closed, its monotone
                        continue

                    if isinstance(adding_bottom_e, Polyline) or isinstance(adding_top_e, Polyline):
                        # if horizontal of trapezoid is polyline, means it has to be segmented?
                        # or had it be done already?
                        raise

                    else:
                        if line.coinside(top_edge, adding_bottom_e,consider_direction=True):
                            print(m)
                            pl1 = polyline.remove_edge(m,adding_bottom_e)
                            t.remove(adding_bottom_e)
                            pl2 = polyline.con_from_lines(t)

                            print(pl1.vertices)
                            print(pl2.vertices)
                            new_mono = polyline.join(pl1,pl2)
                            print(new_mono)
                            new_mono = polyline.iron(new_mono)
                            print(new_mono)
                            # monotone[i][1] = polygone.merge(m,adding_shape)
                            break


                pass


        # triangulation
        # deed to considier out of shape triangulation


class morph:
    @staticmethod
    def extrude(geo:Geometry, direction:Vector) -> Geometry:
        if isinstance(geo, Flat):
            pass


        elif isinstance(geo, Line):
            raise
        else:
            raise

class trans:
    def __init__(self, caller):
        self._caller = caller

    @ mymethod
    def test(first, second):
        print('this is a test method', first)

    @staticmethod
    def orient(geo:Geometry, source:Plane, target:Plane) -> Geometry:
        """
        orient given geometry from source plane to target plane
        :param geo: thing to orient
        :param source: reference plane of geo
        :param target: result plane of geo
        :return: geo
        """
        tom,_ = matrix.trans_between_origin_and_plane(source)
        _,tpm = matrix.trans_between_origin_and_plane(target)
        geo = trans.transform(geo, tom)
        geo = trans.transform(geo, tpm)
        return geo

    @staticmethod
    def move(geo:Geometry, vec: Vector) -> Geometry:
        x = Matrix.translation(vec)

        return trans.transform(geo, x)

    # @tlist.calitem
    # def test(x, y):
    #     print(x, y)
    #     pass


    @staticmethod
    def transform(geo:Geometry, *matrices:Matrix) -> Geometry:
        """

        :param geo:
        :param matrices:
        :return:
        """
        # not going to change coordinate directly
        # yet gonna change plane indication world orientation of geometry
        if isinstance(geo, Geometry):
            r = geo.pla.raw
        elif isinstance(goe, (Vector,Plane)):
            r = geo.raw

        # calculate backward
        for m in reversed(matrices):
            r[:] = m.raw.dot(r)
        return geo
    # @tlist.calitem
    # def rect_mapping(geometry: Geometry, source: Rect, target: Rect):
    #     source_v = source.vertex()
    #     target_v = target.vertex()
    #     m_trans = matrix.translation(vector.con2pt(source_v[0], target_v[0]))
    #     m_rotate = None
    #     m_scale = None
    #     m_sheer = None
    #
    #     # t = target()*np.invert(source())
    #     # print(t)
    #     # vectors = vector.con2pt(source.vertex(),target.vertex())
    #     # average = vector.average(vectors)

    @staticmethod
    def rotate_around_axis(geometry:Geometry, axis:Line, angle, degree=False):
        if not isinstance(axis,Line):
            if isinstance(axis, Vector):
                axis = line.con_from_vector(axis)
            else:
                raise TypeError
        axis_start,_ = line.decon(axis)
        # vector from axis
        axis_vector = vector.con_line(axis)
        # what is this for? want to fine another vector that is close to x and perpendicular
        ref_point = Point(1,0,0)

        projected_point = point.perpendicular_on_vector(axis_vector,ref_point)
        perpen_v = vector.con_2_points(projected_point, ref_point)
        # and build a reference plane
        ref_plane = plane.con_2_vectors(axis_vector, perpen_v, 'z', 'x', axis_start)
        xpo,xop = matrix.trans_between_origin_and_plane(ref_plane)

        # back force move
        geometry = trans.transform(geometry, xpo)
        # using rotation z because input axis is set as z while building ref_plane
        geometry = trans.rotate_around_z(geometry,angle,degree)
        geometry = trans.transform(geometry, xop)

        return geometry

    @staticmethod
    def rotate_around_x(geometry:Geometry, angle, degree=False, ):
        """
        roatate counter_clockwise looking at origin
        :param geometry:
        :param angle:
        :param degree:
        :return:
        """
        x = matrix.rotation_x(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_y(geometry:Geometry, angle, degree=False):
        """
        rotate counter_clockwise looking at origin
        :param geometry:
        :param angle:
        :param degree:
        :return:
        """
        x = matrix.rotation_y(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_z(geo:Geometry, angle:Number, degree=False):
        """
        rotate counter_clockwise looking at origin
        :param geo:
        :param angle:
        :param degree:
        :return:
        """
        x = matrix.rotation_z(angle, degree)
        return trans.transform(geo, x)


class line:
    @mymethod
    def unique_lines(lines:(list, tuple), consider_direction = False) -> list:
        to_compare= lines.copy()
        unique = []
        while True:
            for l in to_compare:
                to_compare.remove(l)
                unique.append(l)
                similar = []
                for ll in to_compare:
                    if line.coinside(l, ll, consider_direction=consider_direction):
                        similar.append(ll)
                for i in similar:
                    to_compare.remove(i)
                break

            if len(to_compare) == 0:
                break

        return unique

    @staticmethod
    def is_parallel(line1:Line, line2:Line) -> bool:
        vector1, vector2 = vector.con_line(line1), vector.con_line(line2)
        if math.any_one_of(vector.is_parallel(vector1, vector2), -1,1):
            return True
        return False

    @staticmethod
    def start(lin:Line) -> Point:
        return Point(*lin.start)

    @staticmethod
    def end(lin:Line) -> Point:
        return Point(*lin.end)

    @mymethod
    def decon(lin:Line):
        return [Point(*lin.raw.copy()[:3, 0]), Point(*lin.raw.copy()[:3, 1])]

    @staticmethod
    def has_vertex(lin:Line, poi:Point):
        start, end = lin.vertices
        coord = poi.xyz
        if all([a==b for a,b in zip(start,coord)]):
            return [ True, 0 ]
        elif all([a==b for a,b in zip(end, coord)]):
            return [ True, 1 ]
        else:
            return False

    @staticmethod
    def middle(lin:Line):
        if not isinstance(lin, Line):
            raise TypeError
        coord = []
        for a,b in zip(*lin.vertices):
            coord.append((a+b)/2)
        return Point(*coord)

    @staticmethod
    def coinside(line1:Line, line2:Line, consider_direction = True) -> bool:
        if consider_direction:
            return np.sum(np.equal(line1.raw, line2.raw)) == 8
        else:
            return any([
                np.sum(np.equal(line1.raw, line2.raw)) == 8,
                np.sum(np.equal(line1.raw, np.flip(line2.raw,1))) == 8])

    @staticmethod
    def flipped(lin:Line):
        return Line(lin.end,lin.start)

    @staticmethod
    def con_two_points(start:Point, end:Point) -> Line:
        return Line(start.xyz, end.xyz)

    @staticmethod
    def con_point_vector(start:Point, vec:Vector) -> Line:
        return line.con_two_points(start, trans.move(vec, start))

    @staticmethod
    def con_from_vector(vector:Vector):
        end = vector.raw.copy().transpose().tolist()[0][:3]
        return Line([0,0,0],end)


class data:
    @mymethod
    def filter_type(lis:(tuple, list), *t:type, include_exclude = True) -> list:
        if include_exclude:
            new_list = []
        else:
            new_list = lis.copy()

        for i in lis:
            for ii in t:
                if isinstance(i, ii):
                    if include_exclude:
                        new_list.append(i)
                    else:
                        new_list.remove(i)

        return new_list


    @staticmethod
    def shift(lis,step):
        new_lis = []
        l = len(lis)
        index = step%l
        for i in lis:
            new_lis.append(lis[index])
            index = (index+1)%l
        return new_lis

    @staticmethod
    def sublist_by_unique_key(lis:(list,tuple), keys:(list, tuple)):
        if not isinstance(lis, (list,tuple)) or not isinstance(keys,(list,tuple)):
            raise TypeError
        if len(lis) != len(keys):
            raise ValueError

        unique_keys = set(keys)
        dic = dict(zip(unique_keys, [[] for i in range(len(unique_keys))]))
        for k,i in zip(keys, lis):
            dic[k].append(i)

        return dic

    @staticmethod
    def cull_pattern(lis:(tuple,list), mask:(tuple, list), flip_mask = False) -> list:
        if isinstance(lis, (tuple, list)):
            if len(lis) != len(mask):
                raise
            if flip_mask:
                mask = [ not m for m in mask]

            new_list = []
            for v,m in zip(lis, mask):
                if m:
                    new_list.append(v)

            return new_list

        else:
            raise Exception('not defined yet')

    @staticmethod
    def split_pattern(lis:(tuple, list), mask:(tuple, list), flip_mask=False) -> list:
        if isinstance(lis, (tuple, list)):
            if len(lis) != len(mask):
                raise TypeError
            true_list = []
            false_list = []
            for v,m in zip(lis, mask):
                if m:
                    true_list.append(v)
                else:
                    false_list.append(v)
            if flip_mask:
                return [ false_list, true_list ]
            else:
                return [ true_list, false_list]

        else:
            raise Exception('not defined yet')

    @staticmethod
    def list_item(lis:(tuple, list), *index:int):
        if isinstance(lis, (tuple, list)):
            if len(index) == 0:
                return None

            new_list = []
            for i in index:
                i = i% len(lis)
                new_list.append(lis[i])

            if len(new_list) == 1:
                return new_list[0]
            else:
                return new_list

        else:
            raise Exception('not defined yet')
class string:
    @mymethod
    def start(stri:String) -> Point:
        return Point(*stri.raw[:3, 0])
    @mymethod
    def end(stri:String) -> Point:
        return Point(*stri.raw[:3, -1])
    @mymethod
    def flip(stri:String) -> String:
        raw = np.flip(stri.raw.copy(), 1)
        return stri.__class__.from_raw(raw)

    @mymethod
    def vertex(stri:String):
        raw = stri.raw[:3].transpose().tolist()
        points = []
        for i in raw:
            points.append(Point(*i))
        return points

    @mymethod
    def edges(stri:String):
        pass

    @mymethod
    def decon(stri:String):
        raw = np.flip(stri.raw[:3].transpose().tolist())
        points = []
        for i in raw:
            points.append(Point(*i))
        edges = []
        for i in range(len(points)-1):
            edges.append(line.con_two_points(points[i], points[i+1]))
        return [edges, points]

class polyline:
    @mymethod
    def iron(poll:Polyline) -> Polyline:
        # look through each edge and see the vector of it
        edges = polyline.edges(poll)

        for i,e in enumerate(edges):
            this_v = vector.con_line(e)
            para_edges = []
            index = i
            while True:
                index = (index+1)%len(edges)
                next_e = edges[index]
                next_v = vector.con_line(next_e)
                if vector.is_parallel(this_v, next_v) == 1:
                    para_edges.append(next_e)
                else:
                    break
            if len(para_edges) != 0:
                s,e = line.start(e), line.end(para_edges[-1])
                ironned = line.con_two_points(s,e)
                edges[i] = ironned
                for i in para_edges:
                    edges.remove(i)

        new_poll = poll.__class__().append(*edges)
        return new_poll

    @mymethod
    def remove_edge(poll:Polyline, edge:Line) -> Polyline:
        poll_vertices = polyline.vertices(poll)
        split = None
        s,e = line.decon(edge)
        for i,v in enumerate(poll_vertices[1:-1]):
            if point.coinside(v, s):
                if point.coinside(poll_vertices[i+2],e):
                    split = i+1
                elif point.coinside(poll_vertices[i], e):
                    split = i

        if split is None:
            return poll
        first, second = poll_vertices[:split+1],poll_vertices[split+1:]
        if point.coinside(first[0], second[-1]):
            merged = second+first[1:]
            return polyline.con_from_points(merged)
        else:
            return [polyline.con_from_points(first), polyline.con_from_points(second)]

    @mymethod
    def con_polygone(polg:[Polygone, Polyline],a:str, *b:int, **c:dict):
        poll = Polyline()
        poll.raw = polg.raw.copy()
        return poll

    @staticmethod
    def start(pol: Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return Point(*pol.raw[:3, 0])

    @staticmethod
    def end(pol: Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return Point(*pol.raw[:3, -1])

    @staticmethod
    def start_end(pol:Polyline):
        if not isinstance(pol, Polyline):
            raise TypeError
        return [ Point(*pol.raw[:3, 0]), Point(*pol.raw[:3, -1]) ]

    @staticmethod
    def join(*segments:(tuple, list)):
        """
        excepts segments and return joined
        :return:
        """
        new_p_lists = []
        for l in segments:
            if not isinstance(l, String):
                raise WrongInputTypeError(l, String)
            new_p_lists.append(string.vertex(l))

        print('new p list',len(new_p_lists), new_p_lists)
        organized = []
        while True:
            for l in new_p_lists:
                print('join looking for joint ', l)
                organized.append(l)
                new_p_lists.remove(l)
                to_remove = []
                for ll in new_p_lists:
                    to_remove.append(ll)
                    # search for joint
                    if point.coinside(l[0],ll[0]):
                        l[:] = list(reversed(ll)) + l[1:]
                    elif point.coinside(l[0],ll[-1]):
                        l[:] = ll + l[1:]
                    elif point.coinside(l[-1],ll[0]):
                        l[:] = l + ll[1:]
                    elif point.coinside(l[-1],ll[-1]):
                        l[:] = l + list(reversed(ll)[1:])
                    else:
                        to_remove.remove(ll)

                for i in to_remove:
                    new_p_lists.remove(i)

                break
            if len(new_p_lists) == 0:
                break

        shapes = []
        for l in organized:
            shape = polyline.con_from_points(l)
            if polyline.is_closed(shape):
                shape = polygone.con_polyline(shape)
            shapes.append(shape)

        if len(shapes) == 1:
            return shapes[0]
        return shapes


    @staticmethod
    def con_from_lines(lines:(tuple, list)) -> Polyline:
        if not isinstance(lines, (tuple, list)):
            raise TypeError
        if len(lines) == 0:
            return None
        lines = lines.copy()
        starting_line= lines.pop(0)
        sorted_vertex = line.decon(starting_line)
        while True:
            flag_found = False
            to_remove = []
            for l in lines:
                cloud = sorted_vertex[0], sorted_vertex[-1]
                # if the line can be joined from start or end of collected
                s,e = line.decon(l)
                if any(point.in_points(cloud, s,e)):
                    flag_found = True
                    if point.coinside(sorted_vertex[0], s):
                        sorted_vertex.insert(0,e)
                    elif point.coinside(sorted_vertex[0], e):
                        sorted_vertex.insert(0,s)
                    elif point.coinside(sorted_vertex[-1], s):
                        sorted_vertex.append(e)
                    elif point.coinside(sorted_vertex[-1], e):
                        sorted_vertex.append(s)
                    to_remove.append(l)

            if not flag_found:
                return None

            for i in to_remove:
                lines.remove(i)

            if len(lines) == 0:
                break

        return polyline.con_from_points(sorted_vertex)

    @staticmethod
    def con_from_points(points_list:(tuple, list)) -> Polyline:
        if not isinstance(points_list, (tuple, list)):
            raise TypeError
        if len(points_list) == 0:
            return None

        raw = points_list[0].raw.copy()
        for p in points_list[1:]:
            if not isinstance(p, Point):
                raise
            raw = np.hstack((raw, p.raw.copy()))

        return Polyline.from_raw(raw)



    @staticmethod
    def decon(pol:Union[Polyline,Polygone]) -> list:
        """
        deconstructs polyline into points and lines
        :param pol:
        :return: [ list of lines, list of points ]
        """
        coords = pol.raw[:3].transpose().tolist()
        points = []
        for i in coords:
            points.append(Point(*i))

        lines = []
        for i in range(len(points)-1):
            lines.append(line.con_two_points(points[i], points[i+1]))

        return [lines, points]

    @staticmethod
    def vertices(poll: Polyline):
        coords = poll.raw[:3].transpose().tolist()
        points = []
        for i in coords:
            points.append(Point(*i))
        return points

    @staticmethod
    def edges(pol:Polyline):
        lines = []
        points = polyline.vertices(pol)
        for i in range(len(points)-1):
            lines.append(line.con_two_points(points[i],points[i+1]))
        return lines

    @staticmethod
    def is_closed(pol:Polyline):
        raw = pol.raw
        if all(np.equal(raw[:3,-1], raw[:3,0])):
            return True
        else:
            return False

class polygone:

    @mymethod
    def string_in(polg:Polygone, line:String):
        pass

    @mymethod
    def point_in(pol: Polygone, poi: Point):
        """
        tests whether point is (out in on) the polyline
        returns:
        0 if point is out
        1 if point is in
        2 if point is on the boundary
        :param pol: closed Polygon
        :param poi: Point to test
        :return: out, in, on sign
        """
        if not polyline.is_closed(pol):
            return None
        edges, vertices = polyline.decon(pol)

        # see point on polyline
        for e in edges:
            if poi.x == 7 and poi.y == 7:
                print(e.vertices, point.is_on_line(e, poi))
            if point.is_on_line(e, poi):
                return 2

        # see point in out polyline
        x_max = sorted(set(pol.raw[0]))[-1]
        end_point = Point(*poi.xyz)
        end_point.x = x_max + 1

        c_line = line.con_two_points(poi, end_point)
        iter_count = 0

        while True:
            flag_break = True
            # if can't find the case something is wrong
            if iter_count == 100:
                raise

            # see if crossing is valid
            inter = intersection.pline_line(pol, c_line)
            # if any one of intersection is a line or a vertex do it again
            print(inter)
            print('sss', data.filter_type(inter, Line))

            if len(data.filter_type(inter,Line)) != 0:
                flag_break = False
            elif any(point.in_points(vertices, *inter)):
                flag_break = False

            if flag_break:
                break
            else:
                c_line.raw[1,1] += 1
                iter_count += 1

        # # check peaks
        # if len(inter) != 0:
        #     mask = point.in_points(cloud, *inter)
        #     inter = data.cull_pattern(inter, mask, flip_mask=True)

        # count intersection
        if len(inter) % 2 == 0:
            return 0
        else:
            return 1

    @mymethod
    def con_edges(edges:List[Line]):
        # need edge crossing checking
        poll = polyline.con_from_lines(edges)
        return polygone.con_polyline(poll)

    @mymethod
    def con_polyline(poll:Polyline):
        return Polygone.from_raw(poll.raw.copy())


    @mymethod
    def merge(polg1:Polygone, polg2:Polygone, iron=True):
        raise
        print(polg1, polg2)
        edges1, edges2 = polyline.edges(polg1), polyline.edges(polg2)
        print(edges1)
        print(edges2)
        # find all intersections
        intersec = [[],[]]
        for e in edges1:
            for ee in edges2:
                i = intersection.line_line(e, ee)
                if isinstance(i, Line):
                    print('intersection', e.vertices, ee.vertices)
                    intersec[0].append(i)
                elif isinstance(i, Point):
                    intersec[1].append(i)
        print(intersec)
        intersec[0] = line.unique_lines(intersec[0])
        intersec[1] = point.unique_points(intersec[1])[0]
        print('ddd')
        print(intersec)
        for i in intersec[0]:
            print(i.vertices)
        lines_point_pool = []
        for l in intersec[0]:
            lines_point_pool += line.decon(l)
        mask = point.in_points(lines_point_pool, *intersec[1])
        intersec[1] = data.cull_pattern(intersec[1], mask, flip_mask=True)


        pass

    @mymethod
    def split(polg:Polygone, lin:Line) -> List[Polygone]:

        pass





class math:

    """
    this wrapping is for precision control
    """
    @staticmethod
    def biggest(values, key=None):
        if key == None:
            return sorted(values)[-1]
        elif isinstance(key, callable):
            return sorted(values, key)[-1]
        elif isinstance(key, (list, tuple)):
            if len(values) != len(key):
                raise ValueError
            return sorted(zip(key, values), key=lambda x:x[0])[-1][1]
        else:
            raise TypeError

    @staticmethod
    def smallest(values, key=None):
        if key == None:
            return sorted(values)[0]
        elif isinstance(key, callable):
            return sorted(values, key)[0]
        elif isinstance(key, (list, tuple)):
            if len(values) != len(key):
                raise ValueError
            return sorted(zip(key, values), key=lambda x: x[0])[0][1]
        else:
            raise TypeError

    @staticmethod
    def any_one_of(compared, *values):
        for v in values:
            if compared == v:
                return True
        return False

    @staticmethod
    def sqrt(v):
        return np.sqrt(v, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def square(v):
        return np.square(v, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def power(base, exponent):
        return np.power(base, exponent, dtype=DEF_FLOAT_FORMAT)

class trigonometry:
    """
    this wrapping is for precision control
    """
    pi = np.pi
    pi2 = np.pi*2
    pih = np.pi/2

    @staticmethod
    def sin(v):
        return np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def cos(v):
        return np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def tan(v):
        return np.tan(v,dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def arccos(cos_v):
        return np.arccos(cos_v,dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def arcsin(sin_v):
        return np.arcsin(sin_v, dtype=DEF_FLOAT_FORMAT)

    @staticmethod
    def degree_radian(degree):
        return np.radians(degree, dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def radian_degree(radian):
        return np.degrees(radian, dtype=DEF_FLOAT_FORMAT)

class tri(trigonometry):
    pass





class rectangle:
    @staticmethod
    def con_center_width_height(plane:(Plane,Point), width:Number, height:Number) -> Rectangle:
        if not isinstance(width,Number) or not isinstance(height, Number):
            raise TypeError

        if isinstance(plane, Point):
            x,y,z = plane.xyz
            w,h = width/2, height/2
            return Rectangle([x-w,y+h,z],[x-w,y-h,z],[x+w,y-h,z],[x+w,y+h,z])

        elif isinstance(plane, Plane):
            rect = Rectangle([-w,+h,0],[-w,-h,0],[+w,-h,0],[+w,+h,0])
            return trans.orient(rect, Plane(), plane)

        else:
            raise TypeError


class hexahedron:

    @staticmethod
    def decon(hexa:Hexahedron) -> (Point,
                                   (Point,Point,Point,Point,Point,Point,Point,Point),
                                   (Rectangle,Rectangle,Rectangle,Rectangle,Rectangle,Rectangle)):
        pass
    @staticmethod
    def face_of(hexa:Hexahedron, *index:int):
        """
        how to correctly order vertex and faces
        face[0] = vertex 0,1,2,3 bottom
        face[1] = vertex 0,7,6,1
        face[2] = vertex 1,6,5,2
        face[3] = vertex 2,5,4,3
        face[4] = vertex 3,4,7,0
        face[5] = vertex 4,5,6,7 top

        :param index:
        :return:
        """
        if len(index) == 0 :
            raise ValueError
        if not all([isinstance(i, Number) for i in index]):
            raise ValueError
        vertex = hexa.vertex
        faces = []
        for i in index:
            i = i % 6
            if i == 0:
                a,b,c,d = vertex[0:4]
            elif i == 5:
                a,b,c,d = vertex[4:8]
            else:
                a,b,c,d = i-1%4, 8-i, 5+i, i%4
                a,b,c,d = vertex[a],vertex[b],vertex[c],vertex[d]
            faces.append(Tetragon(a,b,c,d))

        if len(faces) == 1:
            return faces[0]
        return faces

