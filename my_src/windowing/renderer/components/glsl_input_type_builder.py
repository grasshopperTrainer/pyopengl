import weakref
import numpy as np
import copy
# from ...my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
from windowing.windows import Windows
import numbers

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

        target = self._dict[instance][self._name]
        if self._kind == 0:
            if len(target) != len(value):
                raise
        elif self._kind == 1:
            if isinstance(value, numbers.Number):
                pass
            else:
                value = np.array(value) if len(value) == 1 else np.array((value,))

        try:
            self._dict[instance][self._name] = value
        except:
            self._dict[instance][self._name] = value.flatten('F')

        self.save_attribute(instance) if self._kind == 0 else self.save_uniform(instance)


    def set_array(self,instance, array):
        self._dict[instance] = array

    def save_attribute(self, instance):
        buffer = self._dict[instance]
        start_pos = buffer.dtype.names.index(self._name)
        # finde starting offset
        start_off = 0
        for i in range(start_pos):
            dtype = buffer.dtype[i]
            bytesize = dtype.itemsize
            start_off += bytesize

        data = buffer[self._name]
        # print()
        # print(self._name)
        # print(buffer)
        # print(data)
        for i in range(buffer.size):
            off = start_off + buffer.itemsize * i
            element = data[i]
            size = element.itemsize * element.size
            # with instance.context as gl:
            #     instance._vertex_buffer.bind()
            #     gl.glBufferSubData(Unique_glfw_context.GL_ARRAY_BUFFER, off, size, element)
            instance._attribute_push_que.append((Unique_glfw_context.glBufferSubData,(Unique_glfw_context.GL_ARRAY_BUFFER, off, size, element)))

class vector(glsl_attribute):
    _dtype = np.float32

    def save_uniform(self, instance):
        n = int(self.__class__.__name__.split('vec')[1])
        c = 1
        d = self._dict[instance][self._name][0]
        t = d.dtype.kind
        l = self._location
        instance._uniform_push_que[self._name] = eval(f'Unique_glfw_context.glUniform{n}{t}v'),(l,c,d)

class vec2(vector):
    _n = 2
    _dict = weakref.WeakKeyDictionary()

class vec3(vector):
    _n = 3

class vec4(vector):
    _n = 4

class matrix(glsl_attribute):

    def save_uniform(self, instance):
        n = int(self.__class__.__name__.split('mat')[1])
        d = self._dict[instance][self._name][0]
        l = self._location
        c = 1
        t = d.dtype.kind
        instance._uniform_push_que[self._name] = eval(f'Unique_glfw_context.glUniformMatrix{n}{t}v'),(l,c,False,d)

class mat4(matrix):
    _n = 16
    _dtype = np.float32
    pass

class integer(glsl_attribute):
    _n = 1
    _dtype = np.int


    def save_uniform(self, instance):
        d = self._dict[instance][self._name][0]
        instance._uniform_push_que[self._name] = Unique_glfw_context.glUniform1i,(self._location, d)

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
        glsl_type = type(f'shader_object{cls._count}', (GLSL_input_type_template,), {})

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
            print(i)

            if i[1] == 'int':
                i[1] = 'integer'
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
    @property
    def context(self):
        return self._context()

    def __init__(self,shader, vertex_array, vertex_buffer):
        if not  vertex_buffer._context == vertex_buffer._context == shader._context:
            raise
        self._context = weakref.ref(vertex_buffer.context)

        self._vertex_array = vertex_array
        self._vertex_buffer = vertex_buffer
        self._shader = shader
        # copy buffer structure
        self._attribute_buffer = copy.deepcopy(self.__class__._attribute_buffer)
        self._uniform_buffer = copy.deepcopy(self.__class__._uniform_buffer)

        # initiate property objects
        for kind, dtype, name, location in self._att_dict:
            exec(f"self.{name}.set_array(self, self._{kind}_buffer)")


        self._flag_resized = False
        self._attribute_push_que = []
        self._uniform_push_que = {}
        self._captured = []

    def push_all(self, context, att, uni):
        # print('=================')
        # # print(att)
        # for i in att:
        #     print(i)
        # print()
        # for i in uni.items():
        #     print(i)
        # print(uni)
        if context != self.context:
            raise
        # TODO attribute update sequence and uniform update sequence is little bit different...
        #   that's because shader is shared and vertex buffer is not... what if vertex buffer is also shared? need to think about it more
        with self.context as gl:
            if att != None:
                self._vertex_buffer.bind()
                for f, args in att:
                    f(gl,*args)
                # self._attribute_push_que = []
            if att != None:
                for f, args in uni.values():
                    f(gl,*args)

        # lately bound _ pipeline assigned
        for f, args in self._uniform_push_que.values():
            f(gl, *args)
        self._uniform_push_que = {}
        # print('dddddddddddd')
        # print(self._attribute_push_que)
        # print(self._uniform_push_que)
        # self._uniform_push_que = []
    def capture_push_value(self):
        att = copy.deepcopy(self._attribute_push_que)
        uni = copy.deepcopy(self._uniform_push_que)
        self._attribute_push_que = []
        self._uniform_push_que = {}
        # self._captured.append((att,uni))
        return att, uni

    def resize(self, n):
        self._attribute_buffer.resize(n, refcheck=False)
        self._vertex_array.bind()
        self._vertex_buffer.bind()
        self._vertex_buffer.set_attribpointer(self._attribute_buffer)
        self._vertex_buffer.unbind()
        # self._flag_resized = True

        # exit()

    # def copy(self,shader, vao, vbo):
    #     new = self.__class__(vao, vbo, shader)
    #     new._attribute_buffer = self._attribute_buffer
    #     new._uniform_buffer = self._uniform_buffer
    #     new.resize(len(new._attribute_buffer))
    #
    #
    #     return new
    # @classmethod
    # def validate_uniform_location(cls):
    #     mark = None
    #     for i, v in enumerate(cls._att_dict):
    #         if v[0] == 'uniform':
    #             mark = i
    #             print(cls.shader, v[2])
    #             gl.glGetUniformLocation(cls.shader,v[3])
    #     cls._flag_uniform_location_validated = True
