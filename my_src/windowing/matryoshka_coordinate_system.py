import weakref

class Record_change_value:
    _instance_set = weakref.WeakSet()
    _rest_called = False

    def __init__(self):
        self._dict = weakref.WeakKeyDictionary()
        self._instance_set.add(self)
        pass

    def __set__(self, instance, value):
        # three ways to define coordinate value
        if not (callable(value) or isinstance(value, (int, float))):
            raise

        if instance not in self._dict:
            self._dict[instance] = [None, False]

        # set value changed only if value input value is actucally different
        if self._dict[instance][0] != value:
            self._dict[instance][0] = value
            self._dict[instance][1] = True
        # else:
        #     self._dict[instance][1] = False

    def __get__(self, instance, owner):
        v = self._dict[instance][0]
        return v

    @classmethod
    def reset_all(cls):
        for ins in cls._instance_set:
            for lis in ins._dict.values():
                lis[1] = False

    def is_changed(self, instance):
        return self._dict[instance][1]


# class Hollow_mother:
#     pixel_x = 0
#     pixel_y = 0
#     pixel_w = 1
#     pixel_h = 1
#
class Matryoshka_coordinate_system:
    x = Record_change_value()
    y = Record_change_value()
    w = Record_change_value()
    h = Record_change_value()

    _pixel_x = Record_change_value()
    _pixel_y = Record_change_value()
    _pixel_w = Record_change_value()
    _pixel_h = Record_change_value()


    def __init__(self,posx,posy,width,height):
        self.cls = self.__class__

        self.x = posx
        self.y = posy
        self.w = width
        self.h = height

        self._pixel_x = None
        self._pixel_y = None
        self._pixel_w = None
        self._pixel_h = None

        self._vertex = [(),(),(),()]

        self._mother = None
        self._children = weakref.WeakSet()


    @property
    def pixel_x(self):
        if any(self.cls.x.is_changed(self),
               self.mother.cls._pixel_w.is_changed(self.mother),
               self.mother.cls._pixel_x.is_changed(self.mother)):
            result = None
            if isinstance(self.x, float):
                result = self.x * self.mother.pixel_w
            elif callable(self.x):
                result = self.x(self.mother.pixel_w)
            else:
                result = self.x

            self._pixel_x = result + self.mother.pixel_x

        return self._pixel_x

    @property
    def pixel_y(self):
        if any(self.cls.y.is_changed(self),
               self.mother.cls._pixel_h.is_changed(self.mother),
               self.mother.cls._pixel_y.is_changed(self.mother)):
            result = None
            if isinstance(self.y, float):
                result = self.y * self.mother.pixel_h
            elif callable(self.y):
                result = self.y(self.mother.pixel_h)
            else:
                result = self.y

            self._pixel_y = result + self.mother.pixel_y

        return self._pixel_y

    @property
    def pixel_w(self):
        if any(self.cls.w.is_changed(self),
               self.mother.cls._pixel_w.is_changed(self.mother)):
            if isinstance(self.w, float):
                self._pixel_w = self.w * self.mother.pixel_w
            elif callable(self.w):
                self._pixel_w = self.w(self.mother.pixel_w)
            else:
                self._pixel_w = self.w

        return self._pixel_w

    @property
    def pixel_h(self):
        if any(self.cls.h.is_changed(self),
               self.mother.cls._pixel_h.is_changed(self.mother)):
            if isinstance(self.h, float):
                self._pixel_h = self.h * self.mother.pixel_h
            elif callable(self.h):
                self._pixel_h = self.h(self.mother.pixel_h)
            else:
                self._pixel_h = self.h

        return self._pixel_h

    @property
    def vertex(self, *index):
        vertex_list = []
        if len(index) == 0:
            index = 0, 1, 2, 3

        # call to check change?
        # self.posx, self.posy, self.width, self.height

        # recalculate and save
        if any(self.cls._pixel_x.is_changed(self),
               self.cls._pixel_y.is_changed(self),
               self.cls._pixel_h.is_changed(self),
               self.cls._pixel_w.is_changed(self)):

            x = self._pixel_x
            y = self._pixel_y
            width = self._pixel_w
            height = self._pixel_h

            self._vertex[0] = (x, y)
            self._vertex[1] = (x + width, y)
            self._vertex[2] = (x + width, y + height)
            self._vertex[3] = (x, y + height)

            self._flag_coordinate_updated = False
        else:
            pass

        for i in index:
            vertex_list.append(self._vertex[i])

        if len(index) == 1:
            return vertex_list[0]
        return vertex_list


    def make_mother_of(self, *objects):
        for child in objects:
            child.make_child_of(self)

    def make_child_of(self, object):
        self._mother = weakref.ref(object)

    @property
    def mother(self):
        if self._mother is None:
            return None
        return self._mother()

    @property
    def children(self):
        return list(self._children)



