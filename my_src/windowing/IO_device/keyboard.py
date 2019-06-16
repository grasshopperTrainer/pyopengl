import glfw


class Keyboard:
    str_num_dict = {
        None: -1,
        ' ': 32,
        "'": 39,
        ',': 44,
        '-': 45,
        '.': 46,
        '/': 47,
        '0': 48,
        '1': 49,
        '2': 50,
        '3': 51,
        '4': 52,
        '5': 53,
        '6': 54,
        '7': 55,
        '8': 56,
        '9': 57,
        ';': 59,
        '=': 61,
        'a': 65,
        'b': 66,
        'c': 67,
        'd': 68,
        'e': 69,
        'f': 70,
        'g': 71,
        'h': 72,
        'i': 73,
        'j': 74,
        'k': 75,
        'l': 76,
        'm': 77,
        'n': 78,
        'o': 79,
        'p': 80,
        'q': 81,
        'r': 82,
        's': 83,
        't': 84,
        'u': 85,
        'v': 86,
        'w': 87,
        'x': 88,
        'y': 89,
        'z': 90,
        '{': 91,
        '\W': 92,
        '}': 93,
        '`': 96,
        'wld1': 161,
        'wld2': 162,
        'esc': 256,
        'ent': 257,
        'tab': 258,
        'bks': 259,
        'ins': 260,
        'del': 261,
        'rig': 262,
        'lef': 263,
        'dwn': 264,
        'up': 265,
        'pup': 266,
        'pdn': 267,
        'hom': 268,
        'end': 269,
        'cpl': 280,
        'scl': 281,
        'nul': 282,
        'prs': 283,
        'pau': 284,
        'f1': 290,
        'f2': 291,
        'f3': 292,
        'f4': 293,
        'f5': 294,
        'f6': 295,
        'f7': 296,
        'f8': 297,
        'f9': 298,
        'f10': 299,
        'f11': 300,
        'f12': 301,
        'f13': 302,
        'f14': 303,
        'f15': 304,
        'f16': 305,
        'f17': 306,
        'f18': 307,
        'f19': 308,
        'f20': 309,
        'f21': 310,
        'f22': 311,
        'f23': 312,
        'f24': 313,
        'f25': 314,
        'f26': 320,
        'kp1': 321,
        'kp2': 322,
        'kp3': 323,
        'kp4': 324,
        'kp5': 325,
        'kp6': 326,
        'kp7': 327,
        'kp8': 328,
        'kp9': 329,
        'kp.': 330,
        'kp/': 331,
        'kp*': 332,
        'kp-': 333,
        'kp+': 334,
        'kpent ': 335,
        'kp= ': 336,
        'lsft ': 340,
        'lcnt ': 341,
        'lalt ': 342,
        'lsup ': 343,
        'rsft ': 344,
        'rcnt ': 345,
        'ralt ': 346,
        'rsup ': 347,
        'men ': 348,
        'lst ': 348,
    }

    def __init__(self, window):
        self._window = window

        self._pressed_keys = []

        event_list = ('action', 'press', 'release')
        self._event = dict(zip(event_list, len(event_list) * (None,)))

        glfw.set_key_callback(self._window._glfw_window, self.key_callback)
        glfw.set_char_callback(self._window._glfw_window,self.char_callback)

    def __call__(self, func):
        self._event['action'] = func

    def delete(self):

        self._window = None

        repos = [
            (glfw._key_callback_repository, self.key_callback),
            (glfw._char_callback_repository, self.char_callback)
        ]
        for repo, func in repos:
            to_delete = None
            for n, f in repo.items():
                if f[0] == func:
                    to_delete = n

            if to_delete != None:
                del repo[to_delete]


    def __del__(self):
        print(f'gc, Keyboard {self}')

    def action(self, func):
        self._event['action'] = func

    def press(self, func):
        self._event['press'] = func

    def release(self, func):
        self._event['release'] = func

    def key_callback(self, instance, key, scancode, action, mods):
        if action is 1:
            self.pressed_keys.append(key)
        if action is 0:
            self.pressed_keys.remove(key)


    def char_callback(self, window, codepoint):
        pass


    def trans(self, key):
        return self.__class__.str_num_dict[key]

    @property
    def pressed_keys(self):
        return self._pressed_keys

    def key_pressed(self, *keys):
        pressed = True
        for key in keys:
            pressed = pressed and self.trans(key) in self.pressed_keys
        return pressed

    def keys(self):
        return self.__class__.str_num_dict.keys()
