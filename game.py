import os, sys
import json
import pygame
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

TILE_WIDTH = 16
MAX_VEL = TILE_WIDTH / 4
JUMP_VEL = -TILE_WIDTH / 2
GRAVITY = 1
BACKGROUND = (100, 100, 100)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
GOLD = pygame.Color(255, 223, 0)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
SCREEN_MODES = 0 

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


class Player():
    def __init__(self, pos):
        self.color = RED
        self.rect = pygame.Rect(pos[0], pos[1], TILE_WIDTH, TILE_WIDTH)
        self.innerRect = pygame.Rect(pos[0] + 2, pos[1] + 2, TILE_WIDTH - 4, TILE_WIDTH - 4)
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = GRAVITY
        self.grounded = False
        self.touchingWallLeft = False
        self.touchingWallRight = False

    def move_right(self):
        self.x_acc = min(1, self.x_acc+1)

    def move_left(self):
        self.x_acc = max(-1, self.x_acc-1)

    def jump(self):
        if self.grounded:
            self.y_vel = JUMP_VEL
            self.grounded = False
    
    def walljumpright(self):
        if self.touchingWallLeft:
            self.y_vel = JUMP_VEL
            self.x_vel = -JUMP_VEL
            self.touchingWallLeft = False
            self.touchingWallRight = False

    def walljumpleft(self):
        if self.touchingWallRight:
            self.y_vel = JUMP_VEL
            self.x_vel = JUMP_VEL
            self.touchingWallLeft = False
            self.touchingWallRight = False


    def shiftColorRight(self):
        if self.color == RED:
            self.color = GREEN
        elif self.color == GREEN:
            self.color = BLUE
        elif self.color == BLUE:
            self.color = RED

    def shiftColorLeft(self):
        if self.color == RED:
            self.color = BLUE
        elif self.color == BLUE:
            self.color = GREEN
        elif self.color == GREEN:
            self.color = RED

    def move(self, dx, dy, platforms):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0, platforms)
        if dy != 0:
            self.move_single_axis(0, dy, platforms)
        self.innerRect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, TILE_WIDTH - 4, TILE_WIDTH - 4)

    def move_single_axis(self, dx, dy, platforms):
        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0: # Moving right; Hit the left side of the wall
                    self.rect.right = platform.rect.left
                    self.touchingWallRight = True
                    self.x_vel = 0
                    self.x_acc = 0
                if dx < 0: # Moving left; Hit the right side of the wall
                    self.rect.left = platform.rect.right
                    self.touchingWallLeft = True
                    self.x_vel = 0
                    self.x_acc = 0
                if dy > 0: # Moving down; Hit the top side of the wall
                    self.rect.bottom = platform.rect.top
                    self.grounded = True
                    self.y_vel = 0
                if dy < 0: # Moving up; Hit the bottom side of the wall
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0

    def isDead(self, platforms):
        for platform in platforms:
            if self.color == platform.color or platform.color == WHITE:
                if self.rect.colliderect(platform.rect) \
                or self.rect.left == platform.rect.right and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.top \
                or self.rect.right == platform.rect.left and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.top \
                or self.rect.top == platform.rect.bottom and self.rect.left < platform.rect.right and self.rect.right > platform.rect.left \
                or self.rect.bottom == platform.rect.top and self.rect.left < platform.rect.right and self.rect.right > platform.rect.left :
                    return platform
        return None

    def update(self, platforms):
        self.x_vel += self.x_acc
        self.y_vel += self.y_acc

        self.grounded = False
        self.touchingWallLeft = False
        self.touchingWallRight = False

        if self.x_acc > 0:
            self.x_acc -= 1
        elif self.x_acc < 0:
            self.x_acc += 1
        elif self.x_vel > 0:
            self.x_acc -= 1
        elif self.x_vel < 0:
            self.x_acc += 1

        self.x_vel = max(-MAX_VEL, min(MAX_VEL, self.x_vel))
        self.y_vel = max(JUMP_VEL, min(-JUMP_VEL, self.y_vel))
        self.move(self.x_vel, self.y_vel, platforms)



class Platform:
    def __init__(self, pos, color=BLUE):
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], TILE_WIDTH, TILE_WIDTH)

class Goal:
    def __init__(self, pos):
        self.color = GOLD
        self.rect = pygame.Rect(pos[0], pos[1], TILE_WIDTH, TILE_WIDTH)