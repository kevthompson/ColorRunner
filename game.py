import os, sys
import json
import pygame
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

display_width = 800
display_height = 600

tile_width = 16
max_vel = tile_width / 4
jump_vel = -tile_width / 2
gravity = 1
background = (100, 100, 100)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
gold = pygame.Color(255, 223, 0)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
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

def load_level(level_name):
    player = Player((-1, -1))
    goal = Goal((-1, -1))
    platforms = []
    x = y = 0
    src="{0}/levels.json".format(main_dir)
    with open(src) as f:
        stages = json.load(f)
    if level_name not in stages:
        game_win()
    level_width = len(stages[level_name])
    level_height = len(stages[level_name][0])
    for row in stages[level_name]:
        for col in row:
            if col is " ":
                pass
            elif col is "s":
                player = Player((x, y))
            elif col is "G":
                goal = Goal((x, y))
            elif col is "r":
                platforms.append(Platform((x, y), red))
            elif col is "g":
                platforms.append(Platform((x, y), green))
            elif col is "b":
                platforms.append(Platform((x, y), blue))
            elif col is "w":
                platforms.append(Platform((x, y), white))
            x += tile_width
        y += tile_width
        x = 0
    return player, goal, platforms

class Player():
    def __init__(self, pos):
        self.color = red
        self.rect = pygame.Rect(pos[0], pos[1], tile_width, tile_width)
        self.inner_rect = pygame.Rect(pos[0] + 2, pos[1] + 2, tile_width - 4, tile_width - 4)
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = gravity
        self.grounded = False
        self.walltouch_left = False
        self.walltouch_right = False

    def move_right(self):
        self.x_acc = min(1, self.x_acc+1)

    def move_left(self):
        self.x_acc = max(-1, self.x_acc-1)

    def jump(self):
        if self.grounded:
            self.y_vel = jump_vel
            self.grounded = False
    
    def walljump_right(self):
        if self.walltouch_left:
            self.y_vel = jump_vel
            self.x_vel = -jump_vel
            self.walltouch_left = False
            self.walltouch_right = False

    def walljump_left(self):
        if self.walltouch_right:
            self.y_vel = jump_vel
            self.x_vel = jump_vel
            self.walltouch_left = False
            self.walltouch_right = False

    def move(self, dx, dy, platforms):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0, platforms)
        if dy != 0:
            self.move_single_axis(0, dy, platforms)
        self.inner_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, tile_width - 4, tile_width - 4)

    def move_single_axis(self, dx, dy, platforms):
        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0: # Moving right; Hit the left side of the wall
                    self.rect.right = platform.rect.left
                    self.walltouch_right = True
                    self.x_vel = 0
                    self.x_acc = 0
                if dx < 0: # Moving left; Hit the right side of the wall
                    self.rect.left = platform.rect.right
                    self.walltouch_left = True
                    self.x_vel = 0
                    self.x_acc = 0
                if dy > 0: # Moving down; Hit the top side of the wall
                    self.rect.bottom = platform.rect.top
                    self.grounded = True
                    self.y_vel = 0
                if dy < 0: # Moving up; Hit the bottom side of the wall
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0

    def is_dead(self, platforms):
        for platform in platforms:
            if self.color == platform.color or platform.color == white:
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

        if self.x_acc > 0:
            self.x_acc -= 1
        elif self.x_acc < 0:
            self.x_acc += 1
        elif self.x_vel > 0:
            self.x_acc -= 1
        elif self.x_vel < 0:
            self.x_acc += 1

        self.x_vel = max(-max_vel, min(max_vel, self.x_vel))
        self.y_vel = max(jump_vel, min(-jump_vel, self.y_vel))
        if self.walltouch_left or self.walltouch_right:
            self.y_vel = min(-jump_vel / 4, self.y_vel)

        self.grounded = False
        self.walltouch_left = False
        self.walltouch_right = False

        self.move(self.x_vel, self.y_vel, platforms)


class Platform:
    def __init__(self, pos, color=blue):
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], tile_width, tile_width)

class Goal:
    def __init__(self, pos):
        self.color = gold
        self.rect = pygame.Rect(pos[0], pos[1], tile_width, tile_width)

def shift_color_right(color):
    if color == red:
        return green
    elif color == green:
        return blue
    elif color == blue:
        return red

def shift_color_left(color):
    if color == red:
        return blue
    elif color == blue:
        return green
    elif color == green:
        return red


def draw(player, goal, platforms):
    screen = pygame.display.get_surface()
    screen.fill(background)
    for platform in platforms:
        pygame.draw.rect(screen, platform.color, platform.rect)
    if(goal.rect.x > 0 and goal.rect.y > 0):
        pygame.draw.rect(screen, goal.color, goal.rect)
    if(player.rect.x > 0 and player.rect.y > 0):
        pygame.draw.rect(screen, black, player.rect)
        pygame.draw.rect(screen, player.color, player.rect.inflate(-4, -4))
    pygame.display.flip()