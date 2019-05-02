from glumpy import app
from doodler import Doodler


class Screen:
    WINDOWS = {}

    @classmethod
    def get_window(cls, name):
        return

    @classmethod
    def __init__(cls):
        # inithialization of doodler
        # cls.doo = do.Doodler()
        cls._framerate = 60
        cls.currentwindow = None;

        print('___ Screen initialized')
        pass

    @classmethod
    def get_currentwindow(cls):
        return cls.currentwindow

    @classmethod
    def get_doodler(cls):
        return cls.doo

    @classmethod
    def init(cls, func):
        # print(func.__name__)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            print('initial setting done')
            pass

        wrapper()
        # return wrapper

    @classmethod
    def add_window(cls, width: int = 500, height: int = 500, title: str = None, color: list = [1, 1, 1, 1]):

        # make title of the window
        if title is None:
            title = 'window' + str(len(cls.WINDOWS) + 1)
        else:
            title = title
        new_window = app.Window(width=width, height=height, title=title, color=color)

        # run default initiation
        @new_window.event
        def on_init():
            pass

        @new_window.event
        def on_resize(width: int, height: int):
            pass

        # insert window to the window dictionary(self.WINDOWS)
        cls.WINDOWS[title] = new_window
        print(f'___ new window {title} MADE')

    @property
    def width(self):
        return self.currentwindow.width

    @property
    def height(self):
        return self.currentwindow.height

    @classmethod
    def event(cls, func):
        # decorator for describing window actions
        window = object
        title = func.__name__
        try:
            window = cls.WINDOWS[title]
            cls.currentwindow = window
            print(window, func.__name__)
            Doodler.push_window(window)

            @window.event
            def on_draw(dt):
                # push window into doodler
                # so Doodler function could retrive Window info
                window.clear()
                func()
                pass

            print(f'___ add action to {title}')

        except KeyError:
            print(f'___ unable to add action to "{title}"\n'
                  f'    no such window titled "{title}"')

    @classmethod
    def run(cls):

        # routine for every window
        # for window in Screen.WINDOWS.values():
        #     window
        app.run(framerate=cls._framerate)

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, framerate: int):
        self._framerate = framerate
