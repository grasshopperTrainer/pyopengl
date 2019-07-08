#shader vertex
#version 430 core

layout(location = 0) attribute vec2 a_position;
layout(location = 1) attribute vec2 a_texCoord;

layout(location = 0) uniform mat4 MM;
layout(location = 1) uniform mat4 PM;
layout(location = 2) uniform mat4 VM;

varying vec2 v_texCoord;

void main() {
    v_texCoord = a_texCoord;

    gl_Position = PM*VM*vec4(a_position,0, 1);
}

#shader fragment
#version 430 core

layout(location = 3) uniform vec4 u_fillcol;
layout(location = 4) uniform vec4 u_id_color;
layout(location = 5) uniform sampler2D texSlot;
layout(location = 6) uniform bool useTexture;

varying vec2 v_pos;
varying vec2 v_texCoord;

layout(location = 0) out vec4 diffuse_color;
layout(location = 1) out vec4 id_color;

void main() {
    if(useTexture) {
        vec4 texColor = texture(texSlot, v_texCoord);
        diffuse_color = texColor;
    }
    else {
        diffuse_color = u_fillcol;
        id_color = u_id_color;
    }
}