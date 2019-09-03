# from windowing.window import Window
# from main_window import Main_window
# Window.glfw_init()
#
# Main_window()
# # Main_window()
# # Main_window()
# # Main_window()
#
# Window.run_single_thread()

import prohopper as pr
import time
import numpy as np
import random
testing_vertex = [0,1],[5,0],[6,2],[3,3],[5,4],[3,5],[5,5],[6,3],[7,3],[8,7],[6,7],[5,6],[3,7],[1,5],[3,4],[2,2],[0,1]
p = pr.Polyline(*testing_vertex)
r = pr.tests.triangulatioin(p)
print(r)
print('end of code')

# how to benchmark?????? generate points and do move calculation and measure?
# n = 100000
# points = []
# raws = np.empty(n,dtype=np.ndarray)
# for i in range(n):
#     a = [random.random() for i in range(3)]
#     p = pr.Point(*a)
#     points.append(p)
#     raws[i] = p.raw
#
# # s = time.time()
# # summ = points[0].raw
# # for p in points[1:]:
# #     summ += p.raw
# # e = time.time()
# # print(f'{e-s}')
# #
# # s = time.time()
# # k = np.sum(raws)
# # e = time.time()
# # print(f'{e-s}')


# s = time.time()
# d = np.hstack(raws)
# e = time.time()
# print(d)
# print(d.shape)
# print(f'{e-s}')
#
# s = time.time()
# def it():
#     l = len(raws)
#     i = 0
#     while i < l:
#         yield raws[i][:]
#         i += 1
# k = it()
# d = np.fromiter(it(),dtype=np.float64)
# e = time.time()
# print(d)
# print(d.shape)
# print(f'{e-s}')
