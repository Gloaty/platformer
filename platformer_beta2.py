import pygame, sys
from pygame.locals import *

pygame.init()

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer")


#load images
light_img = pygame.image.load("assets/light.png")
player_img = pygame.image.load("assets/player.png")
bg_img = pygame.image.load("assets/bg.png")

run = True
while run:

    screen.blit(bg_img, (0, 0))
    screen.blit(light_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        pygame.display.update()

pygame.quit()
