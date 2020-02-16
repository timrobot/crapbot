import cv2
import sys

class FastCam:
  def __init__(self, _id=0):
    self.cam = None
    self._color = None
    self._depth = None
    if _id != -1:
      self.connect(_id)

  def connect(self, _id=0):
    self.cam = cv2.VideoCapture(_id)
    if self.cam.isOpened():
      self.cam.set(cv2.CAP_PROP_AUTOFOCUS, False)
      self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
      self.cam.set(cv2.CAP_PROP_FPS, 260)
      self.cam.set(cv2.CAP_PROP_SATURATION, 64)
    else:
      print("Could not open camera")

  def connected(self):
    return self.cam.isOpened()

  def read(self):
    res, self._color = self.cam.read()
    return self._color

  @property
  def color(self):
    return self._color

  @property
  def depth(self):
    return self._depth

if __name__ == "__main__":
  cam = FastCam()
  while True:
    im = cam.read()
    cv2.imshow("hi", im)
    cv2.waitKey(1)
