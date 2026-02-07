import sqlite3
from datetime import datetime

# ตั้งค่าชื่อไฟล์ Database
DB_NAME = "maintenance_logs.db"

# --- ส่วนจัดการ Database (SQLite) ---

def init_db():
    """สร้างตารางใน Database ถ้ายังไม่มี"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # [UPDATED] 
    # 1. เปลี่ยน timestamp เป็น TEXT (เพื่อรับค่า string จากบอร์ด/mock)
    # 2. เพิ่มคอลัมน์ status (INTEGER)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, 
            ax REAL, ay REAL, az REAL, 
            temp REAL, amp REAL, 
            rul_predict REAL,
            status INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_data_sqlite(data):
    """บันทึกข้อมูลลง SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # [UPDATED] รับค่า timestamp และ status เข้ามาบันทึกตรงๆ
    cursor.execute('''
        INSERT INTO sensor_summary (timestamp, ax, ay, az, temp, amp, rul_predict, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['timestamp'], 
        data['ax'], data['ay'], data['az'], 
        data['temp'], data['amp'], 
        data['rul_predict'],
        data['status']
    ))
    
    conn.commit()
    conn.close()

def cleanup_old_sqlite_data():
    """ลบข้อมูลใน Database ที่เก่ากว่า 7 วัน"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ลบข้อมูลที่เก่ากว่า 7 วัน นับจากเวลาปัจจุบัน
    cursor.execute("DELETE FROM sensor_summary WHERE timestamp < datetime('now', '-7 days')")
    
    deleted_count = cursor.rowcount
    if deleted_count > 0:
        print(f"🧹 History Cleaner: Removed {deleted_count} old records.")
        
    conn.commit()
    conn.close()