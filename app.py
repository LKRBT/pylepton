#!/usr/bin/env python

import cv2
import time
import threading
import numpy as np

from twilio.rest import Client
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3
from flask import Flask, render_template

from get_cfg import get_cfg
#from send_sms import send_sms

app = Flask(__name__)

cfg = get_cfg()

message = f"http://{cfg['PI']['HOST']}:{cfg['PI']['PORT']}\n{cfg['ANDROID']['MESSAGE']}"

fire_flag = False
last_time = None

def send_sms(client, message):   
    client.messages.create(
        from_ = cfg['TWILIO']['FROM_NUM'],
        to = cfg['TWILIO']['TO_NUM'],
        body = message
    )
    
def check_for_fire(data):
  global fire_flag, last_time
  temper = (data - 27315) / 100.0
  temper = temper.reshape(120,160)
  _, max_val, _, max_loc = cv2.minMaxLoc(temper)
  #for row in temper:
  #  print(str)
  if max_val >= 40:
    if last_time is None:
        last_time = time.time()
    elif time.time() - last_time >= 3:
        send_sms(client, message)
        fire_flag = True
  else:
    last_time = None
    fire_flag = False
  
  return "{:.2f}C".format(max_val), max_loc
  
def capture_ir(device=None):
  with Lepton3(device) as l:
    a,_ = l.capture()
  val, loc = check_for_fire(a)
  x, y = loc
    
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  frame = np.uint8(a)
  frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
  
  cv2.line(frame, (x - 10, y), (x - 2, y), (255, 255, 255), 1)
  cv2.line(frame, (x + 2, y), (x + 10, y), (255, 255, 255), 1)
  cv2.line(frame, (x, y - 10), (x, y - 2), (255, 255, 255), 1)
  cv2.line(frame, (x, y + 2), (x, y + 10), (255, 255, 255), 1)
  cv2.circle(frame, (x, y), 2, (255, 255, 255), 1)
  cv2.putText(frame, val, (x + 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)

  return frame

def capture_rgb(picam2):
  frame = picam2.capture_array("main")
  frame = cv2.flip(frame, -1)
  frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  
  return frame

def generate_rgb_frames():
    global fire_flag
    picam2 = Picamera2()
    picam2.start()
    while True:
        frame = capture_rgb(picam2)
        if fire_flag:
            cv2.imwrite(cfg['PI']['RGB_PATH'], frame)
        
def generate_ir_frames():
    global fire_flag
    while True:
        frame = capture_ir(device=cfg['PI']['SERIAL_PORT'])
        if fire_flag:
            cv2.imwrite(cfg['PI']['IR_PATH'], frame)
        
@app.route('/')
def home(): 
  return render_template('index.html')

if __name__ == '__main__':
  client = Client(cfg['TWILIO']['SID'], cfg['TWILIO']['TOKEN'])
  
  ir_thr = threading.Thread(target=generate_ir_frames)
  ir_thr.daemon = True
  ir_thr.start()
  

  rgb_thr = threading.Thread(target=generate_rgb_frames)
  rgb_thr.daemon = True
  rgb_thr.start()
   
  app.run(host=cfg['PI']['HOST'], port=cfg['PI']['PORT'])
