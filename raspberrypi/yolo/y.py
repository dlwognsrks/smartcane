# 아두이노 초음파센서로 1m 내로 들어오면 인식된 장애물을 음성메세지로 출력

import serial
import torch
import cv2
from gtts import gTTS
import os
import time

# 시리얼 포트와 통신 설정
ser = serial.Serial('/dev/ttyACM0', 9600)  # '/dev/ttyACM0'는 Arduino와 연결된 포트

# YOLO 모델 불러오기 (yolov5s.pt 기본 가중치 사용)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 카메라 설정
cap = cv2.VideoCapture(0)  # USB 웹캠 또는 라즈베리 파이 카메라

# 음성 안내 함수 (gTTS 사용)
def speak(text):
    tts = gTTS(text=text, lang='ko')
    tts.save("detected.mp3")
    os.system("mpg321 detected.mp3")

while True:
    # 초음파 센서로 거리 감지 (1m 이하일 때 객체 인식 및 음성 안내)
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line == "DETECT":
            # 1m 이내에 장애물 감지 시 객체 인식 수행
            ret, frame = cap.read()
            if not ret:
                continue

            # YOLO로 객체 탐지
            results = model(frame)

            # 인식된 객체 이름 출력 및 음성 안내
            detected_objects = results.pandas().xyxy[0]
            if not detected_objects.empty:
                # 첫 번째 인식된 객체에 대해 안내 (필요에 따라 변경 가능)
                obj_name = detected_objects.iloc[0]['name']
                confidence = detected_objects.iloc[0]['confidence']
                message = f"{obj_name}이 감지되었습니다. "

                print(message)
                speak(message)  # gTTS로 음성 안내

    # 카메라에서 프레임 읽기 및 YOLO로 객체 탐지 (상시 실행)
    ret, frame = cap.read()
    if not ret:
        continue

    # YOLO로 객체 탐지 (신호등 및 기타 일반 객체 감지)
    results = model(frame)

    # 인식된 객체 화면에 표시
    results.render()
    cv2.imshow('Object Detection', results.imgs[0])

    # 'q' 키로 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 해제
cap.release()
cv2.destroyAllWindows()
