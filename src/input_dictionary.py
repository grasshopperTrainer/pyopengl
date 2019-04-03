import glfw
import inspect



class _Input_dicts:
    # read keys from glfw.__init__ and make dictionalry of keys and buttons
    _module = inspect.getmodule(glfw)
    _source = inspect.getsource(_module).splitlines()

    def _con_dict(lines, keywordss: list):
        dicts = [{}] * len(keywordss)
        for line in lines:
            for index, keywords in enumerate(keywordss):
                dict = dicts[index]
                key_header_in_line = False
                if '=' in line:
                    for key in keywords:
                        if key in line:
                            if line.index(key) is 0:
                                key_header_in_line = True
                                break

                    if key_header_in_line:
                        key_value = [i.strip() for i in line.split('=')]
                        try:
                            # for unsigned int and signed int
                            dict[key_value[0]] = int(key_value[1])
                        except:
                            # for hex
                            if key_value[1][:2] == '0x':
                                dict[key_value[0]] = int(key_value[1], 16)
                            # for value directing to another
                            else:
                                dict[key_value[0]] = dict[key_value[1]]

        return dicts

    _dicts = _con_dict(_source, [['KEY', 'MOD'], ['MOUSE'], ['JOYSTICK']])

    keyboard = _dicts[0]
    mouse = _dicts[1]
    joystick = _dicts[2]
    # @property
    # def keyboard_dict(self):
    #
    #     return self.__class__._dicts[0]
    # @property
    # def mouse_dict(self):
    #     return self.__class__._dicts[1]
    # @property
    # def joystick_dict(self):
    #     return self.__class__._dicts[2]

