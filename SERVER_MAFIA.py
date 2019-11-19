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
name_dic = {'example': '홍은기'}
room_list = {}
min_player, max_player = 1, 12
mafia_num = {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3}


def isalpha(text):
    for char in text:
        if not 'a' <= char <= 'z' and not 'A' <= char <= 'Z':
            return False
    return True


class CError(BaseException):
    pass


def not_con(sock):
    try:
        sock.send(bytes('2H3DTESTAB!%FTTHFASDF', 'UTF-8'))
        time.sleep(0.1)
        return 0
    except Exception as e:
        print(e)
        return 1


def remove(sock):
    try:
        global name_dic, client_list
        del name_dic[sock]
        client_list.remove(sock)
        sock.close()
    except:
        return


def cerror_block(inner_func):
    def dec_f(*args, **kwargs):
        nonlocal inner_func
        try:
            return inner_func(*args, **kwargs)
        except CError:
            return

    return dec_f


def error_block(inner_func):
    def dec_f(client, *args, **kwargs):
        nonlocal inner_func
        try:
            return inner_func(client, *args, **kwargs)
        except:
            if client in name_dic:
                print("{}의 연결에 실패했습니다.".format(name_dic[client]))
            remove(client)
            raise CError

    return dec_f


def sendm(client, msg, enter=True, line=True, line_chr='='):
    try:
        if line:
            msg = line_chr * 100 + '\n' + msg
        if enter:
            msg = msg + '\n'
        error_block(socket.socket.send)(client, msg.encode('utf-8'))
    except CError:
        return None


def recvm(client):
    try:
        x = error_block(socket.socket.recv)(client, 1024)
        return x.decode('utf-8')
    except CError:
        return None


