import weakref


class Value:
    def __init__(self, value):
        self._v = value
    @property
    def value(self):
        return self._v

class Record_change_value:
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
            self._dict[instance] = Value(None)

        # set value changed only if value input value is actucally different
        if self._dict[instance].value != value:
            self._dict[instance] = Value(value)
            instance.make_updated_all()
        # else:
        #     self._dict[instance][1] = False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            v = self._dict[instance].value
            return v
    def get_ref(self, instance):
        return weakref.ref(self._dict[instance])

class Hollow_mother:
    def __init__(self):
        self.pixel_x = 0
        self.pixel_y = 0
        self.pixel_w = 1
        self.pixel_h = 1
        self.cls = self
        self._pixel_w = self
        self._pixel_h = self
        self._pixel_x = self
        self._pixel_y = self
    def is_changed(self, instance):
        return False
    def __call__(self, *args, **kwargs):
        return self

class Matryoshka_coordinate_system:
    x = Record_change_value()
    y = Record_change_value()
    w = Record_change_value()
    h = Record_change_value()

    # _vertex = Record_change_value()
    #
    # _pixel_x = Record_change_value()
    # _pixel_y = Record_change_value()
    # _pixel_w = Record_change_value()
    # _pixel_h = Record_change_value()

    def __init__(self,posx,posy,width,height):
        self._children = weakref.WeakSet()

        self.x = posx
        self.y = posy
        self.w = width
        self.h = height

        # self._pixel_x = posx
        # self._pixel_y = posy
        # self._pixel_w = width
        # self._pixel_h = height

        self._vertex = [(),(),(),()]

        self._mother = Hollow_mother()


        self._flag_update = True

    @property
    def pixel_x(self):
        if isinstance(self.x, float):
            result = int(self.x * self.mother.pixel_w)
        elif callable(self.x):
            result = int(self.x(self.mother.pixel_w))
        else:
            result = self.x

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

    def vertex(self, *index):

        vertex_list = []
        if len(index) == 0:
            index = 0, 1, 2, 3

        # call to check change?
        # self.posx, self.posy, self.width, self.height

        # recalculate and save
        if self._flag_updated:
            print('need to refresh vertex')
            x = self.pixel_x
            y = self.pixel_y
            width = self.pixel_w
            height = self.pixel_h

            new_vertex = (x, y), (x + width, y), (x + width, y + height), (x, y + height)
            self._vertex = new_vertex

            self._flag_updated = False

        else:
            pass

        for i in index:
            vertex_list.append(self._vertex[i])

        if len(index) == 1:
            return vertex_list[0]
        return vertex_list
    def make_updated_all(self):
        self._flag_updated = True
        for child in self._children:
            child.make_updated_all()

    def is_mother_of(self, *objects):
        for child in objects:
            self._children.add(child)
            child.is_child_of(self)

    def is_child_of(self, mother):
        self._mother = weakref.ref(mother)
        mother._children.add(self)
        # self._ref_pixel_x = mother.__class__._pixel_x.get_ref(mother)
        # self._ref_pixel_y = mother.__class__._pixel_y.get_ref(mother)
        # self._ref_pixel_w = mother.__class__._pixel_w.get_ref(mother)
        # self._ref_pixel_h = mother.__class__._pixel_h.get_ref(mother)


    @property
    def mother(self):
        if isinstance(self._mother, Hollow_mother):
            return self._mother
        return self._mother()

    @property
    def children(self):
        return list(self._children)



