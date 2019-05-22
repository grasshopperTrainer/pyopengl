from patterns.update_check_descriptor import UCD
from patterns.strict_method_implant import SMI

class A(SMI):


    ddd = None
    s = SMI.should_arg()

    def a(self):
        pass

    def b(self):
        pass


    @SMI.should_func
    def d(self):
        pass

    @SMI.should_func
    @property
    def p(self):
        pass




class B(A):
    a = 10

    def k(self):
        pass
    pass

    def p(self):
        pass

    def s(self):
        pass
    @property
    def kkk(self):
        pass



b = B()
