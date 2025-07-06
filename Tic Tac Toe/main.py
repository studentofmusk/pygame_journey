import pygame
from pygame.locals import *

pygame.init()

screen_width = 300
screen_height = 300

# define color
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# define font
font = pygame.font.SysFont(None, 40)

# create again rectange
again_rect = Rect(screen_width//2 -80, screen_height//2, 160, 50)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("TicTacToe")

# define variables
line_width = 6
markers = []
clicked = False
pos = []
player = 1
winner = 0
gameover = False


def draw_grid():
    bg = (255, 255, 200)
    grid = (50, 50, 50)

    screen.fill(bg)
    for x in range(1, 3):
        pygame.draw.line(screen, grid, (0, x*100), (screen_width, x*100), line_width)
        pygame.draw.line(screen, grid, (x*100, 0), (x*100, screen_height), line_width)

def draw_markers():
    x_pos = 0
    for i in range(3):
        y_pos = 0
        for j in range(3):
            if markers[i][j] == 1:
                pygame.draw.line(screen, red, (x_pos * 100 + 15, y_pos * 100 + 15), (x_pos * 100 + 85, y_pos * 100 + 85), line_width)
                pygame.draw.line(screen, red, (x_pos * 100 + 15, y_pos * 100 + 85), (x_pos * 100 + 85, y_pos * 100 + 15), line_width)
            elif markers[i][j] == -1:
                pygame.draw.circle(screen, green, (x_pos * 100 + 50, y_pos * 100 + 50), 36, line_width)
            y_pos += 1
        x_pos += 1


def check_winner():
    global winner, gameover
    
    y_pos = 0
    for row in markers:

        row_sum = sum(row)
        if row_sum == 3:
            winner = 1
            gameover = True
        if row_sum == -3:
            winner = 2
            gameover = True

        column_sum = markers[0][y_pos] + markers[1][y_pos] + markers[2][y_pos]
        if column_sum == 3:
            winner = 1
            gameover = True
        if column_sum == -3:
            winner = 2
            gameover = True

    # check diagonal
    diag1 = markers[0][0] + markers[1][1] + markers[2][2]
    diag2 = markers[0][2] + markers[1][1] + markers[2][0]
    
    if diag1 == 3 or diag2 == 3:
        winner = 1
        gameover = True

    if diag1 == -3 or diag2 == -3:
        winner = 2
        gameover = True

        

def draw_winner():
    win_text = "Player" + str(winner) + " wins!"
    win_img = font.render(win_text, True, blue)        
    pygame.draw.rect(screen, green, (screen_width//2 - 100, screen_height//2 - 60, 200, 50))
    screen.blit(win_img, (screen_width//2 -100 , screen_height // 2 - 50))

    again_text = "Play Again?"
    again_img = font.render(again_text, True, blue)
    pygame.draw.rect(screen, green, again_rect)
    screen.blit(again_img, (screen_width//2 -80, screen_height//2 + 10))

for i in range(3):
    row = [0] * 3
    markers.append(row)

run = True

while run:

    draw_grid()
    draw_markers()

    # add event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if not gameover:
            if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
                clicked = True
            if event.type == pygame.MOUSEBUTTONUP and clicked == True:
                clicked = False
                pos = pygame.mouse.get_pos()
                cell_x = pos[0]
                cell_y = pos[1]

                if markers[cell_x//100][cell_y//100] == 0:
                    markers[cell_x//100][cell_y//100] = player
                    player *= -1
                    check_winner()
    if gameover:
        draw_winner()
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
        if event.type == pygame.MOUSEBUTTONUP and clicked == True:
            clicked = False
            pos = pygame.mouse.get_pos()
            if again_rect.collidepoint(pos):
                # reset state
                gameover = False
                winner = 0
                markers = [[0]*3 for i in range(3)]
                player = 1
                pos = []
        

    pygame.display.update()
    
pygame.quit()