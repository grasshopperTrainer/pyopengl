from windowing.renderer.components import *
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL
from .render_object_registry import Render_object_registry
from numbers import Number
# from windowing.frame_buffer_like.layers import Layers
from ..my_openGL.unique_glfw_context import Unique_glfw_context
from windowing.frame_buffer_like.viewport.viewports import Viewports
from windowing.mcs import MCS
from ..renderer.renderer_template import Renderer_builder
import weakref

class Frame_renderer:
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('copy_frame'))
    # frame_renderer.use_texture(frame_renderer.Texture_new(0,0,0,))
    renderer.use_vertex_array(renderer.Vertexarray())
    renderer.use_vertex_buffer(renderer.Vertexbuffer())
    renderer.use_index_buffer(renderer.Indexbuffer((0, 1, 3, 3, 1, 2)))
    renderer.use_drawmode_triangle_strip()

    renderer_obj = None

    @classmethod
    def draw_frame(cls, frame, clip_width, clip_height):

        # initiation
        if cls.renderer_obj is None:
            cls.renderer_obj = cls.renderer()
            cls.renderer_obj.shader_io.resize(4)
            cls.renderer_obj.shader_io.vertices = (-1, 1), (-1, -1), (1, -1), (1, 1)
            cls.renderer_obj.shader_io.slot = 0
            cls.renderer_obj.shader_io.tex_coord = (0,1),(0,0),(1,0),(1,1)

        # bind color attachment for recording output of the shader
        for ca in frame._color_attachments:
            ca.bind()

        # define texture area
        w,h = clip_width/frame.pixel_w, clip_height/frame.pixel_h
        # need only part of texture
        cls.renderer_obj.shader_io.tex_coord = (0,h),(0,0),(w,0),(w,h)
        # directly draw
        cls.renderer_obj._draw_(frame.context, frame, frame._viewports[0], cls.renderer_obj.shader_io.capture_push_value())


class Stencil_cleaner:
    renderer = Renderer_builder()
    renderer.use_shader(renderer.Shader('stencil_cleaner'))
    # frame_renderer.use_texture(frame_renderer.Texture_new(0,0,0,))
    renderer.use_vertex_array(renderer.Vertexarray())
    renderer.use_vertex_buffer(renderer.Vertexbuffer())
    renderer.use_index_buffer(renderer.Indexbuffer((0, 1, 3, 3, 1, 2)))
    renderer.use_drawmode_triangle_strip()

    renderer_obj = None

    @classmethod
    def clear(cls,context):
        # initiation
        if cls.renderer_obj is None:
            cls.renderer_obj = cls.renderer()
            cls.renderer_obj.shader_io.resize(4)
            cls.renderer_obj.shader_io.vertices = (-1, 1), (-1, -1), (1, -1), (1, 1)
            cls.renderer_obj.shader_io.push_latest()

        cls.renderer_obj._draw_(context)

    # exit()
