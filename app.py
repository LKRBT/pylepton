#!/usr/bin/env python

from utils.get_cfg import get_cfg
from utils.camerahandler import CameraHandler

import os

if __name__ == '__main__':
  cfg = get_cfg()
  if not os.path.exists(cfg['PI']['FILE_PATH']):
    os.makedirs(cfg['PI']['FILE_PATH'])

  cam = CameraHandler(cfg)
  cam.loop()
