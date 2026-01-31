# 🔧 Predictive Maintenance for Air Compressor using Edge AI

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0%2B-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> 🎓 **bachelor's Thesis Project** > **Topic:** การพัฒนาระบบบำรุงรักษาเชิงพยากรณ์สำหรับปั๊มลมโดยใช้ Edge AI

---

## 📖 Overview
โปรเจกต์นี้มุ่งเน้นการพัฒนาระบบ **Predictive Maintenance** เพื่อตรวจสอบสุขภาพของเครื่องปั๊มลม (Air Compressor) แบบเรียลไทม์โดยใช้เทคโนโลยี **Edge AI** ประมวลผลข้อมูลการสั่นสะเทือน, อุณหภูมิ และกระแสไฟฟ้า เพื่อทำนายความผิดปกติก่อนที่เครื่องจักรจะเสียหาย ช่วยลด Downtime ในกระบวนการผลิต

### 🚀 ฟีเจอร์หลัก (Key Features)
* ✅ **Real-time Monitoring:** ตรวจจับค่าความสั่นสะเทือน (Vibration) อุณหภูมิ และกระแสไฟฟ้า
* ✅ **Edge Processing:** ประมวลผลโมเดล AI บนอุปกรณ์ Edge (NXP FRDM-MCXN947)
* ✅ **Anomaly Detection:** แจ้งเตือนเมื่อพบความผิดปกติของลูกปืน (Bearing) 
* ✅ **Dashboard:** แสดงผลผ่าน Web Interface

---

## 🛠️ เครื่องมือที่ใช้ (Tech Stack)

| Category | Technologies |
|----------|-------------|
| **Languages** | Python |
| **AI/ML** | TensorFlow Lite, Scikit-learn |
| **Hardware** | NXP FRDM-MCXN947 |
| **Connectivity** | MQTT, REST API |

---

## 📊 ข้อมูลที่ใช้ทดสอบ (Dataset)

โปรเจกต์นี้ใช้ชุดข้อมูลมาตรฐานจาก **Case Western Reserve University (CWRU) Bearing Data Center** ในการเทรนและทดสอบโมเดล

* **Source:** [CWRU Bearing Dataset](https://www.kaggle.com/datasets/brjapon/cwru-bearing-datasets?resource=download)
* **Data Type:** Vibration signals (Accelerometer Data)
* **Sampling Rate:** 48 kHz
* **Conditions Used:**
    * ✅ Normal Baseline
    * ⚠️ Inner Race Fault
    * ⚠️ Outer Race Fault
    * ⚠️ Ball Fault
    * *(Fault diameters: 0.007")*
    * Time Segment ขนาด 2048 points (0.04 วินาที)*

### 📉 ข้อมูลสำหรับการพยากรณ์อายุการใช้งาน (RUL Dataset)
ในส่วนของการทำนายอายุการใช้งานที่เหลืออยู่ (Remaining Useful Life - RUL) โปรเจกต์นี้ใช้โมเดล **LSTM (Long Short-Term Memory)** ที่ได้รับการเทรนด้วยชุดข้อมูลจำลองการเสื่อมสภาพของเครื่องยนต์จาก NASA เพื่อเรียนรู้รูปแบบ (Pattern) ของการเสื่อมสภาพตามกาลเวลา

* **Source:** [NASA Turbofan Jet Engine Data Set](https://www.kaggle.com/datasets/behrad3d/nasa-cmaps?resource=download)
* **Data Set:** FD001 (Turbofan Engine Degradation Simulation)
* **Model:** LSTM (Deep Learning)
* **Usage:** ใช้เป็นข้อมูลตั้งต้นในการเทรนโมเดลเพื่อสร้างกราฟการเสื่อมสภาพ (Degradation Curve) สำหรับทำนาย RUL
---
## ⚙️ การติดตั้ง (Installation)

1. **Clone repository**
   ```bash
   git clone [https://github.com/username/air-compressor-predictive.git](https://github.com/username/air-compressor-predictive.git)
   cd air-compressor-predictive
