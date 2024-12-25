import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import numpy as np
import sys

# Initialize Pygame and OpenGL
pygame.init()

# Get the primary monitor's resolution
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

# Set up the display in borderless fullscreen
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL | pygame.NOFRAME)
pygame.display.set_caption("3D MAGNUS OpenGL")

class Text3D:
    def __init__(self, text="MAGNUS"):
        self.text = text
        # Define vertices for each letter as simple 3D lines
        self.letters = {
            'M': [(-0.5, -0.5, 0), (-0.5, 0.5, 0), (0, 0, 0), (0.5, 0.5, 0), (0.5, -0.5, 0)],
            'A': [(-0.3, -0.5, 0), (0, 0.5, 0), (0.3, -0.5, 0), (-0.15, 0, 0), (0.15, 0, 0)],
            'G': [(0.3, 0.2, 0), (0, 0.3, 0), (-0.3, 0, 0), (-0.3, -0.3, 0), (0, -0.4, 0), (0.3, -0.3, 0), (0.3, 0, 0), (0, 0, 0)],
            'N': [(-0.3, -0.5, 0), (-0.3, 0.5, 0), (0.3, -0.5, 0), (0.3, 0.5, 0)],
            'U': [(-0.3, 0.5, 0), (-0.3, -0.3, 0), (0, -0.5, 0), (0.3, -0.3, 0), (0.3, 0.5, 0)],
            'S': [(0.3, 0.4, 0), (0, 0.5, 0), (-0.3, 0.3, 0), (-0.3, 0.1, 0), (0, 0, 0), (0.3, -0.1, 0), (0.3, -0.3, 0), (0, -0.5, 0), (-0.3, -0.4, 0)]
        }
        self.letter_width = 1.0  # Space between letters

    def draw(self):
        glPushMatrix()
        # Center the text
        total_width = len(self.text) * self.letter_width
        glTranslatef(-total_width/2, 0, 0)
        
        # Set material properties for lighting
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Draw each letter
        for char in self.text:
            if char in self.letters:
                # Draw the letter
                glBegin(GL_LINE_STRIP)
                for vertex in self.letters[char]:
                    # Add depth to make it 3D
                    glVertex3f(vertex[0], vertex[1], 0)
                    glVertex3f(vertex[0], vertex[1], 0.2)  # Back face
                glEnd()
                
                # Draw connecting lines for depth
                glBegin(GL_LINES)
                for vertex in self.letters[char]:
                    glVertex3f(vertex[0], vertex[1], 0)
                    glVertex3f(vertex[0], vertex[1], 0.2)
                glEnd()
            
            # Move to next letter position
            glTranslatef(self.letter_width, 0, 0)
        
        glPopMatrix()

class Particle:
    def __init__(self):
        self.reset()
        self.trail = []
        self.max_trail_length = random.randint(15, 30)
        self.color_scheme = random.choice([
            # Blue-cyan scheme
            {'trail': (0.0, 0.8, 1.0), 'core': (0.5, 1.0, 1.0)},
            # Deep blue scheme
            {'trail': (0.0, 0.4, 1.0), 'core': (0.3, 0.7, 1.0)},
            # Cyan scheme
            {'trail': (0.0, 1.0, 0.8), 'core': (0.4, 1.0, 0.9)},
            # Purple-blue scheme
            {'trail': (0.5, 0.0, 1.0), 'core': (0.7, 0.4, 1.0)}
        ])

    def reset(self):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(3, 8)
        self.pos = np.array([
            math.cos(angle) * radius,
            random.uniform(-3, 3),
            math.sin(angle) * radius
        ])
        self.time = random.uniform(0, 100)
        self.speed = random.uniform(0.02, 0.06)
        self.orbit_radius = radius
        self.base_y = self.pos[1]
        self.size = random.uniform(0.05, 0.15)

    def draw_sphere(self, radius, slices, stacks):
        # Draw a sphere using triangles
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
            glEnd()

    def move(self):
        self.time += self.speed
        
        # Orbital motion with vertical oscillation
        angle = self.time
        self.pos[0] = math.cos(angle) * self.orbit_radius
        self.pos[2] = math.sin(angle) * self.orbit_radius
        self.pos[1] = self.base_y + math.sin(self.time * 2) * 0.5
        
        # Update trail
        self.trail.append(np.copy(self.pos))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw(self):
        # Draw trail with color scheme
        glBegin(GL_LINE_STRIP)
        for i, pos in enumerate(self.trail):
            alpha = i / len(self.trail)
            color = self.color_scheme['trail']
            glColor4f(color[0], color[1], color[2], alpha)
            glVertex3f(*pos)
        glEnd()
        
        glPushMatrix()
        glTranslatef(*self.pos)
        
        # Set up light at particle position with color matching
        light_pos = [0, 0, 0, 1.0]
        color = self.color_scheme['core']
        glLightfv(GL_LIGHT1, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [color[0], color[1], color[2], 1.0])
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.3)
        
        # Draw the glowing particle
        glDisable(GL_LIGHTING)
        glColor4f(*color, 1.0)
        self.draw_sphere(self.size, 8, 8)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Ambient light
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 5.0, 5.0, 1.0])

def main():
    text3d = Text3D()
    particles = [Particle() for _ in range(40)]
    setup_lighting()
    
    # Set up camera
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH/HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    camera_distance = 10.0
    
    clock = pygame.time.Clock()
    rotation = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Exit on any key press
            elif event.type == pygame.KEYDOWN:
                running = False

        # Clear screen and set up camera
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(
            math.sin(rotation*0.01) * camera_distance, 3, math.cos(rotation*0.01) * camera_distance,
            0, 0, 0,
            0, 1, 0
        )
        
        # Draw text
        text3d.draw()
        
        # Update and draw particles
        for particle in particles:
            particle.move()
            particle.draw()
        
        pygame.display.flip()
        clock.tick(60)
        rotation += 1

    pygame.quit()

if __name__ == "__main__":
    main()
