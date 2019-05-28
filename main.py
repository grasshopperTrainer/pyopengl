from windowing.window import Window

from patterns.update_check_descriptor import UCD

# Initialize the library
Window.glfw_init()

# Create a windowed mode window and its OpenGL context
window = Window(640, 480, "Hello World", None, None)
window2 = Window(1000,300,'second_screen',None, window)

window3 = Window(2000, 1000, 'third', None, window2)

@Window.init
def INIT():
    pass

@window2.init
def init():
    tr = BRO.TestBRO(0,0,100,100)
    # alpha = 'ddd'
    tr2 = BRO.TestBRO(100,100,100,200)
    window2.mouse.instant_press_button(1)
    pass
@window3.init
def init():
    # window3.mouse.instant_press_button(1)
    pass
@window2.draw
def draw():
    # renderer.clear(1, 1, 1, 1)
    # renderer.set_variable('u_color', (1, 0.5, alpha, 0.75))
    # renderer._draw_()
    if len(window2.mouse.pressed_button) != 0:
        window2.viewports[0].open()
        window2.viewports[0].clear()
        tr.draw()
        # tr.draw()
        # tr.draw()
        # tr.draw()
    # if len(window2.mouse.pressed_button) != 0:
    #     tr.draw()
        print('dkdkdk')
    pass

@window3.draw
def draw():
    # window3.viewports[0].open()
    # window3.viewports[0].clear(0,0,1,1)

    if len(window3.mouse.pressed_button) != 0:
        window3.viewports[0].open()
        window3.viewports[0].clear()
        tr.draw()
        # tr2.draw()
        print('window3 draw')
    pass


@window.keyboard.press
def event():
    if window.keyboard.key_pressed('esc'):
        window.close()
    if window.keyboard.key_pressed('l'):
        window.layers[0].hide()


# @window3.mouse
# def event():
#     def move():
#         # keymove = 'heyhye'
#         peta = 10
#
#     def enter():
#         # print(rectangle1.a)
#         print('on')
#
#     def exit():
#         print('out')
#
#     def click_press():
#         print(self.size)
#
#     def scroll():
#         print('scrolling')
#         print(window.mouse.scroll_offset)


# @window3.init
# def init():
#     rectangle1 = BRO.Rectangle(pos = [0,0],size=[500,500],fillcol=[0,1,1,1], edgecol=[0,0,0,1])
#     # window.viewports.new(0.5, 0, 0.5, 1.0, 'new')
#     # window.viewports['new'].camera.mode = 2
#     # # window.viewports['new'].camera.move(10, 0, 0, 1)
#     # # window.viewports['new'].camera.lookat([100, 300, 0], [100, 0, 50])
#     #
#     # gui = mygui.testgui()
#     #
#     # image = Renderable_image(500,500)
#     # rectangle2 = BRO.Rectangle(pos = [0,0], size=[1000,1000], fillcol=[1,1,1,1])
#     # rectangle2.render_texture(image.texture)
#
#     rectangle3 = BRO.Rectangle(pos=[500,500], size=[500,500], fillcol=[0,1,0,1])
#
# @window3.draw
# def draw():
#     if len(window3.mouse.pressed_button) != 0 or window3.is_resized:
#         window.viewports[0].open()
#         window.viewports[0].clear(1,0,0,1)
#         rectangle1.draw()
#         rectangle3.draw()
#         print('dkdkdk')



# @window3.testdraw(when = window3.mouse.click_press)
# def ddd():
#     print('click,click')

# @window3.testdraw(window3.mouse.click())
# def draw2():
#     print('dkdkd')

Window.run_single_thread()
# Window.run_multi_thread()

# print(window,type(window))