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
testing_vertex = [0,1],[5,0],[6,2],[3,3],[5,4],[3,5],[5,5],[6,3],[7,3],[8,7],[6,7],[5,6],[3,7],[1,5],[3,4],[2,2],[0,1]
p = pr.Polyline(*testing_vertex)
r = pr.tests.triangulatioin(p)
print(r)
print('end of code')