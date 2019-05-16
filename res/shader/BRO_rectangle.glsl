#shader vertex
#version 430 core

attribute vec2 a_position;
attribute vec4 a_color;

uniform mat4 MM;
uniform mat4 PM;
uniform mat4 VM;

varying vec2 v_pos;

void main() {
    v_pos = a_position;

    gl_Position = PM*VM*vec4(a_position,0, 1);
}

#shader fragment
#version 430 core

uniform vec4 u_fillcol;
uniform vec4 u_edgecol;
uniform vec2 u_size;
uniform float u_edgeweight;
float half_edgeweight = u_edgeweight/2.0;

varying vec2 v_pos;

out vec4 color;

float dist_from_edge(vec2 pos, vec2 size) {
    float dist_x = min(size.x - pos.x, pos.x);
    float dist_y = min(size.y - pos.y, pos.y);
    return min(dist_x, dist_y);
}

void main() {
    float d = dist_from_edge(v_pos, u_size);

    if(d <= half_edgeweight) {
        color = u_edgecol;
    }
    else {
        color = u_fillcol;
    }
}