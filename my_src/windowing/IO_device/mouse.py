import glfw
from patterns.store_instances_dict import SID
from ..my_openGL.glfw_gl_tracker import Trackable_openGL as gl

class Mouse(SID):

    def __init__(self, window):
        self._window = window

        self._scroll_offset = []

        events = ('move', 'enter', 'exit', 'click', 'click_press',
                      'click_release', 'scroll', 'scroll_up', 'scroll_down', 'scroll_right', 'scroll_left')
        empty_lists = [[] for i in range(len(events))]
        self._event = dict(zip(events, empty_lists))
        glfw.set_cursor_pos_callback(self._window.glfw_window, self._callback_mouse_move)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self._callback_mouse_enter)
        glfw.set_mouse_button_callback(self._window.glfw_window, self._callback_mouse_button)
        glfw.set_scroll_callback(self._window.glfw_window, self._callback_mouse_scroll)


        self.instant_mouse_states = []

        self._button_state = {}
        self._cursor_state = {'onscreen':False,'moving':False}

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
        if action is 0:
            self._button_state[button] = False
            self._run_all_func(when='click_release')
        self._run_all_func(when='click')

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

    def _run_all_func(self, when):
        for event in self._event[when]:
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
        for type,key,state in self.instant_mouse_states:
            type[key] = state
        self.instant_mouse_states = []
        self._cursor_state['moving'] = False


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
    def mouse_position(self):
        # flipped to match openGL buffer order
        x, y = glfw.get_cursor_pos(self._window.glfw_window)
        y = self._window.height - y
        # except:
        #     x, y = -1, -1
        return x, y

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
        x,y = self.mouse_position

        self._window.make_window_current()
        self._window.myframe.begin()
        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT1)
        color = gl.glReadPixels(x,y,1,1,gl.GL_RGB,gl.GL_UNSIGNED_BYTE)
        self._window.myframe.end()
        return self._window.myframe.render_unit_registry.object(color)

    def set_object_selection_callback(self, selection, state, func):
        def callback_func():
            print('selection')
            if self.cursor_object == selection:
                func()
        state(callback_func)
