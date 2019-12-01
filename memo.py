# https://gamedev.stackexchange.com/questions/138888/user-input-text-in-pygame
# https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame
# : 출처

import pygame
import pygame as pg
import sys

# initialize game engine
pygame.init()

black = (0,0,0)

validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'

window_width=1024
window_height=720

animation_increment=10
clock_tick_rate=20

font_title = pygame.font.Font('freesansbold.ttf', 64)
font_press_enter = pygame.font.Font('freesansbold.ttf', 32)
Title = font_title.render('Mafia game_MEMO', True, black)
press_enter = font_press_enter.render('press enter key', True, black)
TitleRect = Title.get_rect()
TitleRect.center = (512, 240)
press_enter_Rect = press_enter.get_rect()
press_enter_Rect.center = (512, 480)

# Open a window
size = (window_width, window_height)
screen = pygame.display.set_mode(size)

# Set title to the window
pygame.display.set_caption("Mafia game_memo")

going = True
dead=False
shiftDown = False

clock = pygame.time.Clock()
background_image = pygame.image.load("background.jpeg").convert()

color_inactive = pg.Color('black')
color_active = pg.Color('black')
global color
color = color_inactive

input_box_1 = pg.Rect(10, 10, 140, 32)
input_box_2 = pg.Rect(10, 60, 140, 32)
input_box_3 = pg.Rect(10, 110, 140, 32)
input_box_4 = pg.Rect(10, 160, 140, 32)
input_box_5 = pg.Rect(10, 210, 140, 32)
input_box_6 = pg.Rect(10, 260, 140, 32)
input_box_7 = pg.Rect(10, 310, 140, 32)
input_box_8 = pg.Rect(10, 360, 140, 32)
input_box_9 = pg.Rect(10, 410, 140, 32)
input_box_10 = pg.Rect(10, 460, 140, 32)
input_box_11 = pg.Rect(10, 510, 140, 32)
input_box_12 = pg.Rect(10, 560, 140, 32)

width = 1000
input_box_1.w = width
input_box_2.w = width
input_box_3.w = width
input_box_4.w = width
input_box_5.w = width
input_box_6.w = width
input_box_7.w = width
input_box_8.w = width
input_box_9.w = width
input_box_10.w = width
input_box_11.w = width
input_box_12.w = width

class TextBox(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.text = ""
    self.font = pygame.font.Font(None, 32)
    self.image = self.font.render("", False, [0, 0, 0])
    self.rect = self.image.get_rect()

  def add_chr(self, char):
    global shiftDown
    if char in validChars and not shiftDown:
        self.text += char
    elif char in validChars and shiftDown:
        self.text += shiftChars[validChars.index(char)]
    self.update()

  def update(self):
    old_rect_pos = self.rect.center
    self.image = self.font.render(self.text, False, [0, 0, 0])
    self.rect = self.image.get_rect()
    self.rect.center = old_rect_pos

def screen_blit_textboxes():
    pg.draw.rect(screen, color, input_box_1, 2)
    pg.draw.rect(screen, color, input_box_2, 2)
    pg.draw.rect(screen, color, input_box_3, 2)
    pg.draw.rect(screen, color, input_box_4, 2)
    pg.draw.rect(screen, color, input_box_5, 2)
    pg.draw.rect(screen, color, input_box_6, 2)
    pg.draw.rect(screen, color, input_box_7, 2)
    pg.draw.rect(screen, color, input_box_8, 2)
    pg.draw.rect(screen, color, input_box_9, 2)
    pg.draw.rect(screen, color, input_box_10, 2)
    pg.draw.rect(screen, color, input_box_11, 2)
    pg.draw.rect(screen, color, input_box_12, 2)

def background_change(background):
    display = pygame.display.set_mode(size)
    display.blit(background, [0, 0])

def starting_screen():
    background_change(background_image)
    screen.blit(Title, TitleRect)
    screen.blit(press_enter, press_enter_Rect)
    global going

    while going:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif not hasattr(event, 'key'):
                continue

            elif event.key == pygame.K_0:
                pygame.quit()
                sys.exit()

            elif event.key == pygame.K_RETURN:
                whitebackground = pygame.image.load("background.jpeg").convert()
                background_change(whitebackground)
                going = False
                break

        pygame.display.update()

def main(pg = pygame):
    font = pg.font.Font(None, 32)
    active = False
    textBox = TextBox()
    textBox_1 = TextBox()
    textBox_2 = TextBox()
    textBox_3 = TextBox()
    textBox_4 = TextBox()
    textBox_5 = TextBox()
    textBox_6 = TextBox()
    textBox_7 = TextBox()
    textBox_8 = TextBox()
    textBox_9 = TextBox()
    textBox_10 = TextBox()
    textBox_11 = TextBox()
    textBox_12 = TextBox()
    done = False
    color_inactive = pg.Color('black')
    color_active = pg.Color('black')
    color = color_inactive
    input_box = pg.Rect(10, 10, 140, 32)
    global shiftDown
    shiftDown = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                    shiftDown = False
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box_1.collidepoint(event.pos):
                    input_box = input_box_1
                    textBox = textBox_1
                    active = not active
                elif input_box_2.collidepoint(event.pos):
                    input_box = input_box_2
                    textBox = textBox_2
                    active = not active
                elif input_box_3.collidepoint(event.pos):
                    input_box = input_box_3
                    textBox = textBox_3
                    active = not active
                elif input_box_4.collidepoint(event.pos):
                    input_box = input_box_4
                    textBox = textBox_4
                    active = not active
                elif input_box_5.collidepoint(event.pos):
                    input_box = input_box_5
                    textBox = textBox_5
                    active = not active
                elif input_box_6.collidepoint(event.pos):
                    input_box = input_box_6
                    textBox = textBox_6
                    active = not active
                elif input_box_7.collidepoint(event.pos):
                    input_box = input_box_7
                    textBox = textBox_7
                    active = not active
                elif input_box_8.collidepoint(event.pos):
                    input_box = input_box_8
                    textBox = textBox_8
                    active = not active
                elif input_box_9.collidepoint(event.pos):
                    input_box = input_box_9
                    textBox = textBox_9
                    active = not active
                elif input_box_10.collidepoint(event.pos):
                    input_box = input_box_10
                    textBox = textBox_10
                    active = not active
                elif input_box_11.collidepoint(event.pos):
                    input_box = input_box_11
                    textBox = textBox_11
                    active = not active
                elif input_box_12.collidepoint(event.pos):
                    input_box = input_box_12
                    textBox = textBox_12
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    textBox.add_chr(pygame.key.name(event.key))
                    if event.key == pg.K_BACKSPACE:
                        textBox.text = textBox.text[:-1]
                        textBox.update()
                        print("good")
                        print(textBox.text)
                    if event.key == pygame.K_SPACE:
                        textBox.text += " "
                        textBox.update()
                    if event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                        shiftDown = True

        # Blit the text.
        screen.blit(textBox.image, (input_box.x + 5, input_box.y + 5))
        pg.display.flip()
        clock.tick(30)


starting_screen()
if going == False:
    screen_blit_textboxes()
    main()

pygame.display.flip()
clock.tick(clock_tick_rate)