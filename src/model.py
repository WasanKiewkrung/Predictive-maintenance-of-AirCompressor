print("Start Processing...")

# ==========================================
# 1. SETUP & IMPORTS 📚
# ==========================================
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.io import loadmat
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import to_categorical

# ตั้งค่า Seed
np.random.seed(1234)
tf.random.set_seed(1234)

# ==========================================
# 2. VIBRATION PIPELINE (CWRU) 🌊
# ==========================================
print("\n[STEP 1/3] Processing Vibration Data (CWRU)...")

# --- 2.1 Config & Load ---
file_configs = [
    (0, 'Time_Normal_1_098.mat'),   # Normal
    (1, 'IR007_1_110.mat'),         # Inner Race
    (2, 'OR007_6_1_136.mat'),       # Outer Race
    (3, 'B007_1_123.mat')           # Ball
]
data_folder_path = 'data/raw'

def load_and_label_data(folder, configs):
    all_data = []
    all_labels = []
    for label, filename in configs:
        file_path = os.path.join(folder, filename)
        try:
            mat = loadmat(file_path)
            key_name = [k for k in mat.keys() if 'DE_time' in k]
            if len(key_name) > 0:
                data = mat[key_name[0]]
                all_data.append(data)
                all_labels.append(label)
                print(f"   ✅ Loaded: {filename} | Shape: {data.shape}")
            else:
                print(f"   ⚠️ Key not found: {filename}")
        except FileNotFoundError:
            print(f"   ❌ File not found: {filename}")
    return all_data, all_labels

raw_data, raw_labels = load_and_label_data(data_folder_path, file_configs)

# --- 2.2 Sliding Window (Segmentation) ---
def create_segments(data_list, label_list, time_steps, step):
    segments = []
    labels = []
    for i, data in enumerate(data_list):
        label = label_list[i]
        for x in range(0, len(data) - time_steps, step):
            segment = data[x : x + time_steps]
            segments.append(segment)
            labels.append(label)
    return np.array(segments), np.array(labels)

TIME_STEPS = 1024
STEP = 512

x_vib_train, y_diag_train = create_segments(raw_data, raw_labels, TIME_STEPS, STEP)
print(f"   ✂️ Windowing Done: {x_vib_train.shape}")

# --- 2.3 Vibration Normalization (Z-Score) ---
# ย้ายมาทำตรงนี้เลย เพื่อให้จบกระบวนการของ Vibration
print("   ⚖️ Normalizing Vibration Data...")
vib_mean = x_vib_train.mean()
vib_std = x_vib_train.std()
x_vib_train = (x_vib_train - vib_mean) / (vib_std + 1e-7)
print(f"   ✅ Vibration Ready (Mean: {x_vib_train.mean():.2f}, SD: {x_vib_train.std():.2f})")


# ==========================================
# 3. SENSOR PIPELINE (NASA) 🌡️
# ==========================================
print("\n[STEP 2/3] Processing Sensor Data (NASA)...")

# --- 3.1 Load Data ---
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
NASA_DATA_PATH = os.path.join(script_dir, '..', 'data', 'temp-current', 'train_FD001.txt')
# NASA_DATA_PATH = os.path.join(script_dir, 'data', 'temp-current', 'train_FD001.txt') # ใช้บรรทัดนี้ถ้าไฟล์อยู่ใน src/data

