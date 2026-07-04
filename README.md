# AquaNova - Intelligent River Cleaning System

An AI-powered autonomous river cleaning system that detects floating waste using Computer Vision and assists in automated waste collection.

## Project Overview

AquaNova is a final-year engineering project developed to reduce river pollution by detecting floating waste using Artificial Intelligence and controlling cleaning operations through an integrated hardware and dashboard system.

The project combines:

- Artificial Intelligence
- Computer Vision
- Raspberry Pi
- Arduino
- Web Dashboard

to perform autonomous waste detection and monitoring.

# Features

- AI-based floating waste detection
- TensorFlow Lite model inference
- Real-time camera processing
- Raspberry Pi integration
- Arduino-based hardware control
- GPS data parsing
- Web dashboard for monitoring
- Frontend and backend implementation
- Stores sensor and monitoring data in MongoDB
- Modular project architecture

# Technologies Used

## Programming Languages

- Python
- JavaScript
- HTML
- CSS

## AI & Computer Vision

- TensorFlow Lite
- OpenCV
- NumPy

## Database

- MongoDB

## Raspberry Pi Libraries

- PiCamera2
- RPi.GPIO
- PySerial
- pynmea2

## Hardware

- Raspberry Pi 5 (Camera Module)
- Arduino Nano 
- Solar Panel
- GPS
- HX711 Load Cell
- L298N Motor Driver
- Motors (Servo, Coreless, N20, Pump)
- Propellers
- Conveyor Belt
- Buzzer

## Dashboard

- HTML
- CSS
- JavaScript
- Node.js
- Express.js

# Project Structure

AquaNova_Project
│
├── AI_Model/
│   ├── camera_images/
│   ├── pynmea2/
│   ├── aquanova.py
│   ├── pyserial.py
│   ├── model_unquant.tflite
│   ├── model_unquant2.tflite
│   └── requirements.txt
│
├── Arduino/
│
├── Dashboard/
│   ├── backend/
│   ├── frontend/
│   └── README.md
│
├── Documents/
│
├── .gitignore
│
└── README.md

# Installation

## Clone Repository

```bash
git clone https://github.com/Aaryaashtekar/AquaNova-An-Intelligent-River-Cleaning-System.git
```

```bash
cd AquaNova-An-Intelligent-River-Cleaning-System
```

---

## Install Python Packages

```bash
pip install -r requirements.txt
```

---

## Dashboard Setup

Go inside Dashboard backend.

```bash
cd Dashboard/backend
```

Install packages.

```bash
npm install
```

Run backend.

```bash
node server.js
```

Open frontend by opening

```
Dashboard/frontend/index.html
```
# AI Model

The AI module performs:

- Image acquisition
- Waste detection
- TensorFlow Lite inference
- Serial communication
- GPS data processing

Main file:

```
AI_Model/aquanova.py
```
# Python Dependencies

- numpy
- opencv-python
- tensorflow
- picamera2
- RPi.GPIO
- pyserial
- pynmea2

# Contributors

- Aarya Ashtekar
- Chetana Bendale
- Pranjali Bidwe
- Pranjal Darade
---