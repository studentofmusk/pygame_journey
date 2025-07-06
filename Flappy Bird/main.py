import pygame
from pygame.locals import *
import random 

pygame.init()


screen_width = 564
screen_height = 636

clock = pygame.time.Clock()
fps = 60

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# game variables
scale_ratio = 0.7
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 200 # pixels
pipe_frequency = 1500 # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
passed_in = False

# define fonts
font = pygame.font.SysFont("Bauhaus 93", 60)

# define colors
white = (255, 255, 255)


def draw_text(text, font: pygame.font.Font, color, x, y):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))

def scale_image(image: pygame.Surface, ratio: float = scale_ratio):
    scaled_image = pygame.transform.scale(image, (image.get_width() * ratio, image.get_height() * ratio))
    return scaled_image

def reset_game():
    global score
    pipe_group.empty()
    flappy.rect.center = (70, int(screen_height/2))
    score = 0

# load images
bg = pygame.image.load("img/bg.png")
bg = scale_image(bg, scale_ratio)
ground = pygame.image.load("img/ground.png")
ground = scale_image(ground, scale_ratio)
restart_image = pygame.image.load("img/restart.png")

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        self.counter = 0
        for i in range(1, 4):
            img = pygame.image.load(f"img/bird{i}.png")
            self.images.append(scale_image(img, scale_ratio))

        self.index = 0
        self.image = self.images[self.index]
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.flappy_cooldown = 5
        self.velocity = 0
        self.clicked = False
    
    def update(self):
        # print("Velocity:", self.velocity)
        # print("Brid's Bottom:", self.rect.bottom)

        # Gravity
        if flying == True: 
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
                
            if self.rect.bottom < 525:
                self.rect.y += int(self.velocity)

        if not game_over:
            # Jump
            left_clicked = pygame.mouse.get_pressed()[0] 
            if left_clicked and self.clicked == False:
                self.clicked = True
                if self.rect.bottom >= 525:
                    self.rect.bottom -= 10
                self.velocity = -10

            if not left_clicked:
                self.clicked = False

            # handle animation
            self.counter += 1
            if self.counter > self.flappy_cooldown:
                self.counter = 0
                if self.index >= len(self.images)-1:
                    self.index = 0
                else:
                    self.index += 1
                
            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# Pipe Class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, flip):
        super().__init__()
        self.image = pygame.image.load("img/pipe.png")
        self.image = scale_image(self.image, scale_ratio)
        self.rect: pygame.rect.Rect = self.image.get_rect()
        if flip:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - (pipe_gap//2)]
        else:
            self.rect.topleft = [x, y + (pipe_gap//2)]

    def update(self):
        if not game_over and flying == True:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill() 

# Restart Class
class Button():
    def __init__(self, x, y, image: pygame.Surface):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):
        action = False

        # if button pressed
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(70, int(screen_height/2))
bird_group.add(flappy)

restart_btn = Button(screen_width//2 - 50, screen_height//2 - 75, restart_image)

run = True

while run:

    clock.tick(fps)

    # draw bg
    screen.blit(bg, (0, 0))


    # draw sprites
    bird_group.draw(screen)
    pipe_group.draw(screen)


    # update sprites
    bird_group.update()
    pipe_group.update()

    # check for collision
    if (
        pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or 
        flappy.rect.top < 0
    ):
        game_over = True


    # check the score 
    if len(pipe_group) > 0:
        # # check each pipe
        first_pipe: Pipe = pipe_group.sprites()[0]
        if (
            flappy.rect.left > first_pipe.rect.left and
            flappy.rect.right < first_pipe.rect.right and 
            passed_in == False
        ):
            passed_in = True
        
        if (
            passed_in == True and
            flappy.rect.left > first_pipe.rect.right
        ):
            score += 1
            passed_in = False
    

    # draw score
    draw_text(str(score), font, white, screen_width//2, 20)

    # draw scrolling ground
    screen.blit(ground, (ground_scroll, 525))

    if flappy.rect.bottom >= 525:
        game_over = True
        flying = False

    if not game_over and flying == True:

        # generate pipes
        time_now = pygame.time.get_ticks()

        if time_now - last_pipe > pipe_frequency:
            pipe_shift = random.randint(-75, 75)
            
            bottom_pipe = Pipe(screen_width, int(screen_height/2) + pipe_shift, False)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_shift, True)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0


    if game_over:
        if restart_btn.draw():
            # print("Clicked!") 
            game_over = False
            reset_game()

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    

    pygame.display.update()

pygame.quit()