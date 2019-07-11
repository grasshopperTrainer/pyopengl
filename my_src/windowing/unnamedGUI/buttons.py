from .box import Filled_box
from ..callback_repository import Callback_repository
import weakref

class _Button(Filled_box):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)

        self._color0 = 1, 1, 1, 1
        self._color1 = .5, .5, .5, 1
        self.fill_color = self._color0

        # callback repo
        callbacks = ['to_idle', 'to_pressed', 'to_hover', 'while_idle', 'while_pressed', 'while_hover']
        self._callback_repo = Callback_repository(callbacks)

        # self._callback_repo = Callback_repository

    @property
    def state(self):
        return self._flag_state
    @state.setter
    def state(self, v):
        self._flag_state = v

    @property
    def color0(self):
        return self._color0

    @color0.setter
    def color0(self, *rgba):
        self._color0 = rgba
        if self._flag_state == 0:
            self.fill_color = rgba

    @property
    def color1(self):
        return self._color1

    @color1.setter
    def color1(self, *rgba):
        self._color1 = rgba

    def switch_color(self):

        pass

    def set_input_space(self, window):
        if window != None:
            # remove callback of previous window
            if self.window != None:
                self.window.mouse.remove_callback(identifier=self)
            # assign new window
            self._window = weakref.ref(window)
            window.set_post_draw_callback(
                func= lambda : self.switch_color() if self.mother._flag_update else None,
                identifier=self,
                deleter=self
            )
    # def reset_all_state(self):
    #     self._flag_state = 0
    #     self.set_fill_color(*self._color0)
    #     for box in self._children:
    #         box.reset_all_state()
    def set_to_idle_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('to_idle',function, args, kwargs,identifier, instant, deleter)
    def set_to_pressed_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('to_pressed',function, args, kwargs,identifier, instant, deleter)
    def set_switch_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self.set_to_idle_callback(function, args, kwargs,identifier, instant, deleter)
        self.set_to_pressed_callback(function, args, kwargs,identifier, instant, deleter)

    def set_to_hover_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('to_hover',function, args, kwargs,identifier, instant, deleter)
    def set_while_idle_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('while_idle',function, args, kwargs,identifier, instant, deleter)
    def set_while_pressed_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('while_pressed',function, args, kwargs,identifier, instant, deleter)
    def set_while_hover_callback(self, function, args=(), kwargs={}, identifier='not_given', instant=False, deleter=None):
        self._callback_repo.setter('while_hover',function, args, kwargs,identifier, instant, deleter)

    def exec_to_idle_callback(self):
        self._callback_repo.exec('to_idle')
    def exec_to_pressed_callback(self):
        self._callback_repo.exec('to_pressed')
    def exec_to_hover_callback(self):
        self._callback_repo.exec('to_hover')
    def exec_while_idle_callback(self):
        self._callback_repo.exec('while_idle')
    def exec_while_pressed_callback(self):
        self._callback_repo.exec('while_pressed')
    def exec_while_hover_callback(self):
        self._callback_repo.exec('while_hover')

# few pre_built buttons
class Button_press(_Button):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)
        self._buttons_to_respond = [0,]

        self._flag_reset_pressed_elsewhere = False

    def switch_color(self):
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_LCS(self):
                if mouse.is_just_pressed:
                    if self.state == 0:
                        self.exec_to_pressed_callback()
                        self.fill_color = self.color1
                        self.state = 1
                    else:
                        self.exec_to_idle_callback()
                        self.fill_color = self.color0
                        self.state = 0
                    self.draw()
            else:
                if mouse.is_just_pressed:
                    if self._flag_reset_pressed_elsewhere:
                        if self.state == 1:
                            self.exec_to_idle_callback()
                            self.fill_color = self._color0
                            self._flag_state = 0
                            self.draw()

    def set_reset_pressed_elsewhere(self,b):
        self._flag_reset_pressed_elsewhere = b

    @property
    def buttons_to_respond(self):
        return self._buttons_to_respond

    @buttons_to_respond.setter
    def buttons_to_respond(self, *buttons: int):
        int_buttons = [int(i) for i in buttons]
        self._buttons_to_respond = int_buttons


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
                                self.exec_to_pressed_callback()
                            self.exec_while_pressed_callback()

                        self.fill_color = self.color1
                        self._flag_state = True
                        self.draw()


                elif self.fill_color != self.color0:

                    if self._window != None:
                        self.exec_while_idle_callback()

                    self.fill_color = self.color0
                    self._flag_state = False
                    self.draw()

            elif self.fill_color != self.color0:

                if self._window != None:
                    self.exec_while_idle_callback()

                self.fill_color = self.color0
                self._flag_state = False
                self.draw()


class Button_hover(_Button):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)
        self._hover_count_target = 5
        self._hover_count = 0

    def switch_color(self):
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if self._flag_state == 0:
                    if self._hover_count == self._hover_count_target:
                        self.fill_color = self.color1
                        self._flag_state = 1
                        self.draw()
                    else:
                        self._hover_count += 1
                elif self._flag_state == 1:
                    pass
            else:
                if self._flag_state == 1:
                    self._hover_count = 0
                    self._flag_state = 0
                    self.fill_color = self.color0
                    self.draw()
                elif self._flag_state == 0:
                    pass

    @property
    def hover_target_frame_count(self):
        return self._hover_count_target
    @hover_target_frame_count.setter
    def hover_target_frame_count(self, count:int):
        count = int(count)
        self._hover_count_target = count


class Button_hover_press(Button_press):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)
        self._hover_count = 0
        self._hover_target = 5
        self._hover_color = 1,0,0,1
        self._hovered = False

    def switch_color(self):
        super().switch_color()
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_LCS(self):
                if self._hovered:
                    self.exec_while_hover_callback()
                else:
                    if self._hover_count == self._hover_target:
                        self.fill_color = self._hover_color
                        self._hovered = True
                        self.exec_to_hover_callback()
                        self.draw()
                    else:
                        self._hover_count += 1
            else:
                if self._hovered:
                    if self.state == 0:
                        self.fill_color = self.color0
                    else:
                        self.fill_color = self.color1
                    self.draw()
                    self._hover_count = 0
                    self._hovered = False
