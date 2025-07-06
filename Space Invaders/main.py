import pygame
from pygame.locals import *
import random

mixer = pygame.mixer.init()
pygame.init()

# define fps
clock = pygame.time.Clock()
fps = 60

screen_width = 400
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

# load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)
explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)
laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

# load images
bg = pygame.image.load("img/bg.png")

# define fons
font30 = pygame.font.SysFont("Constantia", 30)
font40 = pygame.font.SysFont("Constantia", 40)

# define colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# define game variables
COLS = 5
ROWS = 5
alien_cooldown = 1000 # 1 second
last_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
gameover = 0 # 0: tie 1: win -1: lost


# Helpers funcs
def draw_bg():
    screen.blit(bg, (0, 0))

def draw_text(text, font: pygame.font.Font, color, x, y):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))

def create_aliens():
    distance = (screen_width-50) // COLS
    row_distance = 50

    for r in range(ROWS):
        for c in range(COLS):
            alien = Alien(10 + c * distance, 50 + r * row_distance)
            alien_group.add(alien)

# ---- Object ----
# Space object
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 8
        self.health = health
        self.health_left = self.health
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 500 # milliseconds

    def update(self):
        gameover = 0
        key = pygame.key.get_pressed()
        if key[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if key[K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed

        # record current time
        time_now = pygame.time.get_ticks()
        
        # shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > self.cooldown:
            laser_fx.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now
        
        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health indicator
        pygame.draw.rect(screen, red, (self.rect.x, self.rect.bottom + 10, self.rect.width, 15))
        if self.health_left > 0: 
            percent = self.health_left/self.health
            pygame.draw.rect(screen, green, (self.rect.x, self.rect.bottom + 10, self.rect.width * percent, 15))
        elif self.health_left <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            gameover = -1
        return gameover
# Bullet object
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# Alien object
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_img = pygame.image.load(f"img/alien{random.randint(1, 5)}.png")
        self.image = pygame.transform.scale(original_img, (25, 25))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_direction = 1
        self.move_counter = 0
        
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        
        if abs(self.move_counter) > 100:
            self.move_direction *= -1
            self.move_counter =  0
        
 
# Bullet object
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            # sound fx
            explosion2_fx.play()

            # reduce the health of spaceship
            spaceship.health_left -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# Explosion object
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images:list[pygame.Surface] = []
        for i in range(1, 5):
            img = pygame.image.load(f"img/exp{i}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            elif size == 2:
                img = pygame.transform.scale(img, (40, 40))
            elif size == 3:
                img = pygame.transform.scale(img, (120, 120))
            
            self.images.append(img)
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
    
    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1

        if (
            self.counter >= explosion_speed and 
            self.index < len(self.images)-1
        ):
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if animation is complete, delete explosion
        if (
            self.index >= len(self.images) - 1 and
            self.counter >= explosion_speed
        ):
            self.kill()

# create sprit groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# create player
spaceship = Spaceship(screen_width//2, screen_height-100, 3)
spaceship_group.add(spaceship)

# create aliens
create_aliens()

run = True

while run:
    clock.tick(fps)
    draw_bg()
    
    if countdown == 0:
        # Attacking Alein
        time_now = pygame.time.get_ticks()
        if (
            time_now - last_shot > alien_cooldown and
            len(alien_bullet_group) < 5 and
            len(alien_group) > 0
        ):
            attacting_alien: Alien = random.choice(alien_group.sprites())
            alien_bullet = AlienBullet(attacting_alien.rect.centerx, attacting_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_shot = time_now

    
        if len(alien_group) == 0:
            gameover = 1

        if gameover == 0:
            # update spaceship
            gameover = spaceship.update()
            # update bullets
            bullet_group.update()
            # update aliens
            alien_group.update()
            # update bullets
            alien_bullet_group.update()
            # update explosions
            explosion_group.update()
        elif gameover == -1:
            draw_text("GAME OVER!", font40, white, screen_width//2 - 100, screen_height//2)
        elif gameover == 1:
            draw_text("YOU WIN!", font40, white, screen_width//2 - 90, screen_height//2)
        

    
    #  draw sprites
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    if countdown > 0:
        draw_text("GET READY", font40, white, screen_width//2 -100, screen_height//2 + 30)
        draw_text(str(countdown), font40, white, screen_width//2 -10, screen_height//2 + 50)
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()