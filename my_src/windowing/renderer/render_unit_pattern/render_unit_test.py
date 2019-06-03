# from patterns.store_instances_dict import SID
# from patterns.strict_method_implant import SMI
# from windowing.renderer.components import *
#
# class RU_template(SMI, SID):
#     """
#     Mother class for render_unit.
#     Can single class have different patter?
#     NO? lets say... child class should be self coded but
#     this template gives basic guild line...
#
#
#     some rules... thinking....
#     1. OpenGL shader is backed just once per Render_unit.
#     2. shader can be given as external glsl or backed dynamically
#     by collecting some info...
#
#     """
#     def __new__(cls):
#         ins = super().__new__(cls)
#         if len(cls._INSTANCES_DICT) == 1:
#             cls._singular_bake_shader()
#         else:
#             def hollow():
#                 print('restricted excess')
#             ins._singular_bake_shader = hollow
#
#         return ins
#
#     _the_shader = SMI.must_arg
#
#     @SMI.must_func
#     @classmethod
#     def _singular_bake_shader(cls):
#         """
#         This should be called only once per this's child class.
#         :return:
#         """
#         pass
#
#     def _draw_(self):
#         pass
#     def _hide_(self):
#         pass
#     def _stop_(self):
#         pass
#
# class Render_unit_loaded_shader(SMI):
#     _loaded_shader = SMI.must_arg
#
#     def __init__(self):
#         pass
#
#     @SMI.must_func
#     @classmethod
#     def _load_shader(cls):
#         # load from repo
#         cls._loaded_shader = Shader()
#         print('single run')
#
#         pass
#
#     pass
#
# class Sample(Render_unit_loaded_shader):
#     _loaded_shader = None
#
#     @classmethod
#     def _load_shader(cls):
#         cls._the_shader = Shader()
#
#     pass
#
#
# a = Sample()