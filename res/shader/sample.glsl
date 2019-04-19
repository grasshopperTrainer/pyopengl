
#shader vertex
#version 330 core

layout(location = 0) in vec4 position;
layout(location = 1) in vec2 texCoord;

varying vec2 v_texCoord;
void main() {
    v_texCoord = texCoord;
    gl_Position = position;
}


#shader fragment
#version 330 core

layout(location = 0) out vec4 color;
uniform vec4 u_color;

uniform sampler2D texSlot;

varying vec2 v_texCoord;

void main() {
    vec4 texColor = texture(texSlot, v_texCoord);
    color = u_color;
}