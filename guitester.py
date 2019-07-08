from windowing.window import Window
from windowing.unnamedGUI.box import _Button
import weakref

class Test_gui:

    def __init__(self, mother):
        # self.left = Window(200,1000, 'left bar',None,None)
        # self.top.make_window_current()
        if 1 in mother.mouse.pressed_button:
            top = Window(1000,200,'top bar', None,None)
            @top.init
            def kkk():
                from windowing.unnamedGUI.box import _Button
                box1 = _Button(0, 0, 100, 100)
                box2 = _Button(100, 0, 100, 100)
                box3 = _Button(200, 0, 100, 100)

            @top.draw
            def kkk():
                box1.draw()
                box2.draw()
                box3.draw()