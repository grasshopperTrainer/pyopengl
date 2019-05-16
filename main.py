from windowing.window import Window

# Initialize the library
Window.glfw_init()


# Create a windowed mode window and its OpenGL context
window = Window(640, 480, "Hello World", None, None)
window2 = Window(1000,300,'second_screen',None, window)

window3 = Window(2000, 500, 'third', None, None)
# window4 = Window(500,1000,'fourth',None,None)
# window3.follows_closing(window, window2)
# window4.follows_closing(window3)
@Window.init
def INIT():
    pass


@window2.draw
def draw():
    # renderer.clear(1, 1, 1, 1)
    # renderer.set_variable('u_color', (1, 0.5, alpha, 0.75))
    # renderer._draw_()
    pass

@window2.init
def init():
    # alpha = 'ddd'
    ceta = 'ceta'


@window.keyboard.press
def event():
    if window.keyboard.key_pressed('esc'):
        window.close()
    if window.keyboard.key_pressed('l'):
        window.layer[0].hide()


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


@window3.init
def init():
    rectangle1 = BRO.Rectangle(pos = [0,0],size=[300,500],fillcol=[0,1,0,1], edgecol=[0,0,0,1])
    window.viewports.new(0.5, 0, 0.5, 1.0, 'new')
    window.viewports['new'].camera.mode = 1
    # window.viewports['new'].camera.move(10, 0, 0, 1)
    window.viewports['new'].camera.lookat([100, 300, 0], [100, 0, 50])

    gui = mygui.testgui()

@window3.draw
def draw():
    gui.run()
    # print(condition)
    condition = any(list(window3.mouse.pressed_button.values()))

    if condition:
        window.viewports[0].open()
        window.viewports[0].clear(1, 0, 0, 1)
        rectangle1.draw()
        window.viewports[1].open()
        window.viewports[1].clear(1, 1, 0, 1)
        rectangle1.draw()

# @window3.testdraw(when = window3.mouse.click_press)
# def ddd():
#     print('click,click')

# @window3.testdraw(window3.mouse.click())
# def draw2():
#     print('dkdkd')

Window.run_single_thread()
# Window.run_multi_thread()

# print(window,type(window))