import socket
import threading
import time
import random

myip = '127.0.0.1'
myport = 50000
address = (myip, myport)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(address)
server_sock.listen()
print('마피아 서버 작동 시작')

client_list = []
client_name_dic = {'홍은기': None}
room_list = {}
min_player, max_player = 6, 12


class CError(BaseException):
    pass


def not_con(sock):
    try:
        sendm(sock, '2H3DTESTAB!%FTTHFASDF')
        return 0
    except CError:
        return 1


def remove(sock):
    global client_name_dic, client_list
    client_name_dic.remove(sock)
    client_list.remove(sock)
    sock.close()


def error_block(inner_func):
    def dec_f(client, *args, **kwargs):
        nonlocal inner_func
        try:
            return inner_func(client, *args, **kwargs)
        except:
            print("연결에 실패했습니다.")
            for socket in client_list:
                if not_con(socket):
                    remove(socket)
            raise CError

    return dec_f


send_tmp = error_block(socket.socket.send)
recv_tmp = error_block(socket.socket.recv)


def sendm(client, message, enter=True, line=True):
    global send_tmp
    if line:
        message = "=" * 30 + '\n' + message
    if enter:
        message = message + '\n'
    send_tmp(client, message.encode('utf-8'))


def recvm(client):
    global recv_tmp
    x = recv_tmp(client, 1024)
    return x.decode('utf-8')


class Job:
    def __init__(self, player):
        self.player = player
        self.life = True

    def night(self):
        pass

    def morning(self):
        pass

    def death(self):
        self.life = False


class Mafia(Job):
    def night(self):
        pass

    def morning(self):
        pass


def name_select(sock):
    global client_name_dic
    try:
        name = '홍은기'
        while name in client_name_dic:
            if name in client_name_dic and name != '홍은기':
                sendm(sock, "이미 있는 이름입니다. 다른 이름을 입력해주세요.\n이름 : ", enter=False)
            else:
                sendm(sock, "이름이 뭔가요?\n이름 : ", enter=False)
            name = recvm(sock).strip(' ')
        sendm(sock, "안녕하세요, {}님!".format(name))
    except CError:
        return
    client_list.append(sock)
    client_name_dic[sock] = name
    print("{}가 접속하였습니다.".format(client_name_dic[sock]))
    print("현재 연결된 사용자: {}".format(client_name_dic))


def room_list_print(sock):
    global room_list
    sendm(sock, "현재 만들어져있는 방들\n"+"-"*30)
    sendm(sock, "제목           사람 수", line=False)
    for name in room_list:
        room = room_list[name]
        sendm(sock, "{}{}    {} / {}".format(name, ' ' * (10 - len(name)), len(room.player_list), room.player_num),
              line=False)


def connection():
    global client_list

    while True:
        client_sock, client_addr = server_sock.accept()
        nameinput = threading.Thread(target=name_select, args=(client_sock,))
        nameinput.start()
        waiting = threading.Thread(target=wait, args=(client_sock, nameinput))
        waiting.start()


def broadcast(cast_list, message, talker=[], enter=True, line=True):
    for sockets in cast_list:
        if sockets not in talker:
            try:
                sendm(sockets, message, enter=enter, line=line)
            except CError:
                continue


