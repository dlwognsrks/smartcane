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
        import smbus  # smbus를 여기서 임포트하여 의존성 관리
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
    tts = gTTS(text=text, lang='ko')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")

if __name__ == '__main__':
    # INA219 객체 생성
    ina219 = INA219(addr=0x42)

    # 윈도우 서버의 IP 주소와 포트
    server_url = "http://192.168.0.133:5000/data"  # <WINDOWS_IP>를 실제 IP로 변경

    alert_triggered = False  # 충전 완료 메시지 출력 여부
    charging = False  # 현재 충전 상태

    while True:
        # 데이터 측정
        bus_voltage = ina219.getBusVoltage_V()
        shunt_voltage = ina219.getShuntVoltage_mV() / 1000
        current = ina219.getCurrent_mA()
        power = ina219.getPower_W()
        p = (bus_voltage - 6) / 2.4 * 100
        p = max(0, min(100, p))  # 0~100%로 제한

        # 디버깅 출력
        print(f"Voltage: {bus_voltage:.2f} V, Current: {current:.2f} mA, Power: {power:.2f} W, Percent: {p:.1f}%")

        # 충전기 연결 감지 (전류 > 0)
        if current > 0 and not charging:
            print("충전을 시작합니다.")  # 디버깅 메시지
            speak_text("충전을 시작합니다.")
            charging = True  # 충전 상태 업데이트
            alert_triggered = False  # 충전 상태가 바뀌면 90% 메시지 재출력을 허용

        # 충전기 제거 감지 (전류 <= 0)
        elif current <= 0 and charging:
            print("충전을 중지합니다.")  # 디버깅 메시지
            speak_text("충전을 중지합니다.")
            charging = False  # 충전 상태 업데이트
            alert_triggered = False  # 충전기 제거 시 메시지 상태 초기화

        # 배터리 충전 90% 이상 메시지
        if p > 90 and charging and not alert_triggered:
            print("충전이 90퍼센트 이상 완료되었습니다. 배터리 상태를 위해 충전을 중지해주세요.")  # 디버깅 메시지
            speak_text("충전이 90퍼센트 이상 완료되었습니다. 배터리 상태를 위해 충전을 중지해주세요.")
            alert_triggered = True  # 플래그 설정

        # 데이터 전송
        data = {
            "load_voltage": round(bus_voltage, 3),
            "current": round(current / 1000, 6),
            "power": round(power, 3),
            "percent": round(p, 1)
        }

        try:
            response = requests.post(server_url, json=data)
            print(f"Response: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Failed to send data: {e}")

        time.sleep(2)
