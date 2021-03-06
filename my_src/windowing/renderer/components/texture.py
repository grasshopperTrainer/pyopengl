import os

# from windowing.my_openGL.unique_glfw_context import Trackable_openGL as gl
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
import numpy as np
from PIL import Image

from .component_bp import RenderComponent
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Texture(RenderComponent):
    _default_internalformat = Unique_glfw_context.GL_RGBA8
    _default_format = Unique_glfw_context.GL_RGBA
    _default_type = Unique_glfw_context.GL_UNSIGNED_BYTE

    RGBA = Unique_glfw_context.GL_RGBA
    RED = Unique_glfw_context.GL_RED
    GREEN = Unique_glfw_context.GL_GREEN
    BLUE = Unique_glfw_context.GL_BLUE

class Texture_new(Texture):

    def __init__(self, width, height, slot, internalformat = None, format = None, type = None,data = None):
        self._size = (width, height)
        self._slot = slot

        if internalformat is None:
            self._internalformat = self._default_internalformat
        else:
            if isinstance(internalformat, str):
                if hasattr(self, internalformat):
                    self._internalformat = eval(f'self.{internalformat}')
                else:
                    raise
            else:
                raise
        if format is None:
            self._format = self._default_format
        else:
            if isinstance(format, str):
                if hasattr(self, format):
                    self._format = eval(f'self.{format}')
                else:
                    raise
            else:
                raise

        if type is None:
            self._type = self._default_type
        else:
            if isinstance(type, str):
                if hasattr(self, type):
                    self._type = eval(f'self.{type}')
                else:
                    raise
            else:
                raise

        self._glindex = None
        self._context = None
        self._data = data

    def build(self, context):
        super().build(context)

        with self.context as gl:
            self._glindex = gl.glGenTextures(1)

            gl.glActiveTexture(gl.GL_TEXTURE0 + self._slot)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)

            # basic setup
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            # gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_R, gl.GL_REPEAT)
            # gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_GENERATE_MIPMAP, gl.GL_TRUE)
            try:
                gl.glTexImage2D(gl.GL_TEXTURE_2D,
                                0,
                                self._internalformat,
                                self._size[0],
                                self._size[1],
                                0,
                                self._format,
                                self._type,
                                self._data)
            except OSError as e:
                while True:
                    try:
                        # TODO why?
                        gl.glTexImage2D(gl.GL_TEXTURE_2D,
                                        0,
                                        self._internalformat,
                                        self._size[0],
                                        self._size[1],
                                        0,
                                        self._format,
                                        self._type,
                                        self._data)
                        break
                    except:
                        pass

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # erase data?
        self._data = None
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def rebuild(self,width, height):
        self._size = width, height

        self.delete()
        self.build()

    def bind(self):
        with self.context as gl:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._slot)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)

    def unbind(self):
        with self.context as gl:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def delete(self):
        if self._glindex != None:
            with self.context as gl:
                gl.glDeleteTextures(self._glindex)
            self._glindex = None
            self._context = None

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

    # @property
    # def internalformat(self):
    #     if self._internalformat is None:
    #         return self.__class__._default_internalformat
    #     else:
    #         return self._internalformat
    # @internalformat.setter
    # def internalformat(self, v):
    #     self._internalformat = v
    #
    # @property
    # def format(self):
    #     if self._format is None:
    #         return self.__class__._default_format
    #     else:
    #         return self._format
    # @format.setter
    # def format(self, v):
    #     self._format = v
    #
    # @property
    # def type(self):
    #     if self._type is None:
    #         return self.__class__._default_type
    #     else:
    #         return self._type
    # @format.setter
    # def format(self, v):
    #     self._type = v


class Texture_load(Texture):
    _repository = 'res/image/'

    def __init__(self, file: str, slot: int=0):
        self.image = None  # type: Image.Image
        if slot is None:
            slot = 0
        self._slot = slot

        self._glindex = None
        self._context = None

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

    def build(self, context):
        super().build(context)

        with self.context as gl:
            self._glindex = np.array(gl.glGenTextures(1), np.uint8)

            gl.glActiveTexture(gl.GL_TEXTURE0 + self._slot)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)
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
            self.image.config_window_close()

            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def bind(self):
        with self.context as gl:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._slot)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._glindex)

    def unbind(self):
        with self.context as gl:
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def delete(self):
        if self._glindex != None:
            with self.context as gl:
                gl.glDeleteTextures(self._glindex)
            self._glindex = None
            self._context = None

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
