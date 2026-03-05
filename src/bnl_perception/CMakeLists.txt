cmake_minimum_required(VERSION 3.8)
project(bnl_perception)

find_package(ament_cmake REQUIRED)

install(
	PROGRAMS
		semantic_observation_node.py
	DESTINATION lib/${PROJECT_NAME}
	RENAME semantic_observation_node
)

install(
	PROGRAMS
		poll_detect_banana.py
	DESTINATION lib/${PROJECT_NAME}
	RENAME poll_detect_banana
)

install(
	DIRECTORY config
	DESTINATION share/${PROJECT_NAME}
)

ament_package()
