from collections import OrderedDict

from .component_bp import RenderComponent
# from .glsl_property_container import GLSL_property_container
from .glsl_input_type_builder import GLSL_input_type_builder, GLSL_input_type_template

from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
import copy

class Shader(RenderComponent):
    _dic_shaders = OrderedDict()

    def __init__(self, file_name: str, name: str = None):
        self._file_name = file_name
        self._vertex, self._fragment, self._attribute, self._uniform = self._load_parse_glsl(file_name)

        self._context = None
        self._glindex = None
        self._name = name

        self._io_type = GLSL_input_type_builder(self._vertex, self._fragment) #type: GLSL_input_type_template

        self._flag_built = False


    def build(self, context):
        super().build(context)

        with self.context as gl:
            # 1. create program
            self._glindex = gl.glCreateProgram()
            # 3. bind shaders
            self._bake_shader()

            self._flag_built = True

    def _load_parse_glsl(self, file_name):
        att = []
        uni = []
        vertex_string = ''
        fragment_string = ''

        # if giving full path
        if '.glsl' in file_name:
            file_path = file_name
        # if using signed directory
        else:
            file_path = f'res/shader/{file_name}.glsl'

        f = open(file_path, 'r')
        lines = f.readlines()
        save_vertex = False
        save_fragment = False
        string_index = -1

        for line in lines:
            # ignore commented
            if line.strip()[:2] == '//':
                continue

            # raise flag
            if '#' in line and 'shader' in line:
                if 'vertex' in line:
                    save_vertex = True
                elif 'fragment' in line:
                    save_vertex = False
                    save_fragment = True
                continue

            # add lines
            if save_vertex is True:
                vertex_string += line
            elif save_fragment is True:
                fragment_string += line

            # store variable names
            if 'attribute ' in line or 'uniform ' in line:
                #find layout
                if line.find('layout') == -1 or line.find('location') == -1:
                    raise SyntaxError("please set location by syntax 'layout(location = #) <attibute, uniform> <type> <param_name>'")
                else:
                    location = int(line.split('location')[1].split('=')[1].split(')')[0].strip())



                if 'attribute ' in line:
                    addto = att
                    l = line.split('attribute ')[1]

                else:
                    addto = uni
                    l = line.split('uniform ')[1]

                l = l.replace(';', '')
                l = l.strip().split(' ')
                type = l[0]
                name = l[1]

                # make default value
                # default_val = 0
                # # # parse 'vec' value
                # if 'vec' in type:
                #     n = int(type.replace('vec', ''))
                #     default_val = (0.0,) * n
                #     pass
                # elif 'sampler' in type:
                #     # if type.split('sampler')[1] == '2D':
                #     default_val = (0,)
                # elif 'float' in type:
                #     default_val = (0.0,)
                # elif 'mat' in type:
                #     default_val =
                # else:
                #     raise TypeError(f"""
                #             in glsl code:
                #             in line: '{line[:-1]}'
                #             type: '{type}' is unknown
                #             please define parsing""")
                #     # TODO parse if other types are used for shader 'attribute', or 'uniform'
                #     pass
                # store value
                addto.append((name, type, location))

            else:
                continue

        return vertex_string, fragment_string, tuple(att), tuple(uni)

    def _bake_shader(self):
        with self.context as gl:
            def compile(type, source):
                id = gl.glCreateShader(type)
                gl.glShaderSource(id, source)
                gl.glCompileShader(id)

                success = gl.glGetShaderiv(id, gl.GL_COMPILE_STATUS)

                if not success:
                    messege = gl.glGetShaderInfoLog(id)
                    print(f'[{self.__class__.__name__}]: failed compile shader')
                    print(messege)
                    gl.glDeleteShader(id)

                    return 0

                return id

            vs = compile(gl.GL_VERTEX_SHADER, self._vertex)
            fs = compile(gl.GL_FRAGMENT_SHADER, self._fragment)

            gl.glAttachShader(self.glindex, vs)
            gl.glAttachShader(self.glindex, fs)
            gl.glLinkProgram(self.glindex)
            gl.glValidateProgram(self.glindex)

            gl.glDeleteShader(vs)
            gl.glDeleteShader(fs)


    # @classmethod
    # def deleteProgram(cls, *index):
    #     d = cls._dic_shaders
    #     if len(index) is 0:
    #         for n in d:
    #             i = d[n][0]
    #             gl.glDeleteProgram(i)
    #     else:
    #         for i in index:
    #             n = list(d.keys())[i]
    #             v = d[n][0]
    #             gl.glDeleteProgram(v)
    def bind(self):
        with self.context as gl:
            gl.glUseProgram(self.glindex)

    def unbind(self):
        with self.context as gl:
            gl.glUseProgram(0)

    def delete(self):
        if self._glindex != None:
            with self.context as gl:
                gl.glDeleteProgram(self._glindex)
            self._glindex = None
            self._context = None

    @property
    def vertexarray(self):
        return self._vao

    @property
    def vertexbuffer(self):
        return self._vbo

    @property
    def indexbuffer(self):
        return self._ibo

    @property
    def glindex(self):
        return self._glindex
    @property
    def io_type(self):
        return self._io_type

    def _validate_uniform_location(self):
        # for i, block in enumerate(self.properties.attribute.blocks):
        #     gl.glBindAttribLocation(self.glindex, i, block._name)
        #     block.location = i
        with self._context as gl:
            for block in self.properties.uniform.blocks:
                block.location = gl.glGetUniformLocation(self.glindex, block.name)
        # exit()
        # gl.glLinkProgram(self.glindex)

    @property
    def properties(self):
        return self._properties

    def __str__(self):
        return f"<Shader object named: '{self._name}', glindex: {self._glindex}>"