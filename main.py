from windowing.window import Window

# Initialize the library
Window.glfw_init()


# Create a windowed mode window and its OpenGL context
window = Window(640, 480, "Hello World", None, None)
window2 = Window(1000,300,'second_screen',None, window)
window3 = Window(2000,500,'third', None, None)
window4 = Window(500,1000,'fourth',None,None)
window3.follows_closing(window, window2)
window4.follows_closing(window3)

@Window.init
def init():
    import numpy as np
    from shader import Shader
    from buffers import Buffer
    from renderer import Renderer

    delta = '100'
    pass

@window.init
def init():

    # glfw.make_context_current(window.glfw_window)
    points = np.zeros(4, [('vertex', np.float32, 2)])
    index = np.array([0,1,2,2,1,3],np.int32)
    points['vertex'] = [-1, 1], [-1, -1], [1, 1], [1, -1]
    #
    buffer = Buffer(points,index)
    program = Shader('sample')
    renderer = Renderer(program,buffer,'quad')

    alpha = 0
    increment = 0.05
    beta = alpha + increment

@window.draw
def draw():
    # print(alpha)
    renderer.clear()
    renderer.set_variable('u_color',(1,alpha,1,1))
    renderer.draw()
    alpha += increment

    if alpha > 1:
        increment = -increment
    elif alpha < 0:
        increment = -increment
    # print(id(alpha))
    # print('alpha from window1: ', alpha)
    # alpha += 1
    # print(self._vars)
    # print(delta)
    # print(ceta)
    # print(ceta)

@window2.init
def init():
    # alpha = 'ddd'
    ceta = 'ceta'

@window2.keyboard.press
def event():
    if window.keyboard.key_pressed(GLFW.GLFW_KEY_A, GLFW.GLFW_KEY_E):
        window.close_window_concequently()

@window2.mouse.move
def event():
    print('mouse moving')
@window2.mouse.enter
def event():
    print('on')
@window2.mouse.exit
def event():
    print('out')
@window2.mouse.click
def event():
    print(window.mouse.button_pressed)
@window2.mouse.scroll
def event():
    print('scrolling')
    print(window.mouse.scroll_offset)

@window2.draw
def draw():
    renderer.clear()
    renderer.set_variable('u_color',(1,1,alpha,1))
    renderer.draw()
    # print(windows.window.name)
    # print(window.keys_pressed)
    # print(window.keys_pressed)
    # print(windows)
    # print('delta')
    # print(alpha)
    print(ceta)

# @window3.draw
# def draw():
#     # print(increment)
#     pass


Window.run_single_thread()
# Window.run_multi_thread()

# print(window,type(window))