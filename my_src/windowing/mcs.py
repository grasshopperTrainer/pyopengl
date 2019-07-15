import weakref
import numpy as np


class WeakOrderedSet:
    def __init__(self):
        self._collection = []
        self._iter_count = 0

    def add(self, v):
        if v not in self._collection:
            self._collection.append(weakref.ref(v))

    def remove(self, index_or_item):
        if isinstance(index_or_item, int):
            self._collection.pop(index_or_item)

        elif isinstance(index_or_item, weakref.ReferenceType):
            if index_or_item in self._collection:
                self._collection.remove(index_or_item)
            else:
                raise KeyError
        else:
            try:
                weaked = weakref.ref(index_or_item)
                if weaked in self._collection:
                    self._collection.remove(weaked)
            except:
                raise

    def __getitem__(self, item):
        # # claen dead
        # dead = []
        # for i in self._collection:
        #     if i() is None:
        #         dead.append(i)
        # for i in dead:
        #     self._collection.remove(i)

        if isinstance(item, int):
            if len(self._collection) > item:
                return self._collection[item]()
    def __iter__(self):
        return self

    def __next__(self):
        # return only alive
        while True:
            if len(self._collection) > self._iter_count:
                candidate = self._collection[self._iter_count]()
                self._iter_count += 1
                if candidate != None:
                    return candidate
            else:
                self._iter_count = 0
                raise StopIteration

    def __len__(self):
        return len(self._collection)
    def pop(self):
        return self._collection.pop()()
    def __add__(self, other):
        if not isinstance(other, (list, tuple)):
            raise
        for i in other:
            self.add(i)
        return self


class Family_Tree:
    def __init__(self, master):
        self._tree = WeakOrderedSet()
        self._tree = {master:{}}
    def get_branch_under(self,origin):
        # need to search for branch first
        # {mother: {child:{} , child: {}, child: {chi, TARGET}}, brother: {chi:{}}, sis: {chi:{},chi:{}}}
        let_break = False
        branch = [self._tree, ]
        while True:
            subs = []
            for dic in branch:
                if origin in dic:
                    branch = dic[origin]
                    let_break = True
                    break
                else:
                    for i in dic.values():
                        subs.append(i)
            if let_break:
                break
            else:
                if len(subs) == 0:
                    # if there isn't
                    raise
                    return {}
                else:
                    branch = subs
        return branch

    def children_of(self, origin):
        offspring = self.get_branch_under(origin)

        # key is mother values are children
        # {child: {}, child:{}, child: {chi:{}, chi:{}}}
        return self._flatten(offspring)

    # def siblings_of(self, origin):
    #     for i in self._tree

    def _flatten(self, branch):
        #example) {child: {}, child:{}, child: {chi:{}, chi:{}}}
        flattened = []
        for m,c in branch.items():
            flattened.append(m)
            flattened += self._flatten(c)
        return flattened

    def graft_under(self, family, origin):
        branch = self.get_branch_under(origin)
        branch.update(family._tree)
        family._tree = self._tree



class Area_definer:
    _instance_set = weakref.WeakSet()
    _rest_called = False

    def __init__(self):
        self._dict = weakref.WeakKeyDictionary()
        self._instance_set.add(self)

    def __set__(self, instance, value):
        # three ways to define coordinate value
        if not (callable(value) or isinstance(value, (int, float))):
            raise

        if instance not in self._dict:
            self._dict[instance] = None

        # set value changed only if value input value is actucally different
        if callable(value) or type(self._dict[instance]) != type(value) or self._dict[instance] != value:
            self._dict[instance] = value
            instance.make_updated_all()
        # else:
        #     self._dict[instance][1] = False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            v = self._dict[instance]
            return v


class Hollow_mother:
        pixel_x = 0
        pixel_y = 0
        pixel_w = 1
        pixel_h = 1

