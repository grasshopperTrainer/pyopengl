from .primitives import *
from .constants import *


class intersection:
    @staticmethod
    def line_line(line1:Line, line2:Line):
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
        directional1 = vector.con_from_line(line1)
        directional2 = vector.con_from_line(line2)
        if vector.compare_parallel(directional1, directional2):

            #1
            if line.coinside(line1,line2) or line.coinside(line1, line.flipped(line2)):
                return Line(a.xyz, b.xyz)
            #2
            elif point.is_on_line(line1,c):
                if point.is_on_line(line1, d):
                    return Line(c.xyz, d.xyz)
                elif d.xyz[0] <= a.xyz[0]:
                    return Line(a.xyz, c.xyz)
                elif d.xyz[0] >= b.xyz[0]:
                    return Line(c.xyz, b.xyz)

            elif point.is_on_line(line1, d):
                if point.is_on_line(line1, c):
                    return Line(c.xyz, d.xyz)
                elif c.xyz[0] <= a.xyz[0]:
                    return Line(a.xyz, d.xyz)
                elif c.xyz[0] >= b.xyz[0]:
                    return Line(d.xyz, b.xyz)
        else:
            #3 is merged with #4
            # TODO 4 vector method? need to understand this more fluently
            cross_two_directional = vector.cross(directional2,directional1)
            if cross_two_directional.length == 0:
                return None
            else:
                cross = vector.cross(directional2,vector.con_two_points(a,c))
                r = cross.length / cross_two_directional.length
                u = directional1*r
                if vector.compare_parallel(cross, cross_two_directional) == 1:
                    return a+u
                else:
                    return a-u


