from windowing.window import Window
from patterns.update_check_descriptor import UCD

# Initialize the library
Window.glfw_init()

# Create a windowed mode window and its OpenGL context
window = Window(640, 480, "Hello World", None, None)
window2 = Window(1000,300,'second_screen',None, window)
window3 = Window(2000, 1000, 'third', None, window2)
window3.close()

@Window.init
def INIT():
    k = 'k'
    from guitester import Test_gui

    pass

@window2.init
def init():
    tr = BRO.TestBRO(0,0,200,200)
    tr2 = BRO.TestBRO(100,100,100,200)

    vp = window2.viewports.new(0.0,0.0,1.0,1.0, 'pers')
    vp.camera.mode = 1
    vp.camera.lookat([0,0,0],[500,500,500])

    window2.mouse.set_object_selection_callback(tr.unit, window2.mouse.click_press, tr.switch_color)
    # window2.mouse.instant_press_button(1)

@window3.init
def init():

    # window3.mouse.instant_press_button(1)
    pass


@window2.draw
def draw():
    # renderer.clear(1, 1, 1, 1)
    # renderer.set_variable('u_color', (1, 0.5, alpha, 0.75))
    # renderer._draw_()
    if len(window2.mouse.pressed_button) != 0 or window2.is_resized:
        window2.viewports[1].open()
        window2.viewports[1].clear(1,1,0,1)
        tr.draw()
        tr2.draw()
        # print(window2.mouse.cursor_object)
        print('end of draw')
        k = Test_gui(window2)
    # gui.draw()

        # exit()
# @window3.draw
# def draw():
#     # window3.viewports[0].open()
#     # window3.viewports[0].clear(0,0,1,1)
#
#     if len(window3.mouse.pressed_button) != 0:
#         window3.viewports[0].open()
#         window3.viewports[0].clear()
#         tr.draw()
#         # tr2.draw()
#         print('window3 draw')
#     pass


@window.keyboard.press
def event():
    if window.keyboard.key_pressed('esc'):
        window.close()
    if window.keyboard.key_pressed('l'):
        window.layers[0].hide()

Window.run_single_thread()