class MCS:
    x = Area_definer()
    y = Area_definer()
    w = Area_definer()
    h = Area_definer()

    # _vertex = Record_change_value()
    #
    # _pixel_x = Record_change_value()
    # _pixel_y = Record_change_value()
    # _pixel_w = Record_change_value()
    # _pixel_h = Record_change_value()

    def __init__(self,posx,posy,width,height):
        self._family_tree = Family_Tree(self)

        self.x = posx
        self.y = posy
        self.w = width
        self.h = height

        self._orientation_matrix = np.eye(4)

        # self._pixel_x = posx
        # self._pixel_y = posy
        # self._pixel_w = width
        # self._pixel_h = height

        self._vertex = [(),(),(),()]

        self._mother = Hollow_mother

        self._flag_update = True
    @property
    def definers(self):
        return self.x, self.y, self.w, self.h
    @definers.setter
    def definers(self, values):
        if len(values) != 4:
            raise
        self.x, self.y, self.w, self.h = values
    @property
    def size(self):
        return self.w, self.h
    @size.setter
    def size(self, v):
        if len(v) != 2:
            raise
        self.w, self.h = v

    @property
    def pixel_x(self):
        if isinstance(self.x, float):
            result = int(self.x * self.mother.pixel_w)
        elif callable(self.x):
            result = int(self.x(self.mother.pixel_w))
        else:
            result = self.x
        # print(self._mother)
        result = result + self.mother.pixel_x

        return result

    @property
    def pixel_y(self):
        if isinstance(self.y, float):
            result = int(self.y * self.mother.pixel_h)
        elif callable(self.y):
            result = int(self.y(self.mother.pixel_h))
        else:
            result = self.y

        result = result + self.mother.pixel_y

        return result

    @property
    def pixel_w(self):
        if isinstance(self.w, float):
            result = int(self.w * self.mother.pixel_w)
        elif callable(self.w):
            result = int(self.w(self.mother.pixel_w))
        else:
            result = self.w
        return result

    @property
    def pixel_h(self):
        if isinstance(self.h, float):
            result = int(self.h * self.mother.pixel_h)
        elif callable(self.h):
            result = int(self.h(self.mother.pixel_h))
        else:
            result = self.h

        return result
    @property
    def pixel_values(self):
        return self.pixel_x, self.pixel_y, self.pixel_w, self.pixel_h

    def vertex(self, *index):
        vertex_list = []
        if len(index) == 0:
            index = 0, 1, 2, 3

        # call to check change?
        # self.posx, self.posy, self.width, self.height

        # recalculate and save
        if self._flag_updated:

            x = self.pixel_x
            y = self.pixel_y
            width = self.pixel_w
            height = self.pixel_h
            print('vertex',x,y,width,height)
            new_vertex = (x, y), (x + width, y), (x + width, y + height), (x, y + height)
            self._vertex = new_vertex

            self._flag_updated = False
            #
            # print()
            #
            # print(self.x, self.y,self.w,self.h)
            # print(self.mother)
            # print(self.pixel_values)
            # print(new_vertex)
        else:
            pass

        for i in index:
            vertex_list.append(self._vertex[i])

        if len(index) == 1:
            return vertex_list[0]
        return vertex_list

    def move(self):

        pass

    def make_updated_all(self):
        self._flag_updated = True
        for child in self.children:
            child.make_updated_all()

    def is_mother_of(self, *objects):
        for child in objects:
            child.is_child_of(self)

    def is_child_of(self, mother):
        # TODO weakly storing children seems to be not working with buttons. why?
        #   that's because when creating button with 'window' window's callback stores button
        mother._family_tree.graft_under(self._family_tree,mother)
        self._flag_update = mother._flag_update

    def replace_child(self):
        pass

    @property
    def mother(self):
        if isinstance(self._mother, weakref.ReferenceType):
            if self._mother() is None:
                self._mother = Hollow_mother
                return self._mother
            else:
                return self._mother()
        else:
            return self._mother

    @property
    def children(self):
        return self._family_tree.children_of(self)

    @property
    def master(self):
        if self._mother is None:
            return self
        else:
            return self.mother
    @property
    def is_active(self):
        return self._flag_update

    def activate(self, depth=None):
        self._flag_update = True
        if depth != None:
            if depth == 0:
                return
            else:
                depth -= 1

        for child in self.children:
            child.activate(depth)

    def deactivate(self, start=None, stop=None):
        # self._flag_update = False
        if start == None and stop==None:
            pass
        else:
            # if from_to == 0:
            #     return
            # else:
            #     from_to -= 1
            print(start, stop)

            target = self
            for i in range(start):
                target = target.children
        for child in self.children:
            child.deactivate(from_to)


    def switch_activation(self, depth = None):
        self._flag_update = not self._flag_update
        if depth != None:
            if depth == 0:
                return
            else:
                depth -= 1
        for child in self.children:
            child.switch_activation(depth)