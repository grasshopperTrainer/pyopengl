from .box import Filled_box, Block
from ..callback_repository import Callback_repository
import weakref
from ..mcs import Family_Tree
import gc
from .box import Textbox

class _Button(Filled_box):
    """
    Buttons are basically box with filled color with functionality for
    interacting with window(input devices).
    """
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)

        self._color0 = 1, 1, 1, 1
        self._color1 = .5, .5, .5, 1
        self.fill_color = self._color0

        # callback repo
        callbacks = ['to_idle', 'to_pressed', 'to_hover', 'while_idle', 'while_pressed', 'while_hover']
        self._callback_repo = Callback_repository(callbacks)

        self._flag_reset_pressed_elsewhere = False

    @property
    def state(self):
        return self._flag_state
    @state.setter
    def state(self, v):
        self._flag_state = v
        if v == 0:
            self.fill_color = self.color0
        elif v == 1:
            self.fill_color = self.color1
        elif v == 2:
            self.fill_color = self.color2
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
            # TODO if resetting window doesn't work correctly this must be a problem
            #   would it be possible to bind callbacks with it's mother? so to make
            #   constructing interaction between children callbacks easy?
            if self.window != None:
                self.window.remove_callback(deleter=self)
            # assign new window
            self._window = weakref.ref(window)
            window.set_post_draw_callback(
                func= lambda : self.switch_color() if self._flag_update else None,
                identifier=self,
                deleter=self
            )

    def set_reset_pressed_elsewhere(self, b):
        self._flag_reset_pressed_elsewhere = b

    def delete(self):
        self.window._callbacks_repo.remove(deleter=self)
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

    def use_to_idle_callback(self, b):
        self._callback_repo.set_exec_flag('to_idle', b)


# few pre_built buttons
class Button_press(_Button):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)
        self._buttons_to_respond = [0,]

    def switch_color(self):
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_LCS(self):
                if mouse.is_just_pressed:
                    if self.state == 0:
                        self.fill_color = self.color1
                        self.state = 1
                        self.exec_to_pressed_callback()
                        self.draw()
                    else:
                        self.fill_color = self.color0
                        self.state = 0
                        self.exec_to_idle_callback()
                        self.draw()
            else:
                if mouse.is_just_pressed:
                    if self._flag_reset_pressed_elsewhere:
                        if self.state == 1:
                            self.fill_color = self._color0
                            self._flag_state = 0
                            self.exec_to_idle_callback()
                            self.draw()
                else:
                    if self.state == 1:
                        self.exec_while_pressed_callback()
                    else:
                        self.exec_while_idle_callback()



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
        self._hover_target = 3
        self._hover_count = 0
        # self._flag_sticky_button = False

    def switch_color(self):
        if self.window != None:
            mouse = self.window.mouse
            if mouse.is_in_area(*self.vertex(0,2)):
                if self._flag_state == 0:
                    if self._hover_count == self._hover_target:
                        self.exec_to_hover_callback()
                        self.fill_color = self.color1
                        self._flag_state = 1
                        self.draw()
                    else:
                        self._hover_count += 1
                elif self._flag_state == 1:
                    pass
            else:
                if self._flag_state == 1:
                    self.exec_to_idle_callback()
                    self._hover_count = 0
                    self._flag_state = 0
                    self.fill_color = self.color0
                    self.draw()
                elif self._flag_state == 0:
                    pass
    #
    # def set_stiky_button(self, b):
    #     if not isinstance(b, bool):
    #         raise
    #     self._flag_sticky_button = b

    @property
    def hover_target_frame_count(self):
        return self._hover_target
    @hover_target_frame_count.setter
    def hover_target_frame_count(self, count:int):
        count = int(count)
        self._hover_target = count