class Room:
    def __init__(self, name, num):
        self.player_list = []
        self.name = name
        self.start_flag = False
        self.end_flag = False
        self.player_num = num
        new_game = threading.Thread(target=self.game_start)
        new_game.start()

    def timer(self, sec):
        time.sleep(sec)

    def people_add(self, sock):
        global client_name_dic
        if len(self.player_list) == self.player_num:
            sendm(sock, "인원이 꽉 찼습니다!")
            return False
        elif self.start_flag:
            sendm(sock, "이미 시작했습니다!")
            return False
        else:
            self.player_list.append(sock)
            sendm(sock, "{} 방에 접속했습니다! ({}/{})".format(self.name, len(self.player_list), self.player_num))
            broadcast(self.player_list,
                      "{}님이 접속하셨습니다! ({}/{})".format(client_name_dic[sock], len(self.player_list), self.player_num),
                      talker=[sock])
            people_chat = threading.Thread(target=self.chat, args=(sock,))
            people_chat.start()
            return True

    def chat(self, sock):
        global client_name_dic
        try:
            sendm(sock, "채팅에 들어오셨습니당. 방을 나가시려면 '!나 나갈래!'라고 입력해주시면 됩니다.")
            while not self.start_flag:
                message = recvm(sock)
                if message == '!나 나갈래!':
                    self.kick(sock)
                    return
                broadcast(self.player_list, client_name_dic[sock] + ' : ' + message, talker=[sock], line=False)
        except CError:
            self.kick(sock)
            return

    def kick(self, sock):
        try:
            sendm(sock, "방에서 나가졌습니다!")
            self.player_list.remove(sock)
            broadcast(self.player_list,"{}님이 나가셨습니다.".format(client_name_dic[sock]))
            waiting = threading.Thread(target=wait, args=(sock,))
            waiting.start()
            return
        except CError:
            return

    def game_start(self):
        while len(self.player_list) < self.player_num:
            time.sleep(1)
        self.start_flag = 1
        broadcast(self.player_list, "인원수가 채워졌으니, 게임을 시작하겠습니다!")


def wait(sock, name_f=False):
    global client_name_dic, min_player, max_player, room_list
    if name_f is not False:
        name_f.join()
    while True:
        try:
            sendm(sock, "방을 만드시려면 'new room'을, 지금 있는 방에 들어가시려면 'enter room'을 입력해주세요.\n입력 : ", enter=False)
            message = recvm(sock)

            if message == 'new room':
                room_name, room_maxp = None, None
                sendm(sock, "방의 이름을 입력해주세요. (영어만 가능)\n방 이름 : ", enter=False)
                while room_name is None or not room_name.isalpha() or room_name in room_list:
                    if room_name in room_list:
                        sendm(sock, "이미 있는 방 이름입니다.\n방 이름 : ", enter=False)
                    elif room_name is not None:
                        sendm(sock, "영어만 가능합니다.\n방 이름 : ", enter=False)
                    room_name = recvm(sock)
                if len(room_name) > 10:
                    room_name = room_name[0:9]
                sendm(sock, "입력되었습니다.")
                sendm(sock, "인원은 몇 명으로 할까요? {}~{}명 사이에서 입력해주세요.\n인원수 : ".format(min_player, max_player), enter=False)
                while room_maxp is None or not room_maxp.isdigit() or int(room_maxp) < min_player or int(
                        room_maxp) > max_player:
                    if room_maxp is not None:
                        sendm(sock, "{}~{}명 사이에서 입력해주세요.\n인원수 : ".format(min_player, max_player), enter=False)
                    room_maxp = recvm(sock)
                room_maxp = int(room_maxp)
                sendm(sock, "입력되었습니다.")
                room_list[room_name] = Room(room_name, room_maxp)
                sendm(sock, "{}({}명 방)이 생성되었습니다.".format(room_name, room_maxp))
                room_list[room_name].people_add(sock)
                return

            if message == 'enter room':
                if len(room_list) == 0:
                    sendm(sock, "만들어져 있는 방이 없네요. 새로운 방을 만들어주세요!")
                    continue
                else:
                    added_flag = False
                    while not added_flag:
                        room_list_print(sock)
                        sendm(sock, "들어가고 싶은 방의 이름을 입력해주세요.\n방 이름 : ", enter=False)
                        room_name = None
                        while room_name not in room_list:
                            if room_name is not None:
                                sendm(sock, "해당 이름을 가진 방이 없습니다.\n방 이름 : ", enter=False)
                            room_name = recvm(sock)
                        sendm(sock, "보내드릴게요.")
                        added_flag = room_list[room_name].people_add(sock)
                        if not added_flag:
                            continue
                    return
        except CError:
            return


Base_Server = threading.Thread(target=connection, args=())
Base_Server.start()

Base_Server.join()
server_sock.close()
