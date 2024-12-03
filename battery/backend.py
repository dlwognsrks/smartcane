from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 메모리에 데이터를 저장하기 위한 변수
latest_data = {}

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://172.31.48.1:3000","*"],  # React 가 실행되는 컴퓨터의 공인ip주소 , * : 추가함. ip 다 허용이래
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST 요청 처리 (라즈베리파이에서 데이터 수신)
@app.post("/api/data")
async def receive_data(request: Request):
    global latest_data
    try:
        # 라즈베리파이에서 데이터 수신
        data = await request.json()
        latest_data = data  # 수신한 데이터를 메모리에 저장
        print("Received data from Raspberry Pi:", data)
        return {"status": "success", "received": data}
    except Exception as e:
        print(f"Error receiving data: {e}")
        return {"error": "Failed to process POST request"}

# GET 요청 처리 (React에서 데이터 요청)
@app.get("/api/data")
async def send_data():
    try:
        # 저장된 데이터를 React로 반환
        print("Sent data to React:", latest_data)
        return latest_data
    except Exception as e:
        print(f"Error sending data: {e}")
        return {"error": "Failed to retrieve data"}
