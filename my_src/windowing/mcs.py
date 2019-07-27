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
    def __init__(self, member):
        try:
            self._member = weakref.ref(member)
        except:
            self._member = member

        self._tree = {member:{}}

    def build_from_text(self, text):
        text = text.splitlines()
        lblank = 0
        collection = {}
        for i, line in enumerate(text):
            line = line.rstrip()
            # clear right blank
            if len(line) != 0:
                blank = len(line) - len(line.lstrip())
                if lblank == 0:
                    lblank = blank
                word = line[lblank:]

                # calculate level
                level = 0
                for letter in word:
                    if letter == ' ':
                        level += 1
                    else:
                        break

                # build complex data structure
                word = word.strip()
                if len(collection) == 0:
                    if level != 0:
                        raise
                    collection = {word: {}}
                else:
                    branch = collection
                    for i in range(level):
                        if isinstance(branch, dict):
                            branch = list(branch.values())[-1]
                        else:
                            branch = branch[-1]
                    branch[word] = {}

        self._tree = collection
    def get_true_branch_of_generation(self, generation):
        pass
    def get_true_branch_of_member(self, origin):
        # {child: {}, child:{}, child: {chi:{}, chi:{}}}
        branch = [self._tree,]
        while True:
            new_branch = []
            for dic in branch:
                if origin in dic:
                    return dic[origin]
                else:
                    new_branch += list(dic.values())

            if len(new_branch) == 0:
                # means tree doesn't have object(origin)
                raise
            else:
                branch = new_branch

    def _flatten(self, branch):
        #example) {child: {}, child:{}, child: {chi:{}, chi:{}}}
        flattened = []
        for m,c in branch.items():
            flattened.append(m)
            flattened += self._flatten(c)
        return flattened

    def offsprings_of(self, origin):
        branch = self.get_true_branch_of_member(origin)
        return self._flatten(branch)

    def siblings_of(self, origin):
        mother = self.mother_of(origin)

        # for origin
        if mother == None:
            return []
        siblings = self.children_of(mother)
        siblings.remove(origin)
        return siblings

    def children_of(self, origin, type=None):
        # {child: {}, child:{}, child: {chi:{}, chi:{}}}
        branch = [self._tree, ]
        while True:
            new_branch = []
            for dic in branch:
                if origin in dic:
                    if type is None:
                        return list(dic[origin].keys())
                    else:
                        return list(filter(lambda x: isinstance(x,type), list(dic[origin].keys())))
                else:
                    new_branch += list(dic.values())

            if len(new_branch) == 0:
                # means tree doesn't have object(origin)
                return []
            else:
                branch = new_branch

    def mother_of(self, origin):
        branch = [self._tree,]

        if origin == self.origin:
            return None

        while True:
            new_branch = []
            for dic in branch:
                for key, value in dic.items():
                    if origin in value:
                        return key
                else:
                    new_branch += list(dic.values())

            if len(new_branch) == 0:
                # not a member of the family
                raise
            branch = new_branch

    @property
    def origin(self):
        return list(self._tree.keys())[0]

    @property
    def all_members(self):
        return self._flatten(self._tree)

    @property
    def all_generation(self):

        def f(branches, generations = []):
            new_branches = []
            generation = []
            for i in branches:
                generation += i.keys()
                new_branches += list(i.values())

            if len(generation) != 0:
                generations.append(generation)

            if len(new_branches) != 0:
                f(new_branches,generations)

            return generations

        return f([self._tree])



    def has_member(self, obj, branch:dict=None):
        if branch is None:
            branch = self._tree

        if obj in branch:
            return True
        else:
            for i in branch.values():
                if self.has_member(obj, i):
                    return True

        return False

    def renounce(self, member):
        mother = self.mother_of(member)
        branch = self.get_true_branch_of_member(mother)
        del branch[member]

    def graft(self, source, target_tree, target):
        if not isinstance(target_tree, self.__class__):
            raise TypeError
        if not self.has_member(source):
            raise
        if not target_tree.has_member(target):
            raise


        source_branch = self.get_true_branch_of_member(source)
        target_branch = {target:target_tree.get_true_branch_of_member(target)}

        # TODO can a member belong in two trees?
        # this case if for relocating existing member
        if self.has_member(target):
            self.renounce(target)

        source_branch.update(target_branch)
        target_tree._tree = self._tree

    @property
    def member(self):
        if isinstance(self._member, weakref.ReferenceType):
            return self._member()
        return self._member

    def generation_from_to(self, member, start, stop):
        # start_stop is reletive from member

        # find master
        masters = member
        if start is None:
            mother = member
            start = 0
            while True:
                mother = self.mother_of(mother)
                if mother == None:
                    break
                start -= 1

            masters = [self.origin]
        elif start < 0:
            for i in range(-start):
                masters = self.mother_of(masters)
            masters = [masters]
        elif start == 0:
            masters = [member]
        else:
            masters = [member]
            for i in range(start):
                new_masters = []
                for master in masters:
                    new_masters += self.children_of(master)
                masters = new_masters

        # ununderstood condition
        if stop != None and start >= stop:
            raise

        # collect members
        offsprings = []
        branches = []
        for master in masters:
            branches.append({master:self.get_true_branch_of_member(master)})

        if stop is None:
            while True:
                new_branches = []
                for dic in branches:
                    offsprings += list(dic.keys())
                    new_branches += list(dic.values())

                if len(new_branches) == 0:
                    break
                else:
                    branches = new_branches
                    continue
        else:
            for i in range(stop-start):
                new_branches = []
                for dic in branches:
                    offsprings += list(dic.keys())
                    new_branches += list(dic.values())
                branches = new_branches

        return offsprings
        # offsprings = []
        # offsprings += masters
        # while True:
        #     children = []
        #     for member in masters:
        #         # is extra searching from begining chore here?
        #         children += self.children_of(member)
        #
        #     start += 1
        #     if stop != None:
        #         if start == stop:
        #             break
        #     else:
        #         if len(children) == 0:
        #             break
        #
        #     offsprings += children
        #     masters = children
        #
        # return offsprings


    def __getitem__(self, item):

        if isinstance(item, int):
            return self.generation_from_to(self.member, item, item+1)
        elif isinstance(item, slice):
            return self.generation_from_to(self.member, item.start, item.stop)
        else:
            raise
        raise


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
        self._name = None
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
        # try:
        if self.mother != None:
            result = result + self.mother.pixel_x
        # except Exception as e:
        #     print(self._family_tree._tree)
        #     print(self, self.mother)
        #     print(result, self.mother.x)
        #     raise e
        return result

    @property
    def pixel_y(self):
        if isinstance(self.y, float):
            result = int(self.y * self.mother.pixel_h)
        elif callable(self.y):
            result = int(self.y(self.mother.pixel_h))
        else:
            result = self.y

        if self.mother != None:
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
        mother._family_tree.graft(mother, self._family_tree, self)

    def replace_child(self):
        pass

    @property
    def mother(self):
        return self._family_tree.mother_of(self)

    @property
    def children(self):
        return self._family_tree.children_of(self,None)
    def children_of_type(self, type):
        return self._family_tree.children_of(self, type)

    @property
    def siblings(self):
        return self._family_tree.siblings_of(self)

    @property
    def is_active(self):
        return self._flag_update

    def pack_children_horizontal(self, origin = (0,0), reverse = False):
        members = self.family[1]
        if len(members) != 0:
            if reverse:
                oldest = members[0]
                offset = -oldest.pixel_w
                oldest.x, oldest.y = offset+origin[0],origin[1]
                for member in members[1:]:
                    offset -= member.pixel_w
                    member.x, member.y = offset+origin[0], origin[1]
            else:
                oldest = members[0]
                oldest.x, oldest.y = origin[0],origin[1]
                offset = oldest.pixel_w
                for member in members[1:]:
                    member.x, member.y = offset+origin[0], origin[1]
                    offset += member.pixel_w

    def pack_children_vertical(self, origin=(0,0), reverse = False):
        members = self.family[1]
        if len(members) != 0:
            if reverse:
                oldest = members[0]
                offset = -oldest.pixel_h
                oldest.x, oldest.y = origin[0], origin[1]+offset
                for member in members[1:]:
                    offset -= member.pixel_h
                    member.x, member.y = origin[0], origin[1]+offset
            else:
                oldest = members[0]
                oldest.x, oldest.y = origin[0], origin[1]
                offset = oldest.pixel_h
                for member in members[1:]:
                    member.x, member.y = origin[0], origin[1]+offset
                    offset += member.pixel_h
        pass

    # def activate(self, depth=None):
    #     self._flag_update = True
    #     if depth != None:
    #         if depth == 0:
    #             return
    #         else:
    #             depth -= 1
    #
    #     for child in self.children:
    #         child.activate(depth)

    # def deactivate(self, start=None, stop=None):
    #     # self._flag_update = False
    #     if start == None and stop==None:
    #         pass
    #     else:
    #         # if from_to == 0:
    #         #     return
    #         # else:
    #         #     from_to -= 1
    #         print(start, stop)
    #
    #         target = self
    #         for i in range(start):
    #             target = target.children
    #
    #     for child in self.children:
    #         child.deactivate(from_to)
    def activate(self):
        self._flag_update = True

    def deactivate(self):
        self._flag_update = False

    def switch_activation(self, depth = None):
        self._flag_update = not self._flag_update
        if depth != None:
            if depth == 0:
                return
            else:
                depth -= 1
        for child in self.children:
            child.switch_activation(depth)

    @property
    def family(self):
        return self._family_tree

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, text):
        if not isinstance(text, str):
            raise TypeError
        self._name = text

    def __str__(self):
        return f"<{self.__class__.__name__}> named '{self._name}'"

    def __repr__(self):
        return self.__str__()