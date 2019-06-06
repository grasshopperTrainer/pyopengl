from windowing.window import Window
from windowing.renderer.BRO.testBRO import TestBRO

class Main_window(Window):
    def __init__(self):
        super().__init__(500,500,'main')
        print('window init')

        self.rect = TestBRO(0,0,100,100)
        self.rect2 = TestBRO(100,100,200,200)
        self.mouse.set_object_selection_callback(self.rect.unit,self.mouse.click_press,self.rect.switch_color)
        self.viewports[0].camera.mode = 1
        self.viewports[0].camera.lookat([0,0,0],[200,200,300])
    def _draw_(self):
        if len(self.mouse.pressed_button) != 0 or self.is_resized:
            self.viewports[0].open()
            self.viewports[0].clear(0,1,1,0)
            self.rect.draw()
            self.rect2.draw()
            if self.mouse.cursor_object == self.rect.unit:
                Top_bar()
            #     print('switch')
            #     self.rect.switch_color()

class Top_bar(Window):
    def __init__(self):
        super().__init__(1000,100, 'top_bar')

    def _draw_(self):
        if self.mouse.is_any_pressed or self.is_resized:
            pass
