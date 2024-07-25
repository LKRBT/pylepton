#!/usr/bin/env python

import cv2
import time
import threading
import numpy as np

from get_cfg import get_cfg
# from send_sms import send_sms
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3
from flask import Flask, render_template

app = Flask(__name__)

cfg = get_cfg()

def check_for_fire(data):
  temper = (data - 27315) / 100.0
  temper = temper.reshape(120,160)
  for row in temper:
    print(str)
    
  
def capture_ir(flip_v=False, device=None):
  with Lepton3(device) as l:
    a,_ = l.capture()
    # check_for_fire(a)
    
  if flip_v:
    cv2.flip(a,0,a)
  
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  
  return np.uint8(a)

def capture_rgb(picam2):
  frame = picam2.capture_array("main")
  
  return frame

def generate_rgb_frames():
    picam2 = Picamera2()
    picam2.start()
    while True:
        frame = capture_rgb(picam2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(cfg['PI']['RGB_PATH'], frame)
        time.sleep(1)
        
def generate_ir_frames(flip_v=False, device=cfg['PI']['SERIAL_PORT']):
    while True:
        frame = capture_ir(flip_v=flip_v, device=device)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        cv2.imwrite(cfg['PI']['IR_PATH'], frame)
        time.sleep(1)
        
@app.route('/')
def home(): 
  return render_template('index.html')

if __name__ == '__main__':
  ir_thr = threading.Thread(target=generate_ir_frames)
  ir_thr.daemon = True
  ir_thr.start()
  

  rgb_thr = threading.Thread(target=generate_rgb_frames)
  rgb_thr.daemon = True
  rgb_thr.start()
   
  app.run(host=cfg['PI']['HOST'], port=cfg['PI']['PORT'])