class Button_hover_press(Button_press):
    def __init__(self,posx,posy,width,height,window=None):
        super().__init__(posx,posy,width,height,window)
        self._hover_count = 0
        self._hover_target = 0
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
                        self.draw()
                        self.exec_to_hover_callback()
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
    @property
    def color2(self):
        return self._hover_color
    @color2.setter
    def color2(self, *rgba):
        if len(rgba) != 4:
            raise ValueError
        self._hover_color = rgba

class Button_list(Block):

    def __init__(self,window, horizontal_vertical,kind, number, width, height):
        super().__init__(0,0,width,height,window)
        if not isinstance(horizontal_vertical, int):
            raise TypeError
        if not _Button in kind.__mro__:
            raise
        if horizontal_vertical != 0 and horizontal_vertical != 1:
            raise ValueError

        self._alignment = horizontal_vertical
        self._number = number
        self._kind = kind

        if number != 0:
            self._unit_width, self._unit_height, self._unit_width_oflast, self._unit_height_oflast = self._calculate_size()
            self._build()


    def _calculate_size(self):
        if self._alignment == 0:
            if self.pixel_w/self._number < 1:
                raise
            unit_width = lambda w: round(w/self._number)
            unit_height = 1.

            unit_width_oflast = lambda w: w - round(w/self._number)*(self._number-1)
            unit_height_oflast = 1.
        else:
            if self.pixel_h/self._number < 1:
                raise
            unit_width = 1.
            unit_height = lambda h: round(h/self._number)
            unit_width_oflast = 1.
            unit_height_oflast = lambda h: h - round(h/self._number)*(self._number -1)

        return unit_width, unit_height, unit_width_oflast, unit_height_oflast

    def _build(self, buttons = None):
        if buttons == None:
            buttons = []
            for i in range(self._number):
                buttons.append(self._kind(0,0,1,1))

        for i in range(self._number-1):
            if self._alignment == 0:
                x,y = lambda w,i=i: w/self._number*i, 0
            else:
                x,y = 0,lambda h, i=i: h/self._number*i
            b = buttons[i]
            b.x, b.y, b.w, b.h = x,y, self._unit_width, self._unit_height
            b.is_child_of(self)
        #last
        if self._alignment == 0:
            x, y = lambda w: w / self._number * (self._number-1), 0
        else:
            x, y = 0, lambda h: h / self._number * (self._number-1)
        b = buttons[-1]
        b.x, b.y, b.w, b.h = x,y,self._unit_width_oflast, self._unit_height_oflast
        b.is_child_of(self)

    def resize(self, width, height):
        pass
    @property
    def number(self):
        return self._number
    @number.setter
    def number(self, n):
        if not isinstance(n, int):
            raise
        if n > self._number:
            number_to_append = n - self._number
            self._number = n
            self._unit_width, self._unit_height, self._unit_width_oflast, self._unit_height_oflast = self._calculate_size()

            children_list = self.children.add(self._kind(0,0,1,1) for i in range(number_to_append))
            self._build(children_list)

        elif n < self._number:
            number_to_remove = self._number - n

            self._number = n
            self._unit_width, self._unit_height, self._unit_width_oflast, self._unit_height_oflast = self._calculate_size()
            for i in range(number_to_remove):
                self.children.pop().delete()
            self.children[-1].size = self._unit_width_oflast, self._unit_height_oflast

    def add(self, *obj):
        if len(obj) == 0:
            self.number += 1
        else:
            self._number += 1
            self._unit_width, self._unit_height, self._unit_width_oflast, self._unit_height_oflast = self._calculate_size()
            for i in obj:
                i.is_child_of(self)
            children_list = self.children + list(obj)
            print("-=----------")
            print(children_list)
            self._build(children_list)


