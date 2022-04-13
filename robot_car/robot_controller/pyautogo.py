#
# Copyright 2022 Jiayi Hoffman. All Rights Reserved.
#
from pyfirmata import Arduino, SERVO, INPUT
import time
import logging

# USB_PORT = "/dev/ttyACM0"  # Arduino Uno WiFi Rev2
# USB_PORT = "/dev/tty.usbmodem14201"
USB_PORT = '/dev/tty.usbmodem14401'

# servo pin
SERVO_PIN = 3
SERVO_START_ANGLE = 80

# motor pins
ENA_PIN = 5
ENB_PIN = 6
IN1_PIN = 7
IN2_PIN = 8
IN3_PIN = 9
IN4_PIN = 10

CAR_SPEED = 0.5

HIGH = 1
LOW = 0

logger = logging.getLogger("robot_controller")

def forward(enA, enB, in1, in2, in3, in4):
   logger.debug('forward')
   enA.write(CAR_SPEED);
   enB.write(CAR_SPEED);
   in1.write(HIGH)
   in2.write(LOW)
   in3.write(LOW)
   in4.write(HIGH)

def back(enA, enB, in1, in2, in3, in4):
   logger.debug('back')
   enA.write(CAR_SPEED);
   enB.write(CAR_SPEED);
   in1.write(LOW)
   in2.write(HIGH)
   in3.write(HIGH)
   in4.write(LOW)

def left(enA, enB, in1, in2, in3, in4):
   logger.debug('left')
   enA.write(0.3);
   enB.write(0.8);
   in1.write(LOW)
   in2.write(HIGH)
   in3.write(LOW)
   in4.write(HIGH)

def right(enA, enB, in1, in2, in3, in4):
   logger.debug('right')
   enA.write(0.8);
   enB.write(0.3);
   in1.write(HIGH)
   in2.write(LOW)
   in3.write(HIGH)
   in4.write(LOW)

def stop_auto(enA, enB):
   logger.debug('stop')
   enA.write(0);
   enB.write(0);

def move_servo(servo_pin, angle):
   if angle < 0:
      angle = 0
   elif angle > 180:
      angle = 180
   else:
      servo_pin.write(angle)
      time.sleep(0.3)  # avoid jitter

   return angle

def stop_servo(servo_pin):
   move_servo(servo_pin, SERVO_START_ANGLE)
   time.sleep(0.3)
   servo_pin.mode = INPUT

def setup_servo_pin(board):
   servo_pin = board.digital[SERVO_PIN]
   servo_pin.mode = SERVO
   move_servo(servo_pin, SERVO_START_ANGLE)
   return servo_pin

def setup_motor_pins(board):
   enA = board.get_pin('d:{}:p'.format(ENA_PIN))
   enB = board.get_pin('d:{}:p'.format(ENB_PIN))

   in1 = board.get_pin('d:{}:o'.format(IN1_PIN))
   in2 = board.get_pin('d:{}:o'.format(IN2_PIN))
   in3 = board.get_pin('d:{}:o'.format(IN3_PIN))
   in4 = board.get_pin('d:{}:o'.format(IN4_PIN))

   return enA, enB, in1, in2, in3, in4

def setup_board():
   return Arduino(USB_PORT)


