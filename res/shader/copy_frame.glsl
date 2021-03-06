# shader vertex
#version 430

layout(location = 0) attribute vec2 vertex;
layout(location = 1) attribute vec2 tex_coord;

varying vec2 v_tex_coord;

void main() {
    v_tex_coord = tex_coord;
    gl_Position = vec4(vertex, 0., 1.);
}

# shader fragment
#version 430

varying vec2 v_tex_coord;

layout(location = 0) uniform sampler2D slot;

out vec4 diffuse_color;

void main() {
    vec4 tex_color = texture(slot, v_tex_coord);
    if (tex_color.a != 1.) {
        diffuse_color = tex_color;
    }
    else {
        diffuse_color = tex_color;
    }
}