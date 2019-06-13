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

        events = ('move', 'enter', 'exit', 'click', 'click_press',
                      'click_release', 'scroll', 'scroll_up', 'scroll_down', 'scroll_right', 'scroll_left')
        empty_lists = [[] for i in range(len(events))]
        self._event = dict(zip(events, empty_lists))

        glfw.set_input_mode(self._window.glfw_window, glfw.STICKY_MOUSE_BUTTONS, glfw.TRUE)
        glfw.set_cursor_pos_callback(self._window.glfw_window, self._callback_mouse_move)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self._callback_mouse_enter)
        glfw.set_mouse_button_callback(self._window.glfw_window, self._callback_mouse_button)
        glfw.set_scroll_callback(self._window.glfw_window, self._callback_mouse_scroll)

        self.instant_mouse_states = []

        self._button_state = {}
        self._cursor_state = {'onscreen':False,'moving':False}

        self._window_selection_area = []

        self._position_registry = Position_registry()

        self._just_released = False
        self._just_pressed = False

        self._mapping_source = None
    # def __call__(self, func):
    #     source = inspect.getsource(func).splitlines()[2:]
    #     source = [line[4:] for line in source]
    #
    #     functions = {}
    #     add = False
    #     # TODO put inside parser
    #     for i, line in enumerate(source):
    #         if line.find('def') == 0:
    #             end = line.find('(')
    #             name = line[3:end].strip()
    #             functions[name] = line + '\n'
    #         elif line[:4] == '    ':
    #             functions[name] += line + '\n'
    #
    #     for func_name in functions:
    #         if func_name in self._event:
    #             self._event[func_name] = functions[func_name]

    def move(self, func):
        self._event['move'].append(func)

    def enter(self, func):
        self._event['enter'].append(func)

    def exit(self, func):
        self._event['exit'].append(func)

    def click(self, func):
        self._event['click'].append(func)

    def click_press(self, func):
        self._event['click_press'].append(func)

    def click_release(self, func):
        self._event['click_release'].append(func)

    def scroll(self, func):
        self._event['scroll'].append(func)

    def scroll_up(self, func):
        self._event['scroll_up'].append(func)

    def scroll_down(self, func):
        self._event['scroll_down'].append(func)

    def scroll_right(self, func):
        self._event['scroll_right'].append(func)

    def scroll_left(self, func):
        self._event['scroll_left'].append(func)

    def _callback_mouse_move(self, context, xpos, ypos):
        self._run_all_func(when='move')
        self._cursor_state['moving'] = True

    def _callback_mouse_enter(self, context, entered):
        if entered:
            self._run_all_func(when='enter')
            self._cursor_state['onscreen'] = True
        else:
            self._run_all_func(when='exit')
            self._cursor_state['onscreen'] = False

    def _callback_mouse_button(self, context, button, action, mods):
        # TODO why first mouse click behaves differently?
        if action is 1:
            self._button_state[button] = True
            self._run_all_func(when='click_press')
            self._just_pressed = True
        if action is 0:
            self._button_state[button] = False
            self._run_all_func(when='click_release')
            self._just_released = True
        self._run_all_func(context,button,action,mods,when='click')

    def _callback_mouse_scroll(self, context, xoffset, yoffset):
        self._scroll_offset = xoffset, yoffset
        if xoffset >= 0:
            self._run_all_func(when='scroll_right')
        else:
            self._run_all_func(when='scroll_left')
        if yoffset >= 0:
            self._run_all_func(when='scroll_up')
        else:
            self._run_all_func(when='scroll_down')

        self._run_all_func(when='scroll')

    def _run_all_func(self, *args, when):
        for event in self._event[when]:
            if hasattr(event,'__self__'):
                if event.__self__.__class__ is self.__class__:
                    event(*args)
            else:
                event()
            # self._window._context_scope.run(event)

    def instant_press_button(self, button: int):
        """
        Triger one-time mouse button click action.
        :param button: button index number
        :return:
        """
        self._button_state[button] = True
        # reset action
        self.instant_mouse_states.append([self._button_state, button, False])

    def instant_mouse_onscreen(self):
        self._flag_cursor_onscreen = True
        self.instant_mouse_states.append([self._cursor_state,'onscreen', False])

    def reset(self):
        self._just_released = False
        self._just_pressed = False

        for type,key,state in self.instant_mouse_states:
            type[key] = state
        self.instant_mouse_states = []
        self._cursor_state['moving'] = False
    @property
    def is_just_released(self):
        return self._just_released

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

    def set_mapping_from_window(self, source_window, source_viewport):
        if isinstance(source_viewport, (int, str)):
            source_viewport = source_window.viewports[source_viewport]
        self._mapping_source = (source_window, source_viewport)
        source_window.mouse.click(self._callback_mouse_button)

    def reset_mapping_from_window(self):
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

        with self._window.myframe:
            gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT1)
            color = gl.glReadPixels(x,y,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE)
            return self._window.myframe.render_unit_registry.object(color)

    def set_object_selection_callback(self, selection, state, func):
        def callback_func():
            print('object selection')
            if self.cursor_object == selection:
                func()
        state(callback_func)

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

