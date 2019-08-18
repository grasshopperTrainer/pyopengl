from .primitives import *
from .constants import *


class intersection:
    @staticmethod
    def pline_line(pol:Polyline, lin:Line):
        if not isinstance(pol, Polyline) or not isinstance(lin, Line):
            raise TypeError
        # TODO how to define plane of polyline
        if lin.vertex[0][2] != 0 or lin.vertex[1][2] != 0:
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
    def line_line(line1:Line, line2:Line, on_line=False):
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
                elif d.xyz[0] < a.xyz[0]:
                    return Line(a.xyz, c.xyz)
                elif d.xyz[0] > b.xyz[0]:
                    return Line(c.xyz, b.xyz)

            elif point.is_on_line(line2, a):
                if point.is_on_line(line2,b):
                    return Line(a.xyz, b.xyz)
                elif b.xyz[0] > d.xyz[0]:
                    return Line(a.xyz,d.xyz)
                elif b.xyz[0] < c.xyz[0]:
                    return Line(c.xyz, a.xyz)

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
                if vector.compare_parallel(cross, cross_two_directional) == 1:
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
    def triangulatioin(pol:Polyline):
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
            print('crossing line:', c_line.vertex)
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
                    condition1 = polyline.point_in(pol, middle_p) == 1 # condition1; not on but in
                    condition2 = False # condition2; at least one vertex is a part of the segment
                    print('dddddddddddddd', vs)
                    for v in vs:
                        print(v, p_inter[i], p_inter[i+1])
                        if point.coinside(v, p_inter[i]) or point.coinside(v, p_inter[i+1]):
                            condition2 = True
                            break
                    print('     conditions ', condition1, condition2)
                    print('     ', v, p_inter[i], p_inter[i+1])
                    print('     ', point.coinside(v, p_inter[i]) or point.coinside(v, p_inter[i+1]))
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
                for v in vs:
                    for i in segments_vertex:
                        if point.coinside(i,v):
                            to_remove.append(v)
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
                            print('     appending down', down.vertex)
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
                            print(e.vertex)
                            print('kkk',has)
                            if has:
                                v_next = line.decon(e)[has[1]-1]
                                new_vec_trace = vector.con_2_points(trace, v_next)
                                # anti clockwise condition
                                side,angle = vector.left_right_halfspace(vec_trace, new_vec_trace)
                                if math.one_of(side, 0,2):
                                    building_trapeziod.append(e)
                                    trace = v_next
                                    vec_trace = new_vec_trace
                                    e_under.remove(e)
                                    flag_found = True
                                    break

                        if not flag_found:
                            # seen through all edges but couldn't find one
                            # -> something is wrong
                            print(s.vertex)
                            print(building_trapeziod)
                            raise
                        # if shape is closed
                        if point.coinside(trace, line.end(s)):
                            # replace colinear edges to pline and organize
                            left = building_trapeziod.pop(1)
                            keys = [line.middle(l).y for l in building_trapeziod]
                            building_trapeziod = data.sublist_by_unique_key(building_trapeziod, keys)
                            building_trapeziod = sorted(building_trapeziod.items(), key = lambda x:x[0])
                            for i, (v,l) in enumerate(building_trapeziod):
                                if len(l) != 1:
                                    building_trapeziod[i] = polyline.con_from_lines(l)
                                else:
                                    building_trapeziod[i] = l[0]
                            building_trapeziod.insert(0,left)
                            # index 0 is alway top and goes clockwise
                            building_trapeziod = data.shift(building_trapeziod, -1)
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
                    for v in vs:
                        if point.coinside(v, s):
                            mark.append(v)
                            break
                    for v in vs:
                        if point.coinside(v, e):
                            mark.append(v)
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
                    vertex = line.start(building_peak[0]), line.start(building_peak[1])
                    for e in e_under:
                        print(e.vertex,point.is_on_line(e,*vertex))
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
                    vec_trace = vector.con_from_line(b).flip()
                    while True:
                        flag_found = False
                        # next edge is always the side of trapeziod
                        # but next can have multiple edges connected to the end of previous
                        candidates = []
                        print(e_under)
                        for e in e_under:
                            has = line.has_vertex(e, trace)
                            print(e.vertex, has, trace)
                            if has:
                                next_trace = line.decon(e)[has[1]-1]
                                directional = vector.con_2_points(trace, next_trace)
                                side, angle = vector.left_right_halfspace(vec_trace, directional)
                                print(side, math.one_of(side, 0,2))
                                if math.one_of(side, 0,2):
                                    candidates.append((angle,directional,e,next_trace))
                                    flag_found = True
                                    print('ddddddd', candidates)
                        print('ddddddd', candidates)
                        if not flag_found:
                            print(e_under[0].vertex)
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

        # monotone Subdivision
        # basic tactic is to read stack and see if any of monotonal adjustant with bottom of inspected
        # another thing to check is parallelity of sides.
        # if any polyline is seen then this needs self division


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
        if not isinstance(lin,Line):
            raise TypeError(f'given input type is {type(lin)}. Line type required')

        return [Point(*lin.raw.copy()[:3, 0]), Point(*lin.raw.copy()[:3, 1])]

    @staticmethod
    def has_vertex(lin:Line, poi:Point):
        start, end = lin.vertex
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
        for a,b in zip(*lin.vertex):
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
    def point_in(pol:Polyline, poi:Point):
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
        if not isinstance(pol, Polyline) or not isinstance(poi, Point):
            raise TypeError
        if not polyline.is_closed(pol):
            return None

        edges,vertices = polyline.decon(pol)

        # see point on polyline
        for e in edges:
            if poi.x == 7 and poi.y == 7:
                print(e.vertex, point.is_on_line(e,poi))
            if point.is_on_line(e, poi):
                return 2

        # see point in out polyline
        x_max = sorted(set(pol.raw[0]))[-1]
        end_point = Point(*poi.xyz)
        end_point.x = x_max+1

        c_line = line.con_two_points(poi, end_point)
        iter_count = 0

        while True:
            flag_break = True
            # if can't find the case something is wrong
            if iter_count == 100:
                raise

            # see if crossing is valid
            inter = intersection.pline_line(pol, c_line)
            for i in inter:
                if isinstance(i, Line) or any(point.in_points(vertices, *inter)):
                    # if any of crossing is a vertex it can be a peak so find crossing again
                    flag_break = False
                    break

            if flag_break:
                break
            else:
                # do crossing test with modified c_line
                c_line.raw[1,1] += 1
                iter_count += 1

        # # check peaks
        # if len(inter) != 0:
        #     mask = point.in_points(cloud, *inter)
        #     inter = data.cull_pattern(inter, mask, flip_mask=True)

        # count intersection
        if len(inter)%2 == 0:
            return 0
        else:
            return 1

    @staticmethod
    def decon(pol:Polyline) -> list:
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
    def vertices(pol: Polyline):
        coords = pol.raw[:3].transpose().tolist()
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


