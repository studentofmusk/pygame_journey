import pygame
from pygame.locals import *
import random
from typing import TypeAlias
import pickle
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 700
screen_height = 700

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Platformer")

# define font
font_70 = pygame.font.SysFont("Bauhaus 93", 70)
font_30 = pygame.font.SysFont("Bauhaus 93", 30)

# game variables
scale_ratio = 0.7
tile_size = 35
gameover = 0
main_menue = True
level = 0
max_level = 7
score = 0

# Types
Tile: TypeAlias = tuple[pygame.Surface, pygame.Rect]

# define colors
white = (255, 255, 255)
blue = (0, 0, 255)

def draw_text(text, font: pygame.font.Font, color, x, y):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))

def scale_image(image: pygame.Surface, ratio: float):
    scaled_image = pygame.transform.scale(image, (image.get_width() * ratio, image.get_height() * ratio))
    return scaled_image

def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, white, (line * tile_size, 0), (line * tile_size, screen_height))
        pygame.draw.line(screen, white, (0, line * tile_size), (screen_width, line * tile_size))

def reset_level(level):
    if level > max_level:
        return -1
    else:
        player.reset(70, screen_height - (56+35))
        blob_group.empty()
        lava_group.empty()
        exit_group.empty()
        
        if os.path.exists(f"levels/level{level}_data"):
            pickle_in = open(f"levels/level{level}_data", "rb")
            world_data = pickle.load(pickle_in)
            world.reset(world_data)
        
        return level
        


# load images
sun_img = scale_image(pygame.image.load("img/sun.png"), scale_ratio)
bg_img = scale_image(pygame.image.load("img/sky.png"), scale_ratio)
restart_img = scale_image(pygame.image.load("img/restart_btn.png"), scale_ratio)
start_img = scale_image(pygame.image.load("img/start_btn.png"), scale_ratio)
exit_img = scale_image(pygame.image.load("img/exit_btn.png"), scale_ratio)


# Player class
class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, gameover):

        dx = 0
        dy = 0
        if gameover == 0:
            # check keypresses
            key = pygame.key.get_pressed()


            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.velocity_y = -13
                self.jumped = True
            
            elif key[pygame.K_SPACE] == False:
                self.jumped = False 

            if key[pygame.K_LEFT]:
                self.counter += 1
                self.direction = -1
                dx -= 5

            if key[pygame.K_RIGHT]:
                self.direction = 1
                self.counter += 1
                dx += 5

            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
            


            # Handle animation
            if self.counter > self.walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]


            # gravity
            self.velocity_y += 1
            if self.velocity_y > 5:
                self.velocity_y = 5

            dy += self.velocity_y

            # assume player is in air
            self.in_air = True

            # Check collisions
            for _, tile_rect in world.tiles:
                if tile_rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile_rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    
                    if self.velocity_y < 0:
                        dy = tile_rect.bottom - self.rect.top
                        self.velocity_y = 0

                    elif self.velocity_y >= 0:
                        dy = tile_rect.top - self.rect.bottom
                        self.velocity_y = 0
                        self.in_air = False
            
            if pygame.sprite.spritecollide(self, blob_group, False):
                gameover = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                gameover = -1
                
            if pygame.sprite.spritecollide(self, exit_group, False):
                gameover = 1


            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif gameover == -1:
            self.image = self.dead_image
            if self.rect.y > 140:
                self.rect.y -= 5
        # draw player
        screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, white, self.rect, 2)

        return gameover
    
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        for num in range(1, 5):
            img_right = pygame.image.load(f"img/guy{num}.png")
            img_right = pygame.transform.scale(img_right, (28, 56))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.dead_image = pygame.image.load("img/ghost.png")
        self.dead_image = scale_image(self.dead_image, scale_ratio)

        self.index = 0
        self.counter = 0
        self.image: pygame.Surface = self.images_right[self.index]
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity_y = 0
        self.jumped = False 
        self.walk_cooldown = 5
        self.direction = 1 # 1: right | -1: left
        
# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = scale_image(pygame.image.load("img/blob.png"), scale_ratio)
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y =  y
        self.direction = 1
        self.counter = 0

    def update(self):
        self.rect.x += self.direction
        self.counter += 1
        if abs(self.counter) > 35:
            self.direction *= -1
            self.counter *= -1

# Lava Class
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Exit Class
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(self.image, (tile_size, int(tile_size * 1.5)))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Coin Class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(self.image, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
# World Class 
class World:
    def __init__(self, data):
        self.reset(data)

    def draw(self):
        for tile in self.tiles:
            tile_img, tile_rect = tile
            screen.blit(tile_img, tile_rect)
            pygame.draw.rect(screen, white, tile_rect, 2)

    def reset(self, data):
        self.tiles: list[Tile] = []
        dirt_img = pygame.image.load("img/dirt.png")
        grass_img = pygame.image.load("img/grass.png")
        for row_count, row in enumerate(data):
            for col_count, tile in enumerate(row):
                
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tiles.append((img, img_rect))

                elif tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tiles.append((img, img_rect))
                
                elif tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 10)
                    blob_group.add(blob)
                
                elif tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size//2))
                    lava_group.add(lava)
                
                elif tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size//2), row_count * tile_size + (tile_size//2))
                    coin_group.add(coin)

                elif tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size//2))
                    exit_group.add(exit)

# Button Class
class Button():
    def __init__(self, x, y, image: pygame.Surface):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    
    def draw(self):
        action = False 
        pos = pygame.mouse.get_pos()

        left_clicked = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(pos):
            if left_clicked and self.clicked == False:
                action = True
                self.clicked = True

        if not left_clicked:
            self.clicked = False


        screen.blit(self.image, self.rect)
        return action        



player = Player(70, screen_height - (56+35))
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# creating dummy coin for score board
score_coin = Coin(tile_size//2, tile_size//2)
coin_group.add(score_coin)

if os.path.exists(f"levels/level{level}_data"):
    pickle_in = open(f"levels/level{level}_data", "rb")
    world = World(pickle.load(pickle_in))

# Buttons
restart_button = Button(screen_width//2 - 35, screen_height//2 + 70, restart_img)
start_button = Button(screen_width//2 - 245, screen_height//2, start_img)
exit_button = Button(screen_width//2 + 105, screen_height//2, exit_img)


run = True

while run:
    
    clock.tick(fps)
    
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (70, 70))
    # draw_grid()


    if main_menue:
        if start_button.draw(): main_menue = False
        if exit_button.draw(): run = False
    else:
        # Draw Level
        world.draw()
        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        if gameover == 0:
            blob_group.update()
            
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            
            draw_text(f"X {score}", font_30, white, tile_size-7, 10)

        gameover = player.update(gameover)

        # if player died
        if gameover == -1:
            draw_text('GAME OVER', font_70, blue, (screen_height//2)-140, screen_width//2)
            clicked = restart_button.draw()
            if clicked:
                # Reset the game
                gameover = 0
                score = 0
                level = reset_level(level)                
        
        # if player completed the level 
        elif gameover == 1:
            score = 0
            gameover = 0
            temp_level = reset_level(level + 1)
            

            if temp_level == -1:
                draw_text("YOU WIN!", font_70, blue, (screen_width//2) -100, screen_height//2)
                if restart_button.draw():
                    level = reset_level(0)
                
            elif temp_level != -1:
                level = temp_level
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        
    pygame.display.update()

pygame.quit()

