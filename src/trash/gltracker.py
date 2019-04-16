import ctypes

import glfw


class GLindex:
    def __init__(self):
        self._storage = {}

    def __get__(self, instance, owner):
        return self._storage

    def __set__(self, instance, value):
        # for first context call
        dict = self._storage
        current_context = id(ctypes.pointer(glfw.get_current_context().contents))
        if not current_context in dict:
            dict[current_context] = []
            dict[current_context] = value
        else:
            if dict[current_context][-1] is not value:
                dict[current_context].append(value)

class GLtracker:
    shader = GLindex()
    vertexarray = GLindex()
    vertexbuffer = GLindex()
    indexbuffer = GLindex()

    @property
    def current(self):
        info = f"""
        currently binding:
        shader          = {self.shader[-1]}
        vertex array    = {self.vertexarray[-1]}
        vertex buffer   = {self.vertexbuffer[-1]}
        index  buffer   = {self.indexbuffer[-1]}
        """
        return info
    @classmethod
    def print_all_per_element(self):
        info = f"""
        shader:
        vertex array:
        vertex buffer:
        index buffer:
        """
        print(info)

    @classmethod
    def print_all_per_context(cls,context):

        shader = cls.shader
        info = ''
    @classmethod
    def get_all_per_context(cls,context):
        i = id(context)
        info = {"shader": None, 'vao': None, 'vbo': None, 'ibo': None}
        print(i, cls.vertexarray)
        if i in cls.shader:
            info['shader'] = cls.shader[i]
        if i in cls.vertexarray:
            info['vao'] = cls.vertexarray[i]
        if i in cls.vertexbuffer:
            info['vbo'] = cls.vertexbuffer[i]
        if i in cls.indexbuffer:
            info['ibo'] = cls.indexbuffer[i]
        return info
    @classmethod
    def print(cls):
        print(cls.shader)
        print(cls.vertexarray)
        print(cls.vertexbuffer)
        print(cls.indexbuffer)