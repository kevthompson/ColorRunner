import os, sys
import json
import pygame
from pygame.locals import *


if not pygame.font: print("Warning, fonts disabled")
if not pygame.mixer: print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

TILE_WIDTH = 16
MAX_VEL = TILE_WIDTH / 4
JUMP_VEL = -TILE_WIDTH / 2
GRAVITY = 1
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
WHITE = pygame.Color(255, 255, 255)
goal_color = pygame.Color(200, 200, 0)

# SCREEN_MODES = pygame.FULLSCREEN | pygame.DOUBLEBUF
# SCREEN_MODES = pygame.OPENGL | pygame.DOUBLEBUF
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
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.x_vel = 0
        self.y_vel = 0
        self.x_acc = 0
        self.y_acc = GRAVITY
        self.grounded = False
        self.touchingWallLeft = False
        self.touchingWallRight = False
        self.rect.topleft = (self.x_pos, self.y_pos)

    def move_right(self):
        self.x_acc = min(1, self.x_acc+1)

    def move_left(self):
        self.x_acc = max(-1, self.x_acc-1)

    def jump(self):
        # jump
        if self.grounded:
            self.y_vel = JUMP_VEL
            self.grounded = False
        # walljump
        elif self.touchingWallLeft:
            self.y_vel = JUMP_VEL
            self.x_vel = -JUMP_VEL
            self.touchingWallLeft = False
            self.touchingWallRight = False
        elif self.touchingWallRight:
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

    def move(self, dx, dy):
        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)
    
    def move_single_axis(self, dx, dy):
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

    def checkDeath(self):
        for platform in platforms:
            if self.color == platform.color or platform.color == WHITE:
                if self.rect.colliderect(platform.rect) \
                or self.rect.left == platform.rect.right and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.top \
                or self.rect.right == platform.rect.left and self.rect.top < platform.rect.bottom and self.rect.bottom > platform.rect.top \
                or self.rect.top == platform.rect.bottom and self.rect.left < platform.rect.right and self.rect.right > platform.rect.left \
                or self.rect.bottom == platform.rect.top and self.rect.left < platform.rect.right and self.rect.right > platform.rect.left :

                    screen.fill((0, 0, 0))
                    pygame.draw.rect(screen, WHITE, platform.rect)
                    pygame.draw.rect(screen, WHITE, player.rect)
                    pygame.display.flip()
                    return True
        return False

    def update(self):
        self.x_vel += self.x_acc
        self.y_vel += self.y_acc
        self.x_pos += self.x_vel
        self.y_pos += self.y_vel

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
        self.move(self.x_vel, self.y_vel)



class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, color=BLUE):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], TILE_WIDTH, TILE_WIDTH)
        platforms.append(self)

def loadLevel(levelnum):
    src="{0}/maps/default.json".format(main_dir)
    x = y = 0
    with open(src) as f:
        stages = json.load(f)
    levelnum += 1
    levelName = "level{0}".format(levelnum)
    if levelName not in stages:
        gameOver()
    level_width = len(stages[levelName])
    level_height = len(stages[levelName][0])
    platforms = []
    for row in stages[levelName]:
        for col in row:
            if col is " ":
                pass
            elif col is "s":
                player_pos = (x, y)
            elif col is "G":
                goal_rect = pygame.Rect(x, y, TILE_WIDTH, TILE_WIDTH)
            elif col is "r":
                platforms.append(Platform((x, y), RED))
            elif col is "g":
                platforms.append(Platform((x, y), GREEN))
            elif col is "b":
                platforms.append(Platform((x, y), BLUE))
            elif col is "w":
                platforms.append(Platform((x, y), WHITE))
            x += TILE_WIDTH
        y += TILE_WIDTH
        x = 0
    return player_pos, goal_rect, level_height, level_width

def gameOver(platform=None):
    screen.fill((0, 0, 0))
    if platform:
        pygame.draw.rect(screen, WHITE, platform.rect)
    pygame.draw.rect(screen, WHITE, player.rect)
    pygame.display.flip()

    print("Game Over")
    raise SystemExit

pygame.init()
pygame.display.set_caption('ColorRunner')
pygame.mouse.set_visible(0)

running = True
platforms = []
levelnum = 0
player_pos, goal_rect, level_height, level_width = loadLevel(levelnum)
screen = pygame.display.set_mode((level_height * TILE_WIDTH, level_width * TILE_WIDTH), SCREEN_MODES)
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((150, 150, 150))
pygame.display.flip()

player = Player(player_pos)

for platform in platforms:
    pygame.draw.rect(screen, platform.color, platform.rect)
pygame.draw.rect(screen, goal_color, goal_rect)
pygame.draw.rect(screen, player.color, player.rect)

clock = pygame.time.Clock()
shiftingLeft = 0
shiftingRight = 0
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    key = pygame.key.get_pressed()

    if key[pygame.K_w]:
        player.jump()
    if key[pygame.K_a]:
        player.move_left()
    if key[pygame.K_d]:
        player.move_right()
    if key[pygame.K_q] and shiftingLeft < 0:
        player.shiftColorLeft()
        shiftingLeft = 10
        shiftingRight = 0
    if key[pygame.K_e] and shiftingRight < 0:
        player.shiftColorRight()
        shiftingRight = 10
        shiftingLeft = 0

    player.update()
    shiftingLeft -= 1
    shiftingRight -= 1

    screen.fill((0, 0, 0))
    for platform in platforms:
        pygame.draw.rect(screen, platform.color, platform.rect)
    pygame.draw.rect(screen, goal_color, goal_rect)
    pygame.draw.rect(screen, player.color, player.rect)
    pygame.display.flip()

    if player.rect.colliderect(goal_rect):    
        platforms = []
        levelnum += 1
        player_pos, goal_rect, level_height, level_width = loadLevel(levelnum)
        player = Player(player_pos)
        screen = pygame.display.set_mode((level_height * TILE_WIDTH, level_width * TILE_WIDTH), SCREEN_MODES)
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((150, 150, 150))
        pygame.display.flip()

    elif player.checkDeath():
        player = Player(player_pos)
        pygame.display.flip()