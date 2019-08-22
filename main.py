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
# testing_vertex = [0,1],[5,0],[6,2],[3,3],[5,4],[3,5],[5,5],[6,3],[7,3],[8,7],[6,7],[5,6],[3,7],[1,5],[3,4],[2,2],[0,1]
# p = pr.Polygone(*testing_vertex)
# r = pr.tests.triangulatioin(p)
# # print(r)
# # print('end of code')
pla = pr.Plane()
pla2 = pr.Plane(o=[20, 20, 20], master=pla)

poi = pr.Point()
lin = pr.Line()
print(lin.WC)
lin.trans.move(pr.Vector(0,1,1))
print(lin.WC)
exit()

# print(pla2.family_tree.get_mother_of(pla2))
# print(pla2.family_tree._tree)
# print(pla.family_tree.get_mother_of(pla))
#
# poi = pr.Point().at(10,20,30)
# print(poi)
# print(poi.LC)
# print(poi.WC)
# print(pla)