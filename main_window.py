from windowing.window import Window
from windowing.renderer.BRO.testBRO import TestBRO

class Main_window(Window):
    def __init__(self):
        super().__init__(500,500,'main')
        print('window init')

        self.rect = TestBRO(0,0,100,100)
        self.rect2 = TestBRO(100,100,200,200)
        self.mouse.set_object_selection_callback(self.rect.unit,self.mouse.click_press,self.rect.switch_color)

    def _draw_(self):
        self.rect.draw()
        if len(self.mouse.pressed_button) != 0 or self.is_resized:
            self.viewports[0].open()
            self.rect2.draw()
            # if 0 in self.mouse.pressed_button and self.mouse.cursor_object == self.rect.unit:
            #     print('switch')
            #     self.rect.switch_color()
