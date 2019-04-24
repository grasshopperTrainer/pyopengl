from collections import OrderedDict
import numpy as np
from OpenGL.GL import *
import ctypes

from error_handler import print_message
from .component_bp import RenderComponent
from .properties import Properties


class Shader(RenderComponent):
    _dic_shaders = OrderedDict()

    def __init__(self, file_name: str, name: str = None):
        self._glindex = None
        self._vertex = ''
        self._fragment = ''
        self._properties = Properties(self)
        # 1. make program to use
        self._bake_shader(file_name, name)
        # 2. store array buffer to use

    def _bake_shader(self, file_name: str, name):

        # if giving full path
        if '.glsl' in file_name:
            file_path = file_name
        # if using signed directory
        else:
            file_path = f'res/shader/{file_name}.glsl'

        self._parse_shader(file_path)
        self._glindex = self._create(self._vertex, self._fragment)

        self.set_variable_location(self._glindex)

        # set name for indexing and store info
        dic = self.__class__._dic_shaders

        # if no name given
        if name is None:
            l = len(dic)
            # self._name = f'undefined{l + 1}'
            self._name = file_name
        else:
            # save index for gl context? and shader info for python internal use
            dic[str(name)] = [self._glindex, self.shader_raw]


    def _create(self, vertex: str, fragment: str):

        program = glCreateProgram()

        vs = self._compile(GL_VERTEX_SHADER, vertex)
        fs = self._compile(GL_FRAGMENT_SHADER, fragment)

        glAttachShader(program, vs)
        glAttachShader(program, fs)
        glLinkProgram(program)
        glValidateProgram(program)

        glDeleteShader(vs)
        glDeleteShader(fs)

        return program

    def _compile(self, type, source):
        id = glCreateShader(type)
        glShaderSource(id, source)
        glCompileShader(id)

        success = glGetShaderiv(id, GL_COMPILE_STATUS)

        if not success:
            messege = glGetShaderInfoLog(id)
            print(f'[{self.__class__.__name__}]: failed compile shader')
            print(messege)
            glDeleteShader(id)

            return 0

        return id

    # def set_variable(self, name ,value):
    #     if name in self.attribute:
    #         self.attribute[name][1] = value
    #     if name in self.uniform:
    #         self.uniform[name][1] = value

    def update_variable(self):

        for name in self.attribute:
            item = self.attribute[name]
            loc = item[2]

            if loc != -1:
                vals = item[1]
                data_type = item[0]
                points = np.zeros(4, [('vertex', np.float32, 2)])
                points['vertex'] = [-1, -1], [1, -1], [1, 1], [-1, 1]
                # glBufferData(GL_ARRAY_BUFFER, 32, points, GL_DYNAMIC_DRAW)
                b = np.array([-1, -1], dtype=np.float32)
                # glBufferSubData(GL_ARRAY_BUFFER,0,32,b)
                glBufferSubData(GL_ARRAY_BUFFER, 0, 8, points['vertex'][0])
                glBufferSubData(GL_ARRAY_BUFFER, 24, 8, points['vertex'][1])

        # update uniform
        for name in self.uniform:
            item = self.uniform[name]
            loc = item[2]
            vals = item[1]
            data_type = item[0]
            if loc != -1:
                if 'vec' in data_type:
                    n = int(data_type.split('vec')[1])
                    exec_line = f'glUniform{n}f(loc'
                    for i in range(n):
                        exec_line += f',vals[{i}]'
                    exec_line += ')'
                    # print(name,loc, exec_line)
                    # glUniform4f(loc, vals[0], vals[1], vals[2], vals[3])
                elif 'sampler' in data_type:
                    exec_line = f'glUniform1i(loc, vals[0])'
                else:
                    print_message("unknown glsl var type. can't parse", "error", var_info=f'{name},{uni[name]}')
                    # raise Exception("unknown glsl var type. can't parse")

                exec(exec_line)
            else:
                pass
    @classmethod
    def deleteProgram(cls, *index):
        d = cls._dic_shaders
        if len(index) is 0:
            for n in d:
                i = d[n][0]
                glDeleteProgram(i)
        else:
            for i in index:
                n = list(d.keys())[i]
                v = d[n][0]
                glDeleteProgram(v)

    def bindbuffer(self, buffer):
        self._vao = buffer.print_va_info
        self._vbo = buffer.vbo
        self._ibo = buffer.ibo

    def build(self):
        pass

    def bind(self):
        glUseProgram(self.glindex)

    def unbind(self):
        glUseProgram(0)

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

    def get_uniform_location(self, name:str):
        return glGetUniformLocation(self.glindex, name)

    def set_uniform(self,name: str, *data):
        l = glGetUniformLocation(self.glindex, name)
        d = ''
        for i in range(len(data)):
            d += f'data[{i}],'
        d = d[:-1]
        # TODO automaite float int check?

        exec(f'glUniform{len(data)}f({l}, {d})')

    def _parse_shader(self, filepath):
        f = open(filepath, 'r')
        lines = f.readlines()
        save_vertex = False
        save_fragment = False
        string_index = -1

        for line in lines:

            # raise flag
            if '#shader' in line:
                if 'vertex' in line:
                    save_vertex = True
                elif 'fragment' in line:
                    save_vertex = False
                    save_fragment = True
                continue

            # add lines
            if save_vertex is True:
                self._vertex += line
            elif save_fragment is True:
                self._fragment += line

            # store variable names
            if 'attribute' in line or 'uniform' in line:

                if 'attribute' in line:
                    head = self.properties.new_attribute
                    l = line.split('attribute')[1]

                else:
                    head = self._properties.new_uniform
                    l = line.split('uniform')[1]

                l = l.replace(';', '')
                l = l.strip().split(' ')
                type = l[0]
                name = l[1]

                # make default value
                default_val = 0
                # parse 'vec' value
                if 'vec' in type:
                    n = int(type.replace('vec', ''))
                    default_val = (0.0,) * n
                    pass
                elif 'sampler' in type:
                    # if type.split('sampler')[1] == '2D':
                    default_val = (0,)
                elif 'float' in type:
                    default_val = (0.0,)
                else:
                    raise TypeError(f"""
                    in glsl code:
                    in line: '{line[:-1]}'
                    type: '{type}' is unknown
                    please define parsing""")
                    # TODO parse if other types are used for shader 'attribute', or 'uniform'
                    pass
                # store value
                head(name, type)

            else:
                continue

    def set_variable_location(self, glindex):
        # add location info
        attributes = self._properties.attribute
        uniforms = self._properties.uniform
        glUseProgram(glindex)
        for block in attributes:
            block.loc = glGetAttribLocation(glindex, block.name)

        for block in uniforms:
            block.loc = glGetUniformLocation(glindex, block.name)

    # @property
    # def vertex(self):
    #     return self._vertex
    #
    # @vertex.setter
    # def vertex(self, value):
    #     self._vertex = value
    #
    # @property
    # def fragment(self):
    #     return self._fragment
    #
    # @fragment.setter
    # def fragment(self,value):
    #     self._fragment = value

    # @property
    # def variables(self):
    #     a = self._attribute.copy()
    #     b = self._uniform.copy()
    #     a.update(b)
    #     return a

    # @property
    # def uniform(self):
    #     """
    #     description on values by index
    #     0 : type of value
    #     1 : type
    #     2 : location in shader
    #     """
    #     return self._uniform
    # @property
    # def attribute(self):
    #     return self._attribute

    @property
    def properties(self):
        return self._properties

    def __str__(self):
        return self._name
