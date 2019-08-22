import weakref

class Family_tree_list:

    def __init__(self):
        print('init of tree')
        # TODO change it to weakref after all is built
        self._tree = {}



    def get_mother_of(self, child):

        def look_through(branch, child):
            if isinstance(branch, dict):
                if len(branch) != 0:
                    for m, child_d in branch.items():
                        if child in child_d:
                            return m
                        else:
                            continue
                    for child_d in branch.values():
                        inner = look_through(child_d, child)
                        if inner != None:
                            return inner
                else:
                    return None
            else:
                return None

        return look_through(self._tree, child)

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

    def is_member(self, obj):

        def look_through(branch:dict, obj):
            if obj in branch:
                return True
            else:
                for i in branch.values():
                    if isinstance(i,dict):
                        if look_through(i, obj):
                            return True
                        else:
                            continue
                    else:
                        continue
            return False

        answer = look_through(self._tree, obj)
        return answer

    def invite_member(self, new_member):
        """
        set a new member as one of high ancestor
        :param new_member:
        :return:
        """
        if self.is_member(new_member):
            raise
        self._tree[new_member] = {}

    def invite_as_mother_of(self, child, mother):
        """
        set a new member as a mother of child member
        :param child:
        :param mother:
        :return:
        """
        if self.is_member(mother):
            raise

    def invite_as_child_of(self, mother, child):
        """
        set a new member as a child of mother member
        :param child:
        :param mother:
        :return:
        """
        if self.is_member(child):
            raise

        b = self.get_true_branch_of_member(mother)
        b[child] = {}



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
        mother = self.get_mother_of(origin)

        # for origin
        if mother == None:
            return []
        siblings = self.children_of(mother)
        siblings.remove(origin)
        return siblings

    def children_of(self, mother, type=None):
        # {child: {}, child:{}, child: {chi:{}, chi:{}}}
        branch = [self._tree, ]
        while True:
            new_branch = []
            for dic in branch:
                if mother in dic:
                    if type is None:
                        return list(dic[mother].keys())
                    else:
                        return list(filter(lambda x: isinstance(x,type), list(dic[mother].keys())))
                else:
                    new_branch += list(dic.values())

            if len(new_branch) == 0:
                # means tree doesn't have object(origin)
                return []
            else:
                branch = new_branch

    def direct_ancestors(self):
        pass
    def all_ancestors(self):
        pass





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





    def renounce(self, member):
        mother = self.get_mother_of(member)
        branch = self.get_true_branch_of_member(mother)
        del branch[member]



    def graft(self, source, target_tree, target):
        if not isinstance(target_tree, self.__class__):
            raise TypeError
        if not self.is_member(source):
            raise
        if not target_tree.is_member(target):
            raise


        source_branch = self.get_true_branch_of_member(source)
        target_branch = {target:target_tree.get_true_branch_of_member(target)}

        # TODO can a member belong in two trees?
        # this case if for relocating existing member
        if self.is_member(target):
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
                mother = self.get_mother_of(mother)
                if mother == None:
                    break
                start -= 1

            masters = [self.origin]
        elif start < 0:
            for i in range(-start):
                masters = self.get_mother_of(masters)
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