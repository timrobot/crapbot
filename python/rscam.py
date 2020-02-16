import pyrealsense2 as rs
import numpy as np

class RSCam(object):
  def __init__(self):
    # try opening the realsense2 pipeline
    self.pipeline = rs.pipeline()
    config = rs.config()
    # 640 width, 480 height, float16-bit depth, 30 framerate
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    # 640 width, 480 height, BGR24-bit color, 30 framerate
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    self.pipeline.start(config)

  def __del__(self):
    self.pipeline.stop()

  def update(self):
    # get the first depth image, use it as the "holder" of all the depth data
    # that comes in
    frames = self.pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    color = frames.get_color_frame()
    #depthData = depth.as_frame().get_data()
    self.__depthFrame__ = np.asanyarray(depth.get_data())
    self.__colorFrame__ = np.asanyarray(color.get_data())

  @property
  def depth(self):
    return self.__depthFrame__

  @property
  def color(self):
    return self.__colorFrame__

  @property
  def depthRGB(self):
    return np.sqrt(self.__depthFrame__.astype(np.float32)) / 255.0
