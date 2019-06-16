import threading
import weakref
import traceback
import gc
from collections import OrderedDict
from time import sleep
from time import time

from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from windowing.my_openGL.glfw_gl_tracker import GLFW_GL_tracker

import glfw as glfw
# import glfw.GLFW as GLFW

from error_handler import *
# from renderers.renderer.renderunit import RenderUnit
from virtual_scope import *

from .IO_device import *
from .layers import *
from .viewport import *

from .frame_buffer_like.frame_buffer_like_bp import FBL

from windowing.frame_buffer_like.renderable_image import Renderable_image
from windowing.frame_buffer_like.frame import Frame
from .windows import Windows


class Window:
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
        import numpy as np
        from windowing.renderer import BRO
        from windowing.frame_buffer_like.renderable_image import Renderable_image
        from windowing.unnamedGUI import mygui
        from windowing.viewport.viewport import Viewport
        import OpenGL.GL as gl
        import glfw as glfw
        pass

    _init_global = _global_init
    _windows = Windows()

    _default_framerate_target = 60
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
        gl.context_specification_check() # check additional specification

    def __enter__(self):
        if Viewport.get_current() not in self.viewports:
            self.viewports[0].open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __new__(cls,*args,**kwargs):
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)
        cls._windows + self
        return weakref.proxy(self)

    def __init__(self, width, height, name, monitor = None, mother_window = None):
        print('initiating window')
        self._size = width, height
        self._name = name
        self._monitor = monitor

        # self.windows + self

        Windows.set_current(self) # for init process may be needing which window is current

        # 1. generate contex first.
        # Do not mix order 1 and 2. There is automated vertex array operation during 2.
        if mother_window is not None:
            self._glfw_window = glfw.create_window(width, height, name, monitor, mother_window._glfw_window)
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
            self._mother_window = weakref.proxy(mother_window)  # type: Window
            mother_window._children_windows.add(self)
            # if window is shared share unique context too
            self._unique_glfw_context = mother_window.unique_glfw_context.give_tracker_to(self)
        else:
            self._mother_window = mother_window  # type: Window
            # this is a unique context wrapper and is a context identifier
            self._unique_glfw_context = GLFW_GL_tracker(self)
        GLFW_GL_tracker.set_current(self._unique_glfw_context)

        # customizable frame
        # TODO frame is leaking memory!!!!!
        m = glfw.get_primary_monitor()
        _,_,max_width,max_height = glfw.get_monitor_workarea(m)
        extra = 500 # this is to cover Windows content area. May be needed for full screen draw
        self._myframe = Frame(max_width+extra, max_height+ extra)  # type: Renderable_image
        # glsl: layout(location = 0), this is default output
        # this is ambient color output
        self._myframe.use_color_attachment(0)
        # this is id_color: please output color for distinguishing drawn objects
        self._myframe.use_color_attachment(1)
        # use basig depth and stencil
        self._myframe.use_depth_attachment(bitdepth=32)
        self._myframe.use_stencil_attachment(bitdepth=16)
        self._myframe.build()

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

        # follow closing of following windows
        # set by follows_closing()

        # drawing layers
        # TODO integrate
        # self._layers = Layers(self)

        # flags for frame drawing and swapping
        self._flag_just_resized = True

        # viewport collection
        self._viewports = Viewports(self)
        #
        self._callbacks = {
            'pre_draw':{},
            'post_draw':{},
            'window_resize':{},
            'window_close':{},
            'window_pos':{},
            'window_refresh':{},
            'window_focused':{},
            'window_maximized':{},
            'window_iconify':{},
            'window_content_scale':{}
        }
        self.initiation_post_glfw_setting()
        self.initiation_gl_setting()
        self.initiation_window_setting()


    @property
    def mother_window(self):
        return self._mother_window
    @property
    def children_windows(self):
        return self._children_windows
    @property
    def draw_func(self):
        return self._draw_func
    @property
    def init_func(self):
        return self._init_func

    # @property
    # def framerate(self):
    #     return self._default_framerate_target
    # @framerate.setter
    # def framerate(self, value):
    #     self._default_framerate_target = value
    def _callback_exec(func):
        def wrapper(*args, **kwargs):
            name = func.__name__.split('_callback')[0]
            self = args[0]
            to_delete = []
            for n, callback in self._callbacks[name].items():
                f, a, k, id, s, w = callback
                try:
                    f(*a, **k)
                except:
                    to_delete.append(n)
                    print(Warning("can't run callback. callback deleted"))
                if s:  # remove if instant
                    to_delete.append(n)

            for i in to_delete:
                del self._callbacks[name][i]

            func(*args, **kwargs)
        return wrapper

    @_callback_exec
    def window_resize_callback(self, window, width, height):
        if any(a < b for a,b in zip(self.myframe.size, self.size)):
            print('window, resize callback activated')
            self.myframe.rebuild(self.size)
        self._flag_just_resized = True

    @_callback_exec
    def window_refresh_callback(self, window):
        # copy from custom myframebuffer and draw it on window

        print(f'{self} refreshed')

    @_callback_exec
    def pre_draw_callback(self):
        pass
    @_callback_exec
    def post_draw_callback(self):
        pass
    @_callback_exec
    def window_pos_callback(self, window, x, y):
        pass
    @_callback_exec
    def window_close_callback(self,window):
        pass
    @_callback_exec
    def window_focused_callback(self,window,focused):
        print(f'{self} focused')
        pass
    @_callback_exec
    def window_iconify_callback(self, window, iconified):
        pass
    @_callback_exec
    def window_content_scale_callback(self, xscale, yscale):
        pass
    @_callback_exec
    def window_maximized_callback(self,window, maximized):
        pass

    def _callback_setter(func):
        def wrapper(self, function, args: tuple = (), kwargs: dict = {}, name: str = 'unknown', instant=False):
            if not callable(function):
                raise TypeError
            if not isinstance(args, tuple):
                raise TypeError
            if not isinstance(kwargs, dict):
                raise TypeError
            callback_name = func.__name__.split('set_')[1].split('_callback')[0]

            # check equal callback
            exist = False
            func_name = function.__qualname__
            callbacks = self._callbacks[callback_name]
            if func_name in callbacks:
                f,a,k,n,i,w = callbacks[func_name]
                if function.__code__ == f.__code__:
                    exist = True

                count = 0
                while True:
                    temp_name = f'{func_name}{count}'
                    if temp_name in callbacks:
                        count += 1
                    else:
                        func_name = temp_name
                        break
            if not exist:
                self._callbacks[callback_name][func_name] = function, args, kwargs, name, instant, weakref.proxy(self)

        return wrapper

    @_callback_setter
    def set_pre_draw_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_post_draw_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_window_resize_callback(self, func, args:tuple = (), kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_window_close_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_window_pos_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_window_iconify_callback(self, func, args:tuple=(),kwargs:dict={}, name:str='unknown', instant = False):
        pass
    @_callback_setter
    def set_window_refresh_callback(self, func=None, args:tuple=(),kwargs:dict={}, name:str='unknown', instant = False):
        pass
    def set_window_refresh(self):
        self.window_refresh_callback(self.glfw_window)

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
            w.set_window_close_callback(self.config_window_close)


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
        # before collecting make context current for gl deletings
        self.make_window_current()

        self.myframe.delete()

        # finally remove window
        glfw.destroy_window(self._glfw_window)

        # if there is no window left, terminate
        if len(self.windows) == 0:
            glfw.terminate()



        # instant collection
        gc.collect()

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

        self._windows - self
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
                glfw.show_window(self.glfw_window)
            else:
                glfw.hide_window(self.glfw_window)
        else:
            glfw.window_hint(glfw.VISIBLE, set)
    # def show(self):
    #     glfw.show_window(self.glfw_window)
    # def hide(self):
    #     glfw.hide_window(self.glfw_window)

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

    def is_child_of(self, mother):
        if mother is self._mother_window:
            return True
        else:
            return False
    def is_mother_of(self, child):
        if child in self._children_windows:
            return True
        else:
            return False
    def is_shared_window(self, win):
        if win in self.shared_windows:
            return True
        else:
            return False

    def copy_frame_from(dst, src, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y):
        if not dst.is_shared_window(src):
            raise

        # interprete to absolute(pixel) values
        args = {'src0x': src0x, 'src0y': src0y, 'src1x': src1x, 'src1y': src1y, 'dst0x': dst0x, 'dst0y': dst0y,
                'dst1x': dst1x, 'dst1y': dst1y}
        for n, v in args.items():
            ref = src if 'src' in n else dst
            ref = ref.width if 'x' in n else ref.height

            if isinstance(v, int):
                args[n] = int(v)
            elif isinstance(v, float):
                args[n] = int(ref * v)
            elif callable(v):
                args[n] = int(v(ref))
        src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y = args.values()

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

    def pin_on_area(self, target_window, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y):
        target_window.copy_frame_from(self, src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)

        def pin_on_area():
            if self.myframe.flag_something_rendered or target_window.myframe.flag_something_rendered:
                target_window.copy_frame_from(self,src0x, src0y, src1x, src1y, dst0x, dst0y, dst1x, dst1y)

        target_window.set_post_draw_callback(pin_on_area,name='_pin_on_area')

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

        target_window.set_post_draw_callback(pin_on_viewport,name='_pin_on_viewport')
        self.set_post_draw_callback(pin_on_viewport,name='_pin_on_viewport')

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
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_STENCIL_TEST)
        a = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        b = gl.glIsEnabled(gl.GL_DEPTH_TEST)
        c = gl.glIsEnabled(gl.GL_STENCIL_TEST)
        if a + b + c != 3:
            raise Exception('enabling test problem')

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

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
    def _draw_(self):
        pass

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
            timer.set_routine_start()
            if cls._display_window():
                # to give access to other windows through keyword 'windows'
                for window in cls._windows: #type: Window
                    # gc.collect()

                    # print(window)
                    #drawing
                    window.make_window_current()
                    # window.viewports[0].open()
                    window.pre_draw_callback()
                    # window.viewports[0].open()
                    window._draw_()
                    # if window.viewports.current_viewport.name == 'menu_bar':
                    #     print(window.viewports.current_viewport.name)
                    #     exit()
                    # if window.viewports.current_viewport.name != 'default':
                    if window.viewports.current_viewport._flag_clear:
                        print(f'{window} need instant clear')
                        window.viewports.current_viewport.clear_instant()
                        # window.viewports.current_viewport._flag_clear = False

                    window.post_draw_callback()

                    if window.myframe._flag_something_rendered:
                        window.make_window_current()
                        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, window.myframe._frame_buffer._glindex)
                        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)  # set source

                        gl.glScissor(0,0,window.width, window.height) # reset scissor to copy all

                        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
                        gl.glBlitFramebuffer(0, 0, window.width, window.height,
                                             0, 0, window.width, window.height,
                                             gl.GL_COLOR_BUFFER_BIT,
                                             gl.GL_LINEAR)

                        # window.buffer_swap_callback()
                        glfw.swap_buffers(window.glfw_window)
                    # window.mouse_posed = False
                    window.myframe.flag_something_rendered = False
                    window._flag_just_resized = False

                    # viewports = window.viewports._viewports
                    #
                    window.mouse.reset_per_frame()
                # z_dict = sorted(cls._windows.get_window_z_position().items())
                # for i,l in z_dict:
                #     for w in l:
                #         w.config_focused(True)
                #         w.config_focused(False)

                glfw.poll_events()
                # for i in glfw._callback_repositories:
                #     print(i)
                #     for ii in i.items():
                #         print(ii)
                # print(glfw._callback_repositories)
                # print(len(GLFW_GL_tracker._windows))
                # print(len(glfw._window_focus_callback_repository))
            else:
                break

            timer.set_routine_end()
            if timer.framecount == framecount:
                break

        # TODO fix ↓
        # Shader.deleteProgram()

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
        self.windows.set_current(self)
        # self.viewports[0].open()

        glfw.make_context_current(None)
        glfw.make_context_current(self.glfw_window)

        GLFW_GL_tracker.set_current(self.unique_glfw_context)
        FBL.set_current(self._myframe)

    # @classmethod
    # def get_current_window(cls):
    #     return cls.windows.get_current()

    @property
    def layers(self):
        return self._layers

    @property
    def viewports(self):
        return self._viewports #type:Viewports

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def size(self):
        self._size = glfw.get_framebuffer_size(self.glfw_window)
        return self._size

    @property
    def is_resized(self):
        return self._flag_just_resized

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
    def unique_glfw_context(self):
        return self._unique_glfw_context
    @property
    def myframe(self):
        return self._myframe

    def gen_child(self,width, height, name, monitor):
        w = Window(width, height, name, monitor, self)
        self.make_window_current()
        return w

    def get_vertex(self, vertex = 0):
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
        self._framecount = 0
        self._frametarget = framerate
        self._name = name
        self._current_framerate = 0

        self._saved_time_frame_start = None
        self._saved_time_frame_end = None
        self._saved_time_second = None

        self._frame_compensation = 0

        self._start_position_set = False
        self._routine_start_position_set = False
        self._print_framerate = False
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
    def set_routine_start(self):
        glfw.set_time(0)
        if self._start_position_set:
            # for compensation
            target = 1 / self._frametarget
            self._frame_compensation = (time() - self._saved_time_frame_start - target)/2
            self._saved_time_frame_start = time()
            # print(self._frame_compensation)

    def set_routine_end(self):
        # measure sleep
        if self._framecount % self._frametarget is 0:
            per_second_rendering_time = time() - self._saved_time_second
            try:
                self._current_framerate = self._frametarget / per_second_rendering_time
            except:
                pass
            else:
                self._saved_time_second = time()
                # if self._print_framerate:
                #     print()
                #     print(f'{self._name}: framerate: {round(self._current_framerate)}')

        target = 1/self._frametarget
        rendering_time = glfw.get_time()

        # if self._print_framerate_drawing:
        #     if self._framecount % self._frametarget is 0:
        #         try:
        #             fps = 1/rendering_time
        #         except:
        #             fps = 0
        #         print(f'drawing_framerate: {fps}')
        #     self._glfwtime = g.get_time()

        self._framecount += 1
        #sleep
        waiting_time = target - rendering_time - self._frame_compensation
        if waiting_time >= 0:
            sleep(waiting_time)
        else:
            pass
    @property
    def framecount(self):
        return self._framecount


