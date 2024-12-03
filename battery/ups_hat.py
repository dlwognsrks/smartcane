# UPS_HAT 의 데이터값을 받아서 라즈베리파이 Fast api 백엔드로 전송하는 코드
# 배터리 상태에 따른 음성메시지 출력

import requests
import time
from gtts import gTTS
import os

# INA219 관련 레지스터 및 설정 상수
_REG_CONFIG = 0x00
_REG_SHUNTVOLTAGE = 0x01
_REG_BUSVOLTAGE = 0x02
_REG_POWER = 0x03
_REG_CURRENT = 0x04
_REG_CALIBRATION = 0x05

class INA219:
    def __init__(self, i2c_bus=1, addr=0x40):
        import smbus
        self.bus = smbus.SMBus(i2c_bus)
        self.addr = addr
        self._cal_value = 0
        self._current_lsb = 0
        self._power_lsb = 0
        self.set_calibration_32V_2A()

    def read(self, address):
        data = self.bus.read_i2c_block_data(self.addr, address, 2)
        return ((data[0] << 8) | data[1])

    def write(self, address, data):
        temp = [(data >> 8) & 0xFF, data & 0xFF]
        self.bus.write_i2c_block_data(self.addr, address, temp)

    def set_calibration_32V_2A(self):
        self._current_lsb = 0.1
        self._cal_value = 4096
        self._power_lsb = 0.002
        self.write(_REG_CALIBRATION, self._cal_value)
        config = (0x01 << 13) | (0x03 << 11) | (0x0D << 7) | (0x0D << 3) | 0x07
        self.write(_REG_CONFIG, config)

    def getShuntVoltage_mV(self):
        value = self.read(_REG_SHUNTVOLTAGE)
        if value > 32767:
            value -= 65536
        return value * 0.01

    def getBusVoltage_V(self):
        value = self.read(_REG_BUSVOLTAGE)
        return (value >> 3) * 0.004

    def getCurrent_mA(self):
        value = self.read(_REG_CURRENT)
        if value > 32767:
            value -= 65536
        return value * self._current_lsb

    def getPower_W(self):
        value = self.read(_REG_POWER)
        return value * self._power_lsb

def speak_text(text):
    """TTS 음성 출력 함수"""
    try:
        tts = gTTS(text=text, lang='ko')
        tts.save("output.mp3")
        os.system("mpg321 -q output.mp3")
    except Exception as e:
        print(f"Error in TTS or playback: {e}")

if __name__ == '__main__':
    ina219 = INA219(addr=0x42)
    backend_url = "http://172.20.10.3:8000/api/data"  # 실제 백엔드 주소로 변경

    alert_triggered = False
    charging = False

    while True:
        try:
            # 데이터 측정
            bus_voltage = ina219.getBusVoltage_V()
            current = ina219.getCurrent_mA()
            power = ina219.getPower_W()
            percent = max(0, min(100, (bus_voltage - 6) / 2.4 * 100))

           
            # 충전 상태 및 음성 안내
            if current > 0 and not charging:
                print("충전을 시작합니다.")
                speak_text("충전을 시작합니다.")
                charging = True
                alert_triggered = False
            elif current <= 0 and charging:
                print("충전을 중지합니다.")
                speak_text("충전을 중지합니다.")
                charging = False
                alert_triggered = False
            if percent > 90 and charging and not alert_triggered:
                print("충전이 90퍼센트 이상 완료되었습니다.")
                speak_text("충전이 90퍼센트 이상 완료되었습니다.")
                alert_triggered = True

            # 데이터 전송
            data = {
                "volt": round(bus_voltage, 3),
                "current": round(current / 1000, 6),
                "power": round(power, 3),
                "percent": round(percent, 1)
            }

            try:
                response = requests.post(backend_url, json=data, timeout=5)
                print(f"Response: {response.status_code} {response.text}")
            except Exception as e:
                print(f"Failed to send data to backend: {e}")

        except Exception as e:
            # 전체 루프에서 발생하는 예외 처리
            print(f"Unexpected error in loop: {e}")

        # 2초 대기 후 루프 재실행
        time.sleep(2)
