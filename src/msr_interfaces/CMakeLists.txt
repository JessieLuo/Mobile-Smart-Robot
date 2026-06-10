cmake_minimum_required(VERSION 3.8)
project(msr_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObjectDetection.msg"
  "msg/ObjectDetections.msg"
  "msg/TaskCommand.msg"
  "msg/TaskState.msg"
  "msg/ArmStatus.msg"
  "msg/VoiceCommand.msg"
  "msg/ToolCall.msg"
  "msg/ToolResult.msg"

  "srv/ParseTask.srv"
  "srv/DetectTarget.srv"
  "srv/AlignTarget.srv"
  "srv/PickObject.srv"
  "srv/PlaceObject.srv"
  "srv/NavigateToSemantic.srv"
  "srv/EmergencyStop.srv"

  "action/SortWaste.action"
  "action/PickPlace.action"
  "action/ExecuteTask.action"

  DEPENDENCIES
    builtin_interfaces
    std_msgs
    geometry_msgs
    action_msgs
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()