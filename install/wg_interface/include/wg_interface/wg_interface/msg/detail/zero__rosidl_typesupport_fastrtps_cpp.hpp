// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include <cstddef>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "wg_interface/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "wg_interface/msg/detail/zero__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace wg_interface
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
cdr_serialize(
  const wg_interface::msg::Zero & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  wg_interface::msg::Zero & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
get_serialized_size(
  const wg_interface::msg::Zero & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
max_serialized_size_Zero(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
cdr_serialize_key(
  const wg_interface::msg::Zero & ros_message,
  eprosima::fastcdr::Cdr &);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
get_serialized_size_key(
  const wg_interface::msg::Zero & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
max_serialized_size_key_Zero(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace wg_interface

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_wg_interface
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, wg_interface, msg, Zero)();

#ifdef __cplusplus
}
#endif

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
