import weakref
import gc
from time import sleep
from time import time

# from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

import glfw as glfw
# import glfw.GLFW as GLFW

from error_handler import *
# from renderers.renderer.renderunit import RenderUnit

from .IO_device import *
from windowing.frame_buffer_like.viewport import *

from .frame_buffer_like.frame_buffer_like_bp import FBL

from windowing.frame_buffer_like.renderable_image import Renderable_image
from windowing.frame_buffer_like.frame import Frame,Layers,Stencil_cleaner
from .windows import Windows
from .callback_repository import Callback_repository
from .mcs import MCS

class Window(MCS):
    """
    Main class for window creation.


    """
    """
    Load packages for internal use.
    MEMO
    import numpy as np
    from windowing.renderer import BRO
    from windowing.renderable_image import Renderable_image
    from windowing.unnamedGUI import mygui
    from windowing.viewport.viewport import Viewport
    import OpenGL.GL as gl
    import glfw as glfw
    """
    def _global_init():
        pass

    _init_global = _global_init
    _windows = Windows()

    _default_framerate_target = 30
    _print_framerate = False

    # ^are UCD still valid?

    @classmethod
    def glfw_init(cls):
        """
        Init GLFW and GL.
        Singular caller for main file.
        :return: None
        """
        glfw.init()
        Unique_glfw_context.context_specification_check() # check additional specification

    def __enter__(self):
        if Windows.get_current() != self:
            self.make_window_current()
        # if Windows.get_current() != self:
        #     self._temp_return_window = Windows.get_current()
        #     self.make_window_current()
        #
        # return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if self._temp_return_window != None:
        #     self._temp_return_window.make_window_current()
        #     self._temp_return_window = None
        pass

    def __new__(cls,*args,**kwargs):
        self = super().__new__(cls)
        print(cls, Window)
        if isinstance(cls, Window):
            print(super())
            print(type(super()))
            print(cls.__mro__)
            print('args',args, kwargs)
            # super().__init__(*args, **kwargs)
            exit()
        self.__init__(*args, **kwargs)
        cls._windows + self
        return weakref.proxy(self)
        # return self

    def __init__(self, width, height, name, monitor = None, mother_window = None):
        super().__init__(0,0,width,height)
        print('initiating window')
        self._size = width, height
        self._name = name
        self._monitor = monitor
        self._temp_return_window = None
        # self.windows + self


        # 1. generate contex first.
        # Do not mix order 1 and 2. There is automated vertex array operation during 2.
        if mother_window is not None:
            try:
                self._glfw_window = glfw.create_window(width, height, name, monitor, mother_window._glfw_window)
            except Exception as e:
                raise e
                exit()
        else:
            self._glfw_window = glfw.create_window(width, height, name, monitor, None)
        # glfw window creation error check
        if not self._glfw_window:
            glfw.terminate()
            raise Exception("can't create glfw context")
        # set it current for farther settings
        glfw.make_context_current(self.glfw_window)

        # 2. store relationship between mother and children
        self._children_windows = weakref.WeakSet()
        if mother_window is not None:
            self._mother_window = weakref.ref(mother_window)  # type: Window
            mother_window._children_windows.add(self)
            # if window is shared share unique context too
            self._glfw_context = mother_window.glfw_context.give_tracker_to(self)
        else:
            self._mother_window = None  # type: Window
            # this is a unique context wrapper and is a context identifier
            self._glfw_context = Unique_glfw_context(self)
        Unique_glfw_context.set_current(self._glfw_context)

        Windows.set_current(self) # for init process may be needing which window is current
        # customizable frame
        # TODO frame is leaking memory!!!!!
        m = glfw.get_primary_monitor()
        # TODO building big frame throws inconsistency with viewports of itself
        _,_,max_width,max_height = glfw.get_monitor_workarea(m)
        extra = 500 # this is to cover Windows content area. May be needed for full screen draw
        self._myframe = Frame(max_width+extra,max_height+extra)  # type: Renderable_image
        # glsl: layout(location = 0), this is default output
        # this is ambient color output
        self._myframe.use_color_attachment(0)
        # this is id_color: please output color for distinguishing drawn objects
        self._myframe.use_color_attachment(1)
        # use basig depth and stencil
        self._myframe.use_depth_attachment(bitdepth=32)
        self._myframe.use_stencil_attachment(bitdepth=8)
        self._myframe.build(self.glfw_context)
        self._myframe.name = f'of window {self.name}'
        self._myframe._viewports = Viewports(self)

        self._layers = Layers(self._myframe)
        self._layers.new(0,'default')
        #
        # # some info for resetting
        # # look at preset_window() for further usage
        # self._init_info = OrderedDict({
        #     'width': width,
        #     'height': height,
        #     'name': name,
        #     'monitor': monitor,
        #     'share': mother_window
        # })
        #
        # option of window closing event
        # tells what to do when window is set to close
        # options are: remove, hide, save
        # look at close_option() setter for furthr usage
        self._close_option = 0
        #
        # frame operation
        self._framerate_target = 60
        self._framecount = 0
        #
        # function to execute in each state
        # self._init_func = None
        # self._draw_func = None
        #
        # # set virtual scoper for executing init and draw functions
        # # TODO think this won't work generally
        # path = inspect.getfile(inspect.currentframe().f_back.f_back)
        # self._context_scope = Virtual_scope(executing_filepath=path)
        #
        # enable inputs
        self._keyboard = Keyboard(weakref.proxy(self))
        self._mouse = Mouse(self)

        # # follow closing of following windows
        # # set by follows_closing()
        #
        # # drawing layers
        # # TODO integrate
        # # self._layers = Layers(self)
        #
        # # flags for frame drawing and swapping
        # self._flag_just_resized = True
        #
        # viewport collection
        # #
        self._callbacks_repo = weakref.WeakKeyDictionary()
        callback_names = [
            'pre_draw',
            'post_draw',
            'window_resize',
            'window_close',
            'window_pos',
            'window_refresh',
            'window_focused',
            'window_maximized',
            'window_iconify',
            'window_content_scale'
        ]
        self._callbacks_repo = Callback_repository(callback_names)

        self.initiation_post_glfw_setting()
        self.initiation_gl_setting()
        self.initiation_window_setting()
        #
        self._flag_movable = True
        # self._dell = False
        self._flag_window_close = False
        self._flag_just_resized = True

        self._previous_window_size = glfw.get_window_size(self.glfw_window)

        # self.make_window_current()

    def handle_close(self):
        if self._flag_window_close:
            self._callbacks_repo.exec('window_close')
            self._close_window()
            if len(Windows.windows) == 0:
                return True
            return False

    @property
    def mother_window(self):
        if isinstance(self._mother_window, weakref.ReferenceType):
            if self._mother_window() is None:
                self._mother_window = None
                return None
            else:
                return self._mother_window()
        else:
            return None

    @property
    def children_windows(self):
        return self._children_windows
    @property
    def draw_func(self):
        return self._draw_func
    @property
    def init_func(self):
        return self._init_func

    def window_resize_callback(self, window, width, height):
        self._flag_just_resized = True
        self.w, self.h = width, height
        self._callbacks_repo.exec('window_resize')
        if any(a < b for a,b in zip(self.myframe.size, self.size)):
            print('window, resize callback activated')
            self.myframe.rebuild(*self.size)
        # gc.collect()

    def window_refresh_callback(self, window):
        self._callbacks_repo.exec('window_refresh')
    def pre_draw_callback(self):
        self._callbacks_repo.exec('pre_draw')
    def post_draw_callback(self):
        self._callbacks_repo.exec('post_draw')
    def window_pos_callback(self, window, x, y):
        self._callbacks_repo.exec('window_pos')
    def window_close_callback(self,window):
        self._flag_window_close = True


    def window_focused_callback(self,window,focused):
        self._callbacks_repo.exec('window_focused')
        print(f'{self} focused')
    def window_iconify_callback(self, window, iconified):
        self._callbacks_repo.exec('window_iconify')
    def window_content_scale_callback(self, window, xscale, yscale):
        self._callbacks_repo.exec('window_content_scale')
    def window_maximized_callback(self,window, maximized):
        self._callbacks_repo.exec('window_maximized')

    def set_pre_draw_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('pre_draw',func,args,kwargs,identifier,instant,deleter)
    def set_post_draw_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('post_draw',func,args,kwargs,identifier,instant,deleter)
    def set_window_resize_callback(self, func, args:tuple = (),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('window_resize',func,args,kwargs,identifier,instant,deleter)
    def set_window_close_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('window_close',func,args,kwargs,identifier,instant,deleter)
    def set_window_pos_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('window_pos',func,args,kwargs,identifier,instant,deleter)
    def set_window_iconify_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('window_iconify',func,args,kwargs,identifier,instant,deleter)
    def set_window_refresh_callback(self, func, args:tuple=(),kwargs:dict={},identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('window_refresh',func,args,kwargs,identifier,instant,deleter)

    def _follow(func):
        def wrapper(self, *windows):
            if not all([isinstance(w, Window) for w in windows]):
                raise TypeError
            func(self, *windows)
        return wrapper

    @_follow
    def follow_window_iconify(self, *windows):
        for w in windows:
            w.set_window_iconify_callback(self.config_iconified)
    @_follow
    def follow_window_close(self, *windows):
        for w in windows:
            w.set_window_close_callback(self._close_window)


    # def (self, window):
    #     if not isinstance(window,Window):
    #         raise TypeError
    #     self.set_window_iconify_callback(window.config_iconified, (True,))

    def set_window_z_position(self, z:int):
        self.windows.set_window_z_position(self,z)
    def test(self):
        glfw.request_window_attention(self.glfw_window)
    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard
    @property
    def instance_name(self):
        return self._instance_name
    @property
    def windows(self):
        return self.__class__._windows

    def _set_config(func):
        def wrapper(self, set:bool):
            if set:
                set = glfw.TRUE
            else:
                set = glfw.FALSE

            hint = 'glfw.' + func.__name__.split('config_')[1].upper()
            if hasattr(self, 'glfw_window'):
                try:
                    glfw.set_window_attrib(self.glfw_window, eval(hint), set)
                except:
                    print(f"hint {hint} can't be set after glfw context creation")
            else:
                glfw.window_hint(eval(hint), set)

        return wrapper


    @_set_config
    def config_decorated(self, set:bool):
        pass
    @_set_config
    def config_resizable(self, set:bool):
        pass

    def __del__(self):
        print(f'gc, Winodw {self}')
        # instant collection

    # def __delattr__(self, item):
    #     try:
    #         self.__dict__[item].__del__()
    #
    def config_window_close(self):
        """
        Closes window concequently.

        To close itself, closes all the child windows beforehand

        :return: None
        """
        # for window in self._windows:
        #     if self in window.children_windows:
        #         window.children_windows.remove(self)



        # GLFW_GL_tracker.remove(self)
        # print()
        # print('currents')
        # print(self)
        # print(list(GLFW_GL_tracker.get_current()._windows.items()))
        # print(Viewport.get_current(),Viewport.get_current()._bound_fbl)
        # print(Windows.get_current())
        # print(FBL.get_current(), FBL.get_current()._window_binding)
        # if Windows.get_current() == self:
        #     Windows.set_current(None)
        # if Viewport.get_current() in self.viewports:
        #     Viewport.set_current(None)
        # if FBL.get_current() == self.myframe:
        #     FBL.set_current(None)
        # del self._mother_window
        # del self._children_windows
        # del self._myframe
        # del self._viewports
        # del self._mouse
        # del self._layers
        # remove window_callbacks
        # before collecting make context current for gl deletings
        # self.__delattr__('pin_on_viewport')
        # del self.pin_on_viewport

        self._flag_window_close = True


        # del dwindow._mouse

        #
        # if self.get_current() != self:
        #     self.get_current().make_window_current()
        # print(list(GLFW_GL_tracker._windows.items()))
        # print(GLFW_GL_tracker._current)
        # print('dddddddddddddddddddd')
        # print(gc.get_referents(self))
        # rf = gc.get_referrers(self)
        # for i in rf:
        #     print(i)
        # raise
    def _close_window(self):
        print(f'{self} close window')
        with self:
            repos = [
                (glfw._framebuffer_size_callback_repository, self.window_resize_callback),
                (glfw._window_refresh_callback_repository, self.window_refresh_callback),
                (glfw._window_pos_callback_repository, self.window_pos_callback),
                (glfw._window_focus_callback_repository, self.window_focused_callback),
                (glfw._window_iconify_callback_repository, self.window_iconify_callback),
                (glfw._window_close_callback_repository, self.window_close_callback),
                (glfw._window_content_scale_callback_repository, self.window_content_scale_callback),
                (glfw._window_maximize_callback_repository, self.window_maximized_callback)
            ]
            for repo, func in repos:
                to_delete = None
                for n, f in repo.items():
                    if f[0] == func:
                        to_delete = n

                if to_delete != None:
                    del repo[to_delete]

            # destroy sub components that has self reference
            self._mouse.delete()
            self._keyboard.delete()
            self._myframe.delete()

            # clean relationship
            for w in self.windows.windows.values():
                if self == w._mother_window:
                    w._mother_window = None
                if self in w._children_windows:
                    w._children_windows.remove(self)

            # remove if global
            # TODO ???
            if Windows.get_current() == self:
                Windows.set_current(None)
            if FBL.get_current == self.myframe:
                FBL.set_current(None)

            # finally remove window
            glfw.destroy_window(self._glfw_window)
            self._windows - self
            self._glfw_window = None
            # if there is no window left, terminate
            if len(self.windows) == 0:
                print('TERMINATE')
                glfw.terminate()

            gc.collect()
            # TODO deleting referensing this window
            #   check this window's context and if it doesn't have any window do the same for the context


            # print("==============")
            # for i in gc.get_referrers(self._glfw_context):
            #     print(type(i), i)
            #     # if callable(i):
            #     #     i()
            # self._glfw_context = None
            # exit()


    def config_movable(self, set:bool):
        self._flag_movable = set

    def config_iconified(self, set: bool=None):
        if set is None:
            set = not glfw.get_window_attrib(self.glfw_window,glfw.ICONIFIED)
        else:
            if set:
                set = glfw.TRUE
            else:
                set = glfw.FALSE

        if hasattr(self, 'glfw_window'):

            if set:
                glfw.iconify_window(self.glfw_window)
            else:
                glfw.restore_window(self.glfw_window)
        else:
            glfw.window_hint(glfw.ICONIFIED, set)

    def config_maximize(self, set):
        if set is None:
            set = not glfw.get_window_attrib(self.glfw_window,glfw.ICONIFIED)
        else:
            if set:
                set = glfw.TRUE
            else:
                set = glfw.FALSE

        if hasattr(self, 'glfw_window'):

            if set:
                glfw.maximize_window(self.glfw_window)
            else:
                glfw.restore_window(self.glfw_window)
        else:
            glfw.window_hint(glfw.MAXIMIZED, set)

    def config_focused(self, set:bool):
        if set:
            set = glfw.TRUE
        else:
            set = glfw.FALSE

        if hasattr(self, 'glfw_window'):
            if set:
                glfw.focus_window(self.glfw_window)
            else:
                pass
        else:
            glfw.window_hint(glfw.FOCUSED, set)

    def config_visible(self, set:bool):
        if set:
            set = glfw.TRUE
        else:
            set = glfw.FALSE

        if hasattr(self, 'glfw_window'):

            if set:
                # return_window = None
                # if Windows.get_current() != self:
                #     return_window = Windows.get_current()
                #     self.make_window_current()
                # without opacity setting nothing will be shown
                glfw.set_window_opacity(self.glfw_window, 0.9999)
                glfw.show_window(self.glfw_window)

                # if return_window != None:
                #     Windows.set_current(return_window)
                #     return_window.make_window_current()
            else:
                glfw.hide_window(self.glfw_window)
        else:
            glfw.window_hint(glfw.VISIBLE, set)
    def config_opacity(self, v):
        if not hasattr(self, 'glfw_window'):
            raise
        # TODO 1.0 doesn't work may be a bug?
        v = float(max(min(v, 0.9999), 0.0))
        glfw.set_window_opacity(self.glfw_window, v)

    def _get_config(func):
        @property
        def wrapper(self):
            hint = 'glfw.' + func.__name__.split('is_')[1].upper()
            return bool(glfw.get_window_attrib(self.glfw_window,eval(hint)))
        return wrapper

    @_get_config
    def is_visible(self):
        pass

    @_get_config
    def is_resizable(self):
        pass
    @_get_config
    def is_focused(self):
        pass
    @_get_config
    def is_maximized(self):
        pass
    @_get_config
    def is_iconifier(self):
        pass
    @property
    def is_resized(self):
        return self._flag_just_resized


    # def is_child_of(self, mother):
    #     if mother is self._mother_window:
    #         return True
    #     else:
    #         return False
    # def is_mother_of(self, child):
    #     if child in self._children_windows:
    #         return True
    #     else:
    #         return False
    # def is_shared_window(self, win):
    #     if win in self.shared_windows:
    #         return True
    #     else:
    #         return False

    def copy_frame_from(dst, src, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y):
        if not dst.is_shared_window(src):
            raise

        # interprete to absolute(pixel) values
        args = {'src0x': src0x, 'src0y': src0y, 'src1x': src1x, 'src1y': src1y, 'dst0x': dst0x, 'dst0y': dst0y,
                'dst1x': dst1x, 'dst1y': dst1y}
        for n, v in args.items():
            ref = src if 'src' in n else dst
            ref = ref.w if 'x' in n else ref.h

            if isinstance(v, int):
                args[n] = int(v)
            elif isinstance(v, float):
                args[n] = int(ref * v)
            elif callable(v):
                args[n] = int(v(ref))
        src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y = args.values()
        with dst.glfw_context as gl:
            gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, src.myframe._frame_buffer._glindex)
            gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)  # set source

            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, dst.myframe._frame_buffer._glindex) # set target
            gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)

            gl.glBlitFramebuffer(src0x, src0y, src1x, src1y,
                                 dst0x, dst0y, dst1x, dst1y,
                                 gl.GL_COLOR_BUFFER_BIT,
                                 gl.GL_LINEAR)
        dst.myframe.flag_something_rendered = True

        # how to combine object detection?
        # copy id_color? cast mouse movement to another window?
        # if copying id_color... color can be duplicated... how to make it not duplicate?
        # what if not blit but make native draw...

    # def pin_on_area(self, target_window, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y):
    #     target_window.copy_frame_from(self, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)
    #
    #     def pin_on_area():
    #         if self.myframe.flag_something_rendered or target_window.myframe.flag_something_rendered:
    #             target_window.copy_frame_from(self,src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)
    #
    #     target_window.set_post_draw_callback(pin_on_area,name='_pin_on_area')

    def pin_on_viewport(self, target_window, target_viewport:(int, str, Viewport), source_viewport:(int, str, Viewport)):
        if isinstance(target_viewport, (int, str)):
            target_viewport = target_window.viewports[target_viewport]
        if isinstance(source_viewport, (int, str)):
            source_viewport = self.viewports[source_viewport]
        src0x, src0y, srcw, srch = source_viewport.absolute_gl_values
        src1x, src1y = [a + b for a, b in zip((src0x, src0y), (srcw, srch))]
        dst0x, dst0y, dstw, dsth = target_viewport.absolute_gl_values
        dst1x, dst1y = [a + b for a, b in zip((dst0x, dst0y), (dstw, dsth))]

        target_window.copy_frame_from(self, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)

        def pin_on_viewport():

            conditions = [
                self.myframe.flag_something_rendered,
                target_window.myframe.flag_something_rendered,
                self.is_resized,
                target_window.is_resized
            ]
            if any(conditions):
                print('coppying')
                src0x, src0y, srcw, srch = source_viewport.absolute_gl_values
                src1x, src1y = [a + b for a, b in zip((src0x, src0y), (srcw, srch))]
                dst0x, dst0y, dstw, dsth = target_viewport.absolute_gl_values
                dst1x, dst1y = [a + b for a, b in zip((dst0x, dst0y), (dstw, dsth))]
                target_window.copy_frame_from(self,src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)

        target_window.set_post_draw_callback(pin_on_viewport,identifier=f'{self.name}_pin_on_viewport_{target_viewport.name}',deleter=target_viewport)
        self.set_post_draw_callback(pin_on_viewport,identifier=f'{self.name}_pin_on_viewport_{target_viewport.name}',deleter=target_viewport)

    def unpin_from_viewport(self, target_window, target_viewport):
        # target_window._callbacks_repo.remove_by_deleter(target_viewport)
        target_window._callbacks_repo.remove(target_viewport, f'{self.name}_pin_on_viewport_{target_viewport.name}')
        self._callbacks_repo.remove(target_viewport, f'{self.name}_pin_on_viewport_{target_viewport.name}')
        # exit()
        # self._deleter.remove(target_viewport)

    def initiation_post_glfw_setting(self):
        # default setting
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.set_framebuffer_size_callback(self.glfw_window, self.window_resize_callback)
        glfw.set_window_refresh_callback(self.glfw_window, self.window_refresh_callback)
        glfw.set_window_pos_callback(self.glfw_window,self.window_pos_callback)
        glfw.set_window_focus_callback(self.glfw_window,self.window_focused_callback)
        glfw.set_window_iconify_callback(self.glfw_window,self.window_iconify_callback)
        glfw.set_window_close_callback(self.glfw_window,self.window_close_callback)
        glfw.set_window_content_scale_callback(self.glfw_window,self.window_content_scale_callback)
        glfw.set_window_maximize_callback(self.glfw_window,self.window_maximized_callback)

        # glfw.set_window
        # g.swap_interval(60)

    def initiation_gl_setting(self):
        with self.glfw_context as gl:
            gl.glEnable(gl.GL_SCISSOR_TEST)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glEnable(gl.GL_STENCIL_TEST)
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            a = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
            b = gl.glIsEnabled(gl.GL_DEPTH_TEST)
            c = gl.glIsEnabled(gl.GL_STENCIL_TEST)
            if a + b + c != 3:
                raise Exception('enabling test problem')


            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    def initiation_window_setting(self):
        # self._viewports.new(0, 0, 1.0, 1.0, 'default')
        pass

    # def clear(self, *color):
    #     if len(color) == 0:
    #         color = (1, 1, 1, 1)
    #     GL.glClearColor(*color)
    #     GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    #     GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
    #     self._flag_need_swap = True

    @classmethod
    def run_single_thread(cls, framecount = None):
        """
        runs all windows in single thread.
        works very fine.
        :return:
        """

        timer = Timer(cls._default_framerate_target, 'single thread')
        timer.set_init_position()
        # timer.print_framerate()
        # timer.print_framerate_drawing()
        while True:
            # gc.collect()
            timer.set_routine()
            # if cls._display_window():
            # to give access to other windows through keyword 'windows'
            for window in cls._windows: #type: Window

                # window.make_window_current()
                with window.glfw_context:
                    with window.layers[0]:
                        with window.layers[0].viewports[0]:
                            window.pre_draw_callback()
                            window._draw_()
                            window.post_draw_callback()
                            window.mouse.reset_per_frame()

            glfw.poll_events()

            for context in Unique_glfw_context.get_instances():
                if len(context._render_unit_stack) != 0:
                    # print()
                    # print('-----------------------------------------')
                    # draw with order
                    with context as gl:
                        # print('    ',context)
                        for frame, viewports in context._render_unit_stack.items():
                            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, frame._frame_buffer._glindex)
                            attachments = [gl.GL_COLOR_ATTACHMENT0 + i for i in range(len(frame._color_attachments))]
                            gl.glDrawBuffers(len(frame._color_attachments), attachments)
                            # print('      ',frame, frame.mother)
                            # print(frame.pixel_values)
                            # print(frame._color_attachments[0]._size)
                            for viewport,layers in viewports.items():
                                gl.glViewport(*viewport.pixel_values)
                                gl.glScissor(*viewport.pixel_values)
                                # print('          ',viewport)
                                for layer,units in layers.items():
                                    # print('              ', layer)
                                    # this is to seperate layers regardless of depth drawn
                                    gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
                                    # if layer.is_on:
                                    frame._flag_something_rendered = True
                                    for unit in units:
                                        # print('                    ',unit)
                                    #     print(unit)
                                    #     if hasattr(unit[0], 'shader_io'):
                                    #         for i in unit[0].shader_io._captured:
                                    #             # print('   ',i)
                                    #             print()
                                    #             for ii in i[0]:
                                    #                 print('    ', ii)
                                        unit[0]._draw_(gl,frame, viewport, unit[2])
                                        # print()
                                        # print('writing into frame')
                                        # print(unit)
                                        # print(cls._windows.windows['main']._myframe)
                                        # print(gl,frame, viewport)
                    context.render_unit_stack_flush()

            # myframe to glfw buffer
            for window in cls._windows:
                # if window.myframe._flag_something_rendered:
                if window.myframe.something_rendered:
                    window.make_window_current()
                    with window.glfw_context as gl:
                        # gonna draw on window's default frame
                        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, window.myframe._frame_buffer._glindex)
                        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                        gl.glDisable(gl.GL_DEPTH_TEST) # cus layers are treeted as flat sheets
                        gl.glViewport(0,0,window.w, window.h) # reset scissor to copy all
                        gl.glScissor(0,0,window.w, window.h)
                        # gl.glClearStencil(0)
                        # gl.glClear(gl.GL_STENCIL_BUFFER_BIT)
                        # merge frames
                        # for every direct child
                        # TODO: layer's layer how to render? chronically?
                        stencil_bitdepth = window.myframe._stencil_attachment.bitdepth
                        # gl.glStencilMask(stencil_bitdepth)
                        layers = window.layers.all_items()
                        for id, frame in window.layers.all_items():
                            for id,frame in layers:
                                frame.render_area_of_frame(window.w, window.h)
                                frame._flag_something_rendered = False

                        # merged texture to window buffer
                        # after everything is drawn on default frame copy it into window's buffer
                        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, window.myframe._frame_buffer._glindex)
                        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)  # set source

                        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
                        gl.glBlitFramebuffer(0, 0, window.w, window.h,
                                             0, 0, window.w, window.h,
                                             gl.GL_COLOR_BUFFER_BIT,
                                             gl.GL_LINEAR)

                        gl.glEnable(gl.GL_DEPTH_TEST)

                    glfw.swap_buffers(window.glfw_window)

                window.myframe.flag_something_rendered = False
                window._flag_just_resized = False


            to_break = False
            for window in cls._windows:
                to_break = window.handle_close()
            if to_break:
                break

            if timer.framecount == framecount:
                break

        glfw.terminate()

    @classmethod
    def print_framerate(cls, state: bool = True):
        cls._print_framerate = state

    @classmethod
    def _display_window(cls, multi_thread = False):
        """
        checks in every draw_all iteration whether a window
        sould be desplayed.
        If there is no window to display or all are invisible
        returns False thus drawing application terminates.
        :return: bool
        """
        # close operation
        for i,window in enumerate(cls._windows):
            if glfw.window_should_close(window.glfw_window):
                glfw.make_context_current(None)

                if multi_thread:
                    window._terminate_flag = True
                    window.thread.join()
                else:
                    pass
                if window.close_option is 0:
                    window.config_window_close()
                    pass

                elif window.close_option is 1:
                    glfw.hide_window(window.glfw_window)

                elif window.close_option is 2:
                    glfw.destroy_window(window.glfw_window)

        for window in cls._windows:
            if glfw.get_window_attrib(window.glfw_window, glfw.VISIBLE):
                return True
            else:
                continue

        print('TERMINATING GLFW')
        print('first possible cause is : all windows closed')
        print('second possible cause is : all windows hidden')
        return False

    @property
    def glfw_window(self):
        return self._glfw_window

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f"window: '{self.name}'"

    @property
    def close_option(self):
        return self._close_option


    @close_option.setter
    def close_option(self, option: (int, str)):
        """
        Set window attribute for closing operation.
        What does it mean when window_sould_close is raised by g?

        :param option:
        0 or 'c' - remove window from application
        1 or 'h' - hide window (running but not being displayed)
        2 or 's' - save (class)Window property while removing g context
        :return: None
        """
        if isinstance(option, str):
            if option is 'c':
                option = 0
            elif option is 'h':
                option = 1
            elif option is 's':
                option = 2
            else:
                raise ValueError

        if isinstance(option, int):
            self._close_option = option

        else:
            print_message('Type error. Maintain attribute.')

    def make_window_current(self):
        # TODO
        # if self.windows.get_current() != self:
        if self.glfw_window != None:
            glfw.make_context_current(None)
            glfw.make_context_current(self.glfw_window)

        Windows.set_current(self)
        Unique_glfw_context.set_current(self.glfw_context)
        # if hasattr(self, '_myframe'):
        try:
            FBL.set_current(self.layers[0])
        except:
            pass

    # @classmethod
    # def get_current_window(cls):
    #     return cls.windows.get_current()

    # @property
    # def viewports(self):
    #     return self._myframe._viewports #type:Viewports
    @property
    def layers(self) -> Layers:
        return self._layers
    @property
    def size(self):
        return self.pixel_w, self.pixel_h
        # self._size = glfw.get_framebuffer_size(self.glfw_window)
        # return self._size



    @property
    def master_window(self):
        master = None
        if self.mother_window is None:
            return self
        else:
            master = self.mother_window.master_window
        return master

    @property
    def offspring_windows(self, _count=0):
        children = []
        if len(self.children_windows) != 0:
            children += self.children_windows
            for c in self.children_windows:
                children += c.offspring_windows
        return children

    @property
    def shared_windows(self):
        m = self.master_window
        o = m.offspring_windows
        o.insert(0,weakref.proxy(m))
        o.remove(self)
        return o

    @property
    def glfw_context(self):
        return self._glfw_context
    @property
    def myframe(self):
        return self._myframe

    def gen_child(self,width, height, name, monitor):
        w = Window(width, height, name, monitor, self)
        self.make_window_current()
        return w

    def remove_callback(self, deleter=None, identifier=None):
        self._callbacks_repo.remove(deleter, identifier)

    def get_screen_vertex(self, vertex = 0):
        """
        Returns coordinate of window vertex.
        Index goes anti-clockwise begining from top left.

        0-------3
        ｜     ｜
        ｜     ｜
        1-------2

        :param vertex: index of a vertex 0,1,2,3
        :return: tuple(x,y)
        """
        top_left = glfw.get_window_pos(self._glfw_window)
        if vertex == 0:
            return top_left
        elif vertex == 1:
            return top_left[0],top_left[1] + self.height
        elif vertex == 2:
            return top_left[0]+ self.width,top_left[1]+self.height
        elif vertex == 3:
            return top_left[0]+self.width,top_left[1]
        else:
            raise KeyError

    def move_to(self, target_screen_coord, reference_window_coord):
        x,y = int(target_screen_coord[0] - reference_window_coord[0]), int(target_screen_coord[1] - reference_window_coord[1])
        self.position = (x,y)

    @property
    def position(self):
        return glfw.get_window_pos(self.glfw_window)

    @position.setter
    def position(self, pos):
        if self._flag_movable:
            glfw.set_window_pos(self.glfw_window, int(pos[0]), int(pos[1]))

    def set_fix_position(self, target_screen_pos, reference_window_pos):
        self.move_to(target_screen_pos,reference_window_pos)
        self._flag_movable = False

    def set_size_limit(self):
        pass

    @property
    def is_singular(self):
        return self._flag_singular

    @property
    def current(self):
        try:
            self._windows.get_current().name
            return self._windows.current()
        except:
            self._windows.set_current(None)
            return None
    # def follow_cursor(self):
    #     print(self.mouse.window_position)
