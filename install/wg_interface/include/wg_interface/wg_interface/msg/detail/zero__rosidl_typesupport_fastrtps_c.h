// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice
#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "wg_interface/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "wg_interface/msg/detail/zero__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
bool cdr_serialize_wg_interface__msg__Zero(
  const wg_interface__msg__Zero * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
bool cdr_deserialize_wg_interface__msg__Zero(
  eprosima::fastcdr::Cdr &,
  wg_interface__msg__Zero * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
size_t get_serialized_size_wg_interface__msg__Zero(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
size_t max_serialized_size_wg_interface__msg__Zero(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
bool cdr_serialize_key_wg_interface__msg__Zero(
  const wg_interface__msg__Zero * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
size_t get_serialized_size_key_wg_interface__msg__Zero(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
size_t max_serialized_size_key_wg_interface__msg__Zero(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wg_interface
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, wg_interface, msg, Zero)();

#ifdef __cplusplus
}
#endif

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
