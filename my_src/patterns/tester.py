class C:
    def __init__(self):
        self.a = 10
    def __del__(self):
        print('deleting')
        print(self)
        self.a = 20

a = C()
b = C()
a.__del__()
print(a.a)
print(b.a)