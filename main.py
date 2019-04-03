import glfw
import glfw.GLFW as GLFW
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
window2 = Window(1000,300,'second_screen',None, window)
window3 = Window(2000,500,'third', None, window)
print(window.glfw_window)
print(window2.glfw_window)
print(window3.glfw_window)
# wins = []
# for i in range(3):
#     wins.append(Window(1000,50,str(i),None,None))

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
    renderer.clear()
    renderer.set_variable('u_color',(1,alpha,1,1))
    renderer.draw()
    alpha += increment
    if alpha > 1:
        increment = -increment
    elif alpha < 0:
        increment = -increment

@window2.init
def init():
    a = 10

@window2.event
def event():
    if window.key_pressed(GLFW.GLFW_KEY_ESCAPE):
        window.close_window()

@window2.draw
def draw():
    renderer.clear()
    renderer.set_variable('u_color',(1,1,alpha,1))
    renderer.draw()
    # print(windows.window.name)
    # print(window.keys_pressed)
    # print(window.keys_pressed)
    print(windows.window2)

@window3.draw
def draw():
    # print(increment)
    pass


Window.run_single_thread()
# Window.run_multi_thread()

print(window,type(window))