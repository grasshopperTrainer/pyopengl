# shader vertex
#version 430

layout(location = 0) attribute vec2 vertex;

void main() {
    gl_Position = vec4(vertex, 0., 1.);
}

# shader fragment
#version 430

out vec4 diffuse_color;

void main() {
    diffuse_color = vec4(0.,0.,0.,0.);
}