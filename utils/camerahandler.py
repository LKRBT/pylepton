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
        
        self.sms_interval = None
        self.fire_interval = None

        self.ir_frame = None
        self.rgb_frame = None
        
        self.fire_limit = {
            'min': 60,
            'max': 140
        }
        self.fire_cont = None
        self.fire_flag = False
        
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}, 
                                                        controls={"FrameDurationLimits": (1000000 // 100, 1000000 // 100)})
        self.picam2.configure(config)
        
    def check_for_fire(self, data):
        temper = (data - 27315) / 100.0
        temper = temper.reshape(120, 160)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(temper)
        if max_val >= self.fire_limit['min'] and max_val < self.fire_limit['max']:
            mask = temper > self.fire_limit['min']
            self.fire_cont, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if self.fire_interval is None:
                self.fire_interval = time.time()
            elif time.time() - self.fire_interval >= 3:
                self.fire_flag = True
                if self.sms_interval is None or time.time() - self.sms_interval >= 300:
                    send_sms()
                    self.sms_interval = time.time()
        else:
            self.fire_flag = False
            self.fire_interval = None
        
        return "{:.2f}C".format(max_val), max_loc
        
    def capture(self):
        rgb = self.picam2.capture_array("main")
        with Lepton3(self.cfg['PI']['SERIAL_PORT']) as l:
            ir, _ = l.capture()
        
        return rgb, ir
    
    def process_ir(self, frame):
        frame = cv2.flip(frame, -1)
        
        val, (x, y) = self.check_for_fire(frame)
        
        cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(frame, 8, frame)
        frame = np.uint8(frame)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)

        cv2.line(frame, (x - 10, y), (x - 2, y), (255, 255, 255), 1)
        cv2.line(frame, (x + 2, y), (x + 10, y), (255, 255, 255), 1)
        cv2.line(frame, (x, y - 10), (x, y - 2), (255, 255, 255), 1)
        cv2.line(frame, (x, y + 2), (x, y + 10), (255, 255, 255), 1)
        cv2.circle(frame, (x, y), 2, (255, 255, 255), 1)
        cv2.putText(frame, val, (x + 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
        
        if self.fire_cont is not None:
            for contour in self.fire_cont:
                x, y, w, h = cv2.boundingRect(contour)
        
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.putText(frame, "fire", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
        
            self.fire_cont = None
        
        return frame

    @thread_method
    def loop(self):
        self.picam2.start()
        while True:
            rgb, ir = self.capture()
            self.ir_frame = self.process_ir(ir)
            self.rgb_frame = rgb
            if self.fire_flag:
                cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'rgb_img.png', self.rgb_frame)
                cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'ir_img.png', self.ir_frame)
