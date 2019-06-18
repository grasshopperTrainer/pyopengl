import glfw
import weakref
import copy

from patterns.store_instances_dict import SID
from ..my_openGL.glfw_gl_tracker import Trackable_openGL as gl
from ..windows import Windows
from ..callback_repository import Callback_repository

class Position_registry:
    pass
    def new(self):
        pass


class Mouse(SID):

    def __init__(self, window):
        self._window = window

        callbacks_names = [
            'any',
            'move',
            'enter',
            'exit',
            'button',
            'button_press',
            'button_release',
            'scroll',
            'scroll_up',
            'scroll_down',
            'scroll_right',
            'scroll_left'
        ]
        self._callbacks_repo = Callback_repository(window, callbacks_names)

        glfw.set_input_mode(self._window.glfw_window, glfw.STICKY_MOUSE_BUTTONS, glfw.TRUE)
        glfw.set_cursor_pos_callback(self._window.glfw_window, self.mouse_move_callback)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self.mouse_enter_callback)
        glfw.set_mouse_button_callback(self._window.glfw_window, self.mouse_button_callback)
        glfw.set_scroll_callback(self._window.glfw_window, self.mouse_scroll_callback)

        # self.instant_mouse_states = []

        self._scroll_offset = []
        self._button_state = {}
        self._cursor_state = {'onscreen':False,'moving':False}

        self._window_selection_area = []

        self._position_registry = Position_registry()

        self._just_released = False
        self._just_pressed = False

        self._mapping_source = weakref.WeakValueDictionary()

        self._just_values = {
            'pressed':False,
            'released':False
        }

    def delete(self):
        print('deleting mouse')
        # remove window footprint
        self._window = None
        # removing callbacks from a thing called by glfw.pollevent()
        repos = [
            (glfw._cursor_pos_callback_repository, self.mouse_move_callback),
            (glfw._cursor_enter_callback_repository,self.mouse_enter_callback),
            (glfw._mouse_button_callback_repository,self.mouse_button_callback),
            (glfw._scroll_callback_repository,self.mouse_scroll_callback)
        ]
        for repo,func in repos:
            to_delete = None
            for n,f in repo.items():
                if f[0] == func:
                    to_delete = n

            if to_delete != None:
                del repo[to_delete]

        # glfw.poll_events()
        # glfw.post_empty_event()

        # glfw.event

        # exit()
    def __del__(self):
        print(f'gc, Mouse {self}')

    def any_callback(self):
        self._callbacks_repo.exec('any')
    def move_callback(self):
        self._callbacks_repo.exec('move')
    def enter_callback(self):
        self._callbacks_repo.exec('enter')
    def exit_callback(self):
        self._callbacks_repo.exec('exit')
    def button_callback(self):
        self._callbacks_repo.exec('button')
    def button_press_callback(self):
        self._callbacks_repo.exec('button_press')
        self._just_values['pressed'] = True
    def button_release_callback(self):
        self._callbacks_repo.exec('button_release')
        self._just_values['released'] = True
    def scroll_callback(self):
        self._callbacks_repo.exec('scroll')
    def scroll_right_callback(self):
        self._callbacks_repo.exec('scroll_right')
    def scroll_left_callback(self):
        self._callbacks_repo.exec('scroll_left')
    def scroll_up_callback(self):
        self._callbacks_repo.exec('scroll_up')
    def scroll_down_callback(self):
        self._callbacks_repo.exec('scroll_down')


    def set_any_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('any', func, args, kwargs, identifier, instant, deleter)
    def set_move_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('move', func, args, kwargs, identifier, instant, deleter)
    def set_enter_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('enter', func, args, kwargs, identifier, instant, deleter)
    def set_exit_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('exit', func, args, kwargs, identifier, instant, deleter)
    def set_button_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('button', func, args, kwargs, identifier, instant, deleter)
    def set_button_press_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('button_press', func, args, kwargs, identifier, instant, deleter)
    def set_button_release_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str ='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('button_release', func, args, kwargs, identifier, instant, deleter)
    def set_scroll_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('scroll', func, args, kwargs, identifier, instant, deleter)
    def set_scroll_up_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('scroll_up', func, args, kwargs, identifier, instant, deleter)
    def set_scroll_down_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('scroll_down', func, args, kwargs, identifier, instant, deleter)
    def set_scroll_right_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('scroll_right', func, args, kwargs, identifier, instant, deleter)
    def set_scroll_left_callback(self, func, args:tuple=(), kwargs:dict={}, identifier:str='not_given',instant=False,deleter=None):
        self._callbacks_repo.setter('scroll_left', func, args, kwargs, identifier, instant, deleter)

    def mouse_move_callback(self, context, xpos, ypos):
        self.move_callback()
        self.any_callback()
        self._cursor_state['moving'] = True


    def mouse_enter_callback(self, context, entered):
        if entered:
            self.enter_callback()
            self.any_callback()
            self._cursor_state['onscreen'] = True
        else:
            self.exit_callback()
            self.any_callback()
            self._cursor_state['onscreen'] = False

    def mouse_button_callback(self, context, button, action, mods):
        # TODO why first mouse click behaves differently?
        if action is 1:
            self._button_state[button] = True
            self.button_press_callback()
            self.any_callback()
        if action is 0:
            self._button_state[button] = False
            print(self, context, button)
            print(self.window)
            self.button_release_callback()
            self.any_callback()
        self.button_callback()

    def mouse_scroll_callback(self, context, xoffset, yoffset):
        self._scroll_offset = xoffset, yoffset
        if xoffset >= 0:
            self.scroll_right_callback()
            self.any_callback()
        else:
            self.scroll_left_callback()
            self.any_callback()
        if yoffset >= 0:
            self.scroll_up_callback()
            self.any_callback()
        else:
            self.scroll_down_callback()
            self.any_callback()
        self.scroll_callback()

    # def instant_press_button(self, button: int):
    #     """
    #     Triger one-time mouse button click action.
    #     :param button: button index number
    #     :return:
    #     """
    #     self._button_state[button] = True
    #     # reset action
    #     self.instant_mouse_states.append([self._button_state, button, False])
    #
    # def instant_mouse_onscreen(self):
    #     self._flag_cursor_onscreen = True
    #     self.instant_mouse_states.append([self._cursor_state,'onscreen', False])

    def reset_per_frame(self):
        for i in self._just_values:
            self._just_values[i] = False
        # for type,key,state in self.instant_mouse_states:
        #     type[key] = state
        # self.instant_mouse_states = []
        self._cursor_state['moving'] = False

    def _get_just(func):
        @property
        def wrapper(self, *args, **kwargs):
            name = func.__name__.replace('is_just_','')
            return self._just_values[name]
        return wrapper

    @_get_just
    def is_just_released(self):
        pass
    @_get_just
    def is_just_pressed(self):
        pass
    @property
    def pressed_button(self):
        return_list = []
        for n,v in self._button_state.items():
            if v:
                return_list.append(n)

        return tuple(return_list)

    @property
    def button_state(self):
        return self._button_state

    @property
    def cursor_onscreen(self):
        return self._cursor_state['onscreen']
    @property
    def moving(self):
        return self._cursor_state['moving']
    @property
    def window(self):
        return self._window

    @property
    def window_position(self):
        # flipped to match openGL buffer order
        if len(self._mapping_source) != 0 and not self.window.is_focused:
            wi, vp = self._mapping_source['window'], self._mapping_source['viewport']
            ratio = wi.mouse.viewport_position(vp, True)

            size = self.window.size
            mapped = [a * b for a, b in zip(ratio, size)]
            return mapped
        else:
            return glfw.get_cursor_pos(self._window.glfw_window)

    def set_map_from_window(self, source_window, source_viewport):
        if isinstance(source_viewport, (int, str)):
            source_viewport = source_window.viewports[source_viewport]

        # connect position
        self._mapping_source['window'] = source_window
        self._mapping_source['viewport'] = source_viewport

        # connect callbacks
        for n in source_window.mouse._callbacks_repo.callback_names:
            # for func_set in self._callbacks_repo.get_callback_named(n):
            source_window.mouse._callbacks_repo.setter(n, eval(f'self.{n}_callback'), deleter=self.window)

    def reset_map_from_window(self):
        # remove callbacks
        for name, callbacks in self._mapping_source[0].mouse._callbacks.items():
            if self in callbacks:
                del callbacks[self]
        # reset position
        self._mapping_source = None

    @property
    def screen_position(self):
        pos = [a+b for a,b in zip(self.window.get_vertex(0), self.window_position)]
        return pos

    def viewport_position(self, viewport:'Viewport', reparameterize:bool):
        x,y = self.window_position
        a0,a1 = viewport.get_vertex_from_window(0)
        if not reparameterize:
            return x-a1, yy-a2
        else:
            w,h = viewport.abs_width,viewport.abs_height
            return (x-a0)/w, (y-a1)/h

    @property
    def is_any_pressed(self):
        if len(self.pressed_button) != 0:
            return True
        else:
            return False

    @property
    def scroll_offset(self):
        return self._scroll_offset

    def global_button_state(self):
        result = {}
        for instance in self._INSTANCES_DICT.keys():
            d = instance._button_state
            for k,v in d.items():
                if k in result:
                    if v is True:
                        result[k] = True
                else:
                    result[k] = v
        return result

    def global_cursor_state(self):
        result = {}
        for instance in self._INSTANCES_DICT.keys():
            d = instance._cursor_state
            for k,v in d.items():
                if k in result:
                    if v is True:
                        result[k] = True
                else:
                    result[k] = v

        return result

    @property
    def cursor_object(self):
        x,y = self.window_position
        y = self._window.height - y
        self._window.make_window_current()

        self.window.myframe.bind()
        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT1)
        color = gl.glReadPixels(x,y,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE)
        obj = self._window.myframe.render_unit_registry.object(color)

        return obj

    def is_cursor_on_object(self, obj):
        if self.cursor_object == obj:
            return True

    def is_object_pressed(self, obj, button=None):
        if button is None:
            if self.is_just_pressed:
                if self.cursor_object == obj:
                    return True
        else:
            if self.is_just_pressed and button in self.pressed_button:
                if self.cursor_object == obj:
                    return True
        return False

    def set_object_selection_callback(self, selection, callback, func, args:tuple=(), kwargs:dict={}, identifier="not_given"):
        if callable(func):
            def callback_func(func, args, kwargs):
                if self.cursor_object == selection:
                    func(*args,**kwargs)
                    
        # setting multiple
        elif isinstance(func, tuple):
            if not all(callable(x) for x in func):
                raise
            func_n = len(func)
            if func_n != 1:
                if len(args) == 0:
                    args = [args,]*func_n
                if isinstance(kwargs, dict):
                    kwargs = [kwargs,]*func_n

            def callback_func(func,args,kwargs):
                print(self.cursor_object, selection)
                if self.cursor_object == selection:
                    print('object pressing')
                    for f,a,k in zip(func,args,kwargs):
                        f(*a,**k)
        else:
            raise TypeError

        callback(callback_func, args=(func, args, kwargs),identifier=identifier)

    def set_viewport_selection_callback(self, viewport, is_in, callback_state, func):
        def callback_func():
            print('viewport selection')
            x,y = self.window_position

        state(callback_func)

    def is_in_viewport(self, viewport):
        a = viewport.get_vertex_from_window(0)
        b = viewport.get_vertex_from_window(2)
        x,y = self.window_position
        if a[0]< x < b[0] and a[1] < y < b[1]:
            return True
        else:
            return False

    @property
    def is_in_window(self):
        w,h = self._window.size
        x,y = self.window_position
        if 0<x<w and 0<y<h:
            return True
        else:
            return False

