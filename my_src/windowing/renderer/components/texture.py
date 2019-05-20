import os

import OpenGL.GL as gl
import numpy as np
from PIL import Image

from .component_bp import RenderComponent
from patterns.multiple_constructors import MC

class Texture(RenderComponent):
    pass



class Texture_new(Texture):
    def __init__(self, width, height):
        self._size = (width, height)
        self._flag_built = False

    def build(self):
        if not self._flag_built:
            self._flag_built = True

            self._glindex = np.array(gl.glGenTextures(1), np.uint8)

            self.bind()

            # basic setup
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            # gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_R, gl.GL_REPEAT)
            # gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_GENERATE_MIPMAP, gl.GL_TRUE)


            gl.glTexImage2D(gl.GL_TEXTURE_2D,
                            0,
                            gl.GL_RGBA8,
                            self._size[0],
                            self._size[1],
                            0,
                            gl.GL_RGBA,
                            gl.GL_UNSIGNED_BYTE,
                            None)

            self.unbind()

    def bind(self):
        print('this is new texture', self._glindex)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)

    def unbind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    @property
    def pixel_data(self):
        return np.array(self.image)

    @property
    def default_repository(self):
        return self.__class__._repository

    @default_repository.setter
    def default_repository(self, value: str):
        if isinstance(value, str):
            self.__class__._repository = value



class Texture_load(Texture):
    _repository = 'res/image/'

    def __init__(self, file: str, slot: int=0):
        self.image = None  # type: Image.Image
        if slot is None:
            slot = 0
        self.slot = slot

        self._glindex = None
        self._flag_built = False

        # in if file is given as a full path
        if '/' in file:
            path = file
        # if file is given as a name
        else:
            # TODO how to correctly set address of source directory?
            source_path = os.path.dirname(__file__).split('\my_src')[0].replace("\\", '/')
            path = f'{source_path}/{self.__class__._repository}'
            files = os.listdir(path)
            file_name = ''
            for f in files:
                if file == f.split('.')[0]:
                    file_name = f
            path += file_name

        try:
            self.image = Image.open(path)
        except:
            raise FileNotFoundError("can't load file")

    def build(self):
        if not self._flag_built:
            self._flag_built = True
            self._glindex = np.array(gl.glGenTextures(1), np.uint8)

            self.bind()
            # basic setup
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            # gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_GENERATE_MIPMAP, gl.GL_TRUE)


            internalformat = 0
            data_type = None

            if self.image.mode == 'RGBA':
                internalformat = gl.GL_RGBA8
                format = gl.GL_RGBA
            elif self.image.mode == 'RGB':
                internalformat = gl.GL_RGB8
                format = gl.GL_RGB

            if self.pixel_data.dtype == 'uint8':
                data_type = gl.GL_UNSIGNED_BYTE

            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internalformat,
                            self.image.width, self.image.height,
                            0, format, data_type, self.pixel_data)

            # remove image data from memory
            self.image.close()

            self.unbind()

    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    @property
    def pixel_data(self):
        return np.array(self.image)

    @property
    def default_repository(self):
        return self.__class__._repository

    @default_repository.setter
    def default_repository(self, value: str):
        if isinstance(value, str):
            self.__class__._repository = value
