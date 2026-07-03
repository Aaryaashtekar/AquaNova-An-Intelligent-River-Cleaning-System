#include <Servo.h>

// -------- Servo --------
Servo myServo;
int servoPin = A0;

// -------- Motor Driver 1 (Propellers) --------
int IN1_1 = 2;
int IN2_1 = 3;
int IN3_1 = 4;
int IN4_1 = 5;
int ENA_1 = 9;
int ENB_1 = 10;

// -------- Motor Driver 2 (Conveyor + Pump) --------
int IN1_2 = 6;
int IN2_2 = 7;
int IN3_2 = 8;
int IN4_2 = 11;
int ENA_2 = 12;
int ENB_2 = 13;

String cmd;

void setup() {
  Serial.begin(9600);

  myServo.attach(servoPin);

  pinMode(IN1_1, OUTPUT);
  pinMode(IN2_1, OUTPUT);
  pinMode(IN3_1, OUTPUT);
  pinMode(IN4_1, OUTPUT);
  pinMode(ENA_1, OUTPUT);
  pinMode(ENB_1, OUTPUT);

  pinMode(IN1_2, OUTPUT);
  pinMode(IN2_2, OUTPUT);
  pinMode(IN3_2, OUTPUT);
  pinMode(IN4_2, OUTPUT);
  pinMode(ENA_2, OUTPUT);
  pinMode(ENB_2, OUTPUT);
}

// -------- MOVEMENT --------
void forward() {
  digitalWrite(ENA_1, HIGH);
  digitalWrite(ENB_1, HIGH);

  digitalWrite(IN1_1, HIGH);
  digitalWrite(IN2_1, LOW);
  digitalWrite(IN3_1, HIGH);
  digitalWrite(IN4_1, LOW);
}

void left() {
  digitalWrite(IN1_1, LOW);
  digitalWrite(IN2_1, HIGH);
  digitalWrite(IN3_1, HIGH);
  digitalWrite(IN4_1, LOW);
}

void right() {
  digitalWrite(IN1_1, HIGH);
  digitalWrite(IN2_1, LOW);
  digitalWrite(IN3_1, LOW);
  digitalWrite(IN4_1, HIGH);
}

void stopMotor() {
  digitalWrite(IN1_1, LOW);
  digitalWrite(IN2_1, LOW);
  digitalWrite(IN3_1, LOW);
  digitalWrite(IN4_1, LOW);
}

// -------- CONVEYOR --------
void conveyorOn() {
  digitalWrite(ENA_2, HIGH);
  digitalWrite(IN1_2, HIGH);
  digitalWrite(IN2_2, LOW);
}

void conveyorOff() {
  digitalWrite(IN1_2, LOW);
  digitalWrite(IN2_2, LOW);
}

// -------- PUMP --------
void pumpOn() {
  digitalWrite(ENB_2, HIGH);
  digitalWrite(IN3_2, HIGH);
  digitalWrite(IN4_2, LOW);
}

void pumpOff() {
  digitalWrite(IN3_2, LOW);
  digitalWrite(IN4_2, LOW);
}

// -------- SERVO --------
void servoOpen() {
  myServo.write(90);
}

void servoClose() {
  myServo.write(0);
}

void loop() {
  if (Serial.available()) {
    cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "MOVE") forward();
    else if (cmd == "TURN_LEFT") left();
    else if (cmd == "TURN_RIGHT") right();
    else if (cmd == "STOP") stopMotor();

    else if (cmd == "CONVEYOR_ON") conveyorOn();
    else if (cmd == "CONVEYOR_OFF") conveyorOff();

    else if (cmd == "PUMP_ON") pumpOn();
    else if (cmd == "PUMP_OFF") pumpOff();

    else if (cmd == "SERVO_OPEN") servoOpen();
    else if (cmd == "SERVO_CLOSE") servoClose();
  }
}
