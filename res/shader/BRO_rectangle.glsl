#shader vertex
#version 400 core

attribute vec3 a_position;
attribute vec4 a_color;

varying vec4 v_color;

uniform mat4 MM;
uniform mat4 PM;
uniform mat4 VM;
uniform mat4 VPM;

void main() {
    v_color = a_color;
    gl_Position = VPM*PM*VM*vec4(a_position, 1);
}

    #shader fragment
    #version 430 core

uniform vec4 u_color;

varying vec4 v_color;
layout(location = 0) out vec4 color;

void main() {
    color = v_color;
}