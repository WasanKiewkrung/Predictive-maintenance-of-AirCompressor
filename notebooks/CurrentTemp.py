# Cell 1: Load Data & Create RUL Label
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ตั้งค่า path (แก้ให้ตรงกับเครื่องคุณ)
DATA_PATH = 'data/temp-current/train_FD001.txt'

# 1. กำหนดชื่อ Column (ตามคู่มือ NASA แต่เราเลือกใช้บางตัว)
col_names = ['unit_id', 'time_cycles', 'setting_1', 'setting_2', 'setting_3', 
             's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 
             's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21']

try:
    # โหลดไฟล์ (sep='\s+' แปลว่าแยกด้วยช่องว่างกี่ช่องก็ได้)
    df = pd.read_csv(DATA_PATH, sep='\s+', header=None, names=col_names)
    print(f"✅ Loaded NASA Data: {df.shape}")
except FileNotFoundError:
    print("❌ Error: ไม่เจอไฟล์! เช็ค path ดีๆ นะครับ")

# 2. จำลองเป็นข้อมูลปั๊มลม (Simulation Mapping)
# เราเลือก Sensor ที่พฤติกรรมคล้ายปั๊มลมที่สุดมาสวมรอย
# s2 = LPC Outlet Temp -> ยิ่งพัง ยิ่งร้อน (ใช้แทน Temperature)
# s7 = HPC Outlet Pressure -> ยิ่งพัง แรงดันยิ่งเปลี่ยน (ใช้แทน Current Load)
pump_data = df[['unit_id', 'time_cycles', 's2', 's7']].copy()
pump_data.columns = ['unit_id', 'time', 'temperature', 'current']

# 3. สร้างเฉลย RUL (Remaining Useful Life)
# สูตร: RUL = (เวลาตายของเครื่องนั้น) - (เวลาปัจจุบัน)

# หาว่าแต่ละเครื่อง (unit_id) มีอายุยืนสุดที่กี่รอบ (Max Cycle)
max_life = pump_data.groupby('unit_id')['time'].max().reset_index()
max_life.columns = ['unit_id', 'max_life']

# เอาค่า Max Life แปะกลับเข้าไปในตารางหลัก
pump_data = pump_data.merge(max_life, on='unit_id', how='left')

# คำนวณถอยหลัง
pump_data['RUL'] = pump_data['max_life'] - pump_data['time']

# ==========================================
# 📊 PART 2: VISUALIZATION (ต่อท้ายไฟล์เดิม)
# ==========================================
import matplotlib.pyplot as plt

print("\n📈 กำลังวาดกราฟ Run-to-Failure ของเครื่องจักรหมายเลข 1...")

# เลือกดูเฉพาะเครื่องจักรเบอร์ 1 (Unit 1) ตั้งแต่เกิดจนดับ
unit_1 = pump_data[pump_data['unit_id'] == 1]

plt.figure(figsize=(12, 10))

# 1. กราฟ Temperature (จำลอง)
plt.subplot(3, 1, 1)
plt.plot(unit_1['time'], unit_1['temperature'], color='red')
plt.title("Temperature (Sensor 2)")
plt.ylabel("Deg C")
plt.grid(True, alpha=0.3)

# 2. กราฟ Current (จำลอง)
plt.subplot(3, 1, 2)
plt.plot(unit_1['time'], unit_1['current'], color='orange')
plt.title("Current/Pressure (Sensor 7)")
plt.ylabel("Load")
plt.grid(True, alpha=0.3)

# 3. กราฟ RUL (เฉลย)
plt.subplot(3, 1, 3)
plt.plot(unit_1['time'], unit_1['RUL'], color='green', linestyle='--')
plt.title("RUL Target")
plt.xlabel("Time (Cycles)")
plt.ylabel("RUL Left")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show() # ⚠️ หน้าต่างกราฟจะเด้งขึ้นมา