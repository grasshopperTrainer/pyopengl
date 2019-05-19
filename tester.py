# # # from patterns.update_check_descriptor import UCD
# # #
# # #
# # #
# # #
# # # class C:
# # #     a = UCD()
# # #     b = UCD()
# # #     c = UCD()
# # #     def __init__(self, mark):
# # #         print(self.a)
# # #         self.a = mark
# # #         print(self.a)
# # #         self.b = mark*2
# # #         self.c = mark*3
# # #         pass
# # #
# # # #
# # # c = C('a')
# # # cc = C('b')
# # # ccc = C('c')
# # # a = UCD()
# # # print(a._DIC)
# # # print(UCD._DIC)
# # # for i in UCD._DIC.items():
# # #     print(i[0])
# # #     for ii in i[1].items():
# # #         print(list(ii[1].items()))
# # #
# # # # class T:
# # # #     a = 'a'
# # # #     b = 'b'
# # # #     def __init__(self,f,s):
# # # #         self.a = f
# # # #     def d(self):
# # # #         print(self.b, id(self.b))
# # # #
# # # # a = T(1,2)
# # # # b = T(3,4)
# # # # print(a.a,b.a)
# # # # a.d()
# # # # b.d()
# #
# # import numpy as np
# #
# # a = np.array((0,1,2))
# # print(a,type(a))
# # dtypes = np.dtype([('instance', '<U2'),('value',int),('updated',int)])
# #
# # n = np.zeros(1,dtypes)
# # n2 = np.zeros(1,dtypes)
# #
# #
# # print(n)
# # n[0][0] = 'first'
# # n['instance'][0] = 'first'
# # n['value'][0] = 10
# # n['instance'][0] = 'dd'
# # n.resize(4)
# # print(n)
# # new = n.dtype
# # print(new)
# # print(new[0],type(new[0]))
# # print(new[0])
# # new[0] = np.dtype([(new[0].name,'<U10')])
# # n['instance'][0] = '101010'
# # print(n)
#
# a = {"1":1,"2":2}
# for k,v, in a:
#     print(k,v)
print([[],]*3)

for i in range(-2):
    print(I)

a = [[],[]]
b = [[],[]]
c = b + [[],]

for i in a:
    print(id(i))
for i in b:
    print(id(i))
for i in c:
    print(id(i))
print(b)