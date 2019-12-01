import socket, threading

server_ip = '127.0.0.1'
server_port = 50000
address = (server_ip, server_port)
mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysock.connect(address)

def receive():
    global mysock
    while True:
        try:
            data = mysock.recv(1024)
        except ConnectionError:
            print("서버와 접속이 끊겼습니다. Enter를 누르세요.")
            break
        except OSError:
            print("서버와의 접속을 끊었습니다.")
            break

        if not data:
            print("서버로부터 정상적으로 로그아웃했습니다.")
            break
        data=data.decode('UTF-8')
        if data == '2H3DTESTAB!%FTTHFASDF':
            continue

        if data == 'fEEBgFFDASDL%%@FM' or data == '@)!(확인':  # timer
            mysock.send(bytes('test_message'+data, 'UTF-8'))
            continue

        print(data, end='')

    print('소켓의 읽기 버퍼를 닫습니다.')
    try:
        mysock.shutdown(socket.SHUT_RD)
    except OSError:
        print("읽기 버퍼를 닫기 전에 서버에서 연결이 종료되었습니다.")


def main_thread():
    global mysock

    thread_recv = threading.Thread(target=receive, args=())
    thread_recv.start()

    while True:
        try:
            data = input()
        except KeyboardInterrupt:
            continue
        if data == '!quit':
            print("서버와의 접속을 끊는 중입니다.")
            break

        try:
            mysock.send(bytes(data, 'UTF-8'))  # 서버에 메시지를 전송
        except ConnectionError:
            break


    print("소켓의 쓰기 버퍼를 닫습니다.")
    mysock.shutdown(socket.SHUT_WR)
    thread_recv.join()


thread_main = threading.Thread(target=main_thread, args=())
thread_main.start()

thread_main.join()

mysock.close()
print('소켓을 닫습니다.')
print('클라이언트 프로그램이 정상적으로 종료되었습니다.')