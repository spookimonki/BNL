cmake_minimum_required(VERSION 3.8)
project(bnl_sim)

find_package(ament_cmake REQUIRED)

# Install top-level sim assets into the package share so they are discoverable
# via ament_index / FindPackageShare after install.
install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../sim/worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../sim/models
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
