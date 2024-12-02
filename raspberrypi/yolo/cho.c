// 초음파 거리센서 1m 내로 들어오면 yolo객체 탐지 실행할 수 있도록하는 아두이노 코드

const int trigPin = 9; // Trig 핀
const int echoPin = 10; // Echo 핀
long duration;
int distance;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);  // 시리얼 통신 속도 설정
}

void loop() {
  // 초음파 펄스 전송
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Echo 핀에서 펄스 지속 시간 측정
  duration = pulseIn(echoPin, HIGH);

  // 거리를 cm로 변환
  distance = duration * 0.034 / 2;

  // 거리가 100cm 이하일 경우 "DETECT" 메시지 전송
  if (distance <= 100) {
    Serial.println("DETECT");
  }

  delay(500);  // 0.5초 간격으로 측정
}
