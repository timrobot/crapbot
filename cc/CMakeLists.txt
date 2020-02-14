find_package(OpenCV REQUIRED)

include_directories(
  ${OpenCV_INCLUDE_DIRS})

add_definitions(
  ${OpenCV_DEFINITIONS})

add_library(pyshm SHARED
  pyshm.cc)
target_link_libraries(pyshm
  ${OpenCV_LIBRARIES})