class Frame(FBL,MCS):
    def __init__(self, width, height, mother_viewport=None):
        self._previous_frame = None
        super().__init__(0,0,width,height)
        #typecheck
        if not isinstance(width, Number):
            raise TypeError
        if not isinstance(height, Number):
            raise TypeError
        if mother_viewport != None:
            self.is_child_of(mother_viewport)

        # is_window_type = any([c.__name__ == 'Window' for c in window_binding.__class__.__mro__])
        # if not is_window_type:
        #     if window_binding != None:
        #         raise TypeError

        self._size = width, height
        # self._window_binding = window_binding

        self._frame_buffer = Framebuffer()
        self._color_attachments = []
        self._depth_attachment = None
        self._stencil_attachment = None

        self._flag_color_use = False
        self._flag_depth_use = False
        self._flag_stencil_use = False

        self._flag_built = False
        self._flag_something_rendered = False

        self._render_unit_registry = Render_object_registry(self)
        self._context = None

        self._render_stack = []

        self._viewports = Viewports(self)

    def __del__(self):
        print(f'gc, Frame {self}')

    def delete(self):
        print('deleting frame')
        self._stencil_attachment.delete()
        self._depth_attachment.delete()
        self._viewports.delete()
        for i in self._color_attachments:
            i.delete()
        self._frame_buffer.delete()

    def clear(self, *rgba):
        with self:
            print('cleeenging')
            self._viewports[0].clear(*rgba)

    def render_area_of_frame(self, clip_width, clip_height):
        Frame_renderer.draw_frame(self, clip_width, clip_height)

    def new_child(self):
        new_frame = Frame(1.,1.,self)
        # new color attachments
        for i in self.color_attachment:
            new_frame.use_color_attachment(i._slot)
        # new depth attachment
        if self._depth_attachment != None:
            new_frame._depth_attachment = self._depth_attachment.copy()
        # new stencil
        if self._stencil_attachment != None:
            new_frame._stencil_attachment = self._stencil_attachment.copy()

        new_frame.build(self.context)
        new_frame.is_child_of(self)
        # this is for following window
        new_frame._viewports = Viewports(self._viewports._frame())


        return new_frame

    def build(self, context):
        if not (len(self._color_attachments) != 0 or self._depth_attachment != None or self._stencil_attachment != None):
            raise

        self._context = weakref.ref(context)
        with self.context:

            if self._depth_attachment != None:
                self._depth_attachment.build(context)
            if self._stencil_attachment != None:
                self._stencil_attachment.build(context)
            for i in self._color_attachments:
                i.build(context)

            self._frame_buffer.build(context)
            self._frame_buffer.bind_color_attachment(self._color_attachments[0], 0)
            self._frame_buffer.bind_color_attachment(self._color_attachments[1], 1)
            self._frame_buffer.bind_depth_attachment(self._depth_attachment)
            self._frame_buffer.bind_stencil_attachment(self._stencil_attachment)


    def rebuild(self, width, height):
        self._size = width, height
        for i in self._color_attachments:
            i.rebuild(width, height)
        if self._depth_attachment != None:
            self._depth_attachment.rebuild(width, height)
        if self._stencil_attachment != None:
            self._stencil_attachment.rebuild(width, height)

        self.build()

    def __enter__(self):
        # FBL.set_current(self)

        if self._context is None:
            raise

        self._previous_frame = FBL.get_current()
        FBL.set_current(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._previous_frame != None:
            FBL.set_current(self._previous_frame)
            self._previous_frame = None

    def bindDrawBuffer(self):
        with self._context as gl:
            at = [gl.GL_COLOR_ATTACHMENT0 + i for i in range(len(self._color_attachments))]
            at + [gl.GL_DEPTH_ATTACHMENT, gl.GL_STENCIL_ATTACHMENT]
            gl.glDrawBuffers(len(self._color_attachments), at)

    def bind(self):
        self._frame_buffer.bind()
        self.bindDrawBuffer()

    def unbind(self):
        pass

    def begin(self):
        # FBL.set_current(self)
        if not self._flag_built:
            raise

        self._frame_buffer.bind()


    def end(self):
        self._frame_buffer.unbind()

    @property
    def width(self):
        return self._size[0]
    @property
    def height(self):
        return self._size[1]
    @property
    def size(self):
        return self._size
    @property
    def flag_something_rendered(self):
        return self._flag_something_rendered
    @flag_something_rendered.setter
    def flag_something_rendered(self, v):
        if isinstance(v, bool):
            self._flag_something_rendered = v
        else:
            raise
    @property
    def viewports(self):
        return self._viewports

    @property
    def render_unit_registry(self):
        return self._render_unit_registry

    def use_color_attachment(self, slot):
        texture = Texture_new(self.pixel_w,self.pixel_h,slot)
        self._color_attachments.append(texture)
        return texture

    def use_depth_attachment(self,bitdepth):
        if bitdepth not in [16,24,32,'32F']:
            raise ValueError('bit depth can be 16,24,32 or 32F')

        internalformat = f'Renderbuffer.GL_DEPTH_COMPONENT{bitdepth}'

        render = Renderbuffer(self._size[0],self._size[1], eval(internalformat))
        self._depth_attachment = render
        return render

    def use_stencil_attachment(self, bitdepth):
        if bitdepth not in [1,4,8,16]:
            raise ValueError('bit depth can be 1,4,8 or 16')

        internalformat = f'Renderbuffer.GL_STENCIL_INDEX{bitdepth}'
        render = Renderbuffer(self._size[0],self._size[1],eval(internalformat))
        self._stencil_attachment = render
        return render

    @property
    def color_attachment(self):
        return self._color_attachments
    @property
    def depth_attachment(self):
        return self._depth_attachment
    @property
    def stencil_attachment(self):
        return self._stencil_attachment

    @property
    def context(self):
        return self._context()

    @property
    def something_rendered(self):
        for i in self.children_of_type(self.__class__)+[self]:
            if i._flag_something_rendered:
                return True
        return False

class Layers:
    def __init__(self, master_frame):
        # layers(frames) will be drawn on this frame
        self._frame = weakref.ref(master_frame)
        self._layers = {}
        self._current = None

    def __getitem__(self, item) -> Frame:
        if isinstance(item, str):
            for i in self._layers.values():
                if i._name == item:
                    return i
            raise KeyError(f"no such layer named '{item}'")
        elif isinstance(item, int):
            if item in self._layers:
                return self._layers[item]
            raise KeyError(f"no such layer named '{item}'")
        else:
            raise TypeError(f"key should be str or int")

    def new(self, id, name=None):
        if not isinstance(id, int):
            raise TypeError
        if id in self._layers:
            raise
        name = 'unknown' if name is None else name
        new_frame = self._frame().new_child()
        new_frame.name = str(id)
        # viewports follow
        # transparent default
        new_frame.clear(0,0,0,0)
        self._layers[id] = new_frame

        # sort
        s = sorted(self._layers.items())
        split = None
        for i,(id,frame) in enumerate(s):
            if id >= 0:
                split = i
                break
        if split != None:
            s = s[split:] + s[:split]
            self._layers = dict(s)
        return new_frame

    def set_current(self, layer):
        self._current = weakref.ref(layer)

    def all_items(self):
        return list(self._layers.items())

    @property
    def default(self):
        return self[0]

    def get_current(self):
        return self._current()

    def delete(self):
        self._current = None
        self._layers = None