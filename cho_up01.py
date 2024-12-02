#라즈베리파이 부가적으로 사용한 거 거기 코드

import socket
from gtts import gTTS
import os
from threading import Thread

# 라즈베리파이에서 메시지 수신을 위한 TCP 서버 설정
server_ip = '0.0.0.0'
server_port = 5001

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    print(f"라즈베리파이 서버가 {server_port} 포트에서 대기 중...")
    conn, addr = server_socket.accept()
    print(f"윈도우({addr})에서 연결됨")
except Exception as e:
    print(f"TCP 서버 실행 실패: {e}")
    conn = None

# 음성 안내 함수
def speak(text):
    tts = gTTS(text=text, lang='ko')  # 메시지를 한국어로 변환
    tts.save("detected.mp3")  # mp3 파일로 저장
    os.system("mpg321 detected.mp3")  # mp3 파일 재생

# 메시지 수신 및 음성 안내 쓰레드
def message_receiver_thread():
    try:
        while True:
            if conn:
                data = conn.recv(1024)  # 메시지 수신
                if not data:
                    break
                object_name = data.decode('utf-8')  # 객체 이름 디코딩
                print(f"수신된 객체 이름: {object_name}")
                message = f"{object_name}이 감지되었습니다."  # 메시지 생성
                print(message)
                speak(message)  # 음성 출력
    except Exception as e:
        print(f"메시지 수신 오류: {e}")
    finally:
        if conn:
            conn.close()
        if server_socket:
            server_socket.close()

# 쓰레드 실행
receiver_thread = Thread(target=message_receiver_thread)  # 메시지 수신 쓰레드 시작
receiver_thread.start()
receiver_thread.join()