class tests:
    @staticmethod
    def triangulatioin(pol:Polyline):
        raw = pol.raw
        # gonna find all points on y axis
        sorted_by_x = sorted(raw[0])
        x_min = sorted_by_x[0]
        x_max = sorted_by_x[-1]
        line_length = x_max-x_min + 2
        crossing_lines = []
        for i in set(raw[1]):
            crossing_lines.append(line.con_point_vector(Point(x_min-1,i,0),Vector(line_length,0,0)))
        # prepare vertices and edges
        # vertices
        vertices = polyline.points(pol)
        sorted_vertices = point.sort(vertices, 'y')
        # do i need to remove duplicated
        sorted_vertices = point.unique_points(sorted_vertices)
        # edges
        edges = polyline.edges(pol)
        for e in edges:
            # organize so all edges head right_up corner
            if e.start[1] > e.end[1]:
                # make so start of all edges are downward
                e.flip()
            elif e.start[1] == e.end[1]:
                if e.start[0] > e.end[0]:
                    e.flip()
        edges_to_look_for = edges.copy()

        # do tripezoidal, triangulatioin seperately
        # there are three steps

        # trapezoidal Decomposition
        horizontals = []
        verticals = []
        trapezoid = []
        for c_line in crossing_lines:
            print()
            print('c_line', c_line.vertex)
            print(horizontals)
            intersections = []
            segments = []
            to_remove = []
            for e in edges_to_look_for:
                y = c_line.start[1]
                if e.start[1] == y:
                    print(' c_line touching start of line', e.vertex)
                    intersections.append(Point(*e.start))
                elif e.start[1] < y and e.end[1] > y:
                    print(' c_line crossing middle of a line', e.vertex)
                    ip = intersection.line_line(c_line, e)
                    intersections.append(ip)
                    verticals.append(Line(e.start,ip.xyz))
                    segments.append(Line(ip.xyz, e.end))
                    to_remove.append(e)
                elif e.end[1] == y:
                    print(' c_line touching end of line',e.vertex)
                    intersections.append(Point(*e.end))
                    verticals.append(e)
                    to_remove.append(e)
                elif e.end[1] < y:
                    # this is exactly for horizontal that was on a previous p_line so discarded
                    print(' c_line is above line',e.vertex)
                    horizontals.append(e)
                    to_remove.append(e)

            print('horizontal boundaries')
            for i in horizontals:
                print(i.vertex)
            print('vertical boundaries')
            for i in verticals:
                print(i.vertex)
            print()

            for i in to_remove:
                edges_to_look_for.remove(i)

            # sort intersections
            intersections = point.unique_points(intersections)
            intersections = point.sort(intersections, 'x')

            # initial case
            if len(horizontals)+ len(verticals) == 0:
                pass
            else:
                # before searching for shattered need to see if whole searching area is a trapezoid with segmented edges
                if len(horizontals) >= 2:
                    print('dddddddddddddddddddddddddddd')
                    bottom = polyline.con_from_lines(horizontals)
                    print(horizontals)
                    for i in horizontals:
                        print(i.vertex)
                    print(bottom)
                    if bottom != None:
                        if len(verticals) != 2:
                            pass
                        else:
                            top = polyline.con_from_points(intersections)
                            print(intersections)
                            print(point.in_points(polyline.start_end(top), line.end(verticals[0]),line.end(verticals[1])))
                            if all(point.in_points(polyline.start_end(top), line.end(verticals[0]),line.end(verticals[1]))):

                                trapezoid.append([bottom, verticals[0],verticals[1], top])
                                edges_to_look_for += segments
                                print('+++++++++++++++++')
                                print(polyline.edges(top))
                                print('+++++++++++++++++')
                                verticals = []
                                horizontals = polyline.edges(top)
                                continue
                            else:
                                pass

                horizontals_to_search = horizontals.copy()
                verticals_to_search = verticals.copy()
                for n in range(len(intersections) - 1):
                    # need to find triangle pointing up

                    vertex1, vertex2 = intersections[n], intersections[n+1]
                    print('     looking after shape of', vertex1, vertex2)
                    new_trapeziod = []

                    if len(horizontals_to_search) + len(verticals_to_search) == 0:
                        break

                    # find two verticals connected to diagonal
                    for b in verticals_to_search:
                        if point.coinside(vertex1, line.end(b)):
                            new_trapeziod.append(b)
                            break
                    for b in verticals_to_search:
                        if point.coinside(vertex2, line.end(b)):
                            new_trapeziod.append(b)
                            break

                    # if two are found
                    if len(new_trapeziod) == 2:
                        verticals_to_search.remove(new_trapeziod[0])
                        verticals_to_search.remove(new_trapeziod[1])

                        s,e = line.start(new_trapeziod[0]), line.start(new_trapeziod[1])

                        if point.coinside(s, e):
                            # if starting points coinside -> it's a triangle
                            pass
                        else:
                            # if trepazoid
                            searching_line = line.con_two_points(s,e)
                            print(s,e)
                            for b in horizontals_to_search:
                                if line.coinside(b,searching_line):
                                    print('     third',b)
                                    # bottom boundary takes i=0
                                    new_trapeziod.insert(0,b)
                                    horizontals_to_search.remove(b)
                                    break

                            if len(new_trapeziod) != 3:
                                # means diagonal is useless so move to next
                                continue

                        for i in new_trapeziod:
                            try:
                                horizontals.remove(i)
                            except:
                                print(i.vertex)
                                for ii in horizontals:
                                    print(ii.vertex)
                                for ii in verticals:
                                    print(ii.vertex)

                                verticals.remove(i)

                        diagonal = line.con_two_points(vertex1, vertex2)
                        new_trapeziod.append(diagonal)
                        trapezoid.append(new_trapeziod)
                        horizontals.append(diagonal)
                        continue

                    else:
                        # if diagonal is not connected at least to two boundaries
                        # this diagonal is useless
                        continue

            # for searching intersecting wiwh c_line
            edges_to_look_for += segments

            print('---------trapeziod--------')
            for i in trapezoid:
                print(i)
            # print(intersections)

        # monotone Subdivision

        # triangulation



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
    def start(lin:Line) -> Point:
        return Point(*lin.start)

    @staticmethod
    def end(lin:Line) -> Point:
        return Point(*lin.end)

    @staticmethod
    def decon(lin:Line):
        return [Point(*lin.raw.copy()[:3, 0]), Point(*lin.raw.copy()[:3, 1])]

    @staticmethod
    def has_vertex(lin:Line, poi:Point):
        start, end = lin.vertex
        coord = poi.xyz
        if all([a==b for a,b in zip(start,coord)]) or all([a==b for a,b in zip(end, coord)]):
            return True
        return False

    @staticmethod
    def middle(line:Line):
        coord = []
        for a,b in line.vertex:
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



class polyline:
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

    @staticmethod
    def con_any_from_lines():
        pass

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
                lines.remove(l)

            if len(lines) == 0:
                break

        return polyline.con_from_points(sorted_vertex)

    @staticmethod
    def con_from_points(points_list:(tuple, list)) -> Polyline:
        if not isinstance(points_list,(tuple, list)):
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
    def point_in(pol:Polyline, point:Point):
        pass


    @staticmethod
    def decon(pol:Polyline) -> list:
        """
        deconstructs polyline into points and lines
        :param pol:
        :return: [list of points, list of lines]
        """
        coords = pol.raw[:3].transpose().tolist()
        points = []
        for i in coords:
            points.append(Point(*i))

        lines = []
        for i in range(len(points)-1):
            lines.append(line.con_two_points(points[i], points[i+1]))

        return [points, lines]

    @staticmethod
    def points(pol: Polyline):
        coords = pol.raw[:3].transpose().tolist()
        points = []
        for i in coords:
            points.append(Point(*i))
        return points

    @staticmethod
    def edges(pol:Polyline):
        lines = []
        points = polyline.points(pol)
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


