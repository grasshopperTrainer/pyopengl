#shader vertex
#version 430 core

attribute vec2 a_position;
attribute vec2 a_texCoord;

uniform mat4 MM;
uniform mat4 PM;
uniform mat4 VM;

varying vec2 v_texCoord;

void main() {
    v_texCoord = a_texCoord;

    gl_Position = PM*VM*MM*vec4(a_position,0, 1);
}

#shader fragment
#version 430 core

uniform vec4 u_fillcol;
uniform sampler2D texSlot;
uniform bool useTexture;


varying vec2 v_pos;
varying vec2 v_texCoord;

out vec4 color;

void main() {
    if(useTexture) {
        vec4 texColor = texture(texSlot, v_texCoord);
        color = texColor;
    }
    else {
        color = u_fillcol;
    }
}