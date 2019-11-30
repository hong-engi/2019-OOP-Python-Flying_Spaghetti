# https://gamedev.stackexchange.com/questions/138888/user-input-text-in-pygame
# https://self-learning-java-tutorial.blogspot.com/2015/12/pygame-setting-background-image.html
# https://devnauts.tistory.com/61
# 파이게임을 통해 마피아게임을 그래픽으로 구현하고자 했지만 실패한 코드
# 죄송합니다ㅠㅠ (2304 박로진)
import socket, threading
import pygame, sys

server_ip = '127.0.0.1'
server_port = 50000
address = (server_ip, server_port)

# 소켓을 이용해서 서버에 접속
mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysock.connect(address)

pygame.init()

validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'

black = (0, 0, 0)

window_width = 1024
window_height = 576

clock_tick_rate = 40

# Open a window
size = (window_width, window_height)
screen = pygame.display.set_mode(size)

font_title = pygame.font.Font('freesansbold.ttf', 64)
font_press_enter = pygame.font.Font('freesansbold.ttf', 32)
Title = font_title.render('Mafia game', True, black)
press_enter = font_press_enter.render('press enter key', True, black)
TitleRect = Title.get_rect()
TitleRect.center = (512, 238)
press_enter_Rect = press_enter.get_rect()
press_enter_Rect.center = (512, 328)

timelist = list(range(1000))
morninglist = []
nightlist = []
checknightormorning = 0

for i in timelist:
    morninglist.append("{}번째 낮".format(i))
    nightlist.append("{}번째 밤".format(i))

# Set title to the window
pygame.display.set_caption("Mafia Game")

dead = True
shiftDown = False

clock = pygame.time.Clock()
background_image = pygame.image.load("whitebackground.jpeg").convert()


class TextBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.text = ""
        self.font = pygame.font.Font(None, 20)
        self.image = self.font.render("Type here", False, [128, 0, 0])
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


def starting_screen():
    background_change(background_image)
    screen.blit(Title, TitleRect)
    screen.blit(press_enter, press_enter_Rect)
    global dead

    while dead:

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
                whitebackground = pygame.image.load("whitebackground.jpeg").convert()
                background_change(whitebackground)
                dead = False
                break

        pygame.display.update()


def background_change(background):
    display = pygame.display.set_mode(size)
    display.blit(background, [0, 0])


def print_text(text, a, b):
    font = pygame.font.Font('freesansbold.ttf', 32)
    judge_text = font.render(text, True, black)
    judge_text_rect = judge_text.get_rect()
    judge_text_rect.center = (a, b)
    screen.blit(judge_text, judge_text_rect)


def quit_by_enter_key():
    while True:

        if not hasattr(pygame.event, 'key'):
            continue

        elif pygame.event.key == pygame.K_RETURN:
            pygame.quit()
            sys.exit()


# 서버로부터 메시지를 받아, 출력하는 함수.
def receive():
    global mysock
    global background_image
    global checknightormorning
    while True:
        try:
            data = mysock.recv(1024)  # 서버로 부터 값을 받는것
        except ConnectionError:
            background_change(pygame.image.load("error.jpg").convert())
            print_text("서버와 접속이 끊겼습니다. Enter을 누르세요", 576, 288)
            quit_by_enter_key()
            break
        except OSError:
            background_change(pygame.image.load("error.jpg").convert())
            print_text("서버와의 접속을 끊었습니다. Enter을 누르세요", 576, 288)
            quit_by_enter_key()
            break

        if not data:  # 넘어온 데이터가 없다면.. 로그아웃!
            background_change(pygame.image.load("error.jpg").convert())
            print_text("서버로부터 정상적으로 로그아웃했습니다.\nEnter을 누르세요", 576, 288)
            quit_by_enter_key()
            break

        data = data.decode('UTF-8')
        if data == '2H3DTESTAB!%FTTHFASDF':  # 연결 확인
            continue

        if data == 'fEEBgFFDASDL%%@FM' or data == '@)!(확인':  # timer
            mysock.send(bytes('test_message' + data, 'UTF-8'))
            continue

        for i in morninglist:
            if i == data:
                # background_change(pygame.image.load("dayimage.jpg").convert())
                # print_text(data, 576, 288)
                checknightormorning = 'morning'

        for i in nightlist:
            if i == data:
                # background_change(pygame.image.load("nightimage.jpeg").convert())
                # print_text(data, 576, 288)
                checknightormorning = 'night'

        if checknightormorning == 'morning':
            background_change(pygame.image.load("dayimage.jpeg").convert())
            print_text(data, 576, 288)
        # print(data, end='')  # 서버로 부터 받은 값을 출력
        elif checknightormorning == 'night':
            background_change(pygame.image.load("nightimage.jpeg").convert())
            print_text(data, 576, 288)

    try:
        mysock.shutdown(socket.SHUT_RD)
    except OSError:
        background_change(pygame.image.load("error.jpg").convert())
        print_text("읽기 버퍼 닫기 전 서버에서 연결이 종료되었습니다.\n Enter을 누르세요", 576, 288)
        quit_by_enter_key()


# 서버에게 메시지를 발송하는 함수 | Thread 활용
def main_thread():
    global mysock
    global shiftDown

    data = None

    textBox = TextBox()
    textBox.rect.center = (512, 432)
    running = True

    # 메시지 받는 스레스 시작
    thread_recv = threading.Thread(target=receive, args=())
    thread_recv.start()

    while True:
        try:

            while running:

                screen.blit(textBox.image, textBox.rect)
                pygame.display.flip()

                for e in pygame.event.get():
                    print('bye')
                    if e.type == pygame.QUIT:
                        print(0)
                        pygame.quit()
                        sys.exit()
                    if e.type == pygame.KEYUP:
                        print(1)
                        if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                            shiftDown = False
                    if e.type == pygame.KEYDOWN:
                        print(2)
                        textBox.add_chr(pygame.key.name(e.key))
                        if e.key == pygame.K_SPACE:
                            print(3)
                            textBox.text += " "
                            textBox.update()
                        if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                            print(4)
                            shiftDown = True
                        if e.key == pygame.K_BACKSPACE:
                            print(5)
                            textBox.text = textBox.text[:-1]
                            textBox.update()
                        if e.key == pygame.K_RETURN:
                            print(6)
                            if len(textBox.text) > 0:
                                print(1)
                                data = textBox.text
                                running = False

        except KeyboardInterrupt:
            print('keyboardinterrupted')
            continue
        if data == '!quit':
            background_change(pygame.image.load("error.jpg").convert())
            print_text("서버와의 접속을 끊었습니다. Enter을 누르세요", 576, 288)
            quit_by_enter_key()
            break

        try:
            mysock.send(bytes(data, 'UTF-8'))  # 서버에 메시지를 전송
        except ConnectionError:
            break

    background_change(pygame.image.load("error.jpg").convert())
    print_text("소켓의 쓰기 버퍼를 닫습니다.", 576, 288)
    mysock.shutdown(socket.SHUT_WR)
    thread_recv.join()


starting_screen()

if not dead:
    # 메시지 보내는 스레드 시작
    thread_main = threading.Thread(target=main_thread, args=())
    thread_main.start()

    # 메시지를 받고, 보내는 스레드가 종료되길 기다림
    thread_main.join()

    # 스레드가 종료되면, 열어둔 소켓을 닫는다.
    mysock.close()
    # print('소켓을 닫습니다.')
    # print('클라이언트 프로그램이 정상적으로 종료되었습니다.')
