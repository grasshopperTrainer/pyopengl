#shader vertex
#version 330 core

layout(location = 0) attribute vec3 a_position;
layout(location = 1) attribute vec4 a_color;

varying vec4 v_color;

void main() {
    v_color = a_color;
    gl_Position = vec4(a_position, 1);
}

    #shader fragment
    #version 330 core

//uniform vec4 u_color;

varying vec4 v_color;
out vec4 color;

void main() {
    color = v_color;
}