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
    from renderers.testrenderer import Renderer
    from renderers.BRO.rectangle import Rectangle

@window.init
def init():
    # window.viewport.new(100, 200, 0.5, 1.0)
    # glfw.make_context_current(window.glfw_window)
    points = np.zeros(4, [('vertex', np.float32, 2), ('texCoord', np.float32, 2)])
    index = np.array([0, 1, 2, 2, 3, 0], np.int32)
    points['vertex'] = [-1, -1], [1, -1], [1, 1], [-1, 1]
    points['texCoord'] = [0, 1], [1, 1], [1, 0], [0, 0]
    #
    renderer = Renderer('quad')
    renderer.bind_shader('sample')
    renderer.bind_vertexbuffer(points)
    renderer.bind_indexbuffer(index)
    renderer.bind_texture('sampleImage')

    # renderer.set_variable('texSlot', 0)

    alpha = 0
    increment = 0.05
    beta = alpha + increment

@window.draw
def draw():
    # print(alpha)
    # gl.glViewport(0,0,100,100)
    # window.viewport.open(0)
    # renderer.clear(1, 0, 1, 1)
    # renderer.set_variable('u_color', (1, 1, alpha, 0.5))
    # renderer.draw()
    # window.viewport.close()
    # renderer.set_variable('u_color', (1, alpha, 0, 0.5))
    # renderer.draw()
    # window.viewport.close(0)

    alpha += increment

    if alpha > 1:
        increment = -increment
    elif alpha < 0:
        increment = -increment


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

@window2.mouse
def event():
    def move():
        # keymove = 'heyhye'
        peta = 10

    def enter():
        print('on')

    def exit():
        print('out')

    def click_press():
        print(window2.size)

    def scroll():
        print('scrolling')
        print(window.mouse.scroll_offset)


@window3.init
def init():
    rectangle1 = Rectangle()


@window3.draw
def draw():
    rectangle1.draw()


Window.run_single_thread()
# Window.run_multi_thread()

# print(window,type(window))