def load_nasa_data(path):
    col_names = ['unit_id', 'time_cycles', 'setting_1', 'setting_2', 'setting_3', 
                 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 
                 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21']
    try:
        df = pd.read_csv(path, sep='\s+', header=None, names=col_names)
        features = ['s2', 's7'] # s2=Temp, s7=Current
        data = df[['unit_id', 'time_cycles'] + features].copy()
        data.columns = ['unit_id', 'time', 'temperature', 'current']
        
        # Create RUL Label
        max_life = data.groupby('unit_id')['time'].max().reset_index()
        max_life.columns = ['unit_id', 'max']
        data = data.merge(max_life, on='unit_id', how='left')
        data['RUL'] = data['max'] - data['time']
        
        print(f"   ✅ Loaded NASA Data: {data.shape}")
        return data
    except FileNotFoundError:
        print(f"   ❌ File not found: {path}")
        return None

nasa_df = load_nasa_data(NASA_DATA_PATH)

if nasa_df is not None:
    # --- 3.2 Scaling (MinMax 0-1) ---
    print("   ⚖️ Scaling Sensor Data (0-1)...")
    scaler = MinMaxScaler()
    feature_cols = ['temperature', 'current']
    nasa_df[feature_cols] = scaler.fit_transform(nasa_df[feature_cols])

    # --- 3.3 Sliding Window ---
    def create_sensor_segments(df, time_steps, features, label_col='RUL'):
        x_segments = []
        y_labels = []
        for unit_id in df['unit_id'].unique():
            unit_data = df[df['unit_id'] == unit_id]
            data_values = unit_data[features].values
            label_values = unit_data[label_col].values
            for i in range(len(unit_data) - time_steps):
                x_segments.append(data_values[i : i + time_steps])
                y_labels.append(label_values[i + time_steps])
        return np.array(x_segments), np.array(y_labels)

    SENSOR_TIME_STEPS = 50
    x_sensor_train, y_rul_train = create_sensor_segments(nasa_df, SENSOR_TIME_STEPS, feature_cols)
    print(f"   ✅ Sensor Ready: {x_sensor_train.shape}")
else:
    x_sensor_train, y_rul_train = np.array([]), np.array([])


# ==========================================
# 4. FINAL CHECK (Pre-Alignment) ✅
# ==========================================
print("\n[STEP 3/3] Data Summary (Ready for Alignment)")
print("-" * 40)
print(f"1. Vibration Input (x_vib_train) : {x_vib_train.shape}")
print(f"2. Sensor Input    (x_sensor_train): {x_sensor_train.shape}")
print(f"3. Diagnosis Label (y_diag_train): {y_diag_train.shape}")
print(f"4. RUL Label       (y_rul_train) : {y_rul_train.shape}")
print("-" * 40)

# ==========================================
# 5. DATA ALIGNMENT (จับคู่ข้อมูล) ✂️
# ==========================================
print("\n[STEP 4/6] Aligning Data (Truncating to match size)...")

# 1. หาจำนวนที่น้อยที่สุด (เพื่อตัดส่วนเกินทิ้ง)
# CWRU มี ~3,700 แต่ NASA มี ~15,000 -> ต้องตัด NASA ให้เหลือเท่า CWRU
min_samples = min(len(x_vib_train), len(x_sensor_train))
print(f"   📉 Truncating data to: {min_samples} samples")

# 2. ตัดข้อมูล (Slicing)
X_vib_final   = x_vib_train[:min_samples]
X_sensor_final = x_sensor_train[:min_samples]

y_diag_final  = y_diag_train[:min_samples]
y_rul_final   = y_rul_train[:min_samples]

# 3. แปลงคำตอบ Diagnosis เป็น One-Hot Encoding
# เช่น Label 0 (Normal) -> [1, 0, 0, 0] เพื่อให้เหมาะกับ Softmax
y_diag_hot = to_categorical(y_diag_final, num_classes=4)

print(f"   ✅ Alignment Complete!")
print(f"      X_vib_final: {X_vib_final.shape}")
print(f"      X_sensor_final: {X_sensor_final.shape}")

# ==========================================
# 5.5 SHUFFLE DATA (หัวใจสำคัญ! ห้ามลืม) 🔀
# ==========================================
from sklearn.utils import shuffle

print("\n[STEP 5.5] Shuffling Data...")
X_vib_final, X_sensor_final, y_diag_hot, y_rul_final = shuffle(
    X_vib_final, X_sensor_final, y_diag_hot, y_rul_final, 
    random_state=42
)
print("   ✅ Data Shuffled! (Train/Val sets will now be balanced)")


# ==========================================
# 6. BUILD HYBRID MODEL (กลับมาใช้ V1 เดิมที่เสถียรที่สุด) 🏗️
# ==========================================
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, Flatten, LSTM, Dense, Concatenate, Dropout
from tensorflow.keras.models import Model

print("\n[STEP 5/6] Building Hybrid Architecture (Classic V1)...")

def build_hybrid_model():
    # --- ขาที่ 1: Vibration (CNN) ---
    input_vib = Input(shape=(1024, 1), name='input_vibration')
    x1 = Conv1D(32, 3, activation='relu')(input_vib)
    x1 = MaxPooling1D(2)(x1)
    x1 = Conv1D(64, 3, activation='relu')(x1)
    x1 = MaxPooling1D(2)(x1)
    x1 = Flatten()(x1)
    x1 = Dense(64, activation='relu')(x1)

    # --- ขาที่ 2: Sensor (LSTM) ---
    input_sensor = Input(shape=(50, 2), name='input_sensors')
    x2 = LSTM(64, return_sequences=False)(input_sensor) # เอา Dropout ในนี้ออก
    x2 = Dense(32, activation='relu')(x2)

    # --- รวมร่าง ---
    combined = Concatenate()([x1, x2])
    z = Dense(128, activation='relu')(combined)
    z = Dropout(0.2)(z) # กลับมาใช้ 0.2 เบาๆ พอ

    # --- Output ---
    output_diag = Dense(4, activation='softmax', name='diagnosis_output')(z)
    output_rul = Dense(1, activation='linear', name='rul_output')(z)

    model = Model(inputs=[input_vib, input_sensor], 
                  outputs=[output_diag, output_rul])
    
    return model

model = build_hybrid_model()

model.compile(
    optimizer='adam',
    loss={'diagnosis_output': 'categorical_crossentropy', 'rul_output': 'mse'},
    loss_weights={'diagnosis_output': 1.0, 'rul_output': 0.1},
    metrics={'diagnosis_output': 'accuracy', 'rul_output': 'mae'}
)

print(model.summary())

# ==========================================
# 7. TRAINING (เริ่มสอน AI) 🚀
# ==========================================
print("\n[STEP 6/6] Starting Training Process...")
print("🔥 Training for 20 Epochs (Press Ctrl+C to stop early)...")

history = model.fit(
    # ป้อนข้อมูลเข้า 2 ประตู
    x={'input_vibration': X_vib_final, 'input_sensors': X_sensor_final},
    
    # ตรวจคำตอบจาก 2 เฉลย
    y={'diagnosis_output': y_diag_hot, 'rul_output': y_rul_final},
    
    epochs=20,          # รอบการฝึก
    batch_size=32,      # สอนทีละ 32 ตัวอย่าง
    validation_split=0.2, # แบ่ง 20% ไว้สอบเก็บคะแนน
    verbose=1
)

print("\n🎉 CONGRATULATIONS! Training Finished.")
print("   (Tip: ถ้า Loss ลดลงเรื่อยๆ แสดงว่า AI เรียนรู้ได้ดีครับ)")

# ==========================================
# 8. SAVE MODEL (บันทึกสมองเก็บไว้ใช้) 💾
# ==========================================
# สร้างโฟลเดอร์ models ถ้ายังไม่มี
if not os.path.exists('models'):
    os.makedirs('models')

model.save('models/hybrid_model_v1.h5')
print("💾 Model saved to 'models/hybrid_model_v1.h5'")

# ==========================================
# 9. VISUALIZATION (ดูผลงานแบบรูปธรรม) 📈
# ==========================================

from sklearn.metrics import confusion_matrix

print("\n📊 กำลังวาดกราฟผลลัพธ์...")
plt.style.use('seaborn-v0_8-whitegrid') # ปรับสไตล์กราฟให้สวย

# สร้างหน้าต่างกราฟใหญ่ๆ (3 ช่อง)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- กราฟที่ 1: ความฉลาดในการแยกโรค (Diagnosis Accuracy) ---
# เป้าหมาย: เส้นต้องพุ่งขึ้นเข้าหา 1.0
axes[0].plot(history.history['diagnosis_output_accuracy'], label='Train Accuracy', color='blue', linewidth=2)
axes[0].plot(history.history['val_diagnosis_output_accuracy'], label='Val Accuracy', color='orange', linestyle='--', linewidth=2)
axes[0].set_title('Diagnosis Accuracy', fontsize=12)
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Accuracy')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# --- กราฟที่ 2: ความผิดพลาดในการทายวันพัง (RUL Error) ---
# เป้าหมาย: เส้นต้องดิ่งลงเข้าหา 0
axes[1].plot(history.history['rul_output_mae'], label='Train MAE', color='red', linewidth=2)
axes[1].plot(history.history['val_rul_output_mae'], label='Val MAE', color='green', linestyle='--', linewidth=2)
axes[1].set_title('RUL Prediction Error', fontsize=12)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Mean Absolute Error (Cycles)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# --- กราฟที่ 3: เฉลย vs ทายจริง (RUL Prediction Check) ---
# ลองให้ AI ทายผลจากข้อมูล 100 ตัวแรกดู
# ทำนายผล
predictions = model.predict(
    {'input_vibration': X_vib_final[:100], 'input_sensors': X_sensor_final[:100]}
)
pred_rul = predictions[1] # เอาคำตอบส่วน RUL ออกมา

# วาดกราฟเปรียบเทียบ
axes[2].plot(y_rul_final[:100], label='Actual RUL', color='black', alpha=0.6)
axes[2].plot(pred_rul, label='Predicted RUL ', color='red', linestyle='--')
axes[2].set_title('Reality vs AI Prediction (100 Samples)', fontsize=12)
axes[2].set_xlabel('Sample Index')
axes[2].set_ylabel('RUL (Cycles)')
axes[2].legend()

plt.tight_layout()
plt.show() # ⚠️ หน้าต่างกราฟจะเด้งขึ้นมา

print("✨ กราฟแสดงผลเรียบร้อย!")