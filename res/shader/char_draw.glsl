# shader vertex
#version 430

layout(location = 0) attribute vec2 vertex;
layout(location = 1) attribute vec2 tex_coord;

layout(location = 0) uniform mat4 PM;
layout(location = 1) uniform mat4 VM;

varying vec2 v_tex_coord;

void main() {
    v_tex_coord = tex_coord;
    gl_Position = PM*VM*vec4(vertex, 0, 1);
}

# shader fragment
#version 430

varying vec2 v_tex_coord;

layout(location = 2) uniform vec4 fill_color;
layout(location = 3) uniform sampler2D slot;

out vec4 diffuse_color;

void main() {
    vec4 sampled = vec4(1,1,1, texture(slot, v_tex_coord).r);
    diffuse_color = fill_color*sampled;
}