cmake_minimum_required(VERSION 3.8)
project(bnl_projection)

find_package(ament_cmake REQUIRED)

install(
	PROGRAMS
		semantic_projection_node.py
		semantic_observation_stub_publisher.py
		semantic_xy_marker_node.py
	DESTINATION lib/${PROJECT_NAME}
)

ament_package()
