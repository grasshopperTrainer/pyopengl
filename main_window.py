from windowing.window import Window
from windowing.renderer.BRO.testBRO import TestBRO
from windowing.my_openGL.glfw_gl_tracker import Trackable_openGL as gl

class Main_window(Window):
    def __init__(self):
        super().__init__(500,500,'main')
        print('window init')

        self.rect = TestBRO(0,0,100,100)
        self.rect2 = TestBRO(100,100,200,200)
        self.mouse.set_object_selection_callback(self.rect.unit,self.mouse.set_button_press_callback,self.rect.switch_color)
        self.viewports[0].camera.mode = 1
        self.viewports[0].camera.lookat([0,0,0],[200,200,300])

        self.viewports.new(0,0, 1., 100,'top_bar')
        self.viewports.new(lambda x:x-400, 100, 400, lambda x:x-100,'side_bar')
        self.viewports.new(20,20,lambda x:x-40,lambda x:x-40,'center').set_min()

        self.flag_topbar_created = False

        self.top_bar = None

    def _draw_(self):
        if len(self.mouse.pressed_button) != 0 or self.is_resized:
            self.viewports[0].open()
            self.viewports[0].clear(0,1,1,0)
            self.rect.draw()
            self.rect2.draw()
            if self.mouse.cursor_object == self.rect.unit:
                if not self.windows.has_window_named('top_bar'):
                    self.top_bar = Top_bar(self)

        if self.top_bar !=None:
            conditions = [
                not self.mouse.is_in_viewport(self.viewports['center']),
                self.top_bar.flag_following,
                self.mouse.is_in_window,
                self.top_bar.mouse.is_just_released
            ]
            if all(conditions):
                self.top_bar.move_to(self.get_vertex(0),(0,0))
                self.top_bar.flag_follow_active = False
                self.top_bar.config_visible(False)
                self.top_bar.pin_on_viewport(self, 'top_bar', 0)
                self.top_bar.mouse.set_map_from_window(self, 'top_bar')
                # self.top_bar.mouse.reset_map_from_window()


class Top_bar(Window):
    def __init__(self, master_window):
        self.config_visible(False)
        super().__init__(1000,100, 'top_bar',None, master_window)
        self.set_window_z_position(1)

        self.follow_window_iconify(master_window)
        self.follow_window_close(master_window)

        self.position = (500,500)
        self.config_visible(True)
        self.config_decorated(False)

        self.viewports.new(0.1,0.1,0.8,0.8, 'center')

        self.flag_follow_active = True
        self.flag_following = False

        self.rect = TestBRO(0,0,100,100)

        self.viewports[0].open()
        self.viewports[0].clear_instant(0,1,0,1)

    def _draw_(self):
        if len(self.keyboard.pressed_keys) != 0:
            print('bar key pressed')

        def f(): print('top bar clicking',self.mouse.window_position)
        self.mouse.set_button_press_callback(f)

        if self.flag_follow_active:
            if not self.mouse.is_in_viewport(self.viewports['center']) and self.mouse.is_in_window and 0 in self.mouse.pressed_button:
                if not self.flag_following:
                    self.flag_following = True
                    self.ref_window_pos = self.mouse.window_position

            if self.flag_following:
                self.move_to(self.mouse.screen_position,self.ref_window_pos)

            if not self.mouse.is_any_pressed:
                if self.flag_following:
                    self.flag_following = False

