#
# Copyright 2022 Jiayi Hoffman. All Rights Reserved.
#
import tkinter as tk
import pyfirmata
import time

#USB_PORT = "/dev/ttyACM0"  # Arduino Uno WiFi Rev2
USB_PORT = "/dev/tty.usbmodem14201"
ROBOT_CTL_KEYS = ['up', 'right', 'down', 'left', 'space']

# ultrasonic sensor pins
TRIGGER_PIN  = 'A5'
ECHO_PIN     = 'A4'

# servo control pin
SERVO_PIN = 3

# moto pins
ENA_PIN = 5
ENB_PIN = 6
IN1_PIN = 7
IN2_PIN = 8
IN3_PIN = 9
IN4_PIN = 10

CAR_SPEED = 0.6
HIGH = 1
LOW = 0

def forward():
   enA.write(CAR_SPEED);
   enB.write(CAR_SPEED);
   in1.write(HIGH)
   in2.write(LOW)
   in3.write(LOW)
   in4.write(HIGH)
   isStopped = False

def back():
   enA.write(CAR_SPEED);
   enB.write(CAR_SPEED);
   in1.write(LOW)
   in2.write(HIGH)
   in3.write(HIGH)
   in4.write(LOW)
   isStopped = False

def left():
   enA.write(0.3);
   enB.write(0.8);
   in1.write(LOW)
   in2.write(HIGH)
   in3.write(LOW)
   in4.write(HIGH)
   isStopped = False

def right():
   enA.write(0.8);
   enB.write(0.3);
   in1.write(HIGH)
   in2.write(LOW)
   in3.write(HIGH)
   in4.write(LOW)
   isStopped = False

def stop_auto():
   enA.write(0);
   enB.write(0);

   isStopped = True

def command_direct(key_index):
   if key_index == 0:
      forward()
   elif key_index == 1:
      right()
   elif key_index == 2:
      back()
   elif key_index == 3:
      left()
   elif key_index == 4:
      stop_auto()

def key_input(event):
   key_pressed = event.keysym.lower()
   key_index = ROBOT_CTL_KEYS.index(key_pressed) if key_pressed in ROBOT_CTL_KEYS else None
   print('key pressed {}, index {}'.format(key_pressed, key_index))
   if key_index is not None:
      command_direct(key_index)

def setup_motor_pins(board):
   enA = board.get_pin('d:{}:p'.format(ENA_PIN))
   enB = board.get_pin('d:{}:p'.format(ENB_PIN))

   in1 = board.get_pin('d:{}:o'.format(IN1_PIN))
   in2 = board.get_pin('d:{}:o'.format(IN2_PIN))
   in3 = board.get_pin('d:{}:o'.format(IN3_PIN))
   in4 = board.get_pin('d:{}:o'.format(IN4_PIN))

   return enA, enB, in1, in2, in3, in4

frontDistance = rightDistance = leftDistance = 0;
isStopped = True

board = pyfirmata.Arduino(USB_PORT)
enA, enB, in1, in2, in3, in4 = setup_motor_pins(board)

# Start iterator to receive input data
pyfirmata.util.Iterator(board).start()

print("use arrow keys to control the robot's direction. press 'space' key to stop the robot")
root = tk.Tk()
frame = tk.Frame(root, width=500, height=500)
frame.bind_all("<Key>", key_input)
root.mainloop()