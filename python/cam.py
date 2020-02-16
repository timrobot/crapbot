import cv2
import sys

class FastCam:
  def __init__(self):
    self.cam = None
    self._color = None
    self._depth = None

  def connect(self, _id=0):
    self.cam = cv2.VideoCapture(_id)
    if cam.isOpened():
      cam.set(cv2.CAP_PROP_AUTOFOCUS, false)
      cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
      cam.set(cv2.CAP_PROP_FPS, 260)
      cam.set(cv2.CAP_PROP_SATURATION, 64)

  def connected(self):
    return self.cam.isOpened()

  def update(self):
    res, self._color = cam.read()
    return res

  @property
  def color(self):
    return self._color

  @property
  def depth(self):
    return self._depth

class RS_D435i:
  def __init__(self):
    self.cam = None
    self._color = None
    self._depth = None

  def connect(self):
    # NOT IMPLEMENTED
    pass

  def connected(self):
    # NOT IMPLEMENTED
    return False

  def update(self):
    # NOT IMPLEMENTED
    return False

  @property
  def color(self):
    return self._color

  @property
  def depth(self):
    return self._depth
