import cv2

from flask import Flask, Response, render_template


class WebHandler:
    def __init__(self, cfg, obj):
        self.app = Flask(__name__)
        
        self.cfg = cfg
        self.cam_handler = obj
        self.setup_routes()
        
    def setup_routes(self):
        self.app.add_url_rule('/video_feed_rgb', 'video_feed_rgb', self.video_feed_rgb)
        self.app.add_url_rule('/video_feed_ir', 'video_feed_ir', self.video_feed_ir)
        self.app.add_url_rule('/detection', 'detection', self.detection)
        self.app.add_url_rule('/stream', 'stream', self.stream)
        self.app.add_url_rule('/', 'home', self.home)
            
    def generate_rgb_frames(self):
        while True:
            frame = self.cam_handler.rgb_frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def generate_ir_frames(self):
        while True:
            frame = self.cam_handler.ir_frame
            _, buffer = cv2.imencode('.png', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

    def video_feed_rgb(self):
        return Response(self.generate_rgb_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def video_feed_ir(self):
        return Response(self.generate_ir_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def detection(self):
        return render_template('detection.html')
        
    def stream(self):
        return render_template('stream.html')
        
    def home(self):
        return render_template('home.html')

    def run(self):
        self.app.run(host=self.cfg['PI']['HOST'], port=self.cfg['PI']['PORT'])
