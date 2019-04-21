#shader vertex
#version 400 core

attribute vec4 a_position;
attribute vec4 a_color;
attribute vec2 a_texCoord;

varying vec4 v_position;
varying vec4 v_color;
varying vec2 v_texCoord;

out vec4 position;

void main() {
    v_position = a_position;
    v_color = a_color;
    v_texCoord = a_texCoord;

    //transformation here

    position = a_position;
}


    #shader fragment
    #version 400 core

uniform sampler2D texSlot;

varying vec4 v_position;
varying vec4 v_color;
varying vec2 v_texCoord;

out vec4 color;

void main() {
    //vec4 texColor = texture(texSlot, v_texCoord);

    color = v_color;
}