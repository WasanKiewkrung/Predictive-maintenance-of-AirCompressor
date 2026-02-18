// model_config.h
#ifndef MODEL_CONFIG_H_
#define MODEL_CONFIG_H_

// ==========================================
// ⚙️ MODEL INPUT PARAMETERS
// ==========================================
// 1. Vibration Input (Shape: [1, 1024, 1])
// สูตร: int8_val = (real_val / SCALE) + ZERO
#define INPUT_VIB_SCALE 0.032791f
#define INPUT_VIB_ZERO -5
#define INPUT_VIB_INDEX 0 // อาจต้องเช็ค index หน้างานอีกที (ปกติคือ 0)

// 2. Sensor Input (Shape: [1, 3])
// สูตร: int8_val = (real_val / SCALE) + ZERO
#define INPUT_SEN_SCALE 0.003663f
#define INPUT_SEN_ZERO -124
#define INPUT_SEN_INDEX 1

// ==========================================
// ⚙️ MODEL OUTPUT PARAMETERS
// ==========================================
// 1. Status Output (Class Probabilities)
// สูตร: real_val = (int8_val - ZERO) * SCALE
#define OUTPUT_STAT_SCALE 0.003480f
#define OUTPUT_STAT_ZERO -128
#define OUTPUT_STAT_INDEX 0 // (เช็ค Index หน้างาน: อันที่มี size=3)

// 2. RUL Output (Remaining Useful Life)
// สูตร: real_val = (int8_val - ZERO) * SCALE
#define OUTPUT_RUL_SCALE 0.003906f
#define OUTPUT_RUL_ZERO -128
#define OUTPUT_RUL_INDEX 1 // (เช็ค Index หน้างาน: อันที่มี size=1)

#endif // MODEL_CONFIG_H_