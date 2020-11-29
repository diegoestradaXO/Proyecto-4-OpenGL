#Diego Estrada
#Carnet 18540
#Gráficas
#Dennis Aldana

import pygame
import numpy
import glm
import pyassimp
import math
import random

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

glClearColor(1, 1, 1, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)

vertex_shader = """
#version 460
layout (location = 0) in vec4 position;
layout (location = 1) in vec4 normal;
layout (location = 2) in vec2 texcoords;

//Se reserva el espacio de las matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform vec4 color;
uniform vec4 light;

out vec4 vertexColor;
out vec2 vertexTexcoords;

void main()
{
    float intensity = dot(normal, normalize(light - position));
    gl_Position = projection * view * model * position;
    vertexColor = color * intensity;
    vertexTexcoords = texcoords;
}

"""

fragment_shader = """
#version 460
layout (location = 0) out vec4 diffuseColor;

in vec4 vertexColor;
in vec2 vertexTexcoords;

uniform sampler2D tex;

void main()
{
    diffuseColor = vertexColor * texture(tex, vertexTexcoords);
}
"""

shader = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER),
)
glUseProgram(shader)

model = glm.mat4(1)
view = glm.mat4(1)
projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000.0)
glViewport(0, 0, 800, 600)

scene = pyassimp.load('./archivos/newBigben.obj')

def glize(node, light, rgbGamingShader):
    model = node.transformation.astype(numpy.float32)
    #render
    for mesh in node.meshes:
        material = dict(mesh.material.properties.items())
        texture = material['file']
        if rgbGamingShader == False:
            texture_surface = pygame.image.load("./archivos/" + texture)
        else:
            texture_surface = pygame.image.load("./archivos/bigben.jpeg" )
        texture_data = pygame.image.tostring(texture_surface,"RGB",1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        vertex_data = numpy.hstack([
            numpy.array(mesh.vertices, dtype=numpy.float32),
            numpy.array(mesh.normals, dtype=numpy.float32),
            numpy.array(mesh.texturecoords[0], dtype=numpy.float32),
        ])

        index_data = numpy.hstack(
            numpy.array(mesh.faces, dtype=numpy.int32)
        )            

        vertex_buffer_object = glGenVertexArrays(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, False, 9 * 4, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 9 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 9 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)

        element_buffer_object = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        glUniformMatrix4fv(
            glGetUniformLocation(shader, "model"), 1 , GL_FALSE,
            model
        )
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "view"), 1 , GL_FALSE, 
            glm.value_ptr(view)
        )
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "projection"), 1 , GL_FALSE, 
            glm.value_ptr(projection)
        )

        diffuse = mesh.material.properties["diffuse"]

        # shader para que parezca neon wave RGB
        if rgbGamingShader == False:
            glUniform4f(glGetUniformLocation(shader, "color"),*diffuse,1)
        else:
            glUniform4f(glGetUniformLocation(shader, "color"),random.randint(0,255)/255,random.randint(0,255)/255,random.randint(0,255)/255,1)
            
        glUniform4f(
            glGetUniformLocation(shader, "light"),
            light.w, light.x, light.y, 1
        )

        glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

    for child in node.children:
        glize(child, light, rgbGamingShader)

camera = glm.vec3(0, 0, 100)

def process_input(rotationX, radius, rotationY, light, rgbGamingShader):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            if event.key == pygame.K_x:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            if event.key == pygame.K_LEFT:
                rotationX = rotationX - 5
                camera.x = radius * math.cos(math.radians(rotationX))
                camera.z = radius * math.sin(math.radians(rotationX))
            if event.key == pygame.K_RIGHT:
                rotationX = rotationX + 10
                camera.x = radius * math.cos(math.radians(rotationX))
                camera.z = radius * math.sin(math.radians(rotationX))
            if event.key == pygame.K_m:
                if radius >= 20:
                    radius = radius - 8
                    camera.x = radius * math.cos(math.radians(rotationX))
                    camera.z = radius * math.sin(math.radians(rotationX))
                else:
                    pass
            if event.key == pygame.K_n:
                if radius <= 100:
                    radius = radius + 8
                    camera.x = radius * math.cos(math.radians(rotationX))
                    camera.z = radius * math.sin(math.radians(rotationX))
                else:
                    pass
            if event.key == pygame.K_UP:
                if rotationY >= 10:
                    rotationY = rotationY - 12
                    camera.y = radius * math.cos(math.radians(rotationY))
                else:
                    pass
            if event.key == pygame.K_DOWN:
                if rotationY <= 130:
                    rotationY = rotationY + 12
                    camera.y = radius * math.cos(math.radians(rotationY))
                else:
                    pass
            if event.key == pygame.K_c:
                light.w = light.w * -1
            if event.key == pygame.K_v:
                light.y = light.y * -1
            if event.key == pygame.K_b:
                light.x = light.x * -1
            if event.key == pygame.K_p:
                if rgbGamingShader == False:
                    rgbGamingShader = True
                else:
                    rgbGamingShader = False

    return rotationX, radius, rotationY, light, rgbGamingShader

rotateX = 0.0
rotateY = 0.0
radius = 100
light = glm.vec4(-100, 300, 0 , 20)
rgbGamingShader = False

while True:
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    view = glm.lookAt(camera, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))    
    glize(scene.rootnode, light, rgbGamingShader)
    rotateX, radius, rotateY, light, rgbGamingShader = process_input(rotateX, radius, rotateY, light, rgbGamingShader)
    clock.tick(15)  
    pygame.display.flip()
