#!/usr/bin/env python

from utils.get_cfg import get_cfg
from utils.camerahandler import CameraHandler
from utils.webhandler import WebHandler

if __name__ == '__main__':
  cfg = get_cfg()
	
  cam = CameraHandler(cfg)
  cam.loop()
  
  web = WebHandler(cfg, cam)
  web.run()
