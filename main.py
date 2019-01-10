import os, sys
import json
import pygame
from pygame.locals import *

from game import *
from menu import *
from creator import *

if not pygame.font: print("Warning, fonts disabled")
if not pygame.mixer: print("Warning, sound disabled")

pygame.init()
pygame.display.set_caption('ColorRunner')
pygame.mouse.set_visible(0)

screen = pygame.display.set_mode((display_width, display_height))

clock = pygame.time.Clock()

def game_loop():
    level_num = 1
    level_name = "level{0}".format(level_num)
    player, goal, platforms = load_level(level_name)
    shifting_left = 0
    shifting_right = 0
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
                player.walljump_left()
            if key[pygame.K_d]:
                player.walljump_right()
        if key[pygame.K_a]:
            player.move_left()
        if key[pygame.K_d]:
            player.move_right()
        if key[pygame.K_q] and shifting_left < 0:
            player.color = shift_color_left(player.color)
            shifting_left = 10
            shifting_right = 0
        if key[pygame.K_e] and shifting_right < 0:
            player.color = shift_color_right(player.color)
            shifting_right = 10
            shifting_left = 0

        shifting_left -= 1
        shifting_right -= 1

        player.update(platforms)

        if player.rect.colliderect(goal): 
            level_num += 1
            level_passed(player, goal)
            level_name = "level{0}".format(level_num)
            player, goal, platforms = load_level(level_name)

        platform = player.is_dead(platforms)
        if platform is not None:
            level_failed(player, platform)  
            level_name = "level{0}".format(level_num)
            player, goal, platforms = load_level(level_name)

        draw(player, goal, platforms)

def game_over(player, platform=None):
    screen.fill(background)
    if platform:
        pygame.draw.rect(screen, white, platform.rect)
    pygame.draw.rect(screen, white, player.rect)
    pygame.display.flip()

    print("Game Over")
    raise SystemExit

def game_win():
    print("You Win")
    raise SystemExit

def level_passed(player, goal):
    screen.fill(background)
    pygame.draw.rect(screen, gold, goal.rect)
    pygame.draw.rect(screen, gold, player.rect)
    pygame.display.flip()
    pygame.time.delay(1000)

def level_failed(player, platform=None):
    screen.fill(background)
    if platform:
       pygame.draw.rect(screen, white, platform.rect)
    pygame.draw.rect(screen, white, player.rect)
    pygame.display.flip()
    pygame.time.delay(1000)

selection = game_menu()
if selection == 0:
    game_loop()
elif selection == 1:
    creator_loop()
else:
    pygame.quit()
    quit()