class Timer:
    def __init__(self,framerate, name):
        self._previous_time = time()
        self._previous_time_per_second = time()
        self._framecount = 0
        self._frametarget = framerate
        self._target_rendering_time = 1/framerate

        self._name = name
        self._current_framerate = 0

        self._saved_time_frame_start = None
        self._saved_time_frame_end = None
        self._saved_time_second = None

        self._frame_compensation = 0

        self._start_position_set = False
        self._routine_start_position_set = False
        self._print_framerate = True
        self._print_framerate_drawing = False
        self._glfwtime = 0

    def set_init_position(self):
        self._start_position_set = True
        self._saved_time_frame_start = time()
        self._saved_time_frame_end = glfw.get_time()
        self._saved_time_second = time()
    def print_framerate(self):
        self._print_framerate = True
    def print_framerate_drawing(self):
        self._print_framerate_drawing = True

    def set_routine(self):
        if self._framecount%self._frametarget == 0:
            rendering_time = time() - self._previous_time_per_second
            self._previous_time_per_second = time()
            per_frame_compensation = (1-rendering_time)/self._frametarget
            try:
                fps = self._frametarget/rendering_time
                self._target_rendering_time = 1/self._frametarget + per_frame_compensation

                print('fps:',round(fps), rendering_time, self._target_rendering_time)
            except:
                pass
        rendering_time = time()-self._previous_time
        self._previous_time = time()
        wait_time = self._target_rendering_time-rendering_time
        # print(rendering_time, wait_time, self._per_frame_compensation)
        self._framecount +=1
        if wait_time > 0:
            sleep(wait_time)
        else:
            # if self._framecount != 1:
            self._previous_time += wait_time
            pass

    @property
    def framecount(self):
        return self._framecount


