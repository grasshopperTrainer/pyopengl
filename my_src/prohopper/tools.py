from .primitives import *

DEF_TOLERANCE = 1.e-9

class morph:
    @staticmethod
    def extrude(geo:Geometry, direction:Vector) -> Geometry:
        if isinstance(geo, Flat):


        elif isinstance(geo, Line):
            raise
        else:
            raise

class trans:

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
                axis = line.con_from_vector(axis)
            else:
                raise TypeError
        axis_start,_ = line.decon(axis)
        # vector from axis
        axis_vector = vector.con_from_line(axis)
        # what is this for? want to fine another vector that is close to x and perpendicular
        ref_point = Point(1,0,0)

        projected_point = point.perpendicular_on_vector(axis_vector,ref_point)
        perpen_v = vector.con_two_points(projected_point, ref_point)
        # and build a reference plane
        ref_plane = plane.con_from_2_vectors(axis_vector, perpen_v, 'z','x', axis_start)
        xpo,xop = matrix.trans_between_origin_and_plane(ref_plane)

        # back force move
        geometry = trans.transform(geometry, xpo)
        # using rotation z because input axis is set as z while building ref_plane
        geometry = trans.rotate_around_z(geometry,angle,degree)
        geometry = trans.transform(geometry, xop)

        return geometry

    @staticmethod
    def rotate_around_x(geometry:Geometry, angle, degree=False, ):
        x = matrix.rotation_x(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_y(geometry:Geometry, angle, degree=False):
        x = matrix.rotation_y(angle, degree)
        return trans.transform(geometry,x)

    @staticmethod
    def rotate_around_z(geometry:Vector, angle, degree=False):
        x = matrix.rotation_z(angle, degree)
        return trans.transform(geometry,x)


class line:
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
    @staticmethod
    def decon(lin:Line):
        return Point(*lin.raw[:3, 0]), Point(*lin.raw[:3, 1])

class point:

    @staticmethod
    def con_from_vector(vec:Vector):
        return Point(*vec.xyz)

    @staticmethod
    def perpendicular_on_vector(vec: Vector, poi: Point):
        vec2 = vector.con_from_point(poi)
        a = vector.angle_2_vectors(vec, vec2)
        l = np.cos(a) * vec2.length
        new_v = vector.amplitude(vec, l)
        return point.con_from_vector(new_v)

    @staticmethod
    def average(*points:(list,tuple)) -> Point:
        coords = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            coords.append(p.xyz)
        coords = np.array(coords).transpose()
        new = []
        for l in coords:
            new.append(sum(l)/len(points))

        return Point(*new)


class vector:
    @staticmethod
    def dot(vec1:Vector, vec2:Vector) -> float:
        return vec1.raw.flatten().dot(vec2.raw.flatten())

    @staticmethod
    def con_two_points(start:Point, end:Point) -> Vector:
        coord = []
        for a,b in zip(start.xyz, end.xyz):
            coord.append(b-a)
        return Vector(*coord)

    @staticmethod
    def quarter_on_plane(vec:Vector, plane_hint:str):
        if not isinstance(vec, Vector):
            raise TypeError
        x,y,z = vec.xyz
        if plane_hint == 'xy' or plane_hint == 'yx':
            if x >= 0:
                if y >= 0:
                    return 0
                else:
                    return 3
            else:
                if y >= 0:
                    return 1
                else:
                    return 2

        elif plane_hint == 'yz' or plane_hint == 'zy':
            if y >= 0:
                if z >= 0:
                    return 0
                else:
                    return 3
            else:
                if z >= 0:
                    return 1
                else:
                    return 2

        elif plane_hint == 'zx' or plane_hint == 'xz':
            if z >= 0:
                if x >= 0:
                    return 0
                else:
                    return 3
            else:
                if x >= 0:
                    return 1
                else:
                    return 2
        else:
            raise ValueError

    @staticmethod
    def vector_2_points(start:Point, end:Point):
        return end-start

    @staticmethod
    def con_from_point(poi:Point):
        return Vector(*poi.xyz)



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
    def con_from_line(line:Line):
        if not isinstance(line, Line):
            raise TypeError
        xyz = []
        for a, b in zip(line.start, line.end):
            xyz.append(b - a)
        return Vector(*xyz)

    @staticmethod
    def unit(vec:Vector):
        if not isinstance(vec, Vector):
            raise TypeError
        if vec.length == 0:
            raise ValueError
        xyz = []
        for i in vec.xyz:
            xyz.append(i/vec.length)
        return Vector(*xyz)

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
    def angle_2_vectors(from_vector, to_vector, degree=False):
        u1,u2 = vector.unit(from_vector), vector.unit(to_vector)
        cos_value = u1.raw.flatten().dot(u2.raw.flatten())
        angle = np.arccos(cos_value)
        if degree:
            return np.degrees(angle)
        else:
            return angle



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
    def project_on_xyplane(vec:Vector):
        new = vec.raw.copy()
        new[2,0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_yzplane(vec:Vector):
        new = vec.raw.copy()
        new[0, 0] = 0
        return Vector().from_raw(new)

    @staticmethod
    def project_on_xzplane(vec:Vector):
        new = vec.raw.copy()
        new[1, 0] = 0
        return Vector().from_raw(new)

class matrix:
    @staticmethod
    def trans_from_origin_to_plane(pla:Plane) -> Matrix:
        return matrix.trans_between_origin_and_plane(pla)[1]
    @staticmethod
    def trans_from_plane_to_origin(pla:Plane) -> Matrix:
        return matrix.trans_between_origin_and_plane(pla)[0]

    @staticmethod
    def trans_between_origin_and_plane(pla:Plane) -> (Matrix, Matrix):
        """
        calculates two transform matrices
            [0] to_origin_matrix: transform matrix from plane to origin
            [1] to_plane_matrix: transform matrix from origin to plane

        :param pla: target plane
        :return: (tom, tpm)
        """
        to_origin_matrices = []
        to_plane_matrices = []
        origin, axis_x, axis_y, axis_z = plane.decon(pla)
        # this is the last move
        to_plane_vector = vector.con_from_point(origin)
        to_origin_matrices.append(matrix.translation(-to_plane_vector))
        to_plane_matrices.append(matrix.translation(to_plane_vector))

        # need to match each vectors
        # gonna match x,y,z
        # so looking into z rotation first

        # look for a vector that can be rotated
        vector_on_xy = vector.project_on_xyplane(axis_x)
        if vector_on_xy.length != 0:
            angle = vector.angle_2_vectors(Vector(1,0,0), vector_on_xy)
        else:
            vector_on_xy = vector.project_on_xyplane(axis_y)
            angle = vector.angle_2_vectors(Vector(0,1,0), vector_on_xy)
        quarter = vector.quarter_on_plane(vector_on_xy,'xy')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_z(angle)
        to_plane = matrix.rotation_z(-angle)
        to_origin_matrices.insert(0,to_origin)
        to_plane_matrices.append(to_plane)
        axis_x = trans.transform(axis_x, to_origin)
        axis_y = trans.transform(axis_y, to_origin)
        axis_z = trans.transform(axis_z, to_origin)

        # look into x rotation
        vector_on_yz = vector.project_on_yzplane(axis_y)
        if vector_on_yz.length != 0:
            angle = vector.angle_2_vectors(Vector(0,1,0), vector_on_yz)
        else:
            vector_on_yz = vector.project_on_yzplane(axis_z)
            angle = vector.angle_2_vectors(Vector(0,0,1), vector_on_yz)
        quarter = vector.quarter_on_plane(vector_on_yz, 'yz')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_x(angle)
        to_plane = matrix.rotation_x(-angle)
        to_origin_matrices.insert(0,to_origin)
        to_plane_matrices.append(to_plane)
        axis_x = trans.transform(axis_x, to_origin)
        axis_y = trans.transform(axis_y, to_origin)
        axis_z = trans.transform(axis_z, to_origin)

        # look into y rotation
        vector_on_xz = vector.project_on_xzplane(axis_z)
        if vector_on_xz.length != 0:
            angle = vector.angle_2_vectors(Vector(0,0,1), vector_on_xz)
        else:
            vector_on_xz = vector.project_on_xzplane(axis_x)
            angle = vector.angle_2_vectors(Vector(1,0,0), vector_on_xz)
        quarter = vector.quarter_on_plane(vector_on_xz, 'xz')
        if quarter == 0 or quarter == 1:
            angle = -angle
        to_origin = matrix.rotation_y(angle)
        to_plane = matrix.rotation_y(-angle)
        to_origin_matrices.insert(0, to_origin)
        to_plane_matrices.append(to_plane)

        # all matrices collected
        to_origin_matrix = matrix.combine_matrix(*to_origin_matrices)
        to_plane_matrix = matrix.combine_matrix(*to_plane_matrices)

        return to_origin_matrix, to_plane_matrix

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
    def scale(x,y,z):
        return Matrix(x,0,0,0,
                      0,y,0,0,
                      0,0,z,0,
                      0,0,0,1)

    @staticmethod
    def rotation_vector(vec:Vector, angle:Number, degree=False):
        raise

    @staticmethod
    def transform(matrix: Matrix, geometry):
        pass

    @staticmethod
    def transformation_2_planes(from_plane: Plane, to_plane: Plane):
        if not isinstance(from_plane, Plane) or not isinstance(to_plane, Plane):
            raise TypeError
        exit()

    @staticmethod
    def combine_matrix(*mat):
        result = np.eye(4)
        for m in reversed(mat):
            x = m.raw.copy()
            result = x.dot(result)
        return Matrix.from_raw(result)

class plane:
    @staticmethod
    def relocate(pla:Plane, new_origin:Point) -> Plane:
        new_raw = pla.raw.copy()
        new_raw[:3, 0] = new_origin.xyz
        return Plane.from_raw(new_raw)

    @staticmethod
    def decon(pla:Plane) -> (Point, Vector, Vector, Vector):
        return Point(*pla.raw[:3,0]), Vector(*pla.raw[:3, 1]),Vector(*pla.raw[:3, 2]),Vector(*pla.raw[:3, 3])

    @staticmethod
    def con_from_2_vectors(axis1: Vector, axis2: Vector, axis1_hint: str, axis2_hint: str, origin:Point):

        """
        Build a plane from given two axis.
        If given axes are not perpendicular axis2 will be transformed to make it correct as axis2_hint.

        :param origin: origin of the new plane
        :param axis1: first axis of the plane
        :param axis2: second axis of the plane
        :param axis1_hint: one of ('x','y','z')
        :param axis2_hint: one of ('x','y','z')
        :return: plane
        """
        # check perpendicularity and if not build new axis2
        if not np.isclose(vector.dot(axis1, axis2), 0.0, atol=DEF_TOLERANCE):
            p = point.con_from_vector(axis2)
            p_on_v = point.perpendicular_on_vector(axis1, p)
            axis2 = vector.con_two_points(p_on_v, p)
        # make a set
        axis = {'x':None, 'y':None, 'z':None}
        axis[axis1_hint] = axis1
        axis[axis2_hint] = axis2

        matrices_origin_to_plane = [matrix.translation(vector.con_from_point(origin))]
        if axis['x'] != None:
            # if axis is given need to match to origin's axis
            # determine by rotating which origin axis y or z
            # TODO what to do with tolarence
            # if np.isclose(v.z,0.0,atol=TOLERANCE):
            if not np.isclose(axis['x'].z,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around y axis
                projected = vector.project_on_xzplane(axis['x'])
                q = vector.quarter_on_plane(projected,'xz')
                angle = vector.angle_2_vectors(Vector(1,0,0), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_y(angle)
                to_plane = matrix.rotation_y(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
            if not np.isclose(axis['x'].y,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around z axis
                projected = vector.project_on_xyplane(axis['x'])
                q = vector.quarter_on_plane(projected, 'xy')
                angle = vector.angle_2_vectors(Vector(1,0,0), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_z(angle)
                to_plane = matrix.rotation_z(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)

        if axis['y'] != None:
            if not np.isclose(axis['y'].z,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around x axis
                projected = vector.project_on_yzplane(axis['y'])
                q = vector.quarter_on_plane(projected, 'yz')
                angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_x(angle)
                to_plane = matrix.rotation_x(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
            if not np.isclose(axis['y'].x,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around z axis
                projected = vector.project_on_xyplane(axis['y'])
                q = vector.quarter_on_plane(projected, 'xy')
                angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_z(angle)
                to_plane = matrix.rotation_z(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)

        if axis['z'] != None:
            # if axis is given need to match to origin's axis
            # determine by rotating which origin axis y or z
            # TODO what to do with tolarence
            # if np.isclose(v.z,0.0,atol=TOLERANCE):
            if not np.isclose(axis['z'].y,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around y axis
                projected = vector.project_on_yzplane(axis['z'])
                q = vector.quarter_on_plane(projected, 'yz')
                angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_x(angle)
                to_plane = matrix.rotation_x(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
            if not np.isclose(axis['z'].x,0.0,atol=DEF_TOLERANCE):
                # there is a value to rotate around z axis
                projected = vector.project_on_xzplane(axis['z'])
                q = vector.quarter_on_plane(projected, 'xz')
                angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
                if q == 0 or q == 1:
                    angle = -angle
                to_origin = matrix.rotation_y(angle)
                to_plane = matrix.rotation_y(-angle)
                matrices_origin_to_plane.append(to_plane)
                axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
                axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)

        default_plane = Plane([0,0,0],[1,0,0],[0,1,0],[0,0,1])
        default_plane = trans.transform(default_plane, *matrices_origin_to_plane)
        return default_plane

    @staticmethod
    def con_vector_point(axis: Vector, poi: Point, axis_hint: str, point_hint: str, origin: Point = Point(0, 0, 0)):
        projected_point = point.perpendicular_on_vector(axis, poi)
        perpen_v = vector.con_two_points(projected_point, poi)
        # and build a reference plane
        ref_plane = plane.con_from_2_vectors(axis, perpen_v, axis_hint, point_hint, origin)
        return ref_plane

    @staticmethod
    def con_3_vectors(x_axis: Vector, y_axis: Vector, z_axis: Vector, origin: Point = Point(0, 0, 0)):
        if not all([isinstance(i, Vector) for i in (x_axis, y_axis, z_axis)]):
            raise TypeError

        return Plane(origin.xyz, x_axis.xyz, y_axis.xyz, z_axis.xyz)

class rectangle:
    @staticmethod
    def con_center_width_height(plane:(Plane,Point), width:Numbfer, height:Number) -> Rectangle:
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

