import math
import numpy as np
from glumpy import gloo, gl, app
from tools import *
import glumpy


class Doodler:
    PROG_POINTS2D = None

    @classmethod
    def bake_shaders(cls):
        vertex_circle = """
        uniform vec2 screensize;
        uniform int linewidth;
        uniform int antilevel;
        uniform vec2 center;
        uniform float radius;
        attribute vec2 vertice;
        
        float colorconst = 100;
        uniform vec4 colorfill;
        uniform vec4 coloredge;
        varying vec4 v_colorfill;
        varying vec4 v_coloredge;
        
        varying vec2 mappedCenter;
        varying vec2 v_vertice;
        
        void main() {
            vec2 direction = vertice - center;
            int addition = int(ceil((linewidth-1)/2)) + antilevel;
            float x = vertice.x + direction.x/abs(direction.x)*addition;
            float y = vertice.y + direction.y/abs(direction.y)*addition;
            vec2 mapped = vec2(x,y)/(screensize/2)-1;
            
            gl_Position = vec4(mapped,0,1);

            mappedCenter = center/(screensize/2)-1;
            v_vertice = mapped;
            
            v_colorfill = colorfill/colorconst;
            v_coloredge = coloredge/colorconst;
        }
        """
        fragment_circle = """
        uniform float radius;
        uniform int linewidth;
        uniform int antilevel;
        
        uniform vec2 screensize;
        
        varying vec2 v_vertice;
        varying vec2 mappedCenter;
        
        varying vec4 v_colorfill;
        varying vec4 v_coloredge;
        
        void main() {
            float ratio = screensize.x/screensize.y;
            float distance = length((v_vertice - mappedCenter)*vec2(ratio,1));
            float r = radius/screensize.x;
            float w = ((linewidth-1)/2)/screensize.x;
            float a = antilevel/screensize.x;
            
            if(distance >= r) {
                float d = clamp(distance-r,w,w+a);
                float m = cos((d-w)/a*radians(90));
                gl_FragColor = mix(vec4(1,1,1,0),v_coloredge,m);
            }
            else {
                float d = clamp(r-distance,w,w+a);
                float m = cos((d-w)/a*radians(90));
                gl_FragColor = mix(v_colorfill,v_coloredge,m);
            }            
            
        }
        """
        cls.PROG_CIRCLS = gloo.Program(vertex_circle, fragment_circle, count=4)

    def __init__(self):
        self.bake_shaders()
        self._colorfill_default = 100, 100, 100, 100
        self._coloredge_default = 0, 0, 0, 100
        self._linewidth_default = 2
        self._antilevel_default = 3

        self._colorfill = 100, 100, 100, 100
        self._coloredge = 0, 0, 0, 100
        self._linewidth = 2
        self._antilevel = 3

        print('___ Doodler initialized')

    @property
    def window(self):
        return self.CURRENTWINDOW

    @property
    def linewidth(self):
        return self._linewidth

    @linewidth.setter
    def linewidth(self, value):
        self._linewidth = value

    @property
    def antilevel(self):
        return self._antilevel

    @antilevel.setter
    def antilevel(self, value):
        self._antilevel = round(value)

    @property
    def colorfill(self):
        return self._colorfill
        pass

    @colorfill.setter
    def colorfill(self, value):
        self._colorfill = value

    @property
    def coloredge(self):
        return self._coloredge

    @coloredge.setter
    def coloredge(self, value):
        self._coloredge = value

    @classmethod
    def drawprohopper(self, *geometry):
        # check if input is prohopper geometry
        if all([isinstance(i, Geometry) for i in geometry]):
            print(geometry)

    def test(self):
        pass

    def point(self):
        pass

    def point2d(self, coord: list = None, color: list = None, size: float = 10, option: int = 0):

        if coord is None:
            coord = self.window.width / 2, self.window.height / 2
        if color is None:
            color = [[0, 0, 0, 100], [0, 0, 0, 100]]

        if option is 0:
            self.circle(coord, color, size)

        elif option is 1:
            pass

    def circle(self, coord: list = [0, 0], color: list = None, size: float = 100):

        if color is None:
            colorfill = self._colorfill
            coloredge = self._coloredge
        elif isinstance(color, (list, tuple)):
            if len(color) is 2 and isinstance(color[0], (list, tuple)):
                colorfill = color[0]
                coloredge = color[1]
            elif isinstance(color[0], (float, int)):
                colorfill = [0, 0, 0, 0]
                colorfill[:len(color)] = color
                coloredge = self._coloredge
            else:
                raise

        radius = size / 2
        center = np.array([coord[0], coord[1]])
        move = np.array([[-radius, radius], [-radius, -radius], [radius, radius], [radius, -radius]])
        p1 = center + move[0]
        p2 = center + move[1]
        p3 = center + move[2]
        p4 = center + move[3]

        program = self.PROG_CIRCLS
        program['screensize'] = self.window.width, self.window.height
        program['linewidth'] = self.linewidth
        program['antilevel'] = self.antilevel
        program['colorfill'] = colorfill
        program['coloredge'] = coloredge

        program['center'] = center
        program['radius'] = radius
        program['vertice'] = p1, p2, p3, p4
        # print(program['vertice'])
        program.draw(gl.GL_TRIANGLE_STRIP)

    def set_antialize(self, level: int = 1, switch: bool = True):
        pass

    @classmethod
    def push_window(cls, window: object):
        # print('doodler: window pushed')
        cls.CURRENTWINDOW = window
        cls.WIN_SIZE = np.ndarray([cls.CURRENTWINDOW.width, cls.CURRENTWINDOW.height])

    @property
    def width(self):
        return self.CURRENTWINDOW.width

    @property
    def height(self):
        return self.CURRENTWINDOW.height

    def get_window(self):
        return self.CURRENTWINDOW