class Complex_button_list:
    def __init__(self, source, kind, unit_width, unit_height, window):
        if not isinstance(source, str):
            raise TypeError
        self._master = None
        self._source = source
        self._kind = kind
        self._unit_width = unit_width
        self._unit_height = unit_height
        self._window = weakref.ref(window)
        self._compile(source)
    @property
    def master(self):
        return self._master

    def _compile(self, text):
        family_tree = Family_Tree(None)
        family_tree.build_from_text(text)

        branches = [family_tree._tree]
        masters = [None for i in range(len(family_tree._tree))]

        while True:
            new_branches = []
            new_masters = []

            for master,branch in zip(masters,branches):

                n = len(branch)
                button_list = Button_list(self._window(),1,Button_hover_press, n, self._unit_width, self._unit_height*n)

                for i in button_list.children:
                    i.color1 = i.color2

                if master != None:
                    button_list.is_child_of(master)
                    button_list.x = master.w
                    # initially don't show or react to input device
                    # for i in button_list.family[0:2]:
                    #     i.deactivate()
                    for i in button_list.family[0:2]:
                        i.deactivate()

                    # set draw action with master button
                    # if hovered need to deactivate currently drawn child and draw hovered child

                    def to_hovered(master, clear_func, self):
                        # print()
                        # print('hovered', master)
                        # print(master.siblings)
                        for in_list_button in master.siblings +[master]:
                            # print('siblings:',in_list_button, in_list_button.family[1:])
                            # all the members below deactivate
                            in_list_button.state = 0
                            # print(in_list_button.family[1:])
                            for child in in_list_button.family[1:]:
                                if not isinstance(child, Textbox):
                                    # print('hovered deactivating', child)
                                    child.deactivate()
                                    child.state = 0
                        # for i in master.family[1:]:
                        #     i.deactivate()
                        #     i.state = 0
                        # clear
                        # activate new list
                        # for i in master.family[0:1]:
                        #     i.activate()
                        # master.children[0].activate()
                        # print('dddddddddddddddddd')
                        # print(master.family[0:1])
                        # print(master.children[0])
                        clear_func()
                        for i in master.family[0:3]:
                            # print('+++',i)
                            i.activate()
                            i.state = 0
                            # i.draw()
                        master.state = 1
                        # draw till master
                        with self._window().layers[-1]:
                            self.draw()


                    master.set_to_hover_callback(
                        lambda m=master,f=self._window().refresh_all,this=self: to_hovered(m,f,this)
                    )

                    def ignore_to_idle(button):
                        button.state = 1
                    master.set_to_idle_callback(
                        lambda m=master:ignore_to_idle(m)
                    )

                else:
                    self._master = Button_press(0,0,*button_list.size, self._window())
                    self._master.set_reset_pressed_elsewhere(True)
                    self._master.color1 = 1,1,1,1

                    # master button if just for cursor detection
                    def master_reset_func(window, button_list):
                        # print('master_to_idle')
                        mouse = window.mouse
                        for i in button_list.family[1:]:
                            if mouse.is_in_LCS(i) and i.is_active:
                                return

                        for i in button_list.family[2:]:
                            print('iiiiiii',i)
                            i.deactivate()
                            i.state = 0
                        for i in button_list.children:
                            i.state = 0
                        # if it's offsprings not pressed
                        window.refresh_all()

                        self.draw()

                    self._window().mouse.set_button_press_callback(
                        lambda w=self._window(), bl=button_list :master_reset_func(w,bl)
                    )

                    button_list.is_child_of(self._master)


                for child, (name,value) in zip(button_list.children, branch.items()):
                    child.name = name

                    # if there is a grandchild
                    # if len(value) != 0:
                    new_branches.append(value)
                    new_masters.append(child)

            branches = new_branches
            masters = new_masters

            if len(branches) == 0:
                break

        for member in self._master.family[1:]:
            if member.name != None:
                text_box = Textbox(0,0,member.pixel_w, member.pixel_h,member.window, member.name, member.pixel_h)
                text_box.text_fill_color = 0,0,1,1
                text_box.is_child_of(member)

        # exit()

    def draw(self):
        self._master.draw()