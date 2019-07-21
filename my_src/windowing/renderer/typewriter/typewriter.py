import freetype as ft
from ..components import *
from windowing.my_openGL.unique_glfw_context import Unique_glfw_context
import weakref
import copy

class Char_texture_container:
    """
    this is simply data container
    """
    def __init__(self, face:ft.Face, character, font):
        buffer = face.glyph.bitmap.buffer
        width = face.glyph.bitmap.width
        height = face.glyph.bitmap.rows

        self._char = character
        self._size = width, height
        self._font = font

        self._texture = Texture_new(width, height, 0, buffer)

        self._left_bearing = face.glyph.bitmap_left
        self._top_bearing = face.glyph.bitmap_top
        self._advance = face.glyph.advance.x

    def build_texture(self, context):
        self._texture.build(context)

class Typewriter:

    def __init__(self, height:int):
        """
        Typewriter instance is a set of charachters
        of its own font and size

        :param height:
        """
        if not isinstance(height, int):
            raise TypeError

        self._height = height
        self._char_dict_template = {}
        self._context_dict = weakref.WeakKeyDictionary()

    def append_chars(self, font_name_or_path, field):
        if not isinstance(font_name_or_path, str):
            raise TypeError

        if isinstance(field, str):
            if field == 'english':
                fields = [(0x0, 0x7f)]
            elif field == 'korean':
                raise
            else:
                raise Exception('language unknown. manually insert unicode field (int,int)')

        elif isinstance(field, (tuple,list)):
            # list of fields
            # ex (29,294)
            # ex ([20,30],[105,50503],[12002,40],[33,304])
            if len(field) == 2:
                fields = [field]
            pass
        # format path
        font_name_or_path = font_name_or_path.strip()
        if '/' not in font_name_or_path:
            # for window fonts
            font_name_or_path = f'C:/Windows/Fonts/{font_name_or_path}.ttf'

        elif font_name_or_path[-4:] != '.ttf':
            raise TypeError

        # # look if its already loaded
        # for (fp,h),tw in self.__class__.font_dict.items():
        #     if font_name_or_path == fp and height == h:
        #         return tw
        # # if new setting is given
        # # save in dict
        # self.__class__.font_dict[(font_name_or_path, height)] = self
        # # save basic property
        # self._font_name_or_path = font_name_or_path
        # self._height = height
        # # ft._init_freetype()
        # # self.face = ft.Face('arial.ttf')
        # # self.face.set_pixel_sizes(0, 50)
        # # self.face.load_char('s')
        # # print(ft.FT_Done_Face(self.face))

        # build template - just a template
        added_char_dict_template = {}
        face = ft.Face(font_name_or_path)
        face.set_pixel_sizes(0,self._height)
        for field in fields:
            for unicode in range(field[0],field[1]+1):
                face.load_char(unicode)
                added_char_dict_template[chr(unicode)] = Char_texture_container(face, chr(unicode), font_name_or_path)

        self._char_dict_template.update(added_char_dict_template)
        # conpy the template and save it with context...
        # I don't need to have copies of pixel values...
        # but i'll have it anyway
        context = Unique_glfw_context.get_current()
        if context != None:
            # if context there is a dic saved with the context already
            # copy new letters, build them and update dict of context
            # can this functionality inside Char_texture_container>>>?
            # no i want opengl indexes blocked

            if context in self._context_dict:
                # only add newely added ones
                copied = copy.deepcopy(added_char_dict_template)
                for i in copied.values():
                    i.build_texture(context)
                self._context_dict[context].update(copied)
            else:
                # means this is the first call so copy whole template and build it
                copied = copy.deepcopy(self._char_dict_template)
                for i in copied.values():
                    i.build_texture(context)
                self._context_dict[context] = copied


    def get_string_texture(self, string:str):
        # how to cooperate with different contexts?
        # _char_dict has all the information needed
        # texture of it is not built yet but it has pixel data to build with
        # when a user is using... inside a context... while context is set current.

        # checking
        context = Unique_glfw_context.get_current()
        if context in self._context_dict:
            char_texture = self._context_dict[context]
        else:
            copied = copy.deepcopy(self._char_dict_template)
            for i in copied.values():
                i.build_texture(context)
            self._context_dict[context] = copied
            char_texture = copied

        # search and return
        texture_list = []
        for letter in string:
            if letter not in char_texture:
                raise

            texture_list.append(char_texture[letter])

        return texture_list

Basic_typewriter = Typewriter(100)
Basic_typewriter.append_chars('arial', [0,128])
