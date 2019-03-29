import glfw
from glfw.GLFW import *
from OpenGL.GL import *

import numpy as np
import time
import ctypes

from shader import Shader
from buffers import Buffer
from gltracker import GLtracker
from renderer import Renderer
from gloverride import *
from window import Window

# Initialize the library
Window.glfw_init()

# Create a windowed mode window and its OpenGL context
window = Window(640, 480, "Hello World", None, None)
# window2 = Window(1000,300,'second_screen',None, None)

@window.init
def init():
    # vertex, index buffers
    points = np.zeros(4, [('vertex', np.float32, 2)])
    points['vertex'] = [-1, 1], [-1, -1], [1, 1], [1, -1]
    index = np.array([0, 1, 2, 2, 1, 3], np.uint32)

    buffer = Buffer(points, index)
    # shader
    program = Shader('sample', 'sample_quad')

    # renderer
    renderer = Renderer(program, buffer,'render1')

    alpha = 0
    increment = 0.05

@window.draw
def draw():

    renderer.clear()
    # set new value
    renderer.set_variable('u_color', (0, alpha, 1, 1))
    # draw
    renderer.draw()

    # animation
    if alpha > 1 or alpha < 0:
        increment = -increment
    alpha += increment


# Window.print_framerate(True)
Window.run_all2()
# Window.run_all()
print(window,type(window))