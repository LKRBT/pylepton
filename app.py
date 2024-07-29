import sys
import cv2
import time
import threading
import numpy as np

from get_cfg import get_cfg
# from send_sms import send_sms
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton

cfg = get_cfg()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('RGB and IR Frames')

        self.rgb_label = QLabel(self)
        self.ir_label = QLabel(self)
		
        self.start_button = QPushButton('Start Camera', self)
        self.start_button.clicked.connect(self.start_cameras)

        self.stop_button = QPushButton('Stop Camera', self)
        self.stop_button.clicked.connect(self.stop_cameras)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.rgb_label)
        hbox.addWidget(self.ir_label)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.stop_button)
        
        self.setLayout(vbox)

        self.rgb_timer = QTimer(self)
        self.rgb_timer.timeout.connect(self.update_rgb_frame)
       
        self.ir_timer = QTimer(self)
        self.ir_timer.timeout.connect(self.update_ir_frame)
        
        self.picam2 = Picamera2()
    
    def start_cameras(self):
        self.picam2.start()
        self.rgb_timer.start(0)  
        self.ir_timer.start(0)  
    
    def stop_cameras(self):
        self.rgb_timer.stop()
        self.ir_timer.stop()
        self.picam2.stop()
        
    def update_rgb_frame(self):
        frame = self.capture_rgb()
        rgb_image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        self.rgb_label.setPixmap(QPixmap.fromImage(rgb_image))

    def update_ir_frame(self):
        frame = self.capture_ir()
        ir_image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_Grayscale8)
        self.ir_label.setPixmap(QPixmap.fromImage(ir_image))

    def capture_rgb(self):
        frame = self.picam2.capture_array("main")
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame
	
    def capture_ir(self, flip_v=False, device=cfg['PI']['SERIAL_PORT']):
        with Lepton3(device) as l:
            a, _ = l.capture()

        if flip_v:
            cv2.flip(a, 0, a)

        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        new_width = a.shape[1] * 4
        new_height = a.shape[0] * 4
        a = cv2.resize(a, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
        return np.uint8(a)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
