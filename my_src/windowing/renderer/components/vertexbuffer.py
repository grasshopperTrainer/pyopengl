import ctypes
from .component_bp import RenderComponent
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Vertexbuffer(RenderComponent):
    GL_DYNAMIC_DRAW = Unique_glfw_context.GL_DYNAMIC_DRAW

    def __init__(self, glusage = None, data = None):

        if glusage is None:
            glusage = self.__class__.GL_DYNAMIC_DRAW
        self._glusage = glusage
        self._data = data

        self._glindex = None
        self._context = None

    def build(self, context=None):
        self._context = context

        with self._context as gl:
            self._glindex = gl.glGenBuffers(1)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glindex)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, 0, None, self._glusage)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def push_buffer(self, buffer):
        datasize = buffer.size * buffer.itemsize
        with self._context as gl:
            gl.glBufferData(gl.GL_ARRAY_BUFFER, datasize, buffer, self._glusage)

    def set_attribpointer(self, buffer_data):
        with self._context as gl:
            """
            This is called after binding VertexArrayObject to bind layout? with VAO.
            Thus is not run in self.build stage and separated.
    
            :param buffer_data: data to insert
            :return:
            """

            # if self._data is not None:
            #     raise

            datasize = buffer_data.size * buffer_data.itemsize

            # TODO glusage resetting needed?

            gl.glBufferData(gl.GL_ARRAY_BUFFER, datasize, buffer_data, self._glusage)

            # set attribute
            # when not constructed dtype
            if buffer_data.dtype.fields is None:
                type = self._dtype_to_gltype(buffer_data.dtype)
                stride = buffer_data.itemsize
                offset = ctypes.c_void_p(0)
                gl.glEnableVertexAttribArray(0)
                gl.glVertexAttribPointer(0, 1, type, gl.GL_FALSE, stride, offset)

            # when using constructed dtype
            else:
                f = buffer_data.dtype.fields
                num_attributes = len(f)
                dtypes = list(f.values())
                offsets = [i[1] for i in dtypes]
                dtypes = [i[0] for i in dtypes]
                # constant one
                stride = sum([i.itemsize for i in dtypes])

                for i in range(num_attributes):
                    d = dtypes[i]
                    size = sum(d.shape)
                    # if size == 0:
                    #     size = 1
                    gltype = self._dtype_to_gltype(d)
                    offset = ctypes.c_void_p(offsets[i])
                    gl.glEnableVertexAttribArray(i)
                    # print()
                    # print('index:',i)
                    # print('size:',size)
                    # print('gltype:',gltype)
                    # print('stride:',stride)
                    gl.glVertexAttribPointer(i, size, gltype, gl.GL_FALSE, stride, offset)
            pass

    def bind(self):
        if self._glindex is None:
            self.build()
        with self._context as gl:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glindex)
    def unbind(self):
        with self._context as gl:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def delete(self):
        if self._glindex != None:
            with self._context as gl:
                gl.glDeleteBuffers(self._glindex)
            self._glindex = None
            self._context = None

    def __del__(self):
        if self._glindex != None:
            self.delete()

    @property
    def data(self):
        return self._data

    def __str__(self):
        return f'<Vertex buffer object with opengl index: {self._glindex}>'
