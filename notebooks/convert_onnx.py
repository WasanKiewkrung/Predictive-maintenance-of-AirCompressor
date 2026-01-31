import tensorflow as tf
import tf2onnx
import onnx

# 1. ตั้งชื่อไฟล์
input_model_path = 'models/hybrid_model_v1.h5'      # ไฟล์สมองเดิมของเรา
output_onnx_path = 'models/hybrid_model_v1.onnx'    # ไฟล์ผลลัพธ์ที่จะเอาไปใช้

print(f"🔄 Loading Keras model from {input_model_path}...")
try:
    model = tf.keras.models.load_model(input_model_path, compile=False)
    print("   ✅ Model Loaded!")
except Exception as e:
    print(f"   ❌ Error Loading Model: {e}")
    exit()

# 2. กำหนดสเปค Input (Signature) ให้ชัดเจน
# ต้องตรงกับตอนเราสร้าง model.py เป๊ะๆ
# Input 1: Vibration (None, 1024, 1)
spec_vib = tf.TensorSpec((None, 1024, 1), tf.int16, name="input_vibration")
# Input 2: Sensor (None, 50, 2)
spec_sensor = tf.TensorSpec((None, 50, 2), tf.float32, name="input_sensors")

# 3. สั่งแปลงร่าง!
print("⚡ Converting to ONNX...")
model_proto, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=[spec_vib, spec_sensor], 
    opset=13 # NXP eIQ Toolkit แนะนำ opset 13 ขึ้นไป
)

# 4. บันทึกไฟล์
onnx.save(model_proto, output_onnx_path)
print(f"🎉 Success! ONNX model saved to: {output_onnx_path}")
print("   👉 Next Step: Import this file into NXP eIQ Toolkit.")