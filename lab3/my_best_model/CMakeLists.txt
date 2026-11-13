cmake_minimum_required(VERSION 3.8)
project(my_best_model)

# Find the ROS 2 build system.
find_package(ament_cmake REQUIRED)

# Copy resources to the installed package directory.
install(DIRECTORY launch urdf config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
