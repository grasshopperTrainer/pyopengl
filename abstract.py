# #
# #
# # # initiate renderer
# # renderer = Renderer()
# #
# # @renderer.init
# # def init():
# #     # things out of recursion
# #     screen1 = renderer.makewindow(name, width, height)
# #     # controll for screen1
# #     # ex) where it sould appear on window
# #     screen1.position(x,y)
# #     # set background color
# #     screen1.background()
# #     # set multiple screen
# #     screen2 = renderer.makewindow(~)
# #
# # @renderer.draw
# # def draw():
# #     @screen1.draw
# #     def draw():
# #         #is this even possible?
# #         pass
# #     # what about dynamic window object creation and management?
# #
# # @renderer.event
# # def event():
# #     @screen1.event
# #     def event():
# #         pass
# #     @screen2.event
# #     def event():
# #         pass
# #
# # # main function for runnging frame draw
# # renderer.thread_run()
# #
# #
# # # how to manage co rutine?
# # # make things culculated behind the scene?
# # # what is it? timing? schedueling? event management?
# #
# # # other python calculation
# # resultA = functionA()
# # # how to connect with other operations?
# # screen1.input('port name', resultA)
# # # how to get info from screen?
# # value = screen1.outpu('ddd')

from PIL import Image

im = Image.open('res/image/sampleImage.png')  # type: Image.Image
