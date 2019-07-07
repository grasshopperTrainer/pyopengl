import weakref
import numpy as np
import copy
# from ...my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
from windowing.windows import Windows
class glsl_attribute:

    def __init__(self, kind, name, location):
        """

        :param kind: 0 - attribute, 1 - uniform
        :param name:
        :param location:
        """
        self._dict = weakref.WeakKeyDictionary()

        self._kind = kind
        self._name = name
        self._location = location
        pass

    def __get__(self, instance, owner):
        if instance not in self._dict:
            self._dict[instance] = {}
            return self
        else:
            return self._dict[instance][self._name]

    def __set__(self, instance, value):
        if instance not in self._dict:
            self._dict[instance] = {}
        if not np.array_equal(self._dict[instance][self._name], value):
            try:
                self._dict[instance][self._name] = value
                # print(id(self._dict[instance[self._name]]))
            except:
                self._dict[instance][self._name] = value.flatten('F')

            if self._kind == 0:
                # instance._attribute_update_que.append(self._name)
                self.push_attribute(instance)
            else:
                self.push_uniform(instance)
                # instance._uniform_update_que.append(self)


    def set_array(self,instance, array):
        self._dict[instance] = array

    def push_attribute(self, instance):
        instance._vertex_buffer.bind()
        buffer = self._dict[instance]
        start_pos = buffer.dtype.names.index(self._name)

        # finde starting offset
        start_off = 0
        for i in range(start_pos):
            dtype = buffer.dtype[i]
            bytesize = dtype.itemsize
            start_off += bytesize

        data = buffer[self._name]
        for i in range(buffer.size):
            off = start_off + buffer.itemsize * i
            element = data[i]
            size = element.itemsize * element.size

            with Unique_glfw_context.get_current() as gl:
                gl.glBufferSubData(gl.GL_ARRAY_BUFFER, off, size, element)

class vector(glsl_attribute):
    _dtype = np.float32

    def push_uniform(self, instance):
        n = int(self.__class__.__name__.split('vec')[1])
        c = 1
        d = self._dict[instance][self._name][0]
        t = d.dtype.kind
        l = self._location

        instance._shader.bind()
        with instance._context as gl:
            exec(f'gl.glUniform{n}{t}v({l},{c},d)')

class vec2(vector):
    _n = 2
    _dict = weakref.WeakKeyDictionary()

class vec3(vector):
    _n = 3

class vec4(vector):
    _n = 4

class matrix(glsl_attribute):

    def push_uniform(self, instance):
        n = int(self.__class__.__name__.split('mat')[1])
        d = self._dict[instance][self._name][0]
        l = self._location
        c = 1
        t = d.dtype.kind
        instance._shader.bind()
        with instance._context as gl:
            exec(f'gl.glUniformMatrix{n}{t}v({l},{c},False,d)')

class mat4(matrix):
    _n = 16
    _dtype = np.float32
    pass

class integer(glsl_attribute):
    _n = 1
    _dtype = np.int


    def push_uniform(self, instance):
        d = self._dict[instance][self._name][0]
        instance.shader.bind()
        gl.glUniform1i(self._location, d)

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
            dtype = eval(f'{i[1]}._dtype')
            n = eval(f'{i[1]}._n')
            att_fields.append((i[2],dtype,n))
        _attribute_buffer = np.zeros(1, att_fields)

        uni_fields = []
        for i in uni_args:
            dtype = eval(f'{i[1]}._dtype')
            n = eval(f'{i[1]}._n')
            uni_fields.append((i[2], dtype, n))
        _uniform_buffer = np.zeros(1, uni_fields)

        glsl_type._attribute_buffer = _attribute_buffer
        glsl_type._uniform_buffer = _uniform_buffer

        # need to create attributes
        for i in att_args:
            exec(f"glsl_type.{i[2]} = {i[1]}(0,'{i[2]}',{i[3]})")
        for i in uni_args:
            exec(f"glsl_type.{i[2]} = {i[1]}(1,'{i[2]}',{i[3]})")

        cls._count += 1

        return glsl_type #type: GLSL_input_type_template


class GLSL_input_type_template:

    _flag_uniform_location_validated = False
    _att_dict = None

    def __init__(self,vertex_array, vertex_buffer, shader):
        if not  vertex_buffer._context == vertex_buffer._context == shader._context:
            raise
        self._context = vertex_buffer._context
        self._vertex_array = vertex_array
        self._vertex_buffer = vertex_buffer
        self._shader = shader
        # copy buffer structure
        self._attribute_buffer = self.__class__._attribute_buffer.copy()
        self._uniform_buffer = self.__class__._uniform_buffer.copy()

        # initiate property objects
        for kind, dtype, name, location in self._att_dict:
            exec(f"self.{name}.set_array(self, self._{kind}_buffer)")


        self._flag_resized = False
        self._attribute_update_que = []
        self._uniform_update_que = []

    def resize(self, n):
        self._attribute_buffer.resize(n, refcheck=False)
        self._vertex_array.bind()
        self._vertex_buffer.bind()
        self._vertex_buffer.set_attribpointer(self._attribute_buffer)
        self._vertex_buffer.unbind()
        self._flag_resized = True

    # @classmethod
    # def validate_uniform_location(cls):
    #     mark = None
    #     for i, v in enumerate(cls._att_dict):
    #         if v[0] == 'uniform':
    #             mark = i
    #             print(cls.shader, v[2])
    #             gl.glGetUniformLocation(cls.shader,v[3])
    #     cls._flag_uniform_location_validated = True
