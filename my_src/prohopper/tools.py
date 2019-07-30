from .primitives import *

class trans:

    @staticmethod
    def move(vec: Vector, geometry:Geometry):
        x = matrix.translation(vec)
        return trans.transform(geometry, x)
    
    # @tlist.calitem
    # def test(x, y):
    #     print(x, y)
    #     pass
    
    @staticmethod
    def transform(geometry:Geometry, *matrices:Matrix):
        r = geometry.raw
        for m in reversed(matrices):
            r = m.raw.dot(r)
        return geometry.__class__.from_raw(np.array(r))
    
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
                axis = Line.from_vector(axis)
            else:
                raise TypeError
    
        # how to rotate around axis...
        # find trans matrices for world z to that axis and put it backward
        print(geometry, axis, angle)
        axis_plane = plane.con_2_vectors(Vector(1,0,0), axis)
        exit()
        x = matrix.transformation_2_planes()
        transform()
        pass

    @staticmethod
    def rotate_around_x(geometry:Geometry, angle, degree=False, ):
        x = matrix.rotation_x(angle, degree)
        return transform(geometry,x)

    @staticmethod
    def rotate_around_y(geometry:Geometry, angle, degree=False):
        x = matrix.rotation_y(angle, degree)
        return transform(geometry,x)

    @staticmethod
    def rotate_around_z(geometry:Vector, angle, degree=False):
        x = matrix.rotation_z(angle, degree)
        return transform(geometry,x)

