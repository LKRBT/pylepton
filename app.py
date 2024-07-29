#!/usr/bin/env python

import cv2
import time
import threading
import numpy as np

from get_cfg import get_cfg
# from send_sms import send_sms
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3
from flask import Flask, Response, render_template

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
  # frame = cv2.flip(frame, 0)
  # frame = cv2.flip(frame, 1)
  
  return frame

def generate_rgb_frames():
    picam2 = Picamera2()
    picam2.start()
    while True:
        frame = capture_rgb(picam2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def generate_ir_frames(flip_v=False, device=cfg['PI']['SERIAL_PORT']):
    while True:
        frame = capture_ir(flip_v=flip_v, device=device)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        _, buffer = cv2.imencode('.png', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed_rgb')
def video_feed_rgb():
  return Response(generate_rgb_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_ir')
def video_feed_ir():
  return Response(generate_ir_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')    

@app.route('/')
def home(): 
  return render_template('index.html')

if __name__ == '__main__':
  app.run(host=cfg['PI']['HOST'], port=cfg['PI']['PORT'])