class point:
    @staticmethod
    def xyz(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.xyz)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def x(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis. append(p.x)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def y(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.y)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def z(*points):
        lis = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError
            lis.append(p.z)
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def in_points(cloud:(tuple, list), *points:Point):
        mask = []
        if len(points) == 0:
            raise

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
        """
        leave only unique points
        :param points:
        :return: [ [unique_points], [uniqueness index of all input] ]
        """
        # what index? index of uniqueness?
        unique_points = []
        unique_index = []
        for p in points:
            if not isinstance(p, Point):
                raise TypeError

            unique = True
            for i,up in enumerate(unique_points):
                # if there is one that has same coordinate value don't add
                # if all is looked and there's isn't one coinside then add
                coinsides = True
                for a,b in zip(up.xyz, p.xyz):
                    # if any component is different go to next
                    if a != b:
                        coinsides = False
                        break
                # for all components equal inspecting point is not unique
                if coinsides:
                    unique = False
                    unique_index.append(i)
                    break
                else:
                    unique_index.append(len(unique_points))
                    continue

            if unique:
                unique_points.append(p)
            else:
                continue
        return [unique_points, unique_index]

    @staticmethod
    def coinside(point1:Point, point2:Point, atol=None) -> bool:
        if atol != None:
            raise
        else:
            return all(np.equal(point1.raw, point2.raw).flatten())

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

            if line.has_vertex(lin,poi):
                results.append(True)
                continue

            directional2 = vector.con_2_points(Point(*lin.start), poi)
            if vector.compare_parallel(directional1,directional2):
                vertex = [lin.start[0], lin.end[0]]
                vertex = sorted(vertex)
                x = poi.x
                print(x,vertex)
                if x >= vertex[0] and x <= vertex[1]:
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
        vec2 = vector.con_point(poi)
        a = vector.angle_2_vectors(vec, vec2)
        l = np.cos(a) * vec2.length
        new_v = vector.amplitude(vec, l)
        return point.con_from_vector(new_v)

    @staticmethod
    def average(points:(list, tuple)) -> Point:
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
    def one_of(compared, *values):
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
        np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def cos(v):
        np.cos(v,dtype=DEF_FLOAT_FORMAT)
    @staticmethod
    def tan(v):
        np.tan(v,dtype=DEF_FLOAT_FORMAT)

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

class vector:
    # @staticmethod
    # def clockwise(vec_reference:Vector, vec_target:Vector, pla:Plane = Plane()) -> bool:
    #     pass


    @staticmethod
    def left_right_halfspace(vec_reference:Vector, vec_target:Vector, pla:Plane= Plane()) -> int:
        """
        identifies whether vector is on the left or right half space
        :param vec_reference:
        :param vec_target:
        :param pla:
        :return: [ left_right_sign, angle_to_left_right ]
        """
        quarter = vector.quarter_plane(vec_reference, pla=pla)
        ref_angle = vector.angle_plane(vec_reference,pla=pla)
        target_angle = vector.angle_plane(vec_target, pla=pla)

        if np.isclose(target_angle, ref_angle, atol=DEF_TOLERANCE):
            return [2, 0]
        else:
            if quarter == 0:
                if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
                    return [0,target_angle - ref_angle]
                elif target_angle < ref_angle:
                    return [1, ref_angle - target_angle]
                else:
                    return [1, ref_angle - (target_angle - tri.pi2)]
            elif quarter == 1:
                if np.isclose(target_angle, ref_angle + tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle and target_angle < ref_angle + tri.pi:
                    return [0, target_angle - ref_angle]
                elif target_angle < ref_angle:
                    return [1, ref_angle - target_angle]
                else:
                    return [1, target_angle - (ref_angle + tri.pi)]
            elif quarter == 2:
                if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle > ref_angle -tri.pi and target_angle < ref_angle:
                    return [1, ref_angle - target_angle]
                elif target_angle < ref_angle - tri.pi:
                    return [0, ref_angle - tri.pi - target_angle]
                else:
                    return [0, target_angle - ref_angle]
            elif quarter == 3:
                if np.isclose(target_angle, ref_angle - tri.pi, atol=DEF_TOLERANCE):
                    return [3, tri.pi]
                elif target_angle < ref_angle and target_angle > ref_angle - tri.pi:
                    return [1, ref_angle - target_angle]
                elif target_angle > ref_angle:
                    return [0, target_angle - ref_angle]
                else:
                    return [0, ref_angle - tri.pi - target_angle]


    @staticmethod
    def project_on_another(vec_projected_on:Vector, vec_projecting:Vector) -> Vector:
        u1,u2 = vector.unit(vec_projected_on), vector.unit(vec_projecting)
        cos_v = vector.dot(u1,u2)
        projected = vector.amplitude(vec_projected_on, cos_v * vector.length(vec_projecting))
        return projected

    @staticmethod
    def length(vec:Vector) -> float:
        x,y,z = vec.xyz
        return np.sqrt(x*x + y*y + z*z)

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
        cos_v = vector.angle_2_vectors(vec1, vec2)
        if cos_v == None:
            return None
        else:
            if np.isclose(cos_v, 0, atol=DEF_TOLERANCE):
                return 1
            elif np.isclose(cos_v, np.pi, atol=DEF_TOLERANCE):
                return -1
            else:
                return 0

    @staticmethod
    def con_2_points(start:Point, end:Point) -> Vector:
        coord = []
        for a,b in zip(start.xyz, end.xyz):
            coord.append(b-a)
        return Vector(*coord)

    @staticmethod
    def quarter_plane(vec:Vector, pla:Plane = Plane()) -> int:
        angle = vector.angle_plane(vec,pla)
        if angle >= 0 and angle <= np.pi/2:
            return 0
        elif angle > np.pi/2 and angle <= np.pi:
            return 1
        elif angle > np.pi and angle <= np.pi*1.5:
            return 2
        else:
            return 3

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
    def con_point(poi:Point):
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
            raise WrongInputTypeError(Vector, vec)
        if vec.length == 0:
            return None
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

    @staticmethod
    def flip(vector:Vector):
        if not isinstance(vector, Vector):
            raise TypeError
        return Vector().from_raw(vector.raw*[[-1],[-1],[-1],[0]])

    @staticmethod
    def angle_2_vectors(from_vector, to_vector, degree=False):
        u1,u2 = vector.unit(from_vector), vector.unit(to_vector)
        if any([i==None for i in (u1,u2)]):
            return None
        cos_value = u1.raw.flatten().dot(u2.raw.flatten())
        angle = tri.arccos(cos_value)
        if degree:
            return tri.radian_degree(angle)
        else:
            return angle

    @staticmethod
    def angle_plane(vec:Vector, pla:Plane, degree:bool=False) -> Number:
        if not isinstance(vec,Vector):
            raise WrongInputTypeError(Vector, vec)
        if not isinstance(pla, Plane):
            raise WrongInputTypeError(Plane, pla)
        if not isinstance(degree, bool):
            raise WrongInputTypeError(bool, degree)

        o,x,y,z = plane.decon(pla)
        vec = vector.unit(vec)
        cos_value1, cos_value2 = vector.dot(x,vec), vector.dot(y,vec)
        if cos_value1 >= 0:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi*2 - tri.arccos(cos_value1)
        else:
            if cos_value2 >= 0:
                angle = tri.arccos(cos_value1)
            else:
                angle = np.pi*2 - tri.arccos(cos_value1)
        print(angle)
        if degree:
            return tri.radian_degree(angle)
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
        to_plane_vector = vector.con_point(origin)
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
        matrix = np.eye(4)
        if degrees:
            angle = np.radians(angle)
        matrix[0] = tri.cos(angle), -tri.sin(angle), 0, 0
        matrix[1] = tri.sin(angle), tri.cos(angle), 0, 0
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
    def decon(pla:Plane) -> [Point, Vector, Vector, Vector]:
        """
        deconstruct plane
        returns origin, vector-x, vector-y, vectorz-z
        :param pla: plane to deconstruct
        :return: [ Point, Vector, Vector, Vector ]
        """
        return [Point(*pla.raw[:3,0]), Vector(*pla.raw[:3, 1]),Vector(*pla.raw[:3, 2]),Vector(*pla.raw[:3, 3])]

    @staticmethod
    def con_2_vectors(axis1: Vector, axis2: Vector, axis1_hint: str, axis2_hint: str, origin:Point):

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
        projected = vector.project_on_another(axis1, axis2)
        axis2 = vector.con_2_points(point.con_from_vector(projected), point.con_from_vector(axis2))
        axis3 = vector.cross(axis1, axis2)

        axis_dic = {'x':None,'y':None,'z':None}
        axis_dic[axis1_hint] = axis1
        axis_dic[axis2_hint] = axis2
        for i in axis_dic:
            if i == None:
                axis_dic[i] = axis3

        if any([i is None for i in axis_dic.values()]):
            raise
        return plane.con_3_vectors(*axis_dic.value(),origin)

        # # check perpendicularity and if not build new axis2
        # if not np.isclose(vector.dot(axis1, axis2), 0.0, atol=DEF_TOLERANCE):
        #     p = point.con_from_vector(axis2)
        #     p_on_v = point.perpendicular_on_vector(axis1, p)
        #     axis2 = vector.con_2_points(p_on_v, p)
        # # make a set
        # axis = {'x':None, 'y':None, 'z':None}
        # axis[axis1_hint] = axis1
        # axis[axis2_hint] = axis2
        #
        # matrices_origin_to_plane = [matrix.translation(vector.con_from_point(origin))]
        # if axis['x'] != None:
        #     # if axis is given need to match to origin's axis
        #     # determine by rotating which origin axis y or z
        #     # TODO what to do with tolarence
        #     # if np.isclose(v.z,0.0,atol=TOLERANCE):
        #     if not np.isclose(axis['x'].z,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around y axis
        #         projected = vector.project_on_xzplane(axis['x'])
        #         q = vector.quarter_on_plane(projected,'xz')
        #         angle = vector.angle_2_vectors(Vector(1,0,0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_y(angle)
        #         to_plane = matrix.rotation_y(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['x'].y,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xyplane(axis['x'])
        #         q = vector.quarter_on_plane(projected, 'xy')
        #         angle = vector.angle_2_vectors(Vector(1,0,0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_z(angle)
        #         to_plane = matrix.rotation_z(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # if axis['y'] != None:
        #     if not np.isclose(axis['y'].z,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around x axis
        #         projected = vector.project_on_yzplane(axis['y'])
        #         q = vector.quarter_on_plane(projected, 'yz')
        #         angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_x(angle)
        #         to_plane = matrix.rotation_x(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['y'].x,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xyplane(axis['y'])
        #         q = vector.quarter_on_plane(projected, 'xy')
        #         angle = vector.angle_2_vectors(Vector(0, 1, 0), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_z(angle)
        #         to_plane = matrix.rotation_z(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # if axis['z'] != None:
        #     # if axis is given need to match to origin's axis
        #     # determine by rotating which origin axis y or z
        #     # TODO what to do with tolarence
        #     # if np.isclose(v.z,0.0,atol=TOLERANCE):
        #     if not np.isclose(axis['z'].y,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around y axis
        #         projected = vector.project_on_yzplane(axis['z'])
        #         q = vector.quarter_on_plane(projected, 'yz')
        #         angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_x(angle)
        #         to_plane = matrix.rotation_x(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #     if not np.isclose(axis['z'].x,0.0,atol=DEF_TOLERANCE):
        #         # there is a value to rotate around z axis
        #         projected = vector.project_on_xzplane(axis['z'])
        #         q = vector.quarter_on_plane(projected, 'xz')
        #         angle = vector.angle_2_vectors(Vector(0, 0, 1), projected)
        #         if q == 0 or q == 1:
        #             angle = -angle
        #         to_origin = matrix.rotation_y(angle)
        #         to_plane = matrix.rotation_y(-angle)
        #         matrices_origin_to_plane.append(to_plane)
        #         axis[axis1_hint] = trans.transform(axis[axis1_hint], to_origin)
        #         axis[axis2_hint] = trans.transform(axis[axis2_hint], to_origin)
        #
        # default_plane = Plane([0,0,0],[1,0,0],[0,1,0],[0,0,1])
        # default_plane = trans.transform(default_plane, *matrices_origin_to_plane)
        # return default_plane

    @staticmethod
    def con_vector_point(axis: Vector, poi: Point, axis_hint: str, point_hint: str, origin: Point = Point(0, 0, 0)):
        projected_point = point.perpendicular_on_vector(axis, poi)
        perpen_v = vector.con_2_points(projected_point, poi)
        # and build a reference plane
        ref_plane = plane.con_2_vectors(axis, perpen_v, axis_hint, point_hint, origin)
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

