#!/usr/bin/env python

import sys
import cv2
import time
import pygame
import threading
import numpy as np

from get_cfg import get_cfg
# from send_sms import send_sms

from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3

cfg = get_cfg()

pygame.init()
infoObject = pygame.display.Info()
size_w = infoObject.current_w
size_h = infoObject.current_h
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

clock = pygame.time.Clock()
clock.tick(60)

def check_for_fire(data, loc=None):
    temper = (data - 27315) / 100.0
    temper = temper.reshape(120, 160)
    
    if loc is not None:
        val = temper[loc[1], loc[0]]
        return "{:.2f}C".format(val)
    
    return "{:.2f}C".format(0)
    
def capture_ir(device=None, loc=None):
    with Lepton3(device) as l:
        a, _ = l.capture()
        a = cv2.flip(a, -1)
        
    val = check_for_fire(a, loc)
        
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)
    frame = np.uint8(a)
    
    origin_h, origin_w = frame.shape[:2]
    
    frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
    frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    if loc is not None:
        scale_w = int(loc[0] * (size_w / 2) / origin_w) 
        scale_h = int(loc[1] * size_h / origin_h)
        
        cv2.line(frame, (scale_w - 20, scale_h), (scale_w - 5, scale_h), (255, 255, 255), 1)
        cv2.line(frame, (scale_w + 5, scale_h), (scale_w + 20, scale_h), (255, 255, 255), 1)
        cv2.line(frame, (scale_w, scale_h - 20), (scale_w, scale_h - 5), (255, 255, 255), 1)
        cv2.line(frame, (scale_w, scale_h + 5), (scale_w, scale_h + 20), (255, 255, 255), 1)
        cv2.circle(frame, (scale_w, scale_h), 5, (255, 255, 255), 1)
        cv2.putText(frame, val, (scale_w + 20, scale_h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

def capture_rgb(picam2):
    frame = picam2.capture_array("main")
    # frame = cv2.flip(frame, -1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
    frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
    
    return frame

def main_loop():
    running = True
    picam2 = Picamera2()
    picam2.start()
    while running:
        rgb = capture_rgb(picam2)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = int((mouse_x - size_w/2)* 160 / (size_w/2))
        mouse_y = int(mouse_y * 120 / size_h)
        ir = capture_ir(device=cfg['PI']['SERIAL_PORT'], loc=(mouse_x, mouse_y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == ord('q'):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.button)
                if event.button == 3:
                    running = False
        
        rgb = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
        ir = pygame.surfarray.make_surface(ir.swapaxes(0, 1))
        
        screen.fill((0, 0, 0))
        screen.blit(rgb, (0, 0))
        screen.blit(ir, (size_w/2, 0))
        pygame.display.flip()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main_loop()