class vector:

    # @tlist.calbranch
    # def average(*vectors: Vector):
    #     v = [i() for i in vectors]
    #     pass
    #
    #
    # @tlist.calitem
    # def con2pt(start: Point, end: Point):
    #     newv = Vector()
    #     newv.set_data(np.subtract(end(), start()))
    #     return newv

    @staticmethod
    def unit(vector:Vector, ):
        if not isinstance(vector, Vector):
            raise TypeError
        return vector/vector.length

    @staticmethod
    def divide(vector:Vector, v, raw=False):
        pass

    @staticmethod
    def multiply(vector:Vector, v, ):
        if raw:
            return vector.raw*v
        else:
            return vector*v

    @staticmethod
    def amplitude(vector:Vector, amp:Number):
        new_v = vector*(amp/vector.length)
        return new_v

    def flip(vector:Vector):
        if not isinstance(vector, Vector):
            raise TypeError
        return Vector().from_raw(vector.raw*[[-1],[-1],[-1],[0]])

    @staticmethod
    def angle_2_vectors(from_vector, to_vector, deegrees=False):
        u1,u2 = vector.unit(from_vector), vector.unit(to_vector)
        cos_value = u1.raw.flatten().dot(u2.raw.flatten())
        angle = np.arccos(cos_value)
        if deegrees:
            return np.degrees(angle)
        else:
            return angle

    @staticmethod
    def project_point_on_vector(point:Point, vector:Vector):
        if not isinstance(point, (Point,Vector)):
            raise TypeError
        if not isinstance(vector, Vector):
            raise TypeError

        angle = vector.angle_2_vectors(point, vector)
        return amplitude(vector, np.cos(angle)*point.length)

    @staticmethod
    def deconstruct(vector:Vector, ):
        on_xy = vector.raw.copy()
        on_xy[2,0] = 0
        on_yz = vector.raw.copy()
        on_yz[0,0] = 0
        on_xz = vector.raw.copy()
        on_xz[1,0] = 0
        return Vector().from_raw(on_xy),Vector().from_raw(on_yz),Vector().from_raw(on_xz)

    @staticmethod
    def project_on_xyplane(vector:Vector, ):
        new = vector.raw.copy()
        new[2,0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_yzplane(vector:Vector, raw=False):
        new = vector.raw.copy()
        new[0, 0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_xzplane(vector:Vector, raw=False):
        new = vector.raw.copy()
        new[1, 0] = 0
        return Vector().from_raw(new)

class matrix:

    @staticmethod
    def translation(vec: Vector):
        if not isinstance(vec, Vector):
            raise TypeError
        matrix = np.eye(4)
        matrix[:3, 3] = vec.xyz
        return Matrix().from_raw(matrix)

    @staticmethod
    def scaling():
        pass

    @staticmethod
    def rotation_x(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[1] = 0, np.cos(angle), -np.sin(angle), 0
        matrix[2] = 0, np.sin(angle), np.cos(angle), 0

        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_y(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = np.cos(angle), 0, np.sin(angle), 0
        matrix[2] = -np.sin(angle), 0, np.cos(angle), 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def rotation_z(angle, degrees=False):
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = np.cos(angle), -np.sin(angle), 0, 0
        matrix[1] = np.sin(angle), np.cos(angle), 0, 0
        return Matrix().from_raw(matrix)

    @staticmethod
    def transform(matrix: Matrix, geometry):
        pass

    @staticmethod
    def transformation_2_planes(from_plane: Plane, to_plane: Plane):
        if not isinstance(from_plane, Plane) or not isinstance(to_plane, Plane):
            raise TypeError
        #
        # # first find two angles
        # # need to apply transformations and then reverse it?
        # obj = np.hstack((axis.raw, point.raw))
        # # TODO is this the best way?
        # xy = vector.project_on_xyplane(axis)
        # # angle1
        # quarter = None
        # if xy.y >= 0:
        #     if xy.x >= 0:  # vector is in first quarter
        #         quarter = 0
        #     else:
        #         quarter = 1
        # else:
        #     if xy.x >= 0:
        #         quarter = 3
        #     else:
        #         quarter = 2
        #
        # rotation_z = np.arccos(xy.x / xy.length)
        # if quarter == 0 or quarter == 1:
        #     rotation_z_matrix = matrix.rotation_z(rotation_z)
        #     # seeing at direction from origin rotation goes clockwise so...
        #     # need to negative
        #     obj = matrix.rotation_z(-rotation_z).raw.dot(obj)
        # if quarter == 2 or quarter == 3:
        #     rotation_z_matrix = matrix.rotation_z(-rotation_z)
        #     obj = matrix.rotation_z(rotation_z).raw.dot(obj)
        #
        # # angle2
        # # x_axis already projected on xz plane so
        # xz = Vector().from_raw(obj[:4, [0]])
        # rotation_y = np.arccos(xz.x / xz.length)
        # if xz.x >= 0:
        #     if xz.z >= 0:
        #         quarter = 2
        #     else:
        #         quarter = 3
        # else:
        #     if xz.z >= 0:
        #         quarter = 0
        #     else:
        #         quarter = 1
        # if quarter == 0 or quarter == 1:
        #     rotation_y_matrix = matrix.rotation_y(rotation_y)
        #     obj = matrix.rotation_y(-rotation_y).raw.dot(obj)
        # else:
        #     rotation_y_matrix = matrix.rotation_y(-rotation_y)
        #     obj = matrix.rotation_y(rotation_y).raw.dot(obj)
        #
        # # angle 3
        # # need to find with second point
        # yz = obj[:3, 1]
        # yz[0] = 0
        # yz = Vector(*yz)
        # rotation_x = np.arccos(yz.y / yz.length)
        # if yz.z >= 0:
        #     if yz.y >= 0:
        #         quarter = 0
        #     else:
        #         quarter = 1
        # else:
        #     if yz.y >= 0:
        #         quarter = 3
        #     else:
        #         quarter = 2
        # if quarter == 0 or quarter == 1:
        #     rotation_x_matrix = matrix.rotation_x(rotation_x)
        #     obj = matrix.rotation_x(-rotation_x).raw.dot(obj)
        # else:
        #     rotation_x_matrix = matrix.rotation_x(-rotation_x)
        #     obj = matrix.rotation_x(rotation_x).raw.dot(obj)
        #
        # # transformation info collected
        # rotations = rotation_z_matrix, rotation_y_matrix, rotation_x_matrix
        # z = trans.transform(Vector(0, 0, 1), *rotations)
        # y = trans.transform(Vector(0, 1, 0), *rotations)
        #
        # if which_axis == 'x':
        #     return con_plane_3_vectors(axis, y, z, origin)
        # elif which_axis == 'y':
        #     return con_plane_3_vectors(z, axis, y, origin)
        # elif which_axis == 'z':
        #     return con_plane_3_vectors(y, z, axis, origin)
        # else:
        #     raise TypeError
        #
        # pass

    @staticmethod
    def combine_matrix(*matrix):
        result = np.eye(4)
        for m in reversed(matrix):
            new_r = m.raw.copy()
            result = new_r.dot(result)
        return Matrix.from_raw(result)

class plane:

    @staticmethod
    def third_perpendicular_vector_from_2(vector1, vector2):

        pass

    @staticmethod
    def con_vector_point(axis: Vector, which_axis, point: Point, origin: Point = Point(0, 0, 0)):
        if not isinstance(point, (Point, Vector)):
            raise TypeError
        if not isinstance(axis, Vector):
            raise TypeError
        if not isinstance(origin, Point):
            raise

        # first find two angles
        # need to apply transformations and then reverse it?
        obj = np.hstack((axis.raw, point.raw))
        # TODO is this the best way?
        xy = vector.project_on_xyplane(axis)
        # angle1
        quarter = None
        if xy.y >= 0:
            if xy.x >= 0:  # vector is in first quarter
                quarter = 0
            else:
                quarter = 1
        else:
            if xy.x >= 0:
                quarter = 3
            else:
                quarter = 2

        rotation_z = np.arccos(xy.x / xy.length)
        if quarter == 0 or quarter == 1:
            rotation_z_matrix = matrix.rotation_z(rotation_z)
            # seeing at direction from origin rotation goes clockwise so...
            # need to negative
            obj = matrix.rotation_z(-rotation_z).raw.dot(obj)
        if quarter == 2 or quarter == 3:
            rotation_z_matrix = matrix.rotation_z(-rotation_z)
            obj = matrix.rotation_z(rotation_z).raw.dot(obj)

        # angle2
        # x_axis already projected on xz plane so
        xz = Vector().from_raw(obj[:4, [0]])
        rotation_y = np.arccos(xz.x / xz.length)
        if xz.x >= 0:
            if xz.z >= 0:
                quarter = 2
            else:
                quarter = 3
        else:
            if xz.z >= 0:
                quarter = 0
            else:
                quarter = 1
        if quarter == 0 or quarter == 1:
            rotation_y_matrix = matrix.rotation_y(rotation_y)
            obj = matrix.rotation_y(-rotation_y).raw.dot(obj)
        else:
            rotation_y_matrix = matrix.rotation_y(-rotation_y)
            obj = matrix.rotation_y(rotation_y).raw.dot(obj)

        # angle 3
        # need to find with second point
        yz = obj[:3, 1]
        yz[0] = 0
        yz = Vector(*yz)
        rotation_x = np.arccos(yz.y / yz.length)
        if yz.z >= 0:
            if yz.y >= 0:
                quarter = 0
            else:
                quarter = 1
        else:
            if yz.y >= 0:
                quarter = 3
            else:
                quarter = 2
        if quarter == 0 or quarter == 1:
            rotation_x_matrix = matrix.rotation_x(rotation_x)
            obj = matrix.rotation_x(-rotation_x).raw.dot(obj)
        else:
            rotation_x_matrix = matrix.rotation_x(-rotation_x)
            obj = matrix.rotation_x(rotation_x).raw.dot(obj)

        # transformation info collected
        rotations = rotation_z_matrix, rotation_y_matrix, rotation_x_matrix
        z = trans.transform(Vector(0, 0, 1), *rotations)
        y = trans.transform(Vector(0, 1, 0), *rotations)

        if which_axis == 'x':
            return plane.con_3_vectors(axis, y, z, origin)
        elif which_axis == 'y':
            return plane.con_3_vectors(z, axis, y, origin)
        elif which_axis == 'z':
            return plane.con_3_vectors(y, z, axis, origin)
        else:
            raise TypeError

    @staticmethod
    def con_2_vectors(axis1: Vector, axis2: Vector, axis1_hint: str, axis2_hint: str):
        print(axis1, axis2, axis1_hint, axis2_hint)
        pass

    @staticmethod
    def con_3_vectors(x_axis: Vector, y_axis: Vector, z_axis: Vector, origin: Point = Point(0, 0, 0)):
        if not all([isinstance(i, Vector) for i in (x_axis, y_axis, z_axis)]):
            raise TypeError

        return Plane(origin.xyz, x_axis.xyz, y_axis.xyz, z_axis.xyz)

    @staticmethod
    def orient(origin_plane, geometry, target_plane):
        pass


