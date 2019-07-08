from windowing.window import Window
import glfw
from windowing.renderer.BRO.testBRO import TestBRO
from windowing.unnamedGUI import *
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
        # print(self.viewports[1].vertex())
        # print(self.viewports[1].get_glfw_vertex(0, 1, 2, 3))
        # exit()
        self.flag_topbar_created = False
        self.top_bar = None

        self.rect = Button_hover(0,0,100,100,self,self.viewports[0])
        # # ui menu bar
        # self.button0 = Button_press(0., 0., 50, 50)
        # self.button1 = Button_press(50, 0., 50, 50)
        # self.button2 = Button_press(100, 0., 50, 50)
        #
        # self.button0_list = Block(0., 0.,50,-200,self,self.viewports[0])
        # self.button0_list.fill_color = 1,0,0,1
        # self.button0_list.is_child_of(self.button0)
        #
        # self.button0_list_buttons = []
        # for i in range(5):
        #     height = 50
        #     button = Button_hover_press(0,-(i+1)*height ,1.0,height)
        #     button.disable_all_draw()
        #     self.button0_list.is_mother_of(button)
        #
        # # right buttons
        # self.button_close = Button_hover_press(lambda x:x-50,0,50,50)
        # self.button_maximize = Button_hover_press(lambda x:x-100,0,50,50)
        # self.button_iconize = Button_hover_press(lambda x:x-150,0,50,50)
        #
        # # Button_hover_press.state
        # self.menu_block = Block(0, lambda x: x - 50, 1.0, 50, window=self, viewport=self.viewports[0])
        # # print(self.menu_block.mother)
        # # exit()
        # self.menu_block.fill_color = 0,1,0,1
        # self.menu_block.is_mother_of(self.button0, self.button1, self.button2,
        #                                   self.button_close, self.button_maximize, self.button_iconize)
        # # self.menu_block.align_horrizontal(self.button0, self.button1, self.button2)
        # # print(self.menu_block.vertex())
        # # print(self.button0.vertex())
        # # exit()
        # self.button0.set_1_just_callback(lambda: (self.button0_list.enable_all_draw(), self.button0_list.draw(), print(self.button0.vertex())))
        # self.button0.set_0_just_callback(lambda: (self.button0_list.reset_all_state(), self.button0_list.disable_all_draw(), self.refresh_all()))
        #
        # self.button_close.set_1_just_callback(
        #     lambda :self.config_window_close(),
        #     identifier='window_close',
        #     deleter=self.button_close
        # )
        # self.button_maximize.set_1_just_callback(
        #     lambda :self.config_maximize(not self.is_maximized),
        #     identifier='window_maximize',
        #     deleter=self.button_close
        # )
        # self.button_iconize.set_1_just_callback(
        #     lambda :self.config_iconified(True),
        #     identifier='window_iconify',
        #     deleter=self.button_close
        # )

        with self.viewports['default']:
            self.viewports['default'].clear(1,0,0,1)
            self.rect.draw()
        # self.refresh_all() # first draw all
        # self.set_window_refresh_callback(self.refresh_all)
        # self.mouse.set_object_selection_callback(self.rect.unit,self.mouse.set_button_press_callback,self.rect.switch_color,None)

    def _draw_(self):
        print(list(self.rect.unit._context_dict.keys()))
        # pos = glfw.get_cursor_pos(self.glfw_window)
        # if 0<pos[0]<100 and 0<pos[1]<100:
        #     print('mouse on position')
        #     self.a = Top_bar(self)
        # elif 400<pos[0]<500 and 0<pos[1]<100:
        #
        #     if self.a == None:
        #         self.a = Top_bar(self)
        #         self.set_window_refresh_callback(self.a.p)
        #         # self.a = None
        #     else:
        #         self.a.config_window_close()
        #         self.a = None
        #         self.y = True
        #         # exit()

        #     self.refresh_all()
        # if self.mouse.is_any_object_pressed():
        #     self.refresh_all()

        if self.mouse.is_in_area([0,0,],[100,100]) and self.mouse.is_just_pressed:
            if not self.windows.has_window_named('top_bar'):
                self.top_bar = Top_bar(self.rect)
                pass
            else:
                if self.top_bar.flag_follow_active:
                    self.top_bar.config_window_close()
                    self.top_bar = None
                    print('top bar removed')
                else:
                    self.top_bar.unpin_from_viewport(self, self.viewports['top_bar'])
                    self.top_bar.config_visible(True)
                    self.top_bar.flag_follow_active = True
                    self.refresh_all()

        if self.top_bar != None:
            # TODO extra processing for looking all conditions at once
            conditions = [
                self.mouse.is_in_viewport(self.viewports['top_bar']),
                self.top_bar.flag_following,
                self.mouse.is_in_window,
                self.top_bar.mouse.is_just_released,
                self.top_bar.flag_follow_active
            ]
            if all(conditions):
                self.top_bar.move_to(self.get_vertex(0),(0,0))
                self.top_bar.flag_follow_active = False
                self.top_bar.config_visible(False)
                self.top_bar.pin_on_viewport(self, 'top_bar', 0)
                self.top_bar.mouse.set_map_from_window(self, 'top_bar')
        pass

    def refresh_all(self):
        print('refreshing')

            # self.rect2.draw()
        # self.viewports['menu_bar'].open().clear(1,0,0,1)
        #     self.menu_block.draw()
            # self.viewports.close()

