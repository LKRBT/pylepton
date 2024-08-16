#!/usr/bin/env python

from utils.get_cfg import get_cfg
from utils.camerahandler import CameraHandler

if __name__ == '__main__':
  cfg = get_cfg()
	
  cam = CameraHandler(cfg)
  cam.loop()