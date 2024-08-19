import sys
import cv2
import time
import pygame
import numpy as np

from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3


pygame.init()
infoObject = pygame.display.Info()
size_w = infoObject.current_w
size_h = infoObject.current_h
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

clock = pygame.time.Clock()
clock.tick(60)

class CameraHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        self.picam2 = Picamera2()
        self.ir_res = (160, 120)
        
    def check_for_fire(self, data):
        temper = (data - 27315) / 100.0
        temper = temper.reshape(120, 160)
        _, max_val, _, max_loc = cv2.minMaxLoc(temper)
		
        return "{:.2f}C".format(max_val), max_loc
	
    def capture(self):
        rgb = self.picam2.capture_array("main")
        with Lepton3(self.cfg['PI']['SERIAL_PORT']) as l:
            ir, _ = l.capture()
        
        return rgb, ir
    
    def process_ir(self, frame):
        frame = cv2.flip(frame, -1)
        
        val, loc = self.check_for_fire(frame)
        
        cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(frame, 8, frame)
        frame = np.uint8(frame)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        scale_w = int(loc[0] * size_w / 2 / self.ir_res[0])
        scale_h = int(loc[1] * size_h / self.ir_res[1])

        cv2.line(frame, (scale_w - 20, scale_h), (scale_w - 5, scale_h), (255, 255, 255), 1)
        cv2.line(frame, (scale_w + 5, scale_h), (scale_w + 20, scale_h), (255, 255, 255), 1)
        cv2.line(frame, (scale_w, scale_h - 20), (scale_w, scale_h - 5), (255, 255, 255), 1)
        cv2.line(frame, (scale_w, scale_h + 5), (scale_w, scale_h + 20), (255, 255, 255), 1)
        cv2.circle(frame, (scale_w, scale_h), 5, (255, 255, 255), 1)
        cv2.putText(frame, val, (scale_w + 20, scale_h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame
	
    def process_rgb(self, frame):
        frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        return frame

    def loop(self):
        running = True
        self.picam2.start()
        while running:
            rgb, ir = self.capture()
            view_ir = self.process_ir(ir)
            view_rgb = self.process_rgb(rgb)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        running = False
                    if event.key == ord('c'):
                        save_rgb = cv2.cvtColor(view_rgb, cv2.COLOR_RGB2BGR)
                        save_ir = cv2.cvtColor(view_ir, cv2.COLOR_RGB2BGR)
                        
                        cv2.imwrite(self.cfg['PI']['IR_PATH'] + str(time.time()) + '.png', save_ir)
                        cv2.imwrite(self.cfg['PI']['RGB_PATH'] + str(time.time()) + '.png', save_rgb)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.button)
                    if event.button == 3:
                        running = False

            rgb = pygame.surfarray.make_surface(view_rgb.swapaxes(0, 1))
            ir = pygame.surfarray.make_surface(view_ir.swapaxes(0, 1))
	
            screen.fill((0, 0, 0))
            screen.blit(rgb, (0, 0))
            screen.blit(ir, (size_w/2, 0))
            pygame.display.flip()
	
            clock.tick(60)
            
        pygame.quit()
        sys.exit()
