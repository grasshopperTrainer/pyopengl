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
            if hasattr(obj, '_hide_'):
                obj._hide_()

    def stop(self):
        for obj in self._objects:
            if hasattr(obj, '_stop_'):
                obj._stop_()


class Layers:

    def __init__(self):
        self._layers = {}

    def __getitem__(self, item) -> _Layer:
        if isinstance(item, (int, str)):
            item = str(item)
            try:
                return self._layers[item]
            except:
                self._layers[item] = _Layer()
                return self._layers[item]

    def __str__(self):
        block = '- layers consists of:\n'
        if len(self._layers) == 0:
            block += '    None\n'
        else:
            for layer in self._layers:
                block += f"    (layer) '{layer}':\n"

                if len(self._layers[layer]) == 0:
                    block += '        None\n'
                else:
                    for item in self._layers[layer]:
                        block += f'        {item}\n'
        block += '- layers end'

        return block