class Job:
    def __init__(self, player, room):
        self.player = player
        self.room = room
        self.alive = True
        self.sel = None
        self.name = 'default'
        self.shut_up = False

    @cerror_block
    def night(self):
        self.sel = None
        self.room.print_players(self.player)
        while not self.room.timeout:
            msg = recvm(self.player)
            if self.room.timeout:
                break
            if msg == '!help':
                self.print_help()
                continue
            if msg[0:1] == '!':
                x = self.num_select(msg)
                if x is not False:
                    self.sel = self.select(self.room.p_list[x])
                continue
            else:
                self.night_talk(msg)

    def night_talk(self, msg):
        pass

    @cerror_block
    def morning(self):
        while not self.room.timeout:
            msg = recvm(self.player)
            if self.room.timeout:
                return
            if msg == '!help':
                self.print_help()
            else:
                self.room.talk(self.player, msg)

    @cerror_block
    def vote(self):
        sendm(self.player, '투표 시간입니다! 투표할 사람을 선택해주세요. \n'
                           '선택하는 방법은 "!(선택 번호)"를 입력해주시면 됩니다.')
        vote_flag = False
        self.room.print_players(self.player)
        while not self.room.timeout:
            msg = recvm(self.player)
            if self.room.timeout:
                break
            if msg[0:1] == '!':
                if not vote_flag:
                    x = self.num_select(msg)
                    if x is False:
                        sendm(self.player, "잘못된 입력입니다.", line=False)
                        continue
                    else:
                        vote_flag = True
                        sel_player = self.room.p_list[x]
                        sendm(self.player, "{}(을)를 선택하셨습니다.".format(name_dic[sel_player]))
                        if self.name == '정치인':
                            sendm(self.player, "당신의 권력으로 두 표를 넣습니다.", line=False)
                        broadcast(self.room.p_list, "{}에 한 표!".format(name_dic[sel_player]),
                                  talker=[self.player])
                        if self.name == '정치인':
                            self.room.vote_list[x] += 1
                        self.room.vote_list[x] += 1
                else:
                    sendm(self.player, "이미 투표하셨습니다.")
            elif msg == '!help':
                self.print_help('morning')
            else:
                self.room.talk(self.player, msg)

    @cerror_block
    def print_help(self, mode='default'):
        sendm(self.player, "사람을 선택할 때에는, 입력창에 '!(사람번호)' 를 입력하시면 됩니다.\n"
                           "예를 들어, {0}번 사람을 선택하고 싶으면 '!{0}'를 입력하시면 됩니다.".format(random.randint(1, 8)))

    @cerror_block
    def death(self):
        sendm(self.player, '축하해오! 당신은 뒤졌어오!')
        while not self.room.end_flag:
            msg = recvm(self.player)
            if self.room.end_flag:
                return
            send_msg = '[DEAD]{} : '.format(name_dic[self.player]) + msg
            if not self.shut_up:
                broadcast(self.room.dead_list, send_msg, talker=[self.player])
                if self.room.shaman is not None and self.room.shaman.alive:
                    sendm(self.room.shaman, send_msg)
            else:
                sendm(self.player, "성불되어서 채팅을 사용할 수 없습니다. 닥치세요.")

    @cerror_block
    def num_select(self, msg, shaman=True):
        msg = msg[1:].strip(' ')
        if msg.isdigit() and 1 <= int(msg) <= self.room.player_num:
            if self.room.job[self.room.p_list[int(msg) - 1]].alive == shaman:
                return int(msg) - 1
            else:
                sendm(self.player, "선택 대상이 아닙니다")
                return False
        else:
            sendm(self.player, "잘못 입력하셨습니다.")
            return False

    @cerror_block
    def final_words(self):
        if self.player == self.room.vote_select:
            broadcast(self.room.p_list, "{}의 최후의 한 마디가 있겠습니다!".format(name_dic[self.player]))
            msg = recvm(self.player)
            if self.room.timeout:
                return
            broadcast(self.room.p_list, "< {} : ".format(name_dic[self.player]) + msg + '>')
        else:
            while not self.room.timeout:
                recvm(self.player)
                if self.room.timeout:
                    return

    @cerror_block
    def final_vote(self):
        final_vote_flag = False
        sendm(self.player, "{}(을)를 죽이는 데 찬성하시면 '찬성' 또는 'y',"
                           "반대하시면 '반대' 또는 'n'을 입력하세요."
                           "입력하지 않으면 반대표로 투표됩니다.".format(name_dic[self.room.vote_select]))
        while not self.room.timeout:
            msg = recvm(self.player)
            if self.room.timeout:
                self.room.downvote += 1
                return
            if not final_vote_flag:
                if msg == '찬성' or msg == 'Y' or msg == 'y':
                    self.room.upvote += 1
                    self.room.downvote -= 1
                    sendm(self.player, "찬성하셨습니다!")
                    final_vote_flag = True
                    continue
                if msg == '반대' or msg == 'N' or msg == 'n':
                    sendm(self.player, "반대하셨습니다!")
                    final_vote_flag = True
                    continue
            self.room.talk(self.player, msg)

    @cerror_block
    def select(self, player):
        sendm(self.player, "밤에 사람을 선택하는 직업이 아닙니다.")
        return None


class Mafia(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '마피아'
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 마피아입니다.\n"
                           "밤에는 마피아끼리 상의하여 죽일 사람을 고르고,\n"
                           "낮에는 아무도 모르게 숨어 시민인 척 하세요.\n"
                           "마피아 수가 시민들보다 많을 시 승리합니다!")

    @cerror_block
    def night_talk(self, msg):
        broadcast(self.room.mafia_list, '[MAFIA]{} : {}'.format(name_dic[self.player], msg),
                  talker=[self.player])
        broadcast(self.room.dead_list, '[MAFIA]{} : {}'.format(name_dic[self.player], msg), talker=self.room.mafia_list)

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "죽일 사람을 선택하세요!\n"
                           "마피아가 여러 명이어도 죽일 사람은 마지막에 선택된 한 사람만 죽일 수 있습니다.")

    @cerror_block
    def select(self, player):
        sendm(self.player, "{}(을)를 죽이기로 결정하셨습니다.".format(name_dic[player]))
        self.room.mafia_select = player
        broadcast(self.room.mafia_list, "[MAFIA_SELECT] {}님이 {}님을 선택하셨어요!"
                  .format(name_dic[self.player], name_dic[player]),
                  talker=[self.player])
        return [True, player]


