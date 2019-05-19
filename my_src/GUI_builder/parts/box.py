

class Box:
    def __init__(self, name, posx, posy, width, height):
        self._name = name
        self._posx = posx
        self._posy = posy
        self._width = width
        self._height = height

        self._scaleable = True
        self._children = []

    def set_min_width(self):
        pass

    def set_min_height(self):
        pass

    def set_children(self, child_box, pos):
        # make iterable form
        boxes = [child_box, ] if isinstance(child_box, Box) else list(child_box)
        poses = [list(pos)] if all(not isinstance(i, (list,tuple)) for i in pos) else list(pos)

        # type check
        all_boxes = all(isinstance(b, Box) for b in boxes)
        all_poses = all(len(p) == 2 and isinstance(p, (list, tuple)) for p in poses)
        if not (all_boxes and all_poses):
            raise TypeError(f'input types incorrect')

        # look through
        for b,(row, column) in zip(boxes,poses):
            n_row = row - len(self._children) + 1
            # add rows to reach target
            if n_row > 0:
                self._children += [[] for i in range(n_row)]
            target_row = self._children[row]

            # add columns to reach target
            n_column = column - len(target_row) + 1
            if n_column > 0:
                target_row += [None,]*n_column

            # put box
            target_row[column] = b

    @classmethod
    def _thistypecheck(cls, box):
        if not isinstance(box, Box):
            raise TypeError(f'input is not an object of (class){cls.__name__}')

    def vstack(self, box, offset: int=0):
        self._thistypecheck(box)
        self._children += [[] for i in offset] + box._children

    def rvstack(self, box, offset: int=0):
        self._thistypecheck(box)
        self._children = box._children + [[] for i in offset] + self._children

    def hstack(self, box, offset: int=0):
        self._thistypecheck(box)
        target = self._children
        source = box._children

        # first match length
        d = len(self._children) - len(box._children)
        if d < 0:
            self._children + [[] for i in range(-d)]
        elif d > 0:
            source = box._children + [[] for i in range(-d)]

        for i,(left, right) in enumerate(zip(target, source)):
            self._children[i] = left + [[] for i in range(offset)] + right

    def rhstack(self, box, offset: int=0):
        self._thistypecheck(box)
        target = box._children
        source = self._children

        # first match length
        d = len(self._children) - len(box._children)
        if d < 0:
            self._children += [[] for i in range(-d)]
        elif d > 0:
            target = box._children + [[] for i in range(-d)]

        for i, (left, right) in enumerate(zip(target, source)):
            self._children[i] = left + [[] for i in range(offset)] + right

    # whats next?
    # need to collect data and set drawing properties?
    # and then...
    # properteis...

a = Box(1,2,3,4,5)
b = Box(1,2,3,3,5)
c = Box(2,3,4,5,6)
a.set_children(b, [1, 2])
