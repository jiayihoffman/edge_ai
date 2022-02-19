#
# Copyright 2022 Jiayi Hoffman. All Rights Reserved.
#
import tkinter as tk
from confluent_kafka import Producer

ROBOT_CTL_KEYS = ['up', 'right', 'down', 'left', 'space']

def create_producer():
   return Producer({'bootstrap.servers': 'localhost:9092'})

def key_input(event, p):
   key_pressed = event.keysym.lower()
   key_index = ROBOT_CTL_KEYS.index(key_pressed) if key_pressed in ROBOT_CTL_KEYS else None
   print('key pressed {}, index {}'.format(key_pressed, key_index))
   if key_index is not None:
      p.produce("command_topic", value=key_index)
      p.flush(30)

if __name__ == "__main__":
   p = create_producer()

   print("use arrow keys to control the robot's direction. press 'space' key to stop the robot")
   root = tk.Tk()
   frame = tk.Frame(root, width=500, height=500)
   frame.bind_all("<Key>", lambda event: key_input(event, p))
   root.mainloop()