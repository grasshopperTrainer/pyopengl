from OpenGL.GL import *
import numpy as np
from vertex_array import Vertex_array
from collections import OrderedDict

class GLindex:
    def __init__(self):
        self._storage = []

    def __get__(self, instance, owner):
        if len(self._storage) is 0:
            return [None]
        else:
            return self._storage

    def __set__(self, instance, value):
        try:
            if value is not self._storage[-1]:
                self._storage.append(value)
        except:
            self._storage.append(value)

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

