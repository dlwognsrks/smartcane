# 라즈베리파이 배터리랑 연결돼있는 쪽 코드


import RPi.GPIO as GPIO
import time
import socket

# 초음파 센서 핀 설정
TRIG = 23  # GPIO 핀 번호 23 (TRIG)
ECHO = 24  # GPIO 핀 번호 24 (ECHO)

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 윈도우 컴퓨터로 메시지 전송을 위한 TCP 클라이언트 설정
windows_ip = '172.20.10.4'  # 윈도우 PC의 IP 주소
windows_port = 5000

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((windows_ip, windows_port))
    print(f"윈도우({windows_ip}:{windows_port}) 연결 성공")
except Exception as e:
    print(f"윈도우 연결 실패: {e}")
    client_socket = None

# 거리 측정 함수
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

try:
    while True:
        # 초음파 센서로 거리 측정
        distance = measure_distance()
        print(f"Measured Distance = {distance} cm")

        # 거리 100cm 이하일 경우 윈도우로 메시지 전송
        if distance <= 100 and client_socket:
            client_socket.sendall(f"Distance: {distance} cm".encode('utf-8'))

        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
    if client_socket:
        client_socket.close()
