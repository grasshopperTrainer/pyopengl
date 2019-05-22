class _Layer:
    def __init__(self):
        self._objects = []
        self._itercount = 0

    def __next__(self):
        if self._itercount < len(self._objects):
            self._itercount += 1

            return self._objects[self._itercount - 1]
        else:
            self._itercount = 0
            raise StopIteration

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        return self

    def add(self, object):
        self._objects.append(object)

    def hide(self):
        for obj in self._objects:
            obj._hide_()

    def stop(self, set: bool = None):
        for obj in self._objects:
            obj._stop_(set)


class Layers:

    def __init__(self, fbl):
        self._layers = {'default': _Layer()}
        self._window = fbl

    def __getitem__(self, item) -> _Layer:
        if isinstance(item, str):
            item = str(item)
            try:
                return self._layers[item]
            except:
                KeyError(f"no such layer named '{item}'")

        if isinstance(item, int):
            n = list(self._layers.keys())[item]
            return self._layers[n]


    def __str__(self):
        block = f"(window)'{self._window.name}' has layers:\n"
        if len(self._layers) == 0:
            block += '    None\n'
        else:
            for layer in self._layers:
                block += f"    (layer)'{layer}':\n"

                if len(self._layers[layer]) == 0:
                    block += '        None\n'
                else:
                    for item in self._layers[layer]:
                        block += f'        {item}\n'
        block += '- layers end'

        return block

    def new(self, name):
        self._layers[name] = _Layer()
