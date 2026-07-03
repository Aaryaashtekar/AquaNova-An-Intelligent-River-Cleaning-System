import cv2
import numpy as np
import tensorflow as tf
import time
import os
from datetime import datetime
from collections import deque
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import serial
import pynmea2
from hx711 import HX711

# ---------------- SERIAL (ARDUINO) ---------------- #
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

def send_cmd(cmd):
    global last_cmd_time
    if time.time() - last_cmd_time > CMD_DELAY:
        ser.write((cmd + '\n').encode())
        print("CMD SENT:", cmd)
        last_cmd_time = time.time()

# ---------------- GPS ---------------- #
gps = serial.Serial('/dev/serial0', 9600, timeout=1)  # change if needed

def read_gps():
    try:
        line = gps.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
            msg = pynmea2.parse(line)
            return msg.latitude, msg.longitude
    except:
        pass
    return None, None

# ---------------- LOAD CELL ---------------- #
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(1)
hx.reset()
hx.tare()

MAX_WEIGHT = 1000  # adjust based on your bin capacity

# ---------------- BUZZER ---------------- #
BUZZER_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def beep(times):
    for _ in range(times):
        GPIO.output(BUZZER_PIN, 1)
        time.sleep(0.3)
        GPIO.output(BUZZER_PIN, 0)
        time.sleep(0.3)

# ---------------- MODEL CONFIG ---------------- #
MODEL_PATH = "/home/admin/waste_detection/model_unquant.tflite"
INPUT_SIZE = (224, 224)
CLASS_NAMES = ["Background", "Waste", "Living_Organism"]

CONF_THRESHOLD = 0.7
DETECTION_INTERVAL = 0.7

# ---------------- LOAD MODEL ---------------- #
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Model loaded successfully")

# ---------------- CAMERA ---------------- #
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# ---------------- VARIABLES ---------------- #
left_hist = deque(maxlen=3)
center_hist = deque(maxlen=3)
right_hist = deque(maxlen=3)

scan_angles = [60, 90, 120]
scan_index = 0

last_detection_time = 0
last_cmd_time = 0
CMD_DELAY = 2

buzzer_80_done = False
buzzer_100_done = False

# ---------------- HELPER FUNCTIONS ---------------- #
def preprocess_frame(frame):
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    img = cv2.resize(frame, INPUT_SIZE)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    return img

def predict_region(region):
    img = preprocess_frame(region)
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    output = output[0]
    idx = np.argmax(output)

    return CLASS_NAMES[idx], float(output[idx])

def get_score(cls, conf, target):
    return conf if cls == target else 0

# ---------------- MAIN LOOP ---------------- #
while True:

    # -------- CAMERA -------- #
    frame = picam2.capture_array()

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    height, width, _ = frame.shape
    current_time = time.time()

    # -------- LOAD CELL -------- #
    weight = abs(hx.get_weight(5))
    percent = (weight / MAX_WEIGHT) * 100
    print(f"Weight: {weight:.2f}g | Fill: {percent:.1f}%")

    if percent > 80 and not buzzer_80_done:
        print(" 80% FULL")
        beep(1)
        buzzer_80_done = True

    if percent > 100 and not buzzer_100_done:
        print("BIN FULL")
        beep(2)
        buzzer_100_done = True

    hx.power_down()
    hx.power_up()

    # -------- GPS -------- #
    lat, lon = read_gps()
    if lat:
        print(f"GPS: {lat}, {lon}")

    # -------- AI DETECTION -------- #
    if current_time - last_detection_time > DETECTION_INTERVAL:

        left = frame[:, :width//3]
        center = frame[:, width//3:2*width//3]
        right = frame[:, 2*width//3:]

        l_cls, l_conf = predict_region(left)
        c_cls, c_conf = predict_region(center)
        r_cls, r_conf = predict_region(right)

        # -------- LIVING ORGANISM -------- #
        if (l_cls == "Living_Organism" and l_conf > CONF_THRESHOLD) or \
           (c_cls == "Living_Organism" and c_conf > CONF_THRESHOLD) or \
           (r_cls == "Living_Organism" and r_conf > CONF_THRESHOLD):

            print("Living Organism Detected")
            send_cmd("STOP")
            send_cmd("TURN_RIGHT")

        else:
            # -------- WASTE DETECTION -------- #
            scores = {
                "LEFT": get_score(l_cls, l_conf, "Waste"),
                "CENTER": get_score(c_cls, c_conf, "Waste"),
                "RIGHT": get_score(r_cls, r_conf, "Waste")
            }

            best = max(scores, key=scores.get)

            if scores[best] > CONF_THRESHOLD:

                print(f" Waste detected at {best}")

                if best == "LEFT":
                    send_cmd("TURN_LEFT")

                elif best == "RIGHT":
                    send_cmd("TURN_RIGHT")

                else:
                    send_cmd("MOVE")

                    time.sleep(2)
                    send_cmd("STOP")

                    # COLLECTION
                    send_cmd("SERVO_OPEN")
                    send_cmd("CONVEYOR_ON")
                    send_cmd("PUMP_ON")

                    time.sleep(5)

                    send_cmd("CONVEYOR_OFF")
                    send_cmd("PUMP_OFF")
                    send_cmd("SERVO_CLOSE")

            else:
                print("Scanning...")
                send_cmd("MOVE")

        last_detection_time = current_time

    # -------- DISPLAY -------- #
#    cv2.imshow("AquaNova", frame)

#   if cv2.waitKey(1) & 0xFF == ord('q'):
#        break

# ---------------- CLEANUP ---------------- #
picam2.stop()
cv2.destroyAllWindows()
GPIO.cleanup()
ser.close()
gps.close()
