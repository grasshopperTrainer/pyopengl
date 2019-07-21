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
        self.viewports.new(0, lambda x:x - 150, 1., 100,'top_bar')
        self.viewports.new(lambda x:x-400, 100, 400, lambda x:x-100,'side_bar')
        self.viewports.new(20,20,lambda x:x-40,lambda x:x-40,'center').set_min()
        self.layers.new(1)
        self.layers.new(-1)

        self.flag_topbar_created = False
        self.top_bar = None

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
        # source ='''
        # first
        #  a
        #   n
        #  aa
        #   mm
        #   mmm
        # second
        #  b
        #   dd
        #   dd
        #   d
        #   d
        # third
        #  c
        #  cc
        #  ccc
        #   kk
        #   k
        #   kkk
        #    l
        #     ll
        # '''
        # self.test = Complex_button_list(source, Button_hover_press, 50, 50, self)
        # self.buttonlist = Button_list(self, 1, Button_hover_press, 0,200,100)
        # self.buttonlist.add()
        # self.buttonlist.add()
        # self.buttonlist.append(Button_hover_press(0,0,200,100))
        # self.kkk = Button_list(self, 0, Button_hover_press,4,400,100)
        self.filledbox_back = Filled_box(0,0,100,100,self)
        self.filledbox_middle = Filled_box(50,50,100,100,self)
        self.filledbox_middle.fill_color = 1,1,0,1
        self.filledbox_front = Filled_box(100,100,100,100,self)
        self.filledbox_front.fill_color = 0,0,1,1
        self.text_box = Textbox('Hellow world',0,50,100,100,self)
        # print(ft)
        # exit()

        # print(self.face.load_char())

        self.set_window_resize_callback(self.refresh_all)
        self.refresh_all()
    #
    def _draw_(self):
        # if self.mouse.is_in_area([0,0,],[100,100]) and self.mouse.is_just_pressed:
        #     if not self.windows.has_window_named('top_bar'):
        #         self.top_bar = Top_bar(self)
        #         pass
        #     else:
        #         if self.top_bar.flag_follow_active:
        #             self.top_bar.config_window_close()
        #             self.top_bar = None
        #             print('top bar removed')
        #         else:
        #             self.top_bar.unpin_from_viewport(self, self.viewports['top_bar'])
        #             self.top_bar.config_visible(True)
        #             self.top_bar.flag_follow_active = True
        #             self.refresh_all()
        #
        # if self.top_bar != None:
        #     # TODO extra processing for looking all conditions at once
        #     conditions = [
        #         self.mouse.is_in_LCS(self.viewports['top_bar']),
        #         self.top_bar.flag_following,
        #         self.mouse.is_in_window,
        #         self.top_bar.mouse.is_just_released,
        #         self.top_bar.flag_follow_active
        #     ]
        #     if all(conditions):
        #         self.top_bar.move_to(self.get_vertex(0),(0,0))
        #         self.top_bar.flag_follow_active = False
        #         self.top_bar.config_visible(False)
        #         self.top_bar.pin_on_viewport(self, 'top_bar', 0)
        #         self.top_bar.mouse.set_map_from_window(self, 'top_bar')
        pass

    def refresh_all(self):
        print('refreshing')
        with self.viewports[0]:
            self.viewports[0].clear()
            # with self.layers[0]:
            #     self.rect.draw()
            with self.layers[0]:
                self.filledbox_back.draw()
            with self.layers[1]:
                self.filledbox_middle.draw()
                # self.cleaner.clear(1,0,1,1)
            with self.layers[-1]:
                self.filledbox_front.draw()
                self.text_box.draw()
            # with self.layers[-1]:
                # self.test.draw()
                # self.buttonlist.draw()
                # self.left_buttons.draw()
                # self.right_buttons.draw()

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