class Top_bar(Window):

    def __init__(self, obj):
        self.config_visible(False)
        super().__init__(1000,100, 'top_bar',None, None)
        self.set_post_draw_callback(obj.switch_color)
        # print('[result of debuging unshared vertex array]')
        # print('of mother')
        # vao = mother.glfw_context._vertex_arrays
        # vaos = vao.collection
        # print(vaos)
        #
        # print()
        # print('bound targets')
        # for i in vaos.values():
        #     print(i.attributes)
        #     # print(i.bound_targets)
        #     # for ii in i.bound_targets:
        #     #     print(ii.name)
        #     #     print(ii.object)
        # print()
        #
        # print('of this')

        # exit()
        # self.set_window_z_position(1)

        # self.follow_window_iconify(mother)
        # self.follow_window_close(mother)

        self.position = (500,500)
        self.config_visible(True)
        self.config_decorated(False)

        self.viewports.new(0.1,0.1,0.8,0.8, 'center')

        self.flag_follow_active = True
        self.flag_following = False
        #
        # self.rect1 = Button_hover(0,0,100,100,self,self.viewports[0])
        #
        # # print('debug, preset color', self.rect1._color1, self.rect1._color2)
        #
        # with self.viewports[0]:
        #     self.viewports[0].clear(0,1,1,1)
        #
        #     # self.viewports[0].open()
        #     # self.viewports[0].clear(0,1,0,1)
        #     self.rect1.draw()
        #     # print(Window._windows.get_current())
        #     # print(FBL.get_current())
        #     # exit()
        # pass

    def _draw_(self):
        # self.viewports[0].open()
        # if self.mouse.is_just_pressed and self.mouse.cursor_object == self.rect1.unit:
        #     print('debug, object press detected')
            # self.viewports[0].open()
            # with self.viewports[0]:
            #     self.rect1.switch_color()

        # if self.flag_follow_active:
        #     if not self.mouse.is_in_viewport(self.viewports['center']) and self.mouse.is_in_window and 0 in self.mouse.pressed_button:
        #         if not self.flag_following:
        #             self.flag_following = True
        #             self.ref_window_pos = self.mouse.window_position
        #
        #     if self.flag_following:
        #         self.move_to(self.mouse.screen_position,self.ref_window_pos)
        #
        #     if not self.mouse.is_any_pressed:
        #         if self.flag_following:
        #             self.flag_following = False
        # pass
        pass

