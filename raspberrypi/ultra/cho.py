# 초음파 하단센서 일정거리 안에 들어오면 장애물 위치 음성 메세지 출력

import serial
from gtts import gTTS
import os
import json
import subprocess

# 음성 출력을 위한 전역 프로세스 변수
current_process = None

def speak_text(text):
    """TTS 음성 출력 함수"""
    global current_process
    try:
        # 이전 음성 프로세스 중단
        if current_process:
            current_process.terminate()
            current_process = None

        # 새 음성 생성 및 출력
        tts = gTTS(text=text, lang='ko')
        tts.save("output.mp3")
        current_process = subprocess.Popen(["mpg321", "output.mp3"])
    except Exception as e:
        print(f"음성 출력 오류: {e}")

if __name__ == "__main__":
    # 아두이노 시리얼 포트 설정
    try:
        arduino = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=0.1)
        print("아두이노 연결 성공!")
    except Exception as e:
        print(f"아두이노 연결 실패: {e}")
        exit()

    # 각 센서 상태를 저장하는 변수
    states = {"right": False, "left": False, "front": False}

    while True:
        try:
            # 아두이노로부터 데이터 읽기
            line = arduino.readline().decode('utf-8').strip()
            if line:
                # JSON 형식 데이터 파싱
                try:
                    data = json.loads(line)
                    right = data.get("right", 0)
                    left = data.get("left", 0)
                    front = data.get("front", 0)

                    # 디버깅 출력
                    print(f"우측 거리: {right} cm, 좌측 거리: {left} cm, 앞쪽 거리: {front} cm")

                    # 우측 감지
                    if right < 20 and not states["right"]:
                        speak_text("우측에 장애물이 있습니다.")
                        states["right"] = True
                    elif right >= 30 and states["right"]:
                        states["right"] = False

                    # 좌측 감지
                    if left < 20 and not states["left"]:
                        speak_text("좌측에 장애물이 있습니다.")
                        states["left"] = True
                    elif left >= 30 and states["left"]:
                        states["left"] = False

                    # 앞쪽 감지
                    if front < 14 and not states["front"]:
                        speak_text("앞쪽에 장애물이 있습니다.")
                        states["front"] = True
                    elif front >= 30 and states["front"]:
                        states["front"] = False

                except json.JSONDecodeError:
                    print(f"데이터 파싱 실패: {line}")

        except Exception as e:
            print(f"오류 발생: {e}")
