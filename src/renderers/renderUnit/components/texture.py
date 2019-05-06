import os

import OpenGL.GL as gl
import numpy as np
from PIL import Image

from .component_bp import RenderComponent


class Texture(RenderComponent):
    _repository = 'res/image/'

    def __init__(self, file: str, slot=0):
        self.image = None  # type: Image.Image
        if slot is None:
            slot = 0
        self.slot = slot

        self._glindex = None

        # in if file is given as a full path
        if '/' in file:
            path = file
        # if file is given as a name
        else:
            # TODO how to correctly set address of source directory?
            source_path = os.path.dirname(__file__).split('\src')[0].replace("\\", '/')
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
        self._glindex = np.array(gl.glGenTextures(1), np.uint8)

        self.bind()
        # basic setup
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

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
                        self.image.w, self.image.h,
                        0, format, data_type, self.pixel_data)

        self.unbind()

        # remove image data from memory
        self.image.close()

    # def __del__(self):
    #     # before instance is deleted...
    #     # gl.glDeleteTextures(self.glindex)

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
