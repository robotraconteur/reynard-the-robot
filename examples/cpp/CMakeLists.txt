cmake_minimum_required(VERSION 3.3)
project(reynard_robotraconteur_client)

set (CMAKE_CXX_STANDARD 11)

find_package(RobotRaconteur REQUIRED)

ROBOTRACONTEUR_GENERATE_THUNK(RR_THUNK_SRCS RR_THUNK_HDRS
    experimental.reynard_the_robot.robdef
	MASTER_HEADER
	INCLUDE_DIRS ${CMAKE_SOURCE_DIR}/../../robdef/
	AUTO_IMPORT
	)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

add_executable(reynard_robotraconteur_client
    reynard_robotraconteur_client.cpp
    ${RR_THUNK_SRCS} ${RR_THUNK_HDRS}
)

target_link_libraries(reynard_robotraconteur_client RobotRaconteurCore)
