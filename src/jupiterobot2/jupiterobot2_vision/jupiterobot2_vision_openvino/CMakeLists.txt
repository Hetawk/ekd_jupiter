cmake_minimum_required(VERSION 3.10)
project(jupiterobot2_vision_openvino)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

find_package(OpenCV REQUIRED COMPONENTS core highgui videoio imgproc imgcodecs)
find_package(OpenVINO REQUIRED COMPONENTS Runtime)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  image_transport
  roscpp
  rospy
  sensor_msgs
  std_msgs
  tf
  OpenVINO
)

if(NOT BIN_FOLDER)
  string(TOLOWER ${CMAKE_SYSTEM_PROCESSOR} ARCH)
  if(ARCH STREQUAL "x86_64" OR ARCH STREQUAL "amd64")
    set(ARCH intel64)
  elseif(ARCH STREQUAL "i386")
    set(ARCH ia32)
  endif()
  set(BIN_FOLDER ${ARCH})
endif()

foreach(artifact IN ITEMS ARCHIVE COMPILE_PDB LIBRARY PDB RUNTIME)
  set("CMAKE_${artifact}_OUTPUT_DIRECTORY" "${CMAKE_CURRENT_BINARY_DIR}/${BIN_FOLDER}/$<CONFIG>")
endforeach()

if(CMAKE_CXX_COMPILER_ID MATCHES "^GNU|(Apple)?Clang$")
  set(COMPILER_IS_GCC_LIKE TRUE)
  add_compile_options(-Wall)
else()
  set(COMPILER_IS_GCC_LIKE FALSE)
endif()

if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm64.*|aarch64.*|AARCH64.*)")
  set(AARCH64 ON)
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm.*|ARM.*)")
  set(ARM ON)
endif()
if(ARM AND NOT CMAKE_CROSSCOMPILING)
  add_compile_options(-march=armv7-a+fp)
endif()

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if your package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES jupiterobot2_vision_openvino
#  CATKIN_DEPENDS cv_bridge image_transport roscpp rospy sensor_msgs std_msgs tf
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
  include/${PROJECT_NAME}
  include/${PROJECT_NAME}/interactive_face_detection
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${OpenVINO_DIR}/../include
)

set(UTILS_SOURCE_FILES
  src/utils/args_helper.cpp
  src/utils/common.cpp
  src/utils/images_capture.cpp
  src/utils/performance_metrics.cpp
)

add_library(utils_lib
  ${UTILS_SOURCE_FILES}
)

add_executable(interactive_face_ros 
  src/interactive_face_detection/detectors.cpp
  src/interactive_face_detection/face.cpp
  src/interactive_face_detection/visualizer.cpp
  src/interactive_face_ros.cpp)

target_link_libraries(utils_lib
  ${OpenCV_LIBRARIES}
  openvino::runtime
  gflags
)

target_link_libraries(interactive_face_ros
  ${catkin_LIBRARIES}
  ${OpenCV_LIBRARIES}
  openvino::runtime
  pthread
  utils_lib
)

## Declare a C++ library
# add_library(${PROJECT_NAME}
#   src/${PROJECT_NAME}/jupiterobot2_vision_openvino.cpp
# )

## Add cmake target dependencies of the library
## as an example, code may need to be generated before libraries
## either from message generation or dynamic reconfigure
# add_dependencies(${PROJECT_NAME} ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Declare a C++ executable
## With catkin_make all packages are built within a single CMake context
## The recommended prefix ensures that target names across packages don't collide
# add_executable(${PROJECT_NAME}_node src/jupiterobot2_vision_openvino_node.cpp)

## Rename C++ executable without prefix
## The above recommended prefix causes long target names, the following renames the
## target back to the shorter version for ease of user use
## e.g. "rosrun someones_pkg node" instead of "rosrun someones_pkg someones_pkg_node"
# set_target_properties(${PROJECT_NAME}_node PROPERTIES OUTPUT_NAME node PREFIX "")

## Add cmake target dependencies of the executable
## same as for the library above
# add_dependencies(${PROJECT_NAME}_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
# target_link_libraries(${PROJECT_NAME}_node
#   ${catkin_LIBRARIES}
# )

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
# catkin_install_python(PROGRAMS
#   scripts/my_python_script
#   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark executables for installation
## See http://docs.ros.org/melodic/api/catkin/html/howto/format1/building_executables.html
# install(TARGETS ${PROJECT_NAME}_node
#   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark libraries for installation
## See http://docs.ros.org/melodic/api/catkin/html/howto/format1/building_libraries.html
# install(TARGETS ${PROJECT_NAME}
#   ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   RUNTIME DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION}
# )

## Mark cpp header files for installation
# install(DIRECTORY include/${PROJECT_NAME}/
#   DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
#   FILES_MATCHING PATTERN "*.h"
#   PATTERN ".svn" EXCLUDE
# )

## Mark other files for installation (e.g. launch and bag files, etc.)
# install(FILES
#   # myfile1
#   # myfile2
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
# )

#############
## Testing ##
#############

## Add gtest based cpp test target and link libraries
# catkin_add_gtest(${PROJECT_NAME}-test test/test_jupiterobot2_vision_openvino.cpp)
# if(TARGET ${PROJECT_NAME}-test)
#   target_link_libraries(${PROJECT_NAME}-test ${PROJECT_NAME})
# endif()

## Add folders to be run by python nosetests
# catkin_add_nosetests(test)
