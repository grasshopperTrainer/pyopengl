"""
override gl~ functions to record binding info
at gltracker.GLtracker

"""
# def glBindVertexArray(array):
#     GLtracker().vertexarray = array
#     gl.glBindVertexArray(array)
#
#
# def glBindBuffer(target, buffer):
#     if target is gl.GL_ARRAY_BUFFER:
#         # if buffer is not GLtracker().vertexbuffer[-1]:
#         GLtracker().vertexbuffer = buffer
#         gl.glBindBuffer(target, buffer)
#
#     elif target is gl.GL_ELEMENT_ARRAY_BUFFER:
#         # if buffer is not GLtracker().indexbuffer[-1]:
#         GLtracker().indexbuffer = buffer
#         gl.glBindBuffer(target, buffer)
#
# def glUseProgram(program):
#     # print(program)
#     # if program is not GLtracker().shader[-1]:
#     GLtracker().shader = program
#     gl.glUseProgram(program)