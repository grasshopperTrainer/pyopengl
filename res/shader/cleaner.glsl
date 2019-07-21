#shader vertex
#version 430 core

layout(location = 0) attribute vec2 coordinate;

void main() {
    gl_Position = vec4(coordinate, 1, 1);
}

#shader fragment
#version 430 core

layout(location = 0) uniform vec4 fill_color;
layout(location = 0) out vec4 diffuse_color;

void main() {
    diffuse_color = fill_color;
}