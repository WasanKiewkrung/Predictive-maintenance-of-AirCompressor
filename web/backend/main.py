import asyncio
import json
import random
import threading
from typing import List
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt # เพิ่ม Library MQTT
from . import database

app = FastAPI()

# --- 1. MQTT Configuration ---
# ใช้ Broker สาธารณะฟรีทดสอบก่อนได้ (หรือเปลี่ยนเป็น IP ของตัวเองถ้าลง Mosquitto ไว้)
MQTT_BROKER = "test.mosquitto.org" 
MQTT_PORT = 1883
MQTT_TOPIC = "factory/compressor/data" # หัวข้อที่จะคุยกัน

# --- 2. Setup CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Connection Manager (WebSocket Hub สำหรับ Frontend) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()

# --- 4. MQTT Client Setup (พระเอกคนใหม่) ---
mqtt_client = mqtt.Client()

# ฟังก์ชันเมื่อต่อ MQTT ติด
def on_connect(client, userdata, flags, rc):
    print(f"📡 MQTT Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC) # รอฟังข้อมูลจากบอร์ด

# ฟังก์ชันเมื่อมีข้อมูลเข้ามาจาก MQTT (Bridge Logic)
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # [สำคัญ] MQTT ทำงานคนละ Thread กับ FastAPI
        # เราต้องใช้ loop ของ asyncio เพื่อส่งข้อมูลเข้า WebSocket
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. ส่งต่อให้ Frontend (WebSocket)
        # ใช้ run_coroutine_threadsafe เพื่อข้าม Thread อย่างปลอดภัย
        asyncio.run_coroutine_threadsafe(manager.broadcast(data), main_loop)
        
        # 2. บันทึกลง Database
        database.insert_data_sqlite(data)
        
        # print(f"Received from MQTT: {data['timestamp']}") # Debug ดูได้
        
    except Exception as e:
        print(f"⚠️ Error processing MQTT message: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# --- 5. Mock Data Generator (แก้ให้ส่งผ่าน MQTT แทน) ---
def generate_mock_data():
    ax = round(random.uniform(-1.5, 1.5), 3)
    ay = round(random.uniform(-1.5, 1.5), 3)
    is_abnormal = abs(ax) > 1.2 or abs(ay) > 1.2
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "ax": ax,
        "ay": ay,
        "az": round(random.uniform(0.9, 1.1), 3),
        "temp": round(random.uniform(45, 65), 1),
        "amp": round(random.uniform(3.5, 5.5), 2),
        "rul_predict": round(random.uniform(50, 400), 0),
        "status": 1 if is_abnormal else 0
    }

# ตัวจำลองบอร์ด: สร้างข้อมูลแล้ว Publish ขึ้น MQTT
async def run_mock_board_simulation_mqtt():
    print("🤖 Mock Simulation Started: Publishing to MQTT...")
    # สร้าง Client แยกอีกตัวสำหรับจำลองฝั่งส่ง (เหมือนเป็นบอร์ด ESP32)
    mock_sender = mqtt.Client()
    mock_sender.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    cleanup_counter = 0
    while True:
        # 1. สร้างข้อมูล
        data = generate_mock_data()
        
        # 2. ส่งขึ้น MQTT (บอร์ดจริงก็จะทำแบบนี้)
        mock_sender.publish(MQTT_TOPIC, json.dumps(data))
        
        # 3. Auto Cleanup Database (Optional)
        cleanup_counter += 1
        if cleanup_counter >= 1000:
            database.cleanup_old_sqlite_data()
            cleanup_counter = 0
            
        await asyncio.sleep(0.1) # 10Hz

# --- 6. Startup Event ---
# เก็บ Loop หลักไว้ใช้ตอน Bridge ข้อมูล
main_loop = None 

@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    # เริ่มต้น Database
    database.init_db()
    print("✅ System Ready: Database Initialized.")

    # เริ่มเชื่อมต่อ MQTT (ฝั่งรับ)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start() # รัน background thread รอรับข้อมูล
    
    # รัน Mock Data (ฝั่งส่ง)
    asyncio.create_task(run_mock_board_simulation_mqtt())

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# --- 7. WebSocket Endpoints ---

# [Frontend] React ยังเข้ามาท่าเดิม ไม่ต้องแก้ React
@app.websocket("/ws/frontend")
async def websocket_frontend(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# [หมายเหตุ] Endpoint /ws/board ลบทิ้งได้เลย เพราะบอร์ดส่งผ่าน MQTT แล้ว

@app.get("/")
def read_root():
    return {"status": "Running", "mode": "MQTT Bridge Mode"}