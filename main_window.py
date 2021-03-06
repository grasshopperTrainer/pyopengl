from windowing.window import Window
import glfw
from windowing.unnamedGUI import *
from windowing.renderer.cleaner import Cleaner

import gc
import freetype as ft

import numpy as np
from windowing.frame_buffer_like.frame_buffer_like_bp import FBL

from windowing.my_openGL.unique_glfw_context import Unique_glfw_context

class Main_window(Window):
    def __init__(self):
        super().__init__(500,500,'main')

        # self.rect2 = TestBRO(100,100,200,200)

        # menu = self.viewports.new(0,0,1.,50, 'menu_bar')
        self.layers.new(-1)
        self.layers.new(1)
        # self.layers.new(-3)
        main_viewport = self.layers[1].viewports.new(0,0,1.0,1.0,'main 3d space')
        main_viewport.camera.set_test_mouse(self.mouse)
        main_viewport.camera.set_mode(1)
        # main_viewport.camera.trans_look_at([0, 0, 0], [100, 0, 100])
        main_viewport.camera.trans_move(100,100,100)
        # main_viewport.camera.trans_pitch(30)
        main_viewport.camera.trans_look_at([0,0,0])

        # main_viewport.camera.trans_move(0,0,100)
        # main_viewport.camera.trans_rotate(30,0,0)

        # self.rect = Button_press(0,0,100,100,self)
        # #
        # # right buttons
        # self.button_iconize = Button_hover_press(0,0,50,50)
        # self.button_maximize = Button_hover_press(50,0,50,50)
        # self.button_close = Button_hover_press(100,0,50,50)
        #
        # self.button_iconize.set_to_pressed_callback(
        #     lambda: self.config_iconified(True),
        # )
        # self.button_maximize.set_switch_callback(
        #     lambda: (self.config_maximize(not self.is_maximized)),
        # )
        # self.button_close.set_to_pressed_callback(
        #     lambda: self.config_window_close(),
        # )
        # self.right_buttons = Block(lambda x:x-150,lambda y:y-50,150,50,self)
        # self.right_buttons.is_mother_of( self.button_iconize, self.button_maximize, self.button_close)
        # # print(self.viewports.get_current())
        # # exit()
        # self.left_buttons = Block(0, lambda  x:x-50, 300, 50, self)
        # buttons = []
        # for i in range(3):
        #     b = Button_hover_press(i*100,0,100,50)
        #     b.is_child_of(self.left_buttons)
        #     buttons.append(b)
        # self.menu_list = Block(0, -250,100,250)
        # self.menu_list.is_child_of(buttons[0])
        # self.menu_list._flag_update = False
        # for i in range(5):
        #     b = Button_hover_press(0,i*50,100,50)
        #     # b._flag_draw = False
        #     b.color0 = 1,1,0,1
        #     b.is_child_of(self.menu_list)
        #
        # buttons[0].set_switch_callback(
        #     lambda: (self.menu_list.switch_activation_with_children(),
        #              self.refresh_all() if not self.menu_list.is_active else self.menu_list.draw())
        # )
        # buttons[0].set_reset_pressed_elsewhere(True)
        source ='''
        first
         a
          n
         aa
          mm
          mmm
        second
         b
          dd
          dd
          d
          d
         d
         f
         d
         d
         f
         g
         s
         d
         f
         g
        third
         c
         cc
         ccc
          kk
          k
          kkk
           l
            ll
        '''
        # self.test = Complex_button_list(source, Button_hover_press, 100, 50, self)
        #
        # self.test.master.x = 0
        # self.test.master.y = lambda y:y-50
        # self.test.master.children[0].pack_children_horizontal()
        # for button in self.test.master.children[0].children:
        #     button.pack_children_vertical(reverse=True)
        #
        #     button.children[0].pack_children_vertical(origin=(0,button.children[0].pixel_h),reverse=True)
        #
        #     for member in button.family[2:]:
        #         if isinstance(member, Button_list):
        #             member.x, member.y = 1.0, member.mother.pixel_h - member.pixel_h
        #             print(member.vertex())
        #             member.pack_children_vertical(origin=(0,member.pixel_h),reverse=True)

        # exit()

        self.filledbox_back = Filled_box(0,0,100,50,self)
        self.red_box = Filled_box(10, 10, 100, 100, self)
        self.red_box.fill_color = 1, 0, 0, 0.9
        self.blue_box = Filled_box(20, 20, 100, 100, self)
        self.blue_box.fill_color = 0.5, 0.5, 1, 0.8
        # self.text_box = Textbox(0,50,200,50,self,'Hellow world',50)
        # self.text_box.text_fill_color = 1,0,0,1
        # print(ft)
        # exit()

        # print(self.face.load_char())

        self.set_window_resize_callback(self.refresh_all)
        self.refresh_all()
    #
    def _draw_(self):

        with self.layers[1] as l:
            with l.viewports[1] as v:
                v.clear()
                self.filledbox_back.draw()
        pass

    def refresh_all(self):
        print('refreshing')
        # self.layers[0].viewports[1].clear()
        # with self.layers[0]:
        #     self.rect.draw()
        with self.layers[0]:
            self.red_box.draw()
        with self.layers[1]:
            self.filledbox_back.draw()
        with self.layers[-1]:
            self.blue_box.draw()
            pass
            # self.cleaner.clear(1,0,1,1)
            # self.text_box.draw()
            pass
            # self.test.draw()
            # self.buttonlist.draw()
            # self.left_buttons.draw()
            # self.right_buttons.draw()
    def clearing(self):
        self.viewports[0].clear()


class Top_bar(Window):

    def __init__(self, mother):
        self.config_visible(False)
        super().__init__(1000,100, 'top_bar',None, mother)
        with self.myframe:
            self.follow_window_iconify(mother)
            self.follow_window_close(mother)

            self.position = (500,500)
            self.config_visible(True)
            self.config_decorated(False)

            self.viewports.new(0.1,0.1,0.8,0.8, 'center')

            self.flag_follow_active = True
            self.flag_following = False

    def _draw_(self):
        if self.flag_follow_active:
            if not self.mouse.is_in_LCS(self.viewports['center']) and self.mouse.is_in_window and 0 in self.mouse.pressed_button:
                if not self.flag_following:
                    self.flag_following = True
                    self.ref_window_pos = self.mouse.window_position

            if self.flag_following:
                self.move_to(self.mouse.screen_position,self.ref_window_pos)

            if not self.mouse.is_just_pressed:
                if self.flag_following:
                    self.flag_following = False
        pass
        pass

