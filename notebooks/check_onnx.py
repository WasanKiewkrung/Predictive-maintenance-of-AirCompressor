import numpy as np
import tensorflow as tf
import onnxruntime as ort
import matplotlib.pyplot as plt

# --- 1. เตรียมข้อมูลสุ่ม 10 ตัวอย่าง (Random Samples) ---
NUM_SAMPLES = 10
print(f"🎲 Generating {NUM_SAMPLES} random samples for verification...")

# สร้างข้อมูลแบบ Int16 (สำหรับ ONNX)
test_vib_int16 = np.random.randint(-5000, 5000, (NUM_SAMPLES, 1024, 1), dtype=np.int16)
# สร้างข้อมูล Sensor (สำหรับทั้งคู่)
test_sensor = np.random.rand(NUM_SAMPLES, 50, 2).astype(np.float32)

# แปลงข้อมูล Vibration เป็น Float32 (สำหรับ Keras)
test_vib_float = test_vib_int16.astype(np.float32)

# --- 2. รัน Keras Model (The Gold Standard) 🧠 ---
print("🧠 Running Keras model...")
# compile=False เพื่อเลี่ยง error เรื่อง metrics
keras_model = tf.keras.models.load_model('models/hybrid_model_v1.h5', compile=False)
keras_results = keras_model.predict(
    {'input_vibration': test_vib_float, 'input_sensors': test_sensor},
    verbose=0
)
keras_diag = keras_results[0] # ผล Diag
keras_rul = keras_results[1]  # ผล RUL

# --- 3. รัน ONNX Model (The Candidate) 🔮 ---
print("🔮 Running ONNX model...")
ort_session = ort.InferenceSession('models/hybrid_model_v1.onnx')

input_feed = {
    'input_vibration': test_vib_int16, # ส่ง Int16 เข้าไปได้เลย!
    'input_sensors': test_sensor
}
onnx_results = ort_session.run(None, input_feed)
onnx_diag = onnx_results[0]
onnx_rul = onnx_results[1]

# --- 4. วาดกราฟพิสูจน์ (Visual Proof) 📊 ---
print("📊 Plotting comparison graphs...")
indices = np.arange(NUM_SAMPLES)

plt.figure(figsize=(12, 8))

# === กราฟที่ 1: เปรียบเทียบ RUL ===
plt.subplot(2, 1, 1)
plt.plot(indices, keras_rul, 'o-', color='blue', label='Keras (.h5)', markersize=10, alpha=0.5)
plt.plot(indices, onnx_rul, 'x--', color='red', label='ONNX (.onnx)', markersize=8)
plt.title('Proof 1: RUL Prediction Comparison (Lines should overlap)', fontsize=14)
plt.ylabel('RUL Value')
plt.legend()
plt.grid(True)

# === กราฟที่ 2: เปรียบเทียบ Diagnosis (เฉพาะคลาส Normal) ===
# ดูว่าความมั่นใจว่าเป็น "Normal" ตรงกันมั้ย
plt.subplot(2, 1, 2)
plt.plot(indices, keras_diag[:, 0], 'o-', color='green', label='Keras (Normal Prob)', markersize=10, alpha=0.5)
plt.plot(indices, onnx_diag[:, 0], 'x--', color='orange', label='ONNX (Normal Prob)', markersize=8)
plt.title('Proof 2: Diagnosis Probability Comparison (Lines should overlap)', fontsize=14)
plt.ylabel('Probability')
plt.xlabel('Sample Index')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# --- 5. คำนวณ Error สูงสุด ---
max_error_rul = np.max(np.abs(keras_rul - onnx_rul))
print(f"\n✨ Maximum RUL Difference: {max_error_rul:.9f}")

if max_error_rul < 1.0: # ยอมรับความต่างได้ไม่เกิน 1 ชั่วโมง/รอบ
    print("✅ RESULT: PASSED! Models are identical.") 
else:
    print("❌ RESULT: FAILED! Differences are too high.")