import pygame
from pygame.locals import *
from pygame.time import Clock

pygame.init()

clock = Clock()
screen_width = 600
screen_height = 600


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout")

# define colors
bg = (234, 218, 184)
# -- block colors
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)
# -- paddle color
paddle_color =  (142, 135, 123)
paddle_outline = (100, 100, 100)
# -- text color
text_color = (78, 81, 139)

# define font
font = pygame.font.SysFont("Constantia", 30)

# define game variables
fps = 60
rows = 6
cols = 6
live_ball = False
gameover = False

# Wall object
class Wall:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.width = screen_width//cols
        self.height = 50

    def create_wall(self):
        self.blocks = []
        
        for row in range(self.rows):
            block_row = []
            for col in range(self.cols):
                # generate x and y possition
                block_x = col * self.width
                block_y = row * self.height

                rect = Rect(block_x, block_y, self.width, self.height)

                # Assign block strength based on row
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                
                block = [rect, strength]
                block_row.append(block)

            # Append the row to the full list of blocks
            self.blocks.append(block_row)
    
    def draw(self):
        for row in self.blocks:
            for block in row:
                # Assign a color based on block strength
                if block[1] == 3:
                    block_color = block_blue
                elif block[1] == 2:
                    block_color = block_green
                elif block[1] == 1:
                    block_color = block_red

                pygame.draw.rect(screen, block_color, block[0])
                pygame.draw.rect(screen, bg, (block[0]), 2)
# Paddle object
class Paddle:
    def __init__(self):
        self.reset()

    def move(self):
        self.direction = 0

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1

        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
            self.direction = 1
    
    def draw(self):
        pygame.draw.rect(screen, paddle_color, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def reset(self):
        self.height = 20
        self.width = int(screen_width/6)
        self.speed = 10
        self.x = int((screen_width/2)-(self.width/2))
        self.y = screen_height - (self.height * 2)
        self.rect: pygame.rect.Rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0
# Ball object
class Ball:
    def __init__(self, x, y):
        self.reset(x, y)
    
    def move(self):
        collision_threshold = 5

        # check for collision
        # start off with the assumption that the wall has been destroyed completely
        wall_destroyed = True

        for row in wall.blocks:
            for block in row:

                # check collision
                if self.rect.colliderect(block[0]):
                    # check if collision was from above
                    if (self.rect.bottom - block[0].top) < collision_threshold and self.speed_y > 0:
                        self.speed_y *= -1 
                    # check if collision was from below
                    if (self.rect.top - block[0].bottom) < collision_threshold and self.speed_y < 0:
                        self.speed_y *= -1 
                    # check if collision was from left
                    if (self.rect.right - block[0].left) < collision_threshold and self.speed_x > 0:
                        self.speed_x *= -1 
                    # check if collision was from right
                    if (self.rect.left - block[0].right) < collision_threshold and self.speed_x > 0:
                        self.speed_x *= -1 

                    # reduce the block's strength by doing damage to it
                    if block[1] > 1:
                        block[1] -= 1
                    else:
                        block[0] = (0, 0, 0, 0)

                if block[0] != (0,0,0,0):
                    wall_destroyed = False
        
        if wall_destroyed:
            self.gameover = 1
        


        # -- border collision
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        elif self.rect.top < 0:
            self.speed_y *= -1
        elif self.rect.bottom > screen_height:
            self.gameover = -1
        
        # -- paddle collision
        if self.rect.colliderect(paddle):
            if abs(self.rect.bottom - paddle.rect.top) > collision_threshold:
                
                self.speed_y *= -1
                self.speed_x += paddle.direction
                
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                # self.speed_x *= -1
                pass

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
    
        return self.gameover

    def draw(self):
        pygame.draw.circle(screen, paddle_color, (self.rect.x + self.radius, self.rect.y + self.radius), self.radius)
        pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.radius, self.rect.y + self.radius), self.radius, 3)

    def reset(self, x, y):
        self.radius = 10
        self.x = x-self.radius
        self.y = y
        self.rect: pygame.rect.Rect = Rect(self.x, self.y, self.radius * 2, self.radius * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.gameover = False


def draw_text(text, text_color, font: pygame.font.Font, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# create wall
wall = Wall(rows, cols)
wall.create_wall()
# create paddle
paddle = Paddle()
# create ball
ball = Ball(screen_width//2, paddle.y - paddle.height)

run = True

while run:
    clock.tick(fps)

    screen.fill(bg)

    # draw all objects
    wall.draw()
    paddle.draw()
    ball.draw()

    if live_ball:
        # move paddle
        paddle.move()
        # ball paddle
        gameover = ball.move()

        if gameover != 0:
            live_ball = False

    if not live_ball:
        if gameover == 0:
            draw_text("CLICK ANYWHERE TO START", text_color, font, 100, screen_height//2 + 100)
        elif gameover == 1:
            draw_text("YOU WON!", text_color, font, 240, screen_height//2 + 50)
            draw_text("CLICK ANYWHERE TO START", text_color, font, 100, screen_height//2 + 100)
        elif gameover == -1:
            draw_text("YOU LOST!", text_color, font, 240, screen_height//2 + 50)
            draw_text("CLICK ANYWHERE TO START", text_color, font, 100, screen_height//2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            # Reset everything
            ball.reset(screen_width//2, paddle.y - paddle.height)
            paddle.reset()
            wall.create_wall()

    pygame.display.update()

pygame.quit()