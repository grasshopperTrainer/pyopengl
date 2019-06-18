class A:
    def a(self):
        pass

    def b(self):

        del self.a


k = A()

k.b()
