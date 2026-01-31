# ==========================================
# 🧪 EDA: CWRU Vibration Analysis (Time & FFT)
# ==========================================
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.fft import fft, fftfreq

# 1. ตั้งค่า Config (แก้ Path ตรงนี้ให้ตรงกับเครื่องคุณ)
DATA_FOLDER = 'data/raw' 

# รายชื่อไฟล์ที่ต้องการเอามาเทียบกัน (Label, Filename)
FILE_CONFIGS = [
    ('Normal Baseline', 'Time_Normal_1_098.mat'),   
    ('Inner Race Fault', 'IR007_1_110.mat'),       
    ('Outer Race Fault', 'OR007_6_1_136.mat'),     
    ('Ball Fault', 'B007_1_123.mat')               
]

# 2. ฟังก์ชันช่วยโหลดและคำนวณ
def get_signal_from_mat(folder, filename):
    """โหลดไฟล์ .mat และดึง array ข้อมูลออกมา"""
    filepath = os.path.join(folder, filename)
    try:
        mat = loadmat(filepath)
        # หา Key ที่มีคำว่า 'DE_time' (Drive End Vibration)
        key = [k for k in mat.keys() if 'DE_time' in k][0]
        return mat[key].flatten()
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None

def calculate_fft(signal, fs=12000):
    """คำนวณ Frequency Domain (FFT)"""
    N = len(signal)
    yf = fft(signal)
    xf = fftfreq(N, 1/fs)
    
    # ตัดเอาแค่ครึ่งแรก (Positive Frequencies)
    idx_half = N // 2
    return xf[:idx_half], 2.0/N * np.abs(yf[:idx_half])

# 3. วาดกราฟเปรียบเทียบ
plt.style.use('ggplot') 
fig, axes = plt.subplots(4, 2, figsize=(15, 12), constrained_layout=True)

print(f"📊 Loading data from: {DATA_FOLDER} and plotting...")

for i, (label_name, filename) in enumerate(FILE_CONFIGS):
    # โหลดข้อมูล
    sig = get_signal_from_mat(DATA_FOLDER, filename)
    
    if sig is None: continue
        
    # --- กราฟซ้าย: Time Domain (ดูคลื่นดิบๆ 2000 จุดแรก) ---
    t_axis = np.arange(2000) / 12000 # แกนเวลา (วินาที)
    axes[i, 0].plot(t_axis, sig[:2000], color='#1f77b4', linewidth=1)
    axes[i, 0].set_title(f"{label_name} - Time Domain", fontsize=12, fontweight='bold')
    axes[i, 0].set_ylabel("Amplitude (g)")
    axes[i, 0].set_xlabel("Time (s)")
    axes[i, 0].grid(True, alpha=0.3)
    
    # --- กราฟขวา: Frequency Domain (FFT Spectrum) ---
    freqs, amps = calculate_fft(sig)
    axes[i, 1].plot(freqs, amps, color='#d62728', linewidth=1)
    axes[i, 1].set_title(f"{label_name} - Frequency Domain (FFT)", fontsize=12, fontweight='bold')
    axes[i, 1].set_ylabel("Magnitude")
    axes[i, 1].set_xlabel("Frequency (Hz)")
    axes[i, 1].set_xlim(0, 4000) # ซูมดูช่วง 0 - 4000 Hz
    axes[i, 1].grid(True, alpha=0.3)

plt.show()