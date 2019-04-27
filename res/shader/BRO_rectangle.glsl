#shader vertex
#version 400 core

layout(location = 0) attribute vec3 a_position;
layout(location = 1) attribute vec4 a_color;

varying vec4 v_color;

void main() {
    v_color = a_color;
    gl_Position = vec4(a_position, 1);
}

    #shader fragment
    #version 430 core

uniform vec4 u_color;

varying vec4 v_color;
layout(location = 0) out vec4 color;

void main() {
    color = u_color;
}