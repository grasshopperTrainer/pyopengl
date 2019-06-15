import glfw
from patterns.store_instances_dict import SID
from ..my_openGL.glfw_gl_tracker import Trackable_openGL as gl

class Position_registry:
    pass
    def new(self):
        pass


class Mouse(SID):

    def __init__(self, window):
        self._window = window

        self._scroll_offset = []
        self._callbacks = {
            'any' : {},
            'move' : {},
            'enter' : {},
            'exit' : {},
            'button' : {},
            'button_press' : {},
            'button_release' : {},
            'scroll' : {},
            'scroll_up' : {},
            'scroll_down' : {},
            'scroll_right' : {},
            'scroll_left' : {}
        }

        glfw.set_input_mode(self._window.glfw_window, glfw.STICKY_MOUSE_BUTTONS, glfw.TRUE)
        glfw.set_cursor_pos_callback(self._window.glfw_window, self.mouse_move_callback)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self.mouse_enter_callback)
        glfw.set_mouse_button_callback(self._window.glfw_window, self.mouse_button_callback)
        glfw.set_scroll_callback(self._window.glfw_window, self.mouse_scroll_callback)

        # self.instant_mouse_states = []

        self._button_state = {}
        self._cursor_state = {'onscreen':False,'moving':False}

        self._window_selection_area = []

        self._position_registry = Position_registry()

        self._just_released = False
        self._just_pressed = False

        self._mapping_source = None

        self._just_values = {
            'pressed':False,
            'released':False
        }

    def _callback_exec(func):

        def wrapper(self, *args, **kwargs):
            name = func.__name__.split('_callback')[0]
            for n,callback in self._callbacks[name].items():
                f, a, k, n, i = callback
                f(*a, **k)
                if i: # remove if instant
                    del self._callbacks[name][n]
            func(self, *args, **kwargs)
            self.any_callback()
        return wrapper

    def any_callback(self):
        for n, callback in self._callbacks['any'].items():
            f, a, k, n, i = callback
            f(*a, **k)
            if i:  # remove if instant
                del self._callbacks['any'][n]

    @_callback_exec
    def move_callback(self):
        pass
    @_callback_exec
    def enter_callback(self):
        pass
    @_callback_exec
    def exit_callback(self):
        pass
    @_callback_exec
    def button_callback(self):
        pass
    @_callback_exec
    def button_press_callback(self):
        self._just_values['pressed'] = True
        pass
    @_callback_exec
    def button_release_callback(self):
        self._just_values['released'] = True
        pass
    @_callback_exec
    def scroll_callback(self):
        pass
    @_callback_exec
    def scroll_right_callback(self):
        pass
    @_callback_exec
    def scroll_left_callback(self):
        pass
    @_callback_exec
    def scroll_up_callback(self):
        pass
    @_callback_exec
    def scroll_down_callback(self):
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
                f,a,k,n,i = callbacks[func_name]
                if function.__code__ == f.__code__:
                    exist = True
                else:
                    exist = False
                    count = 0
                    while True:
                        func_name = f'{func_name}{count}'
                        if func_name in callbacks:
                            count += 1
                        else:
                            break
            if not exist:
                self._callbacks[callback_name][func_name] = function, args, kwargs, name, instant

        return wrapper

    @_callback_setter
    def set_any_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_move_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_enter_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_exit_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_button_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_button_press_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_button_release_callback(self, func, args:tuple=(), kwargs:dict={}, name:str ='unknown',instant=False):
        pass
    @_callback_setter
    def set_scroll_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_scroll_up_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_scroll_down_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_scroll_right_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass
    @_callback_setter
    def set_scroll_left_callback(self, func, args:tuple=(), kwargs:dict={}, name:str='unknown',instant=False):
        pass

    def mouse_move_callback(self, context, xpos, ypos):
        self.move_callback()
        self._cursor_state['moving'] = True


    def mouse_enter_callback(self, context, entered):
        if entered:
            self.enter_callback()
            self._cursor_state['onscreen'] = True
        else:
            self.exit_callback()
            self._cursor_state['onscreen'] = False

    def mouse_button_callback(self, context, button, action, mods):
        # TODO why first mouse click behaves differently?
        if action is 1:
            self._button_state[button] = True
            self.button_press_callback()
        if action is 0:
            self._button_state[button] = False
            self.button_release_callback()
        self.button_callback()

    def mouse_scroll_callback(self, context, xoffset, yoffset):
        self._scroll_offset = xoffset, yoffset
        if xoffset >= 0:
            self.scroll_right_callback()
        else:
            self.scroll_left_callback()
        if yoffset >= 0:
            self.scroll_up_callback()
        else:
            self.scroll_down_callback()
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
        if self._mapping_source != None and not self.window.is_focused:
            wi, vp = self._mapping_source
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
        self._mapping_source = (source_window, source_viewport)

        # connect callbacks
        for name, callbacks in source_window.mouse._callbacks.items():
            callbacks[self] = (eval(f'self.{name}_callback'), (),{},'sys',False)

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
        return self._window.myframe.render_unit_registry.object(color)

    def set_object_selection_callback(self, selection, callback, func):
        def callback_func():
            print('object selection')
            if self.cursor_object == selection:
                func()
        callback(callback_func)

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

