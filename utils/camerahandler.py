import cv2
import time
import numpy as np

from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3

from .send_sms import send_sms
from .parallel import thread_method


class CameraHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        
        self.ir_frame = None
        self.rgb_frame = None
        
        self.s_time = None
        self.sms_flag = True
        self.fire_flag = False

        self.picam2 = Picamera2()
        
    def check_for_fire(self, data):
        temper = (data - 27315) / 100.0
        temper = temper.reshape(120, 160)
        _, max_val, _, max_loc = cv2.minMaxLoc(temper)
        
        if max_val >= 40:
            if self.s_time is None:
                self.s_time = time.time()
            elif time.time() - self.s_time >= 3:
                self.fire_flag = True
                if self.sms_flag:
                    #send_sms()
                    self.sms_flag = False
        else:
            self.s_time = None
            self.fire_flag = False
			
        return "{:.2f}C".format(max_val), max_loc
        
    def capture_ir(self, device=None):
        with Lepton3(device) as l:
            a, _ = l.capture()
	    a = cv2.flip(a, -1)
		
        val, loc = self.check_for_fire(a)
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
        
    def capture_rgb(self):
        frame = self.picam2.capture_array("main")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame

    @thread_method
    def loop(self):
        self.picam2.start()
        while True:
            self.rgb_frame = self.capture_rgb()
            self.ir_frame = self.capture_ir(device=self.cfg['PI']['SERIAL_PORT'])	
			
            if self.fire_flag:
                cv2.imwrite(self.cfg['PI']['RGB_PATH'], self.rgb_frame)
                cv2.imwrite(self.cfg['PI']['IR_PATH'], self.ir_frame)
