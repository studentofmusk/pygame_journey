import pygame
from pygame.locals import *
import random

pygame.init()

# define dimentions
screen_width = 600
screen_height = 600

# define colors
bg = (255, 200, 255)
body_inner = (50, 175, 25)
body_outer = (100, 100, 200)
red = (255, 0, 0)
food_col = (200, 50, 50)
blue = (0, 0, 255)

# define fonts
font = pygame.font.SysFont(None, 40)

# create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake")

# define game variables
cell_size = 10
direction = 1 # 1->up; 2->right; 3->down; 4->left;
update_snake = 0 
food = [0, 0]
new_food = True
new_piece = [0, 0]
score = 0
game_over = False
clicked = False
 
# create snake
snake_pos = [[int(screen_width//2), int(screen_height//2)]]
snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size])
snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size * 2])
snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size * 3])


# setup a rectangle for play again
again_rect = Rect(screen_width//2 - 80, screen_height//2, 160, 50)

def draw_screen():
    screen.fill(bg)

def draw_score():
    score_text = "Score: "+ str(score)
    score_img = font.render(score_text, True, blue)
    screen.blit(score_img, (0, 0))

def is_game_over():
    # if snake has eaten itself
    for segment in snake_pos[1:]:
        if snake_pos[0] == segment:
            return True 
    
    # if snake has gone out of bounds
    if (
        snake_pos[0][0] < 0 or 
        snake_pos[0][0] >= screen_width or
        snake_pos[0][1] < 0 or 
        snake_pos[0][1] >= screen_height
    ):
        return True
     
    return False

def draw_game_over():
    game_over_text = "Game Over!"
    game_over_img = font.render(game_over_text, True, blue)
    # pygame.draw.rect(screen, red, (screen_width//2 - 80, screen_height//2 -60, 160, 50))
    screen.blit(game_over_img, (screen_width//2 - 80, screen_height//2 - 50))

    again_text = "Play Again?"
    again_img = font.render(again_text, True, blue)
    pygame.draw.rect(screen, red, again_rect)
    screen.blit(again_img, (screen_width//2 - 80, screen_height//2 + 10))

    

run = True

while run:
    
    draw_screen()
    draw_score()

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 3:
                direction = 1
            elif event.key == pygame.K_RIGHT and direction != 4:
                direction = 2
            elif event.key == pygame.K_DOWN and direction != 1:
                direction = 3
            elif event.key == pygame.K_LEFT and direction != 2:
                direction = 4

    
    if not game_over:
        if update_snake > 99:
            update_snake = 0
            snake_pos = snake_pos[-1:] + snake_pos[:-1]

            # heading up
            if direction == 1: # up
                snake_pos[0][0] = snake_pos[1][0]
                snake_pos[0][1] = snake_pos[1][1] - cell_size
            elif direction == 2: # right
                snake_pos[0][0] = snake_pos[1][0] + cell_size
                snake_pos[0][1] = snake_pos[1][1]
            elif direction == 3: # down
                snake_pos[0][0] = snake_pos[1][0] 
                snake_pos[0][1] = snake_pos[1][1] + cell_size
            elif direction == 4: # right
                snake_pos[0][0] = snake_pos[1][0] - cell_size
                snake_pos[0][1] = snake_pos[1][1]
                
            game_over = is_game_over()

    if game_over:
        draw_game_over()
        
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
        if event.type == pygame.MOUSEBUTTONUP and clicked == True:
            clicked = False
            pos = pygame.mouse.get_pos()
            if again_rect.collidepoint(pos):
                direction = 1
                update_snake = 0 
                food = [0, 0]
                new_food = True
                new_piece = [0, 0]
                score = 0
                game_over = False

                # create snake
                snake_pos = [[int(screen_width//2), int(screen_height//2)]]
                snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size])
                snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size * 2])
                snake_pos.append([int(screen_width//2), int(screen_height//2)+cell_size * 3])
                
    
    # create food
    if new_food == True:
        new_food = False 
        food[0] = cell_size * random.randint(0, (screen_width//cell_size)-1)
        food[1] = cell_size * random.randint(0, (screen_height//cell_size)-1)

    # draw food 
    pygame.draw.rect(screen, food_col, (food[0], food[1], cell_size, cell_size))


    # check if food has been eaten
    if snake_pos[0] == food:
        new_food = True

        # create a new piece at the last point of the snake's tail
        new_piece = list(snake_pos[-1])
        if direction == 1: # up
            new_piece[1] += cell_size
        elif direction == 2: # right
            new_piece[0] -= cell_size
        elif direction == 3: # down
            new_piece[1] -= cell_size
        elif direction == 4: # left
            new_piece[0] += cell_size
        
        snake_pos.append(new_piece)
        score += 1

    # draw snake 
    head = True
    for x, y in snake_pos:
        if head:
            pygame.draw.rect(screen, body_outer, (x, y, cell_size, cell_size))
            pygame.draw.rect(screen, red, (x+1, y+1, cell_size-2, cell_size-2))
            head = False
        else:
            pygame.draw.rect(screen, body_outer, (x, y, cell_size, cell_size))
            pygame.draw.rect(screen, body_inner, (x+1, y+1, cell_size-2, cell_size-2))

    # update the display
    pygame.display.update()
    update_snake += 1

# end game
pygame.quit()