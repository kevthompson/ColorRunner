import os, sys
import json
import pygame
from pygame.locals import *

from game import *
from menu import *

    
if not pygame.font: print("Warning, fonts disabled")
if not pygame.mixer: print("Warning, sound disabled")

display_width = 800
display_height = 600

pygame.init()
pygame.display.set_caption('ColorRunner')
pygame.mouse.set_visible(0)

screen = pygame.display.set_mode((display_width, display_height))

clock = pygame.time.Clock()

def gameMenu():
    intro = True

    while intro:
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        screen.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("ColorRunner", largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(15)

def gameLoop():
    levelNum = 1
    player, goal, platforms = loadLevel(levelNum)
    shiftingLeft = 0
    shiftingRight = 0
    running = True
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
                player.walljumpleft()
            if key[pygame.K_d]:
                player.walljumpright()
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

        shiftingLeft -= 1
        shiftingRight -= 1

        player.update(platforms)

        if player.rect.colliderect(goal): 
            levelNum += 1
            levelPassed(player, goal)
            player, goal, platforms = loadLevel(levelNum)

        platform = player.isDead(platforms)
        if platform is not None:
            levelFailed(player, platform)  
            player, goal, platforms = loadLevel(levelNum)

        draw(player, goal, platforms)

def loadLevel(levelNum):
    platforms = []
    x = y = 0
    src="{0}/levels.json".format(main_dir)
    with open(src) as f:
        stages = json.load(f)
    levelName = "level{0}".format(levelNum)
    if levelName not in stages:
        gameWin()
    level_width = len(stages[levelName])
    level_height = len(stages[levelName][0])
    for row in stages[levelName]:
        for col in row:
            if col is " ":
                pass
            elif col is "s":
                player = Player((x, y))
            elif col is "G":
                goal = Goal((x, y))
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
    return player, goal, platforms

def draw(player, goal, platforms):
    screen.fill(BACKGROUND)
    for platform in platforms:
        pygame.draw.rect(screen, platform.color, platform.rect)
    pygame.draw.rect(screen, goal.color, goal.rect)
    pygame.draw.rect(screen, BLACK, player.rect)
    pygame.draw.rect(screen, player.color, player.innerRect)
    pygame.display.flip()

def gameOver(player, platform=None):
    screen.fill(BACKGROUND)
    if platform:
        pygame.draw.rect(screen, WHITE, platform.rect)
    pygame.draw.rect(screen, WHITE, player.rect)
    pygame.display.flip()

    print("Game Over")
    raise SystemExit

def gameWin():
    print("You Win")
    raise SystemExit

def levelPassed(player, goal):
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GOLD, goal.rect)
    pygame.draw.rect(screen, GOLD, player.rect)
    pygame.display.flip()
    pygame.time.delay(1000)

def levelFailed(player, platform=None):
    screen.fill(BACKGROUND)
    if platform:
       pygame.draw.rect(screen, WHITE, platform.rect)
    pygame.draw.rect(screen, WHITE, player.rect)
    pygame.display.flip()
    pygame.time.delay(1000)

gameLoop()