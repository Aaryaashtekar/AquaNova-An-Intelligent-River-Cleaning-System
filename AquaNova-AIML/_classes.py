import cv2
import numpy as np
import tensorflow as tf
import time
import os
from datetime import datetime
from collections import deque
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# ---------------- CONFIG ---------------- #
MODEL_PATH = "/home/admin/waste_detection/model_unquant.tflite"
INPUT_SIZE = (224, 224)
CLASS_NAMES = ["Background", "Waste", "Living_Organism"]

CONF_THRESHOLD = 0.70
DETECTION_INTERVAL = 0.7
RETENTION_DAYS = 30

OUTPUT_DIR = "/home/admin/waste_detection/camera_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- SERVO SETUP ---------------- #
SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

# Scan angles
scan_angles = [60, 90, 120]
scan_index = 0

# ---------------- CLEANUP OLD FILES ---------------- #
def cleanup_old_files(directory, days):
    now = time.time()
    cutoff = now - (days * 86400)
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            os.remove(path)

cleanup_old_files(OUTPUT_DIR, RETENTION_DAYS)

# ---------------- LOAD MODEL ---------------- #
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Model loaded successfully")

# ---------------- HELPERS ---------------- #
def preprocess_frame(frame):
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    img = cv2.resize(frame, INPUT_SIZE)
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

def predict_region(region):
    input_data = preprocess_frame(region)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    output = output[0] if len(output.shape) > 1 else output
    idx = np.argmax(output)

    if idx >= len(CLASS_NAMES):
        return "Unknown", float(np.max(output))

    return CLASS_NAMES[idx], float(output[idx])

def get_score(cls, conf, target):
    return conf if cls == target else 0

# ---------------- CAMERA ---------------- #
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# ---------------- VARIABLES ---------------- #
left_hist = deque(maxlen=3)
center_hist = deque(maxlen=3)
right_hist = deque(maxlen=3)

last_detection_time = 0
last_saved_time = 0
SAVE_INTERVAL = 3

signal_text = "Starting..."

# ---------------- MAIN LOOP ---------------- #
while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    height, width, _ = frame.shape

    current_time = time.time()

    if current_time - last_detection_time > DETECTION_INTERVAL:

        # Split regions
        left_roi = frame[:, :width//3]
        center_roi = frame[:, width//3:2*width//3]
        right_roi = frame[:, 2*width//3:]

        # Predictions
        l_cls, l_conf = predict_region(left_roi)
        c_cls, c_conf = predict_region(center_roi)
        r_cls, r_conf = predict_region(right_roi)

        # ---------------- LIVING ORGANISM PRIORITY ---------------- #
        living_detected = (
            (l_cls == "Living_Organism" and l_conf > CONF_THRESHOLD) or
            (c_cls == "Living_Organism" and c_conf > CONF_THRESHOLD) or
            (r_cls == "Living_Organism" and r_conf > CONF_THRESHOLD)
        )

        # ---------------- WASTE SMOOTHING ---------------- #
        left_hist.append(get_score(l_cls, l_conf, "Waste"))
        center_hist.append(get_score(c_cls, c_conf, "Waste"))
        right_hist.append(get_score(r_cls, r_conf, "Waste"))

        smooth_conf = {
            "LEFT": np.mean(left_hist),
            "CENTER": np.mean(center_hist),
            "RIGHT": np.mean(right_hist)
        }

        best_region = max(smooth_conf, key=smooth_conf.get)
        best_conf = smooth_conf[best_region]

        # ---------------- DECISION LOGIC ---------------- #
        if living_detected:
            signal_text = "Living Organism - Avoid"

            print("ACTION: CHANGE PATH 🚫")
            # 👉 Add motor control here (stop/turn)

        elif best_conf > CONF_THRESHOLD:
            signal_text = f"Waste - {best_region}"

            print(f"ACTION: MOVE {best_region} 🧭")

            if best_region == "LEFT":
                pass  # robot.turn_left()
            elif best_region == "RIGHT":
                pass  # robot.turn_right()
            else:
                pass  # robot.forward()

            # Save image with cooldown
            if current_time - last_saved_time > SAVE_INTERVAL:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"waste_{best_region}_{timestamp}.jpg"
                cv2.imwrite(os.path.join(OUTPUT_DIR, filename), frame)
                last_saved_time = current_time

        else:
            signal_text = "Background - Scanning"

            print("ACTION: SCANNING 🔄")

            set_servo_angle(scan_angles[scan_index])
            scan_index = (scan_index + 1) % len(scan_angles)

        last_detection_time = current_time

    # ---------------- DISPLAY ---------------- #
    cv2.line(frame, (width//3, 0), (width//3, height), (0, 255, 0), 2)
    cv2.line(frame, (2*width//3, 0), (2*width//3, height), (0, 255, 0), 2)

    cv2.putText(frame, signal_text, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Waste Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ---------------- #
picam2.stop()
cv2.destroyAllWindows()
pwm.stop()
GPIO.cleanup()