class Police(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '경찰'
        self.check_list = []
        self.use_skill = False
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 경찰입니다.\n"
                           "밤에 사람을 선택하여 그 사람이 마피아인지 볼 수 있습니다.\n"
                           "마피아를 모두 처단할 시 승리합니다!")

    @cerror_block
    def select(self, player):
        if not self.use_skill:
            if player in self.check_list:
                sendm(self.player, "이미 조사한 사람입니다!")
            else:
                self.use_skill = True
                self.check_list.append(player)
                if self.room.job[player].name == '마피아':
                    sendm(self.player, "{}(은)는 마피아입니다!".format(name_dic[player]))
                else:
                    sendm(self.player, "{}(은)는 마피아가 아니었습니다!".format(name_dic[player]))
                return [True, player]
        else:
            sendm(self.player, "이미 능력을 사용했습니다!")
        sendm(self.player, "지금까지의 조사결과를 보고싶으시다면 'watch'를 입력해주세요.")
        return None

    @cerror_block
    def night(self):
        self.use_skill = False
        super().night()

    @cerror_block
    def night_talk(self, msg):
        if msg == 'watch':
            if len(self.check_list) == 0:
                sendm(self.player, "조사를 진행하지 않았습니다!")
            else:
                self.check_print()

    @cerror_block
    def check_print(self):
        sendm(self.player, "-" * 100 + '\n' + "번호    이름")
        for player_num in range(len(self.room.p_list)):
            player = self.room.p_list[player_num]
            if player in self.check_list:
                sendm(self.player, "<{}>  -  [{}]".format(player_num + 1, name_dic[player]), line=False,enter = False
                      )
                if not self.room.job[self.room.p_list[player_num]].alive:
                    sendm(self.player, " - [DEAD]", line=False, enter=False)
                sendm(self.player, " - [{}]".format('마피아' if self.room.job[player].name == '마피아' else '시민'),
                      line=False)
        sendm(self.player, "-" * 100)

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "조사할 사람을 선택하세요!\n"
                           "조사한 사람이 마피아인지 아닌지 확인이 가능합니다!")


class Reporter(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '기자'
        self.report_skill = True
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 기자입니다.\n"
                           "둘째 밤부터, 단 한 번 사람을 선택하여 그 사람의 직업을 볼 수 있습니다.\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def select(self, player):
        if self.room.phase == 1:
            sendm(self.player, "첫 번째 밤에는 취재가 불가능합니다! ㅜㅜ")
            return None
        if self.report_skill:
            self.report_skill = False
            self.room.news = player  #
            sendm(self.player, "{}님을 취재하기로 결정하셨습니다!\n"
                               "다음 날에 살아있다면 기사를 낼 수 있을 겁니다! 살아 있다면요...".format(name_dic[player]))
            return [True, player]
        else:
            sendm(self.player, "이미 능력을 사용하셨습니다!")
        return None

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "조사할 사람을 선택하세요!\n"
                           "조사한 사람의 직업이 낮에 밝혀집니다. 단, 마피아에게 죽으면 밝혀지지 않습니다ㅠㅜ")


class Sherlock(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '탐정'
        self.use_skill = False
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 탐정입니다.\n"
                           "밤에 사람을 선택하여 그 사람이 누굴 선택했는지를 볼 수 있습니다.\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def night(self):
        self.use_skill = False
        super().night()

    @cerror_block
    def select(self, player):
        if player == self.player:
            sendm(self.player, "자신을 선택할 수 없습니다!")
            return None
        if not self.use_skill:
            self.use_skill = True
            sendm(self.player, "{}의 조사를 시작합니다!".format(name_dic[player]))
            inv = threading.Thread(target=self.investigate, args=(player,))
            inv.start()
            return [True, player]
        else:
            sendm(self.player, "이미 능력을 사용하셨습니다!")
        return None

    @cerror_block
    def investigate(self, player):
        p_job = self.room.job[player]
        while not self.room.timeout:
            if p_job.sel is not None and p_job.sel[0]:
                sendm(self.player, "[조사] {} - {}(을)를 선택하였음".format(name_dic[player], name_dic[p_job.sel[1]]),
                      line=False)
                p_job.sel[0] = False

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "쫓아다닐 사람을 선택하세요\n"
                           "선택 후부터, 그 사람이 선택하는 사람을 모두 볼 수 있습니다.")


class Doctor(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '의사'
        self.use_skill = False
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 의사입니다.\n"
                           "밤에 사람을 선택하여 그 사람이 이번 밤에 마피아에게 죽는다면, 살려낼 수 있습니다.\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def night(self):
        self.use_skill = False
        super().night()

    @cerror_block
    def select(self, player):
        sendm(self.player, "{}(을)를 치료합니다.".format(name_dic[player]))
        self.use_skill = True
        self.room.heal = player
        return [True, player]

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "치료할 사람을 선택하세요!\n"
                           "치료하는 사람은 그 날 밤 마피아에게 선택을 당해도 살려낼 수 있습니다.")


class Politician(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '정치인'
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 정치인입니다. 당신이 하는 투표는 두 표로 적용됩니다.\n"
                           "투표로 죽지 않습니다!\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        if mode == 'night':
            sendm(self.player, "정치인은 선택을 하지 않습니다.\n")
        if mode == 'morning':
            sendm(self.player, "투표에서 두 표를 낼 수 있습니다.\n"
                               "또한, 투표로 죽지 않습니다.")


class Soldier(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '군인'
        self.armor = True
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 군인입니다.\n"
                           "마피아의 공격을 한 번 막아냅니다!\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "군인은 선택을 하지 않습니다.\n", line=False)
        if self.armor:
            sendm(self.player, "방탄복을 입고 있어 마피아의 공격을 한 번 방어할 수 있습니다!")
        else:
            sendm(self.player, "방탄복이 부서졌습니다!")


class Terrorist(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '테러리스트'
        self.use_skill = False
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 테러리스트입니다.\n"
                           "밤에 사람을 하나 선택하여, 밤에 마피아에게 죽을 시 선택한 사람이 마피아라면 그 사람을 같이 데려갑니다!\n"
                           "투표에서 죽을 시, 아무나 선택하여 같이 저승길로 데려갈 수 있습니다!\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def night(self):
        self.use_skill = False
        super().night()

    @cerror_block
    def select(self, player):
        if player == self.player:
            sendm(self.player, "자신을 선택할 수 없습니다!")
            return None
        if not self.use_skill:
            self.use_skill = True
            sendm(self.player, "{0}(을)를 선택하셨습니다.\n"
                               "만약 {0}(이)가 마피아고, 이번 밤에 마피아에게 죽는다면 같이 죽게 됩니다.".format(name_dic[player]))
            return [True, player]
        else:
            sendm(self.player, "이미 목표를 설정했습니다.")
        return None

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        if mode == 'night':
            sendm(self.player, "마피아로 의심되는 사람을 한 명 선택하세요!\n"
                               "만약 그 사람이 마피아이고, 마피아가 당신을 죽이면 그 사람을 같이 데려갈 수 있습니다!")
        if mode == 'morning':
            sendm(self.player, "당신은 테러리스트로써 마지막 역할을 하려고 합니다.\n"
                               "사람을 한 명 선택하세요. 그 사람은 당신의 마지막 여행과 함께할 것입니다.")

    @cerror_block
    def final_vote(self):
        if self.room.vote_select == self.player:
            self.room.downvote += 1
            sendm(self.player, "당신의 표는 반대표로 던져질 겁니다.\n"
                               "사람을 한 명 선택하세요. 같이 죽을 사람 하나를.\n"
                               "10초 드립니다. 선택은 신중하게.")
            self.room.print_players()
            sendm(self.player, "선택하는 방법? 번호만 입력하세요.")
            while not self.room.timeout:
                num = recvm(self.player)
                if self.room.timeout:
                    return
                if num.isdigit() and 1 <= int(num) <= self.room.player_num:
                    if self.room.job[self.room.p_list[int(num) - 1]].alive:
                        num = int(num) - 1
                    else:
                        sendm(self.player, "선택 대상이 아닙니다")
                        continue
                else:
                    sendm(self.player, "잘못 입력하셨습니다.")
                    continue
                self.sel = [True, self.room.p_list[num]]
        else:
            super().final_vote()


class Shaman(Job):
    def __init__(self, player, room):
        super().__init__(player, room)
        self.name = '영매'
        self.use_skill = False
        self.tutorial()

    @cerror_block
    def tutorial(self):
        sendm(self.player, "당신은 영매입니다.\n"
                           "당신은 죽은 사람과 대화가 가능합니다. 밤에는 죽은 사람들과 대화가 가능합니다.\n"
                           "밤에 사람을 하나 선택하여, 성불시킵니다. 성불을 하면 그 사람을 채팅 금지로 만들고 직업을 볼 수 있습니다.\n"
                           "마피아가 모두 죽으면 승리합니다!")

    @cerror_block
    def night(self):
        self.use_skill = False
        super().night()

    @cerror_block
    def num_select(self, msg, shaman=True):
        super().num_select(self, msg, shaman=False)

    @cerror_block
    def select(self, player):
        if not self.use_skill:
            self.use_skill = True
            sendm(self.player, "{0}을 성불했습니다. {0}의 직업은 {1}입니다.".format(name_dic[player], self.room.job[player].name))
            self.room.job[player].shut_up = True
            return [True, player]
        else:
            sendm(self.player, "오늘 밤에는 이미 너무 지쳤어요...")
        return None

    @cerror_block
    def night_talk(self, msg):
        broadcast(self.room.dead_list, '[영매]{} : '.format(name_dic[self.player]) + msg)

    @cerror_block
    def print_help(self, mode='default'):
        super().print_help()
        sendm(self.player, "죽은 사람의 채팅은 [DEAD]가 앞에 붙습니다.\n"
                           "사람을 하나 선택하여 성불시킬 수 있습니다."
                           "성불이 되면 영매에게 직업이 알려지고, 침묵 상태가 됩니다.")


@cerror_block
def name_select(sock):
    global name_dic
    name = '홍은기'
    while name in list(name_dic.values()):
        if name in list(name_dic.values()) and name != '홍은기':
            sendm(sock, "이미 있는 이름입니다. 다른 이름을 입력해주세요.\n이름 : ", enter=False)
        else:
            sendm(sock, "이름이 뭔가요?\n이름 : ", enter=False)
        name = recvm(sock).strip(' ')
    name = name[0:9]
    sendm(sock, "안녕하세요, {}님!".format(name))
    client_list.append(sock)
    name_dic[sock] = name
    print("{}(이)가 접속하였습니다.".format(name_dic[sock]))
    print("현재 연결된 사용자: {}".format(name_dic))


@cerror_block
def room_list_print(sock):
    global room_list
    sendm(sock, "         [Room Lists]         \n" + "-" * 30)
    sendm(sock, "제목           사람 수", line=False)
    for name in room_list:
        room = room_list[name]
        sendm(sock, "{}{}    {} / {}".format(name, ' ' * (10 - len(name)), len(room.p_list), room.player_num),
              line=False)


@cerror_block
def connection():
    global client_list

    while True:
        client_sock, client_addr = server_sock.accept()
        nameinput = threading.Thread(target=name_select, args=(client_sock,))
        nameinput.start()
        waiting = threading.Thread(target=wait, args=(client_sock, nameinput))
        waiting.start()


def broadcast(cast_list, msg, talker=[], enter=True, line=True, line_chr='='):
    for sockets in cast_list:
        if sockets not in talker:
            try:
                sendm(sockets, msg, enter=enter, line=line, line_chr=line_chr)
            except CError:
                continue


class Room:  # room 바로가기
    def __init__(self, name, num):
        self.p_list = []
        self.job, self.mafia_list, self.citizen_list, self.dead_list = {}, [], [], []
        self.name = name
        self.player_num = num
        self.start_flag, self.end_flag = False, False
        self.timeout = False
        self.game_cnt = 0
        self.mafia_select, self.vote_select = None, None
        self.upvote, self.downvote = 0, 0
        self.vote_list = [0] * self.player_num
        self.heal = None
        self.shaman = None
        self.news = None
        self.phase = 0
        self.new_game()

    def talk(self, talker, msg):
        broadcast(self.p_list, "{} : {}".format(name_dic[talker], msg), talker=[talker], line=False)

    @cerror_block
    def timer(self, sec):
        self.timeout = False
        time.sleep(sec)
        self.timeout = True
        broadcast(self.p_list, "fEEBgFFDASDL%%@FM", line=False, enter=False, talker=self.dead_list)
        return

    @cerror_block
    def vote_result(self):
        duo_flag, max_vote, voted_player = False, 0, 0
        for i in range(len(self.vote_list)):
            if self.vote_list[i] > max_vote:
                duo_flag, voted_player, max_vote = False, i, self.vote_list[i]
            elif self.vote_list[i] == max_vote:
                duo_flag = True
        if max_vote == 0:
            broadcast(self.p_list, "아무도 투표를 안 했나요? 처형자는 없습니다.")
            return
        elif duo_flag:
            broadcast(self.p_list, "투표를 가장 많이 받은 사람이 2명 이상이므로, 처형자는 없습니다.")
            return
        self.vote_select = self.p_list[voted_player]

    @cerror_block
    def final_vote_result(self):
        if self.vote_select is not None:
            res = self.upvote >= self.downvote
            print("찬성 {0}, 반대 {1}".format(self.upvote, self.downvote))
            if res:
                broadcast(self.p_list, "{}의 처형은 최종 투표에서 찬성되었습니다!".format(name_dic[self.vote_select]))
            else:
                broadcast(self.p_list, "{}의 처형은 최종 투표에서 반대되었습니다!".format(name_dic[self.vote_select]))
                self.vote_select = None
            return res
        else:
            return False

    @cerror_block
    def people_add(self, sock):
        global name_dic
        if len(self.p_list) == self.player_num:
            sendm(sock, "인원이 꽉 찼습니다!")
            return False
        elif self.start_flag:
            sendm(sock, "이미 시작했습니다!")
            return False
        else:
            self.p_list.append(sock)
            self.job[sock] = 'chatter'
            sendm(sock, "{} 방에 접속했습니다! ({}/{})".format(self.name, len(self.p_list), self.player_num))
            broadcast(self.p_list,
                      "{}님이 접속하셨습니다! ({}/{})".format(name_dic[sock], len(self.p_list), self.player_num),
                      talker=[sock])
            people_chat = threading.Thread(target=self.chat, args=(sock,))
            people_chat.start()
            return True

    def chat(self, sock):
        global name_dic
        try:
            sendm(sock, "채팅에 들어오셨습니당. 방을 나가시려면 '!나 나갈래!'라고 입력해주시면 됩니다.")
            while not self.start_flag:
                msg = recvm(sock)
                if self.start_flag:
                    return
                if msg == '!나 나갈래!':
                    self.kick(sock)
                    return
                broadcast(self.p_list, name_dic[sock] + ' : ' + msg, talker=[sock], line=False)
        except [CError, KeyError]:
            self.kick(sock)
            return

    @cerror_block
    def kick(self, sock):
        sendm(sock, "방에서 나가졌습니다!")
        self.p_list.remove(sock)
        broadcast(self.p_list, "{}님이 나가셨습니다.".format(name_dic[sock]))
        waiting = threading.Thread(target=wait, args=(sock,))
        waiting.start()
        return

    @cerror_block
    def game_start(self):
        while len(self.p_list) < self.player_num:
            time.sleep(1)
        self.start_flag = 1
        broadcast(self.p_list, "@)!(확인", enter=False, line=False)
        broadcast(self.p_list, "인원수가 채워졌으니, 게임을 시작하겠습니다! 더 이상 나가실 수 없습니다.\n")
        time.sleep(5)
        cont = self.job_select()
        if not cont:
            self.new_game()
            return
        # 게임 시작
        self.phase = 1
        while self.game_ended() is False:
            self.daynnight()
            self.phase += 1
        broadcast(self.dead_list, "@)!(확인")
        if self.game_ended() == 'C':
            broadcast(self.p_list, "마피아가 모두 죽었습니다.\n시민 팀이 승리했습니다!")
        if self.game_ended() == 'M':
            broadcast(self.p_list, "마피아가 시민보다 많습니다."
                                   "마피아 팀이 승리했습니다!")
        self.job_print()
        self.init()
        return

    @cerror_block
    def kill(self, player, killed):
        if killed == 'by terrorist':
            sendm(player, "테러리스트가 당신을 희생양으로 삼았습니다!", line_chr='!')
            broadcast(self.p_list, "{}(이)가 테러리스트와 같이 먼지가 되었습니다!.".format(name_dic[player]), talker=[player])
        if killed == 'by mafia':
            sendm(player, "마피아가 당신을 죽였습니다!", line_chr='!')
            broadcast(self.p_list, "{}(이)가 마피아의 공격을 받고 사망했습니다!".format(name_dic[player]), talker=[player])
        if killed == 'by vote':
            sendm(player, "민주주의의 법칙으로 인해 당신은 죽었습니다.", line_chr='!')
            broadcast(self.p_list, "{}(이)가 투표로 죽었습니다.".format(name_dic[player]), talker=[player])
        if self.job[player].name == '테러리스트':
            if self.job[player].sel is not None:
                self.kill(self.job[player].sel[1], 'by terrorist')
            self.job[player].sel = None
        if self.job[player].name == '기자':
            self.news = None
        self.job[player].alive = False
        self.dead_list.append(player)
        dead_chat = threading.Thread(target=self.job[player].death, args=())
        dead_chat.start()

    @cerror_block
    def job_print(self):
        text = "-" * 30 + '\n' + "이름        직업" + '\n'
        for player in self.p_list:
            name = name_dic[player]
            text += "{}{}    {} {}\n".format(name, ' ' * (10 - len(name)), self.job[player].name,
                                             '[생존]' if self.job[player].alive else '[사망]')
        broadcast(self.p_list, text, line=False)

    @cerror_block
    def init(self):
        self.job, self.mafia_list, self.citizen_list = {}, [], []
        self.start_flag = False
        self.mafia_select = None
        self.phase = 0
        self.shaman = None
        self.new_game()

    @cerror_block
    def daynnight(self):
        day_num = self.phase // 2
        if self.phase % 2 == 1:
            if day_num == 0:
                for player in self.p_list:
                    self.job[player].print_help('night')
                    sendm(player, '다음에도 도움이 필요하다면 "!help"를 입력해주세요.')
            broadcast(self.p_list, "{}번째 밤".format(day_num))
            self.happening('night', 25)
            if self.mafia_select is not None:
                victim = self.mafia_select
                if self.heal != victim:
                    if self.job[victim].name == '군인' and self.job[victim].armor:
                        sendm(victim, "마피아의 공격을 한 번 막아냈습니다! 방탄복이 부서져 이제는 방어할 수 없습니다.")
                        broadcast(self.p_list, "{}(은)는 군인입니다. 마피아의 공격을 막아냈습니다!".format(name_dic[victim]))
                        self.job[victim].armor = False
                    else:
                        self.kill(victim, 'by mafia')
                else:
                    broadcast(self.p_list, "{}(이)가 마피아의 공격을 받았지만, 의사의 치료를 받고 살았습니다!".format(name_dic[victim]))
            else:
                broadcast(self.p_list, "오늘 밤은 조용하네요...")
            self.mafia_select, self.heal = None, None
        else:
            broadcast(self.p_list, "{}번째 낮".format(day_num))
            if self.news is not None:
                broadcast(self.p_list, "!!!!속보에요 속보!!!!\n"
                                       "{}(이)가 {}래요!".format(name_dic[self.news], self.job[self.news].name),
                          line_chr='#')
                self.news = None
            self.happening('morning', 10)
            self.happening('vote', 30)
            self.vote_result()
            voted_player = self.vote_select
            if voted_player is not None:
                self.happening('final_words', 10)
                self.happening('final_vote', 30)
            if self.final_vote_result():
                self.upvote, self.downvote = 0, 0
                self.vote_list = [0] * self.player_num
                if self.job[voted_player] == '정치인':
                    sendm(voted_player, "당신은 정치인이므로 죽지 않습니다.")
                    broadcast(self.p_list, "{}(은)는 정치인입니다. 투표로 죽지 않습니다.".format(name_dic[self.vote_select]),
                              talker=[voted_player])
                else:
                    self.kill(voted_player, 'by vote')
            self.vote_select = None

    @cerror_block
    def happening(self, func_name, timer_time):
        thread_list = []
        self.timeout = False
        timewatch = threading.Thread(target=self.timer, args=(timer_time,))
        timewatch.start()
        broadcast(self.p_list, "시간 제한은 {}초입니다.".format(timer_time), line=False)
        for player in self.job:
            if self.job[player].alive:
                thread = threading.Thread(target=getattr(self.job[player], func_name), args=())
                thread_list.append(thread)
                thread.start()
        for thread in thread_list:
            thread.join()

    @cerror_block
    def game_ended(self):
        mafia_n, citizen_n = 0, 0
        for mafia in self.mafia_list:
            if self.job[mafia].alive:
                mafia_n += 1
        for citizen in self.citizen_list:
            if self.job[citizen].alive:
                if self.job[citizen].name == '정치인':
                    citizen_n += 1
                citizen_n += 1
        if mafia_n == 0:
            return 'C'
        if mafia_n >= citizen_n:
            return 'M'
        return False

    @cerror_block
    def new_game(self):
        '''
        if self.game_cnt != 0:
            broadcast(self.p_list,"나가실 분은 10초 안에 'X'를 입력해주세요.. 아니면 게임을 다시 시작하겠습니다.")
        '''
        self.game_cnt+=1
        newgame = threading.Thread(target=self.game_start)
        newgame.start()

    @cerror_block
    def print_players(self, sock):
        sendm(sock, "*" * 100 + '\n' + "번호     이름")
        for player_num in range(len(self.p_list)):
            msg = "<{}>  -  [{}]".format(player_num + 1, name_dic[self.p_list[player_num]])
            if not self.job[self.p_list[player_num]].alive:
                msg += " [DEAD]"
            sendm(sock, msg, line=False)
        sendm(sock, "*" * 100, line=False)

    def job_select(self):
        try:
            job_name_list = [Shaman, Terrorist, Soldier, Sherlock, Reporter, Politician]
            job_num_dic = {Mafia: mafia_num[self.player_num], Police: 1, Doctor: 1}
            cnt = job_num_dic[Mafia] + 2
            random.shuffle(job_name_list)
            for job_class in job_name_list:
                if cnt >= self.player_num:
                    break
                job_num_dic[job_class] = 1
                cnt += 1
            random.shuffle(self.p_list)
            job_index = 0
            for player in self.p_list:
                x = random.choice(list(job_num_dic.keys()))
                while job_num_dic[x] == 0:
                    x = random.choice(list(job_num_dic.keys()))
                self.job[player] = x(player, room_list[self.name])
                if self.job[player].name == '마피아':
                    self.mafia_list.append(player)
                else:
                    self.citizen_list.append(player)
                if self.job[player].name == '영매':
                    self.shaman = player
                job_num_dic[x] -= 1
                job_index += 1
            for player in self.job:
                print('{}:{}'.format(name_dic[player], self.job[player].name))
            return True
        except Exception as e:
            print(e)
            broadcast(self.p_list, "오류가 났네요...? 5초만 기다리죠.")
            time.sleep(5)
            return False


@cerror_block
def wait(sock, name_f=None):
    global name_dic, min_player, max_player, room_list
    if name_f is not None:
        name_f.join()
    while True:
        sendm(sock, "방을 만드시려면 'new room'을, 지금 있는 방에 들어가시려면 'enter room'을 입력해주세요.\n입력 : ", enter=False)
        msg = recvm(sock)
        print(msg)

        if msg == 'new room':
            room_name, room_maxp = None, None
            sendm(sock, "방의 이름을 입력해주세요. (영어만 가능)\n방 이름 : ", enter=False)
            while room_name is None or not isalpha(room_name) or room_name in room_list:
                if room_name in room_list:
                    sendm(sock, "이미 있는 방 이름입니다.\n방 이름 : ", enter=False)
                elif room_name is not None:
                    sendm(sock, "영어만 가능합니다.\n방 이름 : ", enter=False)
                room_name = recvm(sock)[0:9]
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

        if msg == 'enter room':
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


Base_Server = threading.Thread(target=connection, args=())
Base_Server.start()

Base_Server.join()
server_sock.close()
