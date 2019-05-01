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
        self._vertex = ''
        self._fragment = ''
        self._file_name = file_name
        self._name = name
        self._properties = Properties(self)

        # 1. create program
        self._glindex = glCreateProgram()
        # 2. load external glsl
        # 3. read attributes and unifroms from shaders
        att_uni = self._load_parse_glsl()
        # 4. store att_uni
        for i in att_uni['att']:
            self._properties.new_attribute(i[0], i[1])
        for i in att_uni['uni']:
            self._properties.new_uniform(i[0], i[1])

        # 3. bind shaders
        self._bake_shader()
        # 2. store array buffer to use
        self._set_properties_location()
        # self.store_self()

    def _load_parse_glsl(self):
        att_uni = {'att': [], 'uni': []}
        # if giving full path
        if '.glsl' in self._file_name:
            file_path = self._file_name
        # if using signed directory
        else:
            file_path = f'res/shader/{self._file_name}.glsl'

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
            if 'attribute ' in line or 'uniform ' in line:

                if 'attribute ' in line:
                    addto = att_uni['att']
                    l = line.split('attribute ')[1]

                else:
                    addto = att_uni['uni']
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
                addto.append([name, type])

            else:
                continue

        return att_uni

    def _bake_shader(self):
        def compile(type, source):
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

        vs = compile(GL_VERTEX_SHADER, self._vertex)
        fs = compile(GL_FRAGMENT_SHADER, self._fragment)

        glAttachShader(self.glindex, vs)
        glAttachShader(self.glindex, fs)
        glLinkProgram(self.glindex)
        glValidateProgram(self.glindex)

        glDeleteShader(vs)
        glDeleteShader(fs)


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

    def _set_properties_location(self):
        for i, block in enumerate(self.properties.attribute.blocks):
            glBindAttribLocation(self.glindex, i, block._name)
            block._location = i

        for block in self.properties.uniform.blocks:
            block._location = glGetUniformLocation(self.glindex, block._name)

        glLinkProgram(self.glindex)
    @property
    def properties(self):
        return self._properties

    def __str__(self):
        return self._name