#pragma once

#include <opencv2/core/core.hpp>

namespace cb {
class FastCam {
public:
  void connect(int id=1) {
    cam = cv::VideoCapture(id);
    if (cam.isOpened()) {
      cam.set(cv::CAP_PROP_AUTOFOCUS, false);
      cam.set(cv::CAP_PROP_FRAME_WIDTH, 640);
      cam.set(cv::CAP_PROP_FPS, 260);
      cam.set(cv::CAP_PROP_SATURATION, 64);
    }
  }

  bool connected() {
    return cam.isOpened();
  }

  void read(cv::Mat& im) {
    cam.read(im);
  }

private:
  cv::VideoCapture cam;
};
}
