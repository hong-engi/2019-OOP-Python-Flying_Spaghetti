# https://gamedev.stackexchange.com/questions/138888/user-input-text-in-pygame
# https://self-learning-java-tutorial.blogspot.com/2015/12/pygame-setting-background-image.html
# https://devnauts.tistory.com/61
import pygame

pygame.init()
validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'

class TextBox(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.text = ""
    self.font = pygame.font.Font(None, 35)
    self.image = self.font.render("Enter your name", False, [0, 0, 0])
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

def new_textBox(a,b):
    newtextBox = TextBox()
    newtextBox.rect.center = (a,b)

window_width = 1024
window_height = 576
size = (window_width, window_height)
screen = pygame.display.set_mode(size)
textBox = TextBox()
shiftDown = False
textBox_x = 576
textBox_y = 30
textBox.rect.center = (textBox_x, textBox_y)
running = True

while running:

  screen.fill([128, 255, 255])
  screen.blit(textBox.image, textBox.rect)
  pygame.display.set_caption("Mafia Game_memo")
  pygame.display.flip()
  for e in pygame.event.get():
    if e.type == pygame.QUIT:
        running = False
    if e.type == pygame.KEYUP:
        if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
            shiftDown = False
    if e.type == pygame.KEYDOWN:
        textBox.add_chr(pygame.key.name(e.key))
        if e.key == pygame.K_SPACE:
            textBox.text += " "
            textBox.update()
        if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
            shiftDown = True
        if e.key == pygame.K_BACKSPACE:
            textBox.text = textBox.text[:-1]
            textBox.update()
        if e.key == pygame.K_RETURN:
            new_textBox(textBox_x, textBox_y + 50)
        if len(textBox.text) > 30:

