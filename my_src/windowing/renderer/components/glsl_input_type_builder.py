import weakref
import numpy as np
import copy


class glsl_attribute:

    def __init__(self, kind, name, location):
        self._dict = weakref.WeakKeyDictionary()
        self._kind = kind
        self._name = name
        self._location = location
        pass

    def __get__(self, instance, owner):
        if instance not in self._dict:
            self._dict[instance] = {}
        if 'array' not in self._dict[instance]:
            return self
        else:
            return self._dict[instance]['value']

    def __set__(self, instance, value):
        if instance not in _dict:
            _dict[instance] = {}
        self._dict[instance]['value'] = value

    def set_array(self,instance, array):
        self._dict[instance]['array'] = array

class vector(glsl_attribute):
    _default_dtype = np.float32

class vec2(vector):
    _n = 2
    _dict = weakref.WeakKeyDictionary()

    def __set__(self, instance, value):
        self._dict[instance] = value

class vec3(vector):
    _n = 3

    pass

class vec4(vector):
    _n = 4

    pass

class matrix(glsl_attribute):
    pass

class mat4(matrix):
    _n = 16
    _default_dtype = np.float32
    pass

class integer(glsl_attribute):
    _n = 1
    _default_dtype = np.uint
    pass

class bool(integer):
    pass

class sampler2D(integer):
    pass


class GLSL_input_type_builder:
    """
    if glsl can be translated as an object instances are the object holding
    variable values. So i need a class generator which will make instances.
    Things class should have
    1. attributes
    2. name? source info?
    3. algorithm for pushing values?  instant push? late push?
    """
    _count = 0

    def __new__(cls, *args, **kwargs):
        glsl_type = type(f'shader_object{cls._count}', (GLSL_input_type_template,), {'kkk':10})

        if len(args) != 2:
            raise
        vertex = args[0].splitlines()
        fragment = args[1].splitlines()

        att_dict = {'vertex': vertex,'fragment': fragment}
        att_args = []
        uni_args = []
        for name, kind in att_dict.items():
            for line in kind:
                if ' attribute ' in line or ' uniform ' in line:
                    words = line.split(' ')
                    words[-1] = words[-1].replace(';','')
                    mark = words.index('attribute') if 'attribute' in words else words.index('uniform')

                    if line.find('layout') < line.find('(') < line.find('location') < line.find(')'):
                        location = int(line[line.find('(')+1:line.find(')')].split('=')[1].strip())
                        words.append(location)
                    else:
                        raise

                    if words[mark] == 'attribute':
                        att_args.append(words[mark:])
                    else:
                        uni_args.append(words[mark:])

        glsl_type._att_dict = att_args + uni_args

        # need to create buffer...
        att_fields = []
        for i in att_args:
            dtype = eval(f'{i[1]}._default_dtype')
            n = eval(f'{i[1]}._n')
            att_fields.append((i[2],dtype,n))
        _attribute_buffer = np.zeros(1, att_fields)

        uni_fields = []
        for i in uni_args:
            dtype = eval(f'{i[1]}._default_dtype')
            n = eval(f'{i[1]}._n')
            uni_fields.append((i[2], dtype, n))
        _uniform_buffer = np.zeros(1, uni_fields)

        glsl_type._attribute_buffer = _attribute_buffer
        glsl_type._uniform_buffer = _uniform_buffer

        # need to create attributes
        for i in att_args:
            exec(f"glsl_type.{i[2]} = {i[1]}('attribute','{i[2]}',{i[3]})")
        for i in uni_args:
            exec(f"glsl_type.{i[2]} = {i[1]}('uniform','{i[2]}',{i[3]})")

        cls._count += 1

        return glsl_type #type: GLSL_input_type_template

    def __init__(self, vertex_str, fragment_str):
        pass

class GLSL_input_type_template:

    def __init__(self):
        # self._vbo = vbo
        # print(vbo, type(vbo))

        # copy buffer structure
        self._attribute_buffer = self.__class__._attribute_buffer.copy()
        self._uniform_buffer = self.__class__._uniform_buffer.copy()

        # initiate property objects
        for kind, dtype, name, location in self._att_dict:
            exec(f"self.{name}.set_array(self, self._{kind}_buffer['{name}'])")


        self._flag_resized = False

    def late_update(self):
        """
        what do i need to update?
        :return:
        """
    
    def resize(self):

        self._flag_resized = True
