import sys

import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#game font
font_score = pygame.font.SysFont('Bauhaus 93', 30)
game_over_font = pygame.font.SysFont('Bauhaus 93', 100)
#define game variables
tile_size = 50
game_over = False
main_menu = True
level = 0
max_level = 7
score = 0

#define colours
white = (255,255,255)
cyan = (0,255,255)
red = (255,0,0)

#load images
light_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/light.png')
bg_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/bgs/altbg3.v4.png')
restart_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/restart_resized_256.png')
start_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/start.png')
exit_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/exit.png')

#load sounds
coin_fx = pygame.mixer.Sound('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/music/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/music/jump.wav')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/music/game_over.wav')
death_fx.set_volume(0.5)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_grid():
    for line in range(0,20):
        pygame.draw.line(screen, (255,255,255), (0,line*tile_size), (screen_width,line*tile_size))
        pygame.draw.line(screen, (255,255,255), (line*tile_size,0), (line*tile_size,screen_height))

def reset_level(level):
    player.reset(100, screen_height - 100)
    enemy_group.empty()
    lava_group.empty()
    door_group.empty()
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

class Player():
    def __init__ (self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:

            #get keypresses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if keys[pygame.K_SPACE] == False:
                self.jumped = False
            if keys[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if keys[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            
            #add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            self.in_air = True
            for tile in world.tile_list:
                #x collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                    dx = 0
                #y collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            
            #enemy collision check
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1

            #lava collision check
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            #door collision check
            if pygame.sprite.spritecollide(self, door_group, False):
                game_over = 1
                    
            #temp
            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                self.jumped = False
                self.vel_y = 0
            
            #update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            draw_text('GAME OVER!', game_over_font, red, screen_width// 2 - 140, screen_height//2)
            self.image = self.death_image
            if self.rect.y > 200:
                self.rect.y -= 5

        #draw player to screen
        screen.blit(self.image, (self.rect.x, self.rect.y))
        #optional - show player rect
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range (1, 3):
            img_right = pygame.image.load(f'/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/player{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.death_image = pygame.image.load(f'/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/ghost_resized_64.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        
class World():
    def __init__(self, data):
        self.tile_list = []
        #load images
        ground_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/altground.png')
        mossy_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/altmossy.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(ground_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile= (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(mossy_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile= (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    enemy_group.add(enemy)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size//2))
                    lava_group.add(lava)
                if tile == 7:
                    diamond = Diamond(col_count * tile_size + (tile_size//2), row_count * tile_size + (tile_size//2))
                    diamond_group.add(diamond)
                    pass
                if tile == 8:
                    door = Door(col_count * tile_size, row_count * tile_size - (tile_size//2))
                    door_group.add(door)
                col_count += 1
            row_count += 1

    def draw (self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/altenemy.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        lava_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/altlava.png')
        self.image = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        door_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/premade/img/exit.png')
        self.image = pygame.transform.scale(door_img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Diamond(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        diamond_img = pygame.image.load('/home/gloaty/Desktop/Coding/Code Metro/Platformer/assets/imgs/diamond.png')
        self.image = pygame.transform.scale(diamond_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

player = Player(100, screen_height - 130)

enemy_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()

if path.exists(f'/home/gloaty/Desktop/Coding/Code Metro/Platformer'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

restart_button = Button(screen_width//2 - 50, screen_height//2 + 100, restart_img)
start_button = Button(screen_width//2 - 350, screen_height//2, start_img)
exit_button = Button(screen_width//2 + 150, screen_height//2, exit_img)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(light_img, (100, 100))

    if main_menu == True:
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False

    else:
        world.draw()

        if game_over == 0:
            enemy_group.update()
            if pygame.sprite.spritecollide(player, diamond_group, True):
                score += 1
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        enemy_group.draw(screen)
        lava_group.draw(screen)
        diamond_group.draw(screen)
        door_group.draw(screen)
        #optional - draw_grid()

        score_diamond = Diamond(tile_size // 2, tile_size // 2)
        diamond_group.add(score_diamond)

        game_over = player.update(game_over)

        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        if game_over == 1:
            level += 1
            if level <= max_level:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', game_over_font, cyan, (screen_width//2) - 140, screen_height//2)
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()