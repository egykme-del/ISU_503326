cmake_minimum_required(VERSION 3.8)
project(my_best_model)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch urdf config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
