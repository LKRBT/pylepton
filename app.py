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

running = True

def check_for_fire(data):
    temper = (data - 27315) / 100.0
    temper = temper.reshape(120, 160)
    for row in temper:
        print(str)
    
def capture_ir(flip_v=False, device=None):
    with Lepton3(device) as l:
        a, _ = l.capture()
        # check_for_fire(a)
    
    if flip_v:
        cv2.flip(a, 0, a)
    
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)
    
    new_width = a.shape[1] * 4
    new_height = a.shape[0] * 4
    frame = cv2.resize(a, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    frame = np.uint8(frame)
    frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    return frame

def capture_rgb(picam2):
    frame = picam2.capture_array("main")
    frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
    
    return frame

def main_loop():
    global running
    picam2 = Picamera2()
    picam2.start()
    while running:
        rgb = capture_rgb(picam2)
        ir = capture_ir(flip_v=False, device=cfg['PI']['SERIAL_PORT'])
        
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

        screen.fill((0, 0, 0))  # Clear the screen
        screen.blit(rgb, (0, 0))
        screen.blit(ir, (size_w/2, 0))
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main_loop()
