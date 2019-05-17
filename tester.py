from patterns.update_check_descriptor import UCD




class C:
    a = UCD()
    b = UCD()
    c = UCD()
    def __init__(self, mark):
        print(self.a)
        self.a = mark
        print(self.a)
        self.b = mark*2
        self.c = mark*3
        pass

#
c = C('a')
cc = C('b')
ccc = C('c')
a = UCD()
print(a._DIC)
print(UCD._DIC)
for i in UCD._DIC.items():
    print(i[0])
    for ii in i[1].items():
        print(list(ii[1].items()))

# class T:
#     a = 'a'
#     b = 'b'
#     def __init__(self,f,s):
#         self.a = f
#     def d(self):
#         print(self.b, id(self.b))
#
# a = T(1,2)
# b = T(3,4)
# print(a.a,b.a)
# a.d()
# b.d()