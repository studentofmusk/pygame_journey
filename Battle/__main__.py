import pygame
from pygame.time import Clock
from typing import TypeAlias, List
import random

clock = Clock()
fps = 60

pygame.init()

bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

# Types
Frame: TypeAlias = pygame.Surface
Animation: TypeAlias = List[Frame]
SpriteGroup: TypeAlias = pygame.sprite.Group


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle")

# define font
font = pygame.font.SysFont("Times New Roman", 26)


# define game variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False

# define colors
red = (255, 0, 0)
green = (0, 255, 0)

# Load Images
# -- background
bg_img = pygame.image.load("img/Background/background.png").convert_alpha()
panel_img = pygame.image.load("img/Icons/panel.png").convert_alpha()
sword_img = pygame.image.load("img/Icons/sword.png").convert_alpha()
potion_img = pygame.image.load("img/Icons/potion.png").convert_alpha()

# Fighter class
class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.max_hp = max_hp
        self.health = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.name = name
        self.actions = ["Idle", "Attack", "Hurt", "Death"] 
        self.action = 0 # 0:Idle 1:Attack 2:Hurt 3:Death

        self.animations: List[Animation] = []
        self.last_update = pygame.time.get_ticks()

        for action_name in self.actions: 
            animation: Animation = []
            for i in range(8):
                frame = pygame.image.load(f"img/{self.name}/{action_name}/{i}.png")
                frame = pygame.transform.scale(frame, (frame.get_width() * 3, frame.get_height() * 3))
                animation.append(frame)
            self.animations.append(animation)

        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        cooldown = 100 # milliseconds

        # handle animation
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > cooldown:
            self.frame_index += 1
            if self.frame_index >= len(self.animations[self.action]):
                if self.action == 3: # death
                    self.frame_index = len(self.animations[self.action])-1
                else:
                    self.idle()
            self.image = self.animations[self.action][self.frame_index]
            self.last_update = time_now

    def idle(self):
        # animation updation
        self.action = 0 # idle
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()

    def hurt(self):
        # animation updation
        self.action = 2 # hurt
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()


    def attact(self, target: 'Fighter'):
        damage = self.strength + random.randint(-5, 5)
        target.health -= damage
        target.hurt()
        if target.health < 1:
            target.health = 0
            target.alive = False
            target.death()
        
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)

        # animation updation
        self.action = 1 # attack
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        

    def death(self):
        # animation updation
        self.action = 3 # death
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()


    def draw(self):
        screen.blit(self.image, self.rect)

# Health class
class HealthBar:
    def __init__(self, x:int, y:int, health:int, max_hp:int):
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.healt = health
    
    def draw(self, health: int):
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, int(150 * (health/self.max_hp)), 20))

class Button:
    def __init__(self, button_image: pygame.Surface, x: int, y: int, scale:tuple[int, int]):
        self.image = pygame.transform.scale(button_image, scale)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self) -> bool:
        action = False
        screen.blit(self.image, self.rect.topleft)
        pos = pygame.mouse.get_pos()
        left_clicked = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(pos):
            if left_clicked and not self.clicked:
                self.clicked = True
                action = True  # Trigger only once when mouse is pressed
        if not left_clicked:
            self.clicked = False  # Reset when mouse is released

        return action

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage: str, color):
        super().__init__()
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    
    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

        

# --- Helper Functions ---
def draw_text(text: str, font:pygame.font.Font, color: tuple[int, int, int], x: int, y:int):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (x, y))

def draw_panel():
    screen.blit(panel_img, (0, screen_height-bottom_panel))

    # show knight status
    draw_text(f'{knight.name} HP: {knight.health}', font, red, 100, screen_height- bottom_panel + 10 )

    for count, bandit in enumerate(bandits):
        draw_text(f'{bandit.name} HP: {bandit.health}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

run = True

# Initiate Fighters
knight = Fighter(200, 260, "Knight", 30, 10, 3)
bandit1 = Fighter(400, 270, "Bandit", 20, 6, 1)
bandit2 = Fighter(700, 270, "Bandit", 20, 6, 1)
bandits = [bandit1, bandit2]


# Initiate Sprite Groups
damage_text_group: SpriteGroup = pygame.sprite.Group()


# Initiate HealthBar
knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.health, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.health, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.health, bandit1.max_hp)

# create buttons
potion_button = Button(potion_img, 100, screen_height-bottom_panel + 70, (64, 64))

while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg_img, (0, 0))
    # draw panel
    draw_panel()


    # draw HPs
    knight_health_bar.draw(knight.health)
    bandit1_health_bar.draw(bandit1.health)
    bandit2_health_bar.draw(bandit2.health)

    # update and draw fighters
    knight.update()
    knight.draw()

    for bandit in bandits:
        bandit.update()
        bandit.draw()

    # draw the damage text 
    damage_text_group.update()
    damage_text_group.draw(screen)

    # control player actions 
    # reset action variables
    attack = False
    potion = False
    target = None

    pos = pygame.mouse.get_pos()

    # make sure mouse is visible
    hide_mouse = False
    for count, bandit in enumerate(bandits):
        if bandit.rect.collidepoint(pos) and bandit.alive:
            hide_mouse = True
            # show sword in place of mouse cursor
            screen.blit(sword_img, pos)
            if clicked:
                attack = True
                target = bandit

    # update visibility
    pygame.mouse.set_visible(not hide_mouse)

    # checking for potion
    if potion_button.draw():
        potion = True

    draw_text(str(knight.potions), font, red, 150, screen_height-bottom_panel+70)
    

    # player action
    if knight.alive == True:
        if current_fighter == 1:
            action_cooldown += 1
            if action_cooldown > action_wait_time:
                # Attack
                if attack and target: 
                    knight.attact(target)
                    action_cooldown = 0
                    current_fighter += 1
                # Potion
                if potion == True:
                    if knight.potions > 0:

                        # check hp over flow
                        required_hp = knight.max_hp - knight.health
                        if required_hp >  potion_effect:
                            heal_amount = potion_effect
                        else: 
                            heal_amount = required_hp

                        knight.health += heal_amount
                        knight.potions -= 1
                        action_cooldown = 0
                        current_fighter += 1

                        damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                        damage_text_group.add(damage_text)                    
                         
    # enemy action
    for count, bandit in enumerate(bandits):
        if current_fighter == 2 + count:
            if bandit.alive == True:
                action_cooldown += 1
                if action_cooldown > action_wait_time:

                    # check if bandit needs to heal first
                    if (bandit.health/bandit.max_hp) < 0.5 and bandit.potions > 0:
                        # check health overflow
                        required_hp = bandit.max_hp - bandit.health 
                        if required_hp > potion_effect:
                            heal_amount = potion_effect
                        else:
                            heal_amount = required_hp

                        bandit.health += heal_amount
                        bandit.potions -= 1
                        current_fighter += 1
                        action_cooldown = 0
                        damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                        damage_text_group.add(damage_text)                    
                         
                    
                    else: # attack
                        bandit.attact(knight)
                        current_fighter += 1
                        action_cooldown = 0
            else:
                current_fighter += 1

    if current_fighter > 1 + len(bandits):
        current_fighter = 1


    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
        else:
            clicked = False
    
    pygame.display.update()

pygame.quit()
