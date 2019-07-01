from .box import Filled_box
from ..callback_repository import Callback_repository
import weakref

class _Button(Filled_box):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)

        self._color0 = 1, 1, 1, 1
        self._color1 = 0, 0, 0, 1

        self.set_window(window)

        self._flag_use_button = True

        self._callback_repo = None

    @property
    def state(self):
        return self._flag_state

    @property
    def color0(self):
        return self._color0

    @color0.setter
    def color0(self, *rgba):
        self._color0 = rgba

    @property
    def color1(self):
        return self._color1

    @color1.setter
    def color1(self, *rgba):
        self._color1 = rgba

    def switch_color(self):
        pass

    def set_window(self, window):
        if window != None:
            # remove callback of previous window
            if self.window != None:
                self.window.mouse.remove_callback(identifier=self)
            # assign new window
            self._window = weakref.ref(window)

            window.set_post_draw_callback(
                func= lambda : self.switch_color() if self._flag_draw else None,
                identifier=self,
                deleter=self
            )

            # callback repo
            callbacks = ['0just','1just','2just', '0','1','2']
            self._callback_repo = Callback_repository(window, callbacks)

    def reset_all_state(self):
        self._flag_state = 0
        self.set_fill_color(*self._color0)
        for box in self._children:
            box.reset_all_state()


    def set_0_just_callback(self, function, args=(), kwargs={},instant=False, identifier='not_given', deleter=None):
        if self._window != None:
            self._callback_repo.setter('0just',function,args,kwargs,identifier, instant, deleter)
    def set_1_just_callback(self, function, args=(), kwargs={}, instant=False, identifier='not_giver', deleter=None):
        if self._window != None:
            self._callback_repo.setter('1just',function,args,kwargs,identifier, instant, deleter)
    def set_2_just_callback(self, function, args=(), kwargs={}, instant=False, identifier='not_giver', deleter=None):
        if self._window != None:
            self._callback_repo.setter('2just',function,args,kwargs,identifier, instant, deleter)
    def set_1_callback(self, function, args=(), kwargs={}, instant=False, identifier='not_giver', deleter=None):
        if self._window != None:
            self._callback_repo.setter('1',function,args,kwargs,identifier, instant, deleter)
    def set_2_callback(self, function, args=(), kwargs={}, instant=False, identifier='not_giver', deleter=None):
        if self._window != None:
            self._callback_repo.setter('2',function,args,kwargs,identifier, instant, deleter)

# few pre_built buttons
class Button_press(_Button):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)
        self._buttons_to_respond = [0,]
        self._flag_config_false_click = True

    def switch_color(self):
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if mouse.is_just_pressed:
                    if self.fill_color == self._color0:
                        if self._window != None:
                            self._callback_repo.exec('1just')
                        self.fill_color = self._color1
                        self._flag_state = True

                    else:
                        if self._window != None:
                            self._callback_repo.exec('0just')
                        self.fill_color = self._color0
                        self._flag_state = False

                    self.draw()
            else:
                if mouse.is_just_pressed:
                    if self._window != None:
                        self._callback_repo.exec('0just')
                    self.fill_color = self._color0
                    self._flag_state = False
                    self.draw()

    @property
    def buttons_to_respond(self):
        return self._buttons_to_respond

    @buttons_to_respond.setter
    def buttons_to_respond(self, *buttons: int):
        int_buttons = [int(i) for i in buttons]
        self._buttons_to_respond = int_buttons

    def config_false_cligk(self, set):
        self._flag_config_false_click = set


class Button_pressing(Button_press):
    def switch_color(self):
        if self.window != None and self.window.is_focused:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if mouse.is_any_pressed:
                    pressed = False
                    for button in self._buttons_to_respond:
                        if button in mouse.pressed_button:
                            pressed = True
                            break

                    if pressed:
                        if self._window != None:
                            if not self._flag_state:
                                self._callback_repo.exec('1just')
                            self._callback_repo.exec('1')

                        self.fill_color = self.color1
                        self._flag_state = True
                        self.draw()


                elif self.fill_color != self.color0:

                    if self._window != None:
                        self._callback_repo.exec('0')

                    self.fill_color = self.color0
                    self._flag_state = False
                    self.draw()

            elif self.fill_color != self.color0:

                if self._window != None:
                    self._callback_repo.exec('0')

                self.fill_color = self.color0
                self._flag_state = False
                self.draw()


class Button_hover(_Button):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)
        self._hover_target_frame_count = 5
        self._hover_accumulate_frame_count = 0

    def switch_color(self):
        if self.window != None and self.window.is_focused:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if self._hover_accumulate_frame_count == self._hover_target_frame_count:
                    if self.fill_color == self.color0:

                        if self._window != None:
                            self._callback_repo.exec('1just')

                        self.fill_color = self.color1
                        self._flag_state = True
                        self.draw()

                    else:
                        if self._window != None:
                            self._callback_repo.exec('1')

                else:
                    self._hover_accumulate_frame_count += 1

            elif self.fill_color == self.color1:

                if self._window != None:
                    self._callback_repo.exec('0')

                self._hover_accumulate_frame_count = 0
                self.fill_color = self.color0
                self._flag_state = False
                self.draw()
    @property
    def hover_target_frame_count(self):
        return self._hover_target_frame_count
    @hover_target_frame_count.setter
    def hover_target_frame_count(self, count:int):
        count = int(count)
        self._hover_target_frame_count = count


class Button_hover_press(Button_hover, Button_press):
    def __init__(self,posx,posy,width,height,window=None,viewport=None):
        super().__init__(posx,posy,width,height,window,viewport)

        self._color2 = 1,0,0,1
        self._click_target_frame_count = 10
        self._click_accumulate_frame_count = 0

    def switch_color(self):
        if self.window != None and self.window.is_focused:
            mouse = self.window.mouse

            if self._click_accumulate_frame_count != 0:
                self._click_accumulate_frame_count -= 1

            # singular press
            if self._flag_state == 1:
                self._flag_state = 0

            if mouse.is_in_area(*self.vertex(0,2)):
                # state click
                if mouse.is_just_pressed:
                    # TODO sticky button?
                    for button in self._buttons_to_respond:
                        if button in mouse.pressed_button:

                            if self._window != None:
                                self._callback_repo.exec('1just')

                            self.fill_color = self.color2
                            self._flag_state = 1
                            self._click_accumulate_frame_count = self._click_target_frame_count
                            self.draw()
                            break

                elif self._click_accumulate_frame_count == 0:
                    # state hover
                    if self._hover_accumulate_frame_count == self._hover_target_frame_count:
                        if self.fill_color != self.color1:

                            if self._window != None:
                                self._callback_repo.exec('2just')

                            self.fill_color = self.color1
                            self._flag_state = 2
                            self.draw()

                        else:
                            if self._window != None:
                                self._callback_repo.exec('2')

                    else:
                        self._hover_accumulate_frame_count += 1


            elif self.fill_color != self.color0:
                if self._click_accumulate_frame_count == 0:

                    if self._window != None:
                        self._callback_repo.exec('0just')

                    self._hover_accumulate_frame_count = 0
                    self.fill_color = self.color0
                    self.draw()
                self._flag_state = 0

    @property
    def color2(self):
        return self._color2
    @color2.setter
    def color2(self, *rgba):
        self._color2 = rgba

    @property
    def click_target_frame_count(self):
        return self._click_target_frame_count

    @click_target_frame_count.setter
    def click_target_frame_count(self, count: int):
        count = int(count)
        self._click_target_frame_count = count