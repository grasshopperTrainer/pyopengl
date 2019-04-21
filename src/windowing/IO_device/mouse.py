import glfw
import inspect


class Mouse:

    def __init__(self, window):
        self._window = window

        self._button_pressed = []
        self._scroll_offset = []
        self._flag_cursor_onscreen = False

        event_list = ('move', 'enter', 'exit', 'click', 'click_press',
                      'click_release', 'scroll', 'scroll_up', 'scroll_down', 'scroll_right', 'scroll_left')
        self._event = dict(zip(event_list, len(event_list) * (None,)))

        glfw.set_cursor_pos_callback(self._window.glfw_window, self._callback_mouse_move)
        glfw.set_cursor_enter_callback(self._window.glfw_window, self._callback_mouse_enter)
        glfw.set_mouse_button_callback(self._window.glfw_window, self._callback_mouse_button)
        glfw.set_scroll_callback(self._window.glfw_window, self._callback_mouse_scroll)

    def __call__(self, func):
        source = inspect.getsource(func).splitlines()[2:]
        source = [line[4:] for line in source]

        functions = {}
        add = False
        # TODO put inside parser
        for i, line in enumerate(source):
            if line.find('def') == 0:
                end = line.find('(')
                name = line[3:end].strip()
                functions[name] = line + '\n'
            elif line[:4] == '    ':
                functions[name] += line + '\n'

        for func_name in functions:
            if func_name in self._event:
                self._event[func_name] = functions[func_name]

    def move(self, func):
        self._event['move'] = func

    def enter(self, func):
        self._event['enter'] = func

    def exit(self, func):
        self._event['exit'] = func

    def click(self, func):
        self._event['click'] = func

    def click_press(self, func):
        self._event['click_press'] = func

    def click_release(self, func):
        self._event['click_release'] = func

    def scroll(self, func):
        self._event['scroll'] = func

    def scroll_up(self, func):
        self._event['scroll_up'] = func

    def scroll_down(self, func):
        self._event['scroll_down'] = func

    def scroll_right(self, func):
        self._event['scroll_right'] = func

    def scroll_left(self, func):
        self._event['scroll_left'] = func

    def _callback_mouse_move(self, context, xpos, ypos):
        self._window._context_scope.run(self._event['move'])

    def _callback_mouse_enter(self, context, entered):
        if entered:
            self._window._context_scope.run(self._event['enter'])
            self._flag_cursor_onscreen = True
        else:
            self._window._context_scope.run(self._event['exit'])
            self._flag_cursor_onscreen = False

    def _callback_mouse_button(self, context, button, action, mods):
        if action is 1:
            self._button_pressed.append(button)
            self._window._context_scope.run(self._event['click_press'])
        if action is 0:
            try:
                self._button_pressed.remove(button)
            except:
                self._window._context_scope.run(self._event['click_release'])

        self._window._context_scope.run(self._event['click'])

    def _callback_mouse_scroll(self, context, xoffset, yoffset):
        self._scroll_offset = xoffset, yoffset
        if xoffset >= 0:
            self._window._context_scope.run(self._event['scroll_right'])
        else:
            self._window._context_scope.run(self._event['scroll_left'])
        if yoffset >= 0:
            self._window._context_scope.run(self._event['scroll_up'])
        else:
            self._window._context_scope.run(self._event['scroll_down'])

        self._window._context_scope.run(self._event['scroll'])

    @property
    def cursor_onscreen(self):
        return self._flag_cursor_onscreen

    @property
    def mouse_position(self):
        x, y = glfw.get_cursor_pos(self._window.glfw_window)
        # except:
        #     x, y = -1, -1
        return x, y

    @property
    def scroll_offset(self):
        return self._scroll_offset

    @property
    def pressed_button(self):
        return self._button_pressed
