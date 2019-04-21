from patterns.strict_method_implant import SMI


class Layerable(SMI):
    # def __new__(cls, *args, **kwargs):
    #     print(super())
    #     self = super().__new__(cls)
    #     self.__init__(*args, **kwargs)
    #     return self

    undefined_exception = Exception("'stop' method should be defined for layerable")

    def _stop_(self):
        pass

    def _hide_(self):
        pass

    def _draw_(self):
        pass