class point:
    @staticmethod
    def in_points(cloud:(tuple, list), *points:Point):
        mask = []
        for p in points:
            co = False
            for i in cloud:
                if point.coinside(p, i):
                    co = True
                    break
            mask.append(co)
        return mask

    @staticmethod
    def unique_points(points:(list, tuple)):
        unique_points = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError

            unique = True
            for i in unique_points:
                # if there is one that has same coordinate value don't add
                # if all is looked and there's isn't one coinside then add
                coinsides = True
                for a,b in zip(i.xyz, p.xyz):
                    # if any component is different go to next
                    if a != b:
                        coinsides = False
                        break
                # for all components equal inspecting point is not unique
                if coinsides:
                    unique = False
                    break
                else:
                    continue

            if unique:
                unique_points.append(p)
            else:
                continue
        return unique_points

    @staticmethod
    def coinside(point1:Point, point2:Point, atol=None) -> bool:
        if atol != None:
            raise
        else:
            return all(np.equal(point1.raw, point2.raw))

    @staticmethod
    def sort(points, mask:str = 'x'):
        """
        sort points by given ingredient

        :param mask: key to sort with, one of 'x','y','z'
        :param points: points to sort
        :return: sorted list of points
        """
        mask_index = {'x':0,'y':1,'z':2}
        if not mask in mask_index:
            raise ValueError
        if not all([isinstance(p, Point) for p in points]):

            raise TypeError

        keys = []
        i = mask_index[mask]
        for p in points:
            keys.append(p.xyz[i])
        sorted_list = sorted(zip(keys, points),key=lambda x: x[0])

        points = [i[1] for i in sorted_list]
        return points

    @staticmethod
    def sort_chunck():
        pass

    @staticmethod
    def equal(point1:Point, point2:Point) -> bool:
        if not isinstance(point1, Point) or not isinstance(point2, Point):
            return TypeError
        for a,b in zip(point1.xyz, point2.xyz):
            if not np.isclose(a,b, atol=DEF_TOLERANCE):
                return False
        return True

    @staticmethod
    def is_on_line(lin:Line, *points:(tuple, list)) -> bool:
        results = []
        directional1 = vector.con_from_line(lin)
        for poi in points:
            if not isinstance(poi, Point):
                raise TypeError

            directional2 = vector.con_two_points(Point(*lin.start), poi)
            if vector.compare_parallel(directional1,directional2):
                start, end = lin.start, lin.end
                x,_,_ = poi.xyz
                if x >= start[0] and x<=end[0]:
                    results.append(True)
                else:
                    results.append(False)
            else:
                results.append(False)

        if len(results) == 1:
            return results[0]
        return results

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
    def cross(vec1:Vector, vec2:Vector) -> Vector:
        if not isinstance(vec1, Vector) or not isinstance(vec2, Vector):
            raise TypeError
        cross = np.cross(vec1.raw[:3,0], vec2.raw[:3,0])
        return Vector(*cross)

    @staticmethod
    def compare_parallel(vec1:Vector, vec2:Vector) -> int:
        """
        definition of return value
        -1 opposite direction
        0 non-parallel
        +1 same direction

        :param vec1:
        :param vec2:
        :return:
        """
        xyz1 = vec1.xyz
        xyz2 = vec2.xyz
        scalars = []
        # if both comparint is 0 -> no effect
        # if one of two is 0 -> non-parallel
        for a,b in zip(xyz1, xyz2):
            zeros = sum([k == 0 for k in (a,b)])
            if zeros == 0:
                scalars.append(a/b)
            elif zeros == 1:
                return 0
            elif zeros == 2:
                pass

        for s in scalars:
            if s != scalars[0]:
                return 0
        if scalars[0] == 0:
            return 0
        elif scalars[0] > 0:
            return 1
        elif scalars[0] < 0:
            return -1

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

    # @staticmethod
    # def multiply(vector:Vector, v, ):
    #     if raw:
    #         return vector.raw*v
    #     else:
    #         return vector*